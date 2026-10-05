"""Knowledge graph extraction agent.

Turns a user's own records (memories, resources, ideas, tasks, courses,
goals) into ``knowledge_nodes`` / ``knowledge_edges`` rows.

Two extraction paths, same output contract:

* :func:`llm_extract` — asks the configured provider for entities and
  relations, then *validates* every field before it can reach the
  database. The model's output is never trusted: unknown node types are
  coerced, labels and summaries are truncated, edge endpoints that do not
  resolve to a real node in the batch are dropped.
* :func:`algorithmic_fallback_extract` — deterministic, no LLM, no
  network. Entities come from the row's own tags plus noun-phrase and
  acronym extraction over its title, and relations come from explicit
  column references (a task pointing at its goal), verbatim title
  mentions, and shared tags.

Both paths return ``(node_proposals, edge_proposals)`` where a proposal
is a plain dict keyed by the source row it came from, so
:func:`extract_knowledge_graph` persists them identically.

Idempotency
-----------
A node's identity is ``(user_id, type, source_table, source_id)``. Every
record therefore produces exactly one node no matter how many times
extraction runs. Proposals carrying no source row (entities the LLM
invented) get a deterministic uuid5-derived ``source_id`` so they dedupe
the same way. Writes go through ``.upsert(on_conflict=...)`` on the
``uq_knowledge_nodes_user_source`` unique index from migration 017, with a
per-row update/insert fallback for databases where that index is absent.
Edges dedupe on the ``UNIQUE (user_id, source_id, target_id, relation)``
constraint that migration 015 already declares.

Every query in this module is filtered by ``user_id``.
"""

import json
import re
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from config.core.supabase import get_supabase_client
from database.schemas.knowledge import (
    DEFAULT_RELATION,
    VALID_NODE_TYPES,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)
from shared.utils.logger import logger
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts

# uuid5 namespace for synthesising stable source_ids for LLM-invented
# entities. Fixed constant so a re-run derives the same id.
_ENTITY_NAMESPACE = uuid.UUID("6f1c9f4a-1c4e-5a7b-9d3f-2b8e7a0c5d41")

# Row budget per source table for a single run.
_MAX_ROWS_PER_SOURCE = 50
# Global caps. Keeps one run from turning a large account into an
# unbounded write fan-out.
_MAX_NODES_PER_RUN = 300
_MAX_EDGES_PER_RUN = 400
# Read bounds for the id/degree resolution passes.
_MAX_NODE_SCAN = 2000
_MAX_EDGE_SCAN = 4000
# PostgREST row limits for the write fan-out.
_WRITE_CHUNK = 50

# Text handling
_MAX_TEXT_LEN = 4000
_MAX_LABEL_LEN = 200
_MAX_SUMMARY_LEN = 280
_MAX_TAG_LEN = 40
_MAX_TAGS_PER_NODE = 8

# Relation derivation
_MAX_TAG_NEIGHBOURS = 6
_MAX_TOKEN_DOC_FREQ = 12
_MIN_SHARED_DERIVED_TAGS = 2
_MIN_MENTION_TOKENS = 2

# Relations that mean the same thing in both directions, so their endpoint
# order carries no information and can be canonicalised. Everything else
# (contributes_to, supports, mentions, references) is directional and keeps
# the orientation its producer chose.
_SYMMETRIC_RELATIONS = frozenset({"related_to", "shares_tag"})

# Explicit references: source column -> (target table, relation verb).
# Only tables that become nodes can be edge targets, which is why
# project_id (projects is not a graph source) is absent.
_GOAL_REF_SPEC: Dict[str, Tuple[str, str]] = {
    "goal_id": ("goals", "contributes_to"),
    "related_goal_id": ("goals", "supports"),
}

# knowledge_nodes tags live as JSONB; memory rows carry their own tag array
# alongside a JSONB `value`, so both need normalising before use.

_SOURCE_SPECS: Dict[str, Dict[str, Any]] = {
    "memory": {
        "node_type": "memory",
        "columns": "id, type, key, value, importance, tags, created_at",
        "label_fields": ("key",),
        "text_fields": ("value",),
        "tag_fields": ("tags",),
        "created_at": "created_at",
        "weight": 0.8,
    },
    "resources": {
        "node_type": "resource",
        "columns": "id, title, url, resource_type, tags, notes, saved_at",
        "label_fields": ("title",),
        "text_fields": ("notes", "resource_type"),
        "tag_fields": ("tags",),
        "created_at": "saved_at",
        "weight": 0.7,
    },
    "ideas": {
        "node_type": "idea",
        "columns": "id, title, description, idea_type, status, created_at",
        "label_fields": ("title",),
        "text_fields": ("description", "idea_type"),
        "tag_fields": (),
        "created_at": "created_at",
        "weight": 0.6,
    },
    "tasks": {
        "node_type": "task",
        "columns": "id, title, description, priority, category, status, goal_id, created_at",
        "label_fields": ("title",),
        "text_fields": ("description", "category"),
        "tag_fields": (),
        "created_at": "created_at",
        "weight": 0.9,
    },
    "courses": {
        "node_type": "course",
        "columns": "id, title, platform, why_enrolled, status, progress_percent, related_goal_id, created_at",
        "label_fields": ("title",),
        "text_fields": ("why_enrolled", "platform"),
        "tag_fields": (),
        "created_at": "created_at",
        "weight": 1.2,
    },
    "goals": {
        "node_type": "goal",
        "columns": "id, title, description, roadmap_type, status, created_at",
        "label_fields": ("title",),
        "text_fields": ("description", "roadmap_type"),
        "tag_fields": (),
        "created_at": "created_at",
        "weight": 1.3,
    },
}

_SOURCE_ORDER = ("memory", "resources", "ideas", "tasks", "courses", "goals")

_STOPWORDS = frozenset("""
    a about above after again against all also am an and any are aren as at be because been before being below
    between both but by can cannot could couldn did didn do does doesn doing don down during each few for from
    further had hadn has hasn have haven having he her here hers herself him himself his how i if in into is isn
    it its itself just let me more most mustn my myself no nor not of off on once only or other ought our ours
    ourselves out over own same shan she should shouldn so some such than that the their theirs them themselves
    then there these they this those through to too under until up very was wasn we were weren what when where
    which while who whom why will with won would wouldn you your yours yourself yourselves
    """.split())

_HASHTAG_RE = re.compile(r"#([A-Za-z][A-Za-z0-9_-]{1,39})")
_QUOTED_RE = re.compile(r"[\"“]([A-Za-z][A-Za-z0-9 _-]{2,40})[\"”]")
_ACRONYM_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,7})\b")
_TITLE_PHRASE_RE = re.compile(r"\b([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+){1,3})\b")
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9+#.-]{2,}")
_UUID_RE = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
# Anything that could break out of a PostgREST filter value.
_UNSAFE_SEARCH_CHARS_RE = re.compile(r"[^A-Za-z0-9 _-]+")

_NODE_KEY_SEP = "|"


def _node_key(node_type: str, source_table: str, source_id: str) -> str:
    """Identity of a node: (type, source table, source row)."""
    return f"{node_type}{_NODE_KEY_SEP}{source_table}{_NODE_KEY_SEP}{source_id}"


def _edge_key(source_id: str, target_id: str, relation: str) -> str:
    """Matches UNIQUE (user_id, source_id, target_id, relation) from 015."""
    return f"{source_id}{_NODE_KEY_SEP}{target_id}{_NODE_KEY_SEP}{relation}"


# ---------------------------------------------------------------------------
# Text helpers — deterministic entity/tag extraction
# ---------------------------------------------------------------------------


def _as_text(value: Any) -> str:
    """Flatten any column value to searchable text.

    ``memory.value`` is JSONB written in two shapes (see the note in
    migration 015 lines 73-81): a raw object or a JSON-encoded string.
    Both have to flatten to something tag extraction can read.
    """
    if value is None:
        return ""
    if isinstance(value, str):
        text = value
    elif isinstance(value, (dict, list)):
        try:
            text = json.dumps(value, default=str)
        except (TypeError, ValueError):
            text = str(value)
    else:
        text = str(value)
    return text[:_MAX_TEXT_LEN]


def normalise_tag(raw: str) -> Optional[str]:
    """Fold one candidate tag into its canonical slug, or drop it.

    Canonical form is lowercase with runs of non-alphanumerics collapsed to
    a single hyphen. Returns None for anything that would produce a
    useless filter chip: empty strings, bare digits, and one-letter tags.
    """
    if not raw:
        return None
    slug = re.sub(r"[^a-z0-9]+", "-", raw.strip().lower()).strip("-")
    if len(slug) < 2 or slug.isdigit():
        return None
    return slug[:_MAX_TAG_LEN]


def extract_tags_from_text(text: str, limit: int = _MAX_TAGS_PER_NODE) -> List[str]:
    """Pull entity-like tags out of free text, deterministically.

    Four passes, in descending order of how much signal they carry:
    hashtags, quoted terms, ALLCAPS acronyms (ML, NLP, DSA), Title Case
    multi-word phrases (Machine Learning), then salient single words.
    Everything is stopword-filtered, normalised and de-duplicated.
    """
    if not text:
        return []

    ordered: List[str] = []

    def push(candidate: str) -> None:
        slug = normalise_tag(candidate)
        if slug and slug not in ordered and slug not in _STOPWORDS:
            ordered.append(slug)

    for match in _HASHTAG_RE.findall(text):
        push(match)
    for match in _QUOTED_RE.findall(text):
        push(match)
    for match in _ACRONYM_RE.findall(text):
        push(match)
    for match in _TITLE_PHRASE_RE.findall(text):
        phrase_words = [w for w in re.split(r"\s+", match) if w.lower() not in _STOPWORDS]
        if len(phrase_words) >= 2:
            push(match)

    # Salient single words, only from the title-ish part of the text so
    # long descriptions do not flood the tag list with noise.
    for word in _WORD_RE.findall(text[:400]):
        lowered = word.lower().strip(".-")
        if len(lowered) < 4 or lowered in _STOPWORDS or lowered.isdigit():
            continue
        push(lowered)

    return ordered[:limit]


def salient_tokens(text: str, limit: int = 12) -> List[str]:
    """Distinctive lowercase words used to propose ``related_to`` edges.

    Four characters minimum and no stopwords, so "the" and "a" can never
    link two unrelated records.
    """
    tokens: List[str] = []
    for word in _WORD_RE.findall(_as_text(text)[:600]):
        lowered = word.lower().strip(".-")
        if len(lowered) < 4 or lowered in _STOPWORDS or lowered.isdigit():
            continue
        if lowered not in tokens:
            tokens.append(lowered)
        if len(tokens) >= limit:
            break
    return tokens


def _first_text(row: Dict[str, Any], fields: Tuple[str, ...]) -> str:
    for field in fields:
        value = _as_text(row.get(field)).strip()
        if value:
            return value
    return ""


# ---------------------------------------------------------------------------
# Record collection
# ---------------------------------------------------------------------------


def _record_tags(row: Dict[str, Any], tag_fields: Tuple[str, ...], label: str) -> Tuple[List[str], List[str]]:
    """Return (all tags, explicit tags) for one source row.

    Explicit tags come from the row's own tag column (resources.tags,
    memory.tags) and are the high-confidence half: sharing a single
    explicit tag is enough to justify an edge. Derived tags come from
    label/summary text and need two before they count.
    """
    explicit: List[str] = []
    for field in tag_fields:
        value = row.get(field)
        candidates: List[Any]
        if isinstance(value, str):
            candidates = [value]
        elif isinstance(value, (list, tuple)):
            candidates = list(value)
        else:
            candidates = []
        for candidate in candidates:
            slug = normalise_tag(_as_text(candidate))
            if slug and slug not in explicit:
                explicit.append(slug)

    derived = extract_tags_from_text(label)
    summary_text = _first_text(row, ("summary", "description", "notes", "why_enrolled", "value"))
    for tag in extract_tags_from_text(summary_text, limit=4):
        if tag not in derived:
            derived.append(tag)

    all_tags = explicit + [t for t in derived if t not in explicit]
    return all_tags[:_MAX_TAGS_PER_NODE], explicit[:_MAX_TAGS_PER_NODE]


def _build_record(row: Dict[str, Any], source_table: str) -> Optional[Dict[str, Any]]:
    """Turn one database row into the extractor's internal record shape."""
    spec = _SOURCE_SPECS[source_table]
    source_id = row.get("id")
    if not source_id:
        return None

    label = _first_text(row, tuple(spec["label_fields"]))
    if not label:
        label = str(source_id)
    label = label[:_MAX_LABEL_LEN]

    text_fields = [_as_text(row.get(field)) for field in spec["text_fields"]]
    body = " ".join(part for part in text_fields if part)[:_MAX_TEXT_LEN]
    all_tags, explicit_tags = _record_tags(row, tuple(spec["tag_fields"]), label)

    # Weight encodes salience for layout: a filled-in row outranks a bare
    # one, and hubs (goals, courses) carry more graph weight than leaves.
    weight = float(spec["weight"])
    if body.strip():
        weight += 0.1
    if explicit_tags:
        weight += 0.1
    weight = round(min(weight, 2.0), 2)

    # Explicit column references (task.goal_id -> goals row).
    references: List[Dict[str, str]] = []
    seen_refs: Set[str] = set()
    for column, (target_table, relation) in _GOAL_REF_SPEC.items():
        target_id = row.get(column)
        if target_id and f"{target_table}:{target_id}" not in seen_refs:
            seen_refs.add(f"{target_table}:{target_id}")
            references.append(
                {
                    "source_table": source_table,
                    "source_id": str(source_id),
                    "target_table": target_table,
                    "target_id": str(target_id),
                    "relation": relation,
                }
            )

    # UUIDs pasted into prose (a task description citing a resource row).
    for match in _UUID_RE.findall(body):
        if f"{source_table}:{match}" in seen_refs:
            continue
        seen_refs.add(f"{source_table}:{match}")
        references.append(
            {
                "source_table": source_table,
                "source_id": str(source_id),
                "target_table": "",
                "target_id": match,
                "relation": "references",
            }
        )

    return {
        "source_table": source_table,
        "source_id": str(source_id),
        "node_type": spec["node_type"],
        "label": label,
        "summary": body[:_MAX_SUMMARY_LEN] or None,
        "tags": all_tags,
        "explicit_tags": explicit_tags,
        "weight": weight,
        "created_at": row.get(spec["created_at"]),
        "text": f"{label} {body}",
        "references": references,
    }


def _fetch_source_rows(user_id: str, source_table: str, limit: int) -> List[Dict[str, Any]]:
    """Read one source table for one user. Always filtered by user_id.

    Ordered by the table's own timestamp column, which is not uniform:
    ``resources`` has ``saved_at`` and no ``created_at`` at all, so
    ordering on a hardcoded ``created_at`` would make PostgREST reject the
    whole query and silently drop the table.
    """
    spec = _SOURCE_SPECS[source_table]
    response = (
        get_supabase_client()
        .from_(source_table)
        .select(spec["columns"])
        .eq("user_id", user_id)
        .order(spec["created_at"], ascending=False)
        .limit(limit)
        .execute()
    )
    return response.data or []


async def collect_records(
    user_id: str, sources: Optional[List[str]] = None, limit_per_source: int = 50
) -> List[Dict[str, Any]]:
    """Read every requested source table for ``user_id`` and normalise rows.

    A table that fails to read is logged and skipped rather than failing
    the whole run — one missing table must not cost the user the graph.
    """
    wanted = [s for s in (sources or list(_SOURCE_ORDER)) if s in _SOURCE_SPECS]
    records: List[Dict[str, Any]] = []
    for source_table in wanted:
        try:
            rows = _fetch_source_rows(user_id, source_table, limit_per_source)
        except Exception as exc:
            logger.error("Knowledge source read failed", user_id=user_id, source_table=source_table, error=exc)
            continue
        for row in rows:
            record = _build_record(row, source_table)
            if record is not None:
                records.append(record)
    records.sort(key=lambda r: (r["source_table"], r["source_id"]))
    return records[:_MAX_NODES_PER_RUN]


# ---------------------------------------------------------------------------
# Algorithmic extraction (no LLM)
# ---------------------------------------------------------------------------


def _tag_inverted_index(records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    index: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for record in records:
        for tag in record["tags"]:
            index[tag].append(record)
    return index


def _share_tag_edges(index: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Connect records that share a tag.

    One shared *explicit* tag is enough (the user tagged both rows on
    purpose). Shared *derived* tags need two, otherwise every record
    containing the word "project" collapses into one giant hub. Each
    record gains at most ``_MAX_TAG_NEIGHBOURS`` tag-derived edges so a
    single popular tag cannot dominate the graph.
    """
    edges: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    connected_per_record: Counter = Counter()

    for tag, group in sorted(index.items()):
        if len(group) < 2:
            continue
        explicit = any(tag in member["explicit_tags"] for member in group)
        threshold = 1 if explicit else _MIN_SHARED_DERIVED_TAGS
        group = sorted(group, key=lambda r: (r["source_table"], r["source_id"]))
        for i, left in enumerate(group):
            for right in group[i + 1 :]:
                if connected_per_record[left["_order"]] >= _MAX_TAG_NEIGHBOURS:
                    continue
                if connected_per_record[right["_order"]] >= _MAX_TAG_NEIGHBOURS:
                    continue
                shared = _shared_tags(left, right)
                if len(shared) < threshold:
                    continue
                edge = {
                    "source_table": left["source_table"],
                    "source_id": left["source_id"],
                    "target_table": right["source_table"],
                    "target_id": right["source_id"],
                    "relation": "shares_tag",
                    "weight": round(min(1.0, 0.4 + 0.2 * len(shared)), 2),
                }
                key = _proposal_key(edge)
                if key in seen:
                    continue
                seen.add(key)
                edges.append(edge)
                connected_per_record[left["_order"]] += 1
                connected_per_record[right["_order"]] += 1
    return edges


def _shared_tags(left: Dict[str, Any], right: Dict[str, Any]) -> List[str]:
    right_tags = set(right["_tag_set"])
    return [tag for tag in left["tags"] if tag in right_tags]


def _token_inverted_index(records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    index: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for record in records:
        for token in record["_tokens"]:
            index[token].append(record)
    return index


def _related_to_edges(index: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Propose ``related_to`` between records that share distinctive words.

    Rare tokens only: a word appearing in more than
    ``_MAX_TOKEN_DOC_FREQ`` records carries no signal and is skipped, which
    is what stops "study" from wiring the whole dataset together. A pair
    needs ``_MIN_SHARED_DERIVED_TAGS`` rare words in common before it is
    linked.
    """
    edges: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for token in sorted(index):
        group = index[token]
        if len(group) < 2 or len(group) > _MAX_TOKEN_DOC_FREQ:
            continue
        group = sorted(group, key=lambda r: (r["source_table"], r["source_id"]))
        for i, left in enumerate(group):
            for right in group[i + 1 :]:
                if left["source_id"] == right["source_id"]:
                    continue
                shared = _shared_rare_tokens(left, right, index)
                if shared < _MIN_SHARED_DERIVED_TAGS:
                    continue
                edge = {
                    "source_table": left["source_table"],
                    "source_id": left["source_id"],
                    "target_table": right["source_table"],
                    "target_id": right["source_id"],
                    "relation": DEFAULT_RELATION,
                    "weight": round(min(0.9, 0.3 + 0.1 * shared), 2),
                }
                key = _proposal_key(edge)
                if key in seen:
                    continue
                seen.add(key)
                edges.append(edge)
    return edges


def _shared_rare_tokens(left: Dict[str, Any], right: Dict[str, Any], index: Dict[str, List[Dict[str, Any]]]) -> int:
    """Count low-frequency tokens the two records have in common."""
    right_tokens = right["_token_set"]
    return sum(
        1 for token in left["_token_set"] if token in right_tokens and len(index.get(token, [])) <= _MAX_TOKEN_DOC_FREQ
    )


def _mention_edges(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Link a record whose prose names another record's title verbatim.

    The needle has to be at least six characters and carry
    ``_MIN_MENTION_TOKENS`` distinctive words, so a one-word label like
    "Read" cannot match everything.
    """
    edges: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for record in records:
        haystack = record["text"].lower()
        for other in records:
            if other["source_id"] == record["source_id"]:
                continue
            needle = other["label"].strip().lower()
            if len(needle) < 6 or needle not in haystack:
                continue
            label_tokens = [t for t in other["_token_set"] if len(t) >= 4]
            if len(label_tokens) < _MIN_MENTION_TOKENS:
                continue
            edge = {
                "source_table": record["source_table"],
                "source_id": record["source_id"],
                "target_table": other["source_table"],
                "target_id": other["source_id"],
                "relation": "mentions",
                "weight": 0.8,
            }
            key = _proposal_key(edge)
            if key in seen:
                continue
            seen.add(key)
            edges.append(edge)
    return edges


def _reference_edges(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Explicit column references (task.goal_id) plus pasted UUID citations.

    Only edges whose target is present in this batch survive the
    resolution pass in :func:`_resolve_edge_targets` — a goal that was not
    in the extraction window produces no dangling row.
    """
    edges: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for record in records:
        for reference in record["references"]:
            edge = dict(reference)
            key = _proposal_key(edge)
            if key in seen:
                continue
            seen.add(key)
            edges.append(edge)
    return edges


def _proposal_key(edge: Dict[str, Any]) -> str:
    """Dedup key for an edge *proposal*, which is keyed by source row.

    Proposals run before node ids exist, so they are keyed by
    (source_table, source_id, target_table, target_id, relation) — the
    relation is part of the key because the same pair may legitimately
    hold both a ``shares_tag`` and a ``mentions`` edge.
    """
    return _NODE_KEY_SEP.join(
        [
            edge["source_table"],
            edge["source_id"],
            edge.get("target_table") or "",
            edge["target_id"],
            edge["relation"],
        ]
    )


def _prepare_records(records: List[Dict[str, Any]]) -> None:
    """Annotate records with the derived sets the edge passes reuse.

    Done once up front: recomputing tokens per candidate pair is what turns
    a linear pass into a quadratic one.
    """
    for order, record in enumerate(records):
        record["_order"] = order
        record["_tag_set"] = set(record["tags"])
        record["_tokens"] = salient_tokens(record["text"])
        record["_token_set"] = set(record["_tokens"])


def algorithmic_fallback_extract(records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Deterministic extraction. No LLM, no network, no randomness.

    Nodes: one per source record, carrying the row's own tags plus tags
    derived from its title and body by :func:`extract_tags_from_text`.

    Edges, in descending confidence:
      * ``contributes_to`` / ``supports`` — explicit column reference
        (tasks.goal_id, courses.related_goal_id, resources.related_goal_id).
      * ``references`` — a UUID pasted into prose.
      * ``mentions`` — another record's title quoted verbatim.
      * ``shares_tag`` — one shared explicit tag, or two shared derived tags.
      * ``related_to`` — two distinctive low-frequency words in common.
    """
    _prepare_records(records)
    if not records:
        return [], []

    nodes = [
        {
            "type": record["node_type"],
            "label": record["label"],
            "summary": record["summary"],
            "tags": record["tags"],
            "source_table": record["source_table"],
            "source_id": record["source_id"],
            "weight": record["weight"],
        }
        for record in records
    ]

    edges: List[Dict[str, Any]] = []
    edges.extend(_reference_edges(records))
    edges.extend(_mention_edges(records))
    edges.extend(_share_tag_edges(_tag_inverted_index(records)))
    edges.extend(_related_to_edges(_token_inverted_index(records)))

    return nodes, _resolve_edge_targets(edges, records)


def _resolve_edge_targets(edges: List[Dict[str, Any]], records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Drop self-edges, edges with no resolvable target, and duplicates.

    A reference carries an empty ``target_table`` when the target row is
    only known by id (a UUID pasted into prose); the id alone is then
    resolved against the batch.

    Direction is meaningful — ``goal <-contributes_to- task`` is the wrong
    reading, so a directional relation keeps the orientation the producer
    chose. Only the symmetric relations are reordered into a canonical
    direction so the same pair always hashes to the same UNIQUE key.
    Deduplication is still unordered, so a pair cannot be linked twice
    with the same relation just because two passes proposed it in opposite
    directions.
    """
    by_table_and_id = {(r["source_table"], r["source_id"]): r for r in records}
    by_id: Dict[str, Dict[str, Any]] = {}
    for record in records:
        by_id.setdefault(record["source_id"], record)

    resolved: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for edge in edges:
        source = (edge["source_table"], edge["source_id"])
        target = edge.get("target_table") or ""
        target_id = edge["target_id"]
        source_record = by_table_and_id.get(source)
        target_record = by_id.get(target_id) if not target else by_table_and_id.get((target, target_id))
        if source_record is None or target_record is None:
            continue
        if source_record["source_id"] == target_record["source_id"]:
            continue

        relation = edge["relation"]
        orientation = _NODE_KEY_SEP.join([source[0], source[1], target, target_id])
        if relation in _SYMMETRIC_RELATIONS and orientation > _NODE_KEY_SEP.join(
            [target, target_id, source[0], source[1]]
        ):
            source_record, target_record = target_record, source_record

        key = _NODE_KEY_SEP.join(sorted([orientation, _NODE_KEY_SEP.join([target, target_id, source[0], source[1]])]))
        if relation not in _SYMMETRIC_RELATIONS:
            key = _NODE_KEY_SEP.join([key, relation])
        if key in seen:
            continue
        seen.add(key)

        resolved.append(
            {
                "source_table": source_record["source_table"],
                "source_id": source_record["source_id"],
                "target_table": target_record["source_table"],
                "target_id": target_record["source_id"],
                "relation": relation,
                "weight": edge.get("weight", 1.0),
            }
        )
    return resolved[:_MAX_EDGES_PER_RUN]


# ---------------------------------------------------------------------------
# LLM extraction
# ---------------------------------------------------------------------------

# No prompts/agents/knowledge_agent.md exists. The memory_agent prompt
# cannot be reused: it instructs the model to emit memories_to_create /
# memories_to_update / memories_to_discard, which would actively fight the
# entity-extraction contract below. The loader call is kept so that adding
# the prompt file later needs no code change.
_INLINE_EXTRACTION_SYSTEM = (
    "You are ARIA's Knowledge Graph extraction agent. You read a batch of a single student's own "
    "records (memories, resources, ideas, tasks, courses, goals) and return the entities they mention "
    "plus the relations between them.\n"
    "Respond with ONLY a JSON object, no prose and no code fence:\n"
    '{"nodes": [{"type": "note|resource|idea|memory|course|task|goal", "label": "...", '
    '"summary": "...", "tags": ["..."], "source_table": "resources|ideas|tasks|courses|goals|memory|extracted", '
    '"source_id": "uuid", "weight": 1.0}], '
    '"edges": [{"source_table": "...", "source_id": "...", "target_table": "...", "target_id": "...", '
    '"relation": "related_to|shares_tag|mentions|references|contributes_to|supports", "weight": 1.0}]}\n'
    "Rules:\n"
    "1. Every source_id MUST be copied verbatim from the input batch. Never invent or modify a UUID.\n"
    "2. Use source_table 'extracted' with a fresh uuid5-style id only for a genuinely new entity that no "
    "record covers; prefer reusing an existing record as the node.\n"
    "3. An edge endpoint must reference a node you emitted, or a record present in the batch.\n"
    "4. Never emit a self-edge, and never emit the same edge twice.\n"
    "5. label <= 200 chars, summary <= 280 chars, tags are lowercase slugs, max 8 tags per node.\n"
    "6. Prefer few high-confidence relations over many speculative ones. If a relation is not supported by "
    "the text, omit it."
)


def _coerce_llm_node(raw: Any, allowed_tables: Set[str]) -> Optional[Dict[str, Any]]:
    """Validate one LLM node proposal. Returns None if unusable.

    Every field is treated as hostile: the type must be one of the seven
    the CHECK constraint allows, the label must be a non-empty string that
    fits the column, and the source row must be either a table in this
    batch or 'extracted'.
    """
    if not isinstance(raw, dict):
        return None
    node_type = raw.get("type")
    if not isinstance(node_type, str) or node_type not in VALID_NODE_TYPES:
        return None
    label = raw.get("label")
    if not isinstance(label, str) or not label.strip():
        return None
    label = label.strip()[:_MAX_LABEL_LEN]

    source_table = raw.get("source_table")
    source_table = source_table if isinstance(source_table, str) and source_table else "extracted"
    source_id = raw.get("source_id")
    source_id = source_id.strip() if isinstance(source_id, str) and source_id.strip() else ""

    if source_table == "extracted":
        # Derived, not copied: force a stable synthetic id so a re-run
        # collapses onto the same node instead of adding a new one. The
        # model is not asked for this id, so it may be absent.
        source_id = str(uuid.uuid5(_ENTITY_NAMESPACE, f"{node_type}:{label.lower()}"))
    elif source_table not in allowed_tables or not source_id:
        return None

    summary = raw.get("summary")
    summary = summary.strip()[:_MAX_SUMMARY_LEN] if isinstance(summary, str) and summary.strip() else None

    tags: List[str] = []
    raw_tags = raw.get("tags")
    if isinstance(raw_tags, list):
        for candidate in raw_tags:
            slug = normalise_tag(_as_text(candidate))
            if slug and slug not in tags:
                tags.append(slug)
            if len(tags) >= _MAX_TAGS_PER_NODE:
                break

    weight = raw.get("weight", 1.0)
    try:
        weight = round(min(2.0, max(0.1, float(weight))), 2)
    except (TypeError, ValueError):
        weight = 1.0

    return {
        "type": node_type,
        "label": label,
        "summary": summary,
        "tags": tags,
        "source_table": source_table,
        "source_id": source_id,
        "weight": weight,
    }


def _coerce_llm_edge(raw: Any, known_ids: Set[str]) -> Optional[Dict[str, Any]]:
    """Validate one LLM edge proposal against the emitted node ids."""
    if not isinstance(raw, dict):
        return None
    relation = raw.get("relation")
    if not isinstance(relation, str) or not relation.strip():
        return None
    relation = relation.strip()[:40]
    source_id = raw.get("source_id")
    target_id = raw.get("target_id")
    if not isinstance(source_id, str) or not isinstance(target_id, str):
        return None
    source_id, target_id = source_id.strip(), target_id.strip()
    if not source_id or not target_id or source_id == target_id:
        return None
    if source_id not in known_ids or target_id not in known_ids:
        return None

    source_table = raw.get("source_table")
    target_table = raw.get("target_table")
    weight = raw.get("weight", 1.0)
    try:
        weight = round(min(2.0, max(0.1, float(weight))), 2)
    except (TypeError, ValueError):
        weight = 1.0

    return {
        "source_table": source_table if isinstance(source_table, str) and source_table else "extracted",
        "source_id": source_id,
        "target_table": target_table if isinstance(target_table, str) and target_table else "extracted",
        "target_id": target_id,
        "relation": relation,
        "weight": weight,
    }


def _batch_for_prompt(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Compact, token-bounded view of the batch handed to the model."""
    return [
        {
            "source_table": record["source_table"],
            "source_id": record["source_id"],
            "type": record["node_type"],
            "label": record["label"],
            "summary": record["summary"],
            "tags": record["tags"],
        }
        for record in records
    ]


async def llm_extract(records: List[Dict[str, Any]]) -> Optional[Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]]:
    """Ask the configured provider for entities and relations.

    Returns None when no provider answered or the payload was unusable, so
    the caller can fall back. Returns an empty tuple when the provider
    answered correctly with "nothing to extract", which is a legitimate
    result and must NOT trigger the fallback.
    """
    if not records:
        return None

    loaded = prompts.get_agent("knowledge_agent")
    system_prompt = loaded.system_prompt if loaded else _INLINE_EXTRACTION_SYSTEM

    user_prompt = (
        "Extract the entities and relations from these records. Prefer one node per record; add an extra "
        "node only for an entity no record covers. Use the source_table and source_id of each record "
        "verbatim.\n\n"
        f"Records:\n{json.dumps(_batch_for_prompt(records), indent=2)}\n\n"
        "Respond ONLY with a valid JSON object matching the schema in your instructions."
    )

    try:
        result = await llm.generate_json(
            user_prompt,
            system=system_prompt,
            max_tokens=4096,
            temperature=0.2,
            agent_name="knowledge_agent",
        )
    except LLMProviderUnavailableError:
        logger.warn("Knowledge LLM unavailable, using algorithmic extraction", records=len(records))
        return None
    except Exception as exc:
        logger.error("Knowledge LLM extraction failed", error=exc, records=len(records))
        return None

    if not isinstance(result, dict) or result.get("parse_error"):
        logger.warn("Knowledge LLM returned unparseable output, using algorithmic extraction")
        return None

    allowed_tables = {record["source_table"] for record in records} | {"extracted"}
    batch_ids = {record["source_id"] for record in records}

    nodes: List[Dict[str, Any]] = []
    raw_nodes = result.get("nodes")
    if isinstance(raw_nodes, list):
        for raw in raw_nodes:
            node = _coerce_llm_node(raw, allowed_tables)
            if node is not None:
                nodes.append(node)
    nodes = nodes[:_MAX_NODES_PER_RUN]

    known_ids = batch_ids | {node["source_id"] for node in nodes}
    edges: List[Dict[str, Any]] = []
    raw_edges = result.get("edges")
    if isinstance(raw_edges, list):
        for raw in raw_edges:
            edge = _coerce_llm_edge(raw, known_ids)
            if edge is not None:
                edges.append(edge)
    edges = edges[:_MAX_EDGES_PER_RUN]

    if not nodes and not edges:
        return None

    logger.info("Knowledge LLM extraction completed", nodes=len(nodes), edges=len(edges), records=len(records))
    return nodes, edges


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def _node_rows(user_id: str, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "user_id": user_id,
            "type": node["type"],
            "label": node["label"],
            "summary": node.get("summary"),
            "tags": node.get("tags") or [],
            "source_table": node.get("source_table"),
            "source_id": node.get("source_id"),
            "weight": node.get("weight", 1.0),
        }
        for node in nodes
    ]


def _upsert_nodes(user_id: str, nodes: List[Dict[str, Any]]) -> int:
    """Write node proposals idempotently. Returns the row count written.

    Primary path is a single bulk upsert resolved against the
    ``uq_knowledge_nodes_user_source`` unique index, which is what makes a
    concurrent double-run safe. If that index is missing the bulk upsert
    fails, and each row falls back to update-then-insert so extraction
    still works on a database that has not run migration 017.
    """
    rows = _node_rows(user_id, nodes)
    if not rows:
        return 0
    supabase = get_supabase_client()
    written = 0
    for start in range(0, len(rows), _WRITE_CHUNK):
        chunk = rows[start : start + _WRITE_CHUNK]
        try:
            supabase.from_("knowledge_nodes").upsert(chunk, on_conflict="user_id,type,source_table,source_id").execute()
            written += len(chunk)
            continue
        except Exception as exc:
            logger.warn("Bulk knowledge node upsert unavailable, falling back to row writes", error=exc)
        for row in chunk:
            try:
                existing = (
                    supabase.from_("knowledge_nodes")
                    .select("id")
                    .eq("user_id", user_id)
                    .eq("type", row["type"])
                    .eq("source_table", row["source_table"])
                    .eq("source_id", row["source_id"])
                    .execute()
                )
                if existing.data:
                    supabase.from_("knowledge_nodes").update(
                        {
                            "label": row["label"],
                            "summary": row["summary"],
                            "tags": row["tags"],
                            "weight": row["weight"],
                        }
                    ).eq("id", existing.data[0]["id"]).eq("user_id", user_id).execute()
                else:
                    supabase.from_("knowledge_nodes").insert(row).execute()
                written += 1
            except Exception as exc:
                logger.error("Knowledge node write failed", user_id=user_id, error=exc)
    return written


def _upsert_edges(user_id: str, edges: List[Dict[str, Any]], node_ids: Dict[str, str]) -> Tuple[int, int]:
    """Write edge proposals on top of resolved node ids.

    ``UNIQUE (user_id, source_id, target_id, relation)`` from migration 015
    is the conflict target, so a repeat run is a no-op. Relations pointing
    at a node this run did not produce are counted as skipped rather than
    written, which is what keeps the table free of dangling endpoints.
    """
    rows: Dict[str, Dict[str, Any]] = {}
    skipped = 0
    for edge in edges:
        source_key = _node_key_for(edge["source_table"], edge["source_id"])
        target_key = _node_key_for(edge["target_table"], edge["target_id"])
        source_node_id = node_ids.get(source_key)
        target_node_id = node_ids.get(target_key)
        if source_node_id is None or target_node_id is None or source_node_id == target_node_id:
            skipped += 1
            continue
        key = _edge_key(source_node_id, target_node_id, edge["relation"])
        rows.setdefault(
            key,
            {
                "user_id": user_id,
                "source_id": source_node_id,
                "target_id": target_node_id,
                "relation": edge["relation"],
                "weight": edge.get("weight", 1.0),
            },
        )

    if not rows:
        return 0, skipped

    supabase = get_supabase_client()
    written = 0
    chunk_rows = list(rows.values())
    for start in range(0, len(chunk_rows), _WRITE_CHUNK):
        chunk = chunk_rows[start : start + _WRITE_CHUNK]
        try:
            supabase.from_("knowledge_edges").upsert(
                chunk, on_conflict="user_id,source_id,target_id,relation"
            ).execute()
            written += len(chunk)
        except Exception as exc:
            logger.error("Knowledge edge upsert failed", user_id=user_id, chunk_size=len(chunk), error=exc)
            skipped += len(chunk)
    return written, skipped


def _node_key_for(source_table: str, source_id: str) -> str:
    """Look a node up by source pair alone.

    One node exists per source row, so source_table + source_id is
    sufficient to find it; the type is derivable from the record.
    """
    return f"{source_table}{_NODE_KEY_SEP}{source_id}"


def _resolve_node_id_index(user_id: str) -> Dict[str, str]:
    """Map 'source_table|source_id' -> node id, plus the typed key form."""
    response = (
        get_supabase_client()
        .from_("knowledge_nodes")
        .select("id, type, source_table, source_id")
        .eq("user_id", user_id)
        .limit(_MAX_NODE_SCAN)
        .execute()
    )
    index: Dict[str, str] = {}
    for row in response.data or []:
        if not row.get("source_id"):
            continue
        index[_node_key_for(row.get("source_table") or "", row["source_id"])] = row["id"]
        index[_node_key(row.get("type", ""), row.get("source_table") or "", row["source_id"])] = row["id"]
    return index


def _refresh_degrees(user_id: str) -> int:
    """Recompute ``knowledge_nodes.degree`` from the user's edge rows.

    015 declares the column as "cached count of incident
    knowledge_edges rows"; nothing else maintains it, so extraction owns
    it. Only rows whose stored degree disagrees are written.
    """
    supabase = get_supabase_client()
    try:
        edge_rows = (
            supabase.from_("knowledge_edges")
            .select("source_id, target_id")
            .eq("user_id", user_id)
            .limit(_MAX_EDGE_SCAN)
            .execute()
        ).data or []
        node_rows = (
            supabase.from_("knowledge_nodes")
            .select("id, degree")
            .eq("user_id", user_id)
            .limit(_MAX_NODE_SCAN)
            .execute()
        ).data or []
    except Exception as exc:
        logger.error("Knowledge degree scan failed", user_id=user_id, error=exc)
        return 0

    counts: Counter = Counter()
    for row in edge_rows:
        if row.get("source_id"):
            counts[row["source_id"]] += 1
        if row.get("target_id"):
            counts[row["target_id"]] += 1

    refreshed = 0
    for row in node_rows:
        node_id = row.get("id")
        if not node_id:
            continue
        degree = counts.get(node_id, 0)
        if row.get("degree") == degree:
            continue
        try:
            supabase.from_("knowledge_nodes").update({"degree": degree}).eq("id", node_id).eq(
                "user_id", user_id
            ).execute()
            refreshed += 1
        except Exception as exc:
            logger.error("Knowledge degree update failed", user_id=user_id, node_id=node_id, error=exc)
    return refreshed


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------


async def extract_knowledge_graph(
    user_id: str,
    sources: Optional[List[str]] = None,
    limit_per_source: int = _MAX_ROWS_PER_SOURCE,
    mode: str = "auto",
) -> Dict[str, Any]:
    """Build (or rebuild) ``user_id``'s knowledge graph from their records.

    ``mode`` is "auto" (LLM, degrading to algorithmic), "llm" (LLM only) or
    "algorithmic" (skip the provider). Returns a summary dict — never a raw
    exception — because apps/api/app/api/knowledge.py hands this straight
    to the HTTP client and exception text can leak schema details.
    """
    if not user_id or not isinstance(user_id, str):
        raise ValueError("extract_knowledge_graph requires a non-empty user_id")

    started = datetime.now(timezone.utc)
    try:
        wanted = [s for s in (sources or list(_SOURCE_ORDER)) if s in _SOURCE_SPECS]
        records = await collect_records(user_id, wanted, limit_per_source)
        if not records:
            return {
                "status": "success",
                "mode": mode,
                "sources_scanned": wanted,
                "records_scanned": 0,
                "nodes_upserted": 0,
                "edges_upserted": 0,
                "edges_skipped": 0,
                "degree_refreshed": 0,
                "summary": "No source records found to extract from.",
            }

        extraction_mode = mode
        extracted: Optional[Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]] = None

        if mode in ("auto", "llm"):
            extracted = await llm_extract(records)

        if extracted is None:
            if mode == "llm":
                logger.warn("LLM-only extraction requested but no provider answered", user_id=user_id)
                nodes, edges = algorithmic_fallback_extract(records)
                extraction_mode = "algorithmic_fallback"
            else:
                nodes, edges = algorithmic_fallback_extract(records)
                extraction_mode = "algorithmic"
        else:
            nodes, edges = extracted
            extraction_mode = "llm"

        # The LLM may emit a node for a source row that is also covered by
        # the batch; keep the first proposal for each identity.
        deduped: Dict[str, Dict[str, Any]] = {}
        for node in nodes:
            deduped.setdefault(_node_key(node["type"], node.get("source_table") or "", node["source_id"]), node)
        nodes = list(deduped.values())[:_MAX_NODES_PER_RUN]

        nodes_written = _upsert_nodes(user_id, nodes)

        # Resolve ids after the write so both newly inserted and previously
        # existing nodes are addressable in one pass.
        node_ids = _resolve_node_id_index(user_id)
        edges_written, edges_skipped = _upsert_edges(user_id, edges, node_ids)
        degree_refreshed = _refresh_degrees(user_id)

        elapsed_ms = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
        logger.info(
            "Knowledge extraction completed",
            user_id=user_id,
            mode=extraction_mode,
            records=len(records),
            nodes=nodes_written,
            edges=edges_written,
            elapsed_ms=elapsed_ms,
        )
        return {
            "status": "success",
            "mode": extraction_mode,
            "sources_scanned": wanted,
            "records_scanned": len(records),
            "nodes_upserted": nodes_written,
            "edges_upserted": edges_written,
            "edges_skipped": edges_skipped,
            "degree_refreshed": degree_refreshed,
            "summary": (
                f"Extracted {nodes_written} nodes and {edges_written} edges from "
                f"{len(records)} records via {extraction_mode}."
            ),
        }
    except Exception as exc:
        logger.error("Knowledge extraction failed", user_id=user_id, error=exc)
        # No str(exc) here: this dict is serialised to the client.
        return {
            "status": "error",
            "mode": mode,
            "sources_scanned": [],
            "records_scanned": 0,
            "nodes_upserted": 0,
            "edges_upserted": 0,
            "edges_skipped": 0,
            "degree_refreshed": 0,
            "summary": "Knowledge extraction failed, no changes made.",
        }


def sanitise_search_term(term: str) -> str:
    """Reduce a user-supplied search term to a PostgREST-safe needle.

    The term is interpolated into an ``or=(label.ilike.%term%,...)`` filter
    string, so any character that could terminate the filter value or start
    a new one is dropped rather than escaped.
    """
    cleaned = _UNSAFE_SEARCH_CHARS_RE.sub(" ", term or "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:200]


async def search_nodes(user_id: str, request: KnowledgeSearchRequest) -> KnowledgeSearchResponse:
    """Search one user's nodes by label or summary. Returns a bare node list.

    The HTTP layer unwraps ``.nodes`` because knowledgeStore.search()
    assigns the response straight into ``nodes`` and calls ``.filter`` on
    it — an envelope here would break the page.
    """
    term = sanitise_search_term(request.query)
    if not term:
        return KnowledgeSearchResponse(query=request.query, nodes=[], count=0)

    try:
        builder = (
            get_supabase_client()
            .from_("knowledge_nodes")
            .select(
                "id, user_id, type, label, summary, tags, source_table, source_id, weight, degree, "
                "created_at, updated_at"
            )
            .eq("user_id", user_id)
        )
        if request.type:
            builder = builder.eq("type", request.type)
        needle = term.replace(" ", "%")
        response = (
            builder.or_(f"label.ilike.%{needle}%,summary.ilike.%{needle}%")
            .order("degree", ascending=False)
            .limit(request.limit)
            .execute()
        )
        rows = response.data or []
    except Exception as exc:
        logger.error("Knowledge search failed", user_id=user_id, error=exc)
        rows = []

    return KnowledgeSearchResponse(query=request.query, nodes=rows, count=len(rows))
