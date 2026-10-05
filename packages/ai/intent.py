"""Intent classification: deterministic rules first, LLM only when rules are unsure.

This is the module AGENTS.md §9.1 claimed existed. Until now `chat.py` had a
five-branch substring check that only ran *after* every LLM provider had already
failed three times, so intent was decided by `if "task" in message`.

Design constraints, in priority order:

1. **Never crash, never return nothing.** Every path returns a
   `Classification` with an intent and a confidence. A blank message is a valid
   message.
2. **The rule layer must be genuinely good, because it is the one that always
   works.** Not `"task" in msg`. Each intent carries weighted keyword families,
   synonym expansion and entity hints, and scores by weighted overlap against a
   normalised token set. Confidence is derived from the *margin* between first
   and second place, not from the raw score, so a message that matches two
   intents equally reports low confidence and earns an LLM second opinion.
3. **The LLM layer is an upgrade, never a dependency.** It only runs when the
   rule result is uncertain, its output is validated against the closed intent
   set, and any failure falls straight back to the rule result.
4. **No new prompt file.** The classifier reuses `prompts.get_agent(
   "memory_agent")` for the JSON discipline it already documents, and states the
   task inline. `scripts/validate_prompts.py` therefore has nothing new to check.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts
from shared.utils.logger import logger
from shared.utils.text_entities import extract_date, extract_minutes, extract_priority

# The closed intent set. Anything outside this list is a bug, not a new intent.
INTENTS: Tuple[str, ...] = (
    "task",
    "goal",
    "course",
    "habit",
    "sleep",
    "income",
    "opportunity",
    "briefing",
    "review",
    "memory",
    "analytics",
    "skill",
    "roadmap",
    "time_tracking",
    "scheduling",
    "help",
    "general",
)

# Below this rule-layer confidence the LLM is asked to break the tie.
LLM_ESCALATION_THRESHOLD = 0.55
# Hard cap on rule confidence. A rule match can never claim to be certain; if
# the message was genuinely unambiguous the LLM layer will not even run.
MAX_RULE_CONFIDENCE = 0.92
# A margin below this between the top two intents means "ambiguous".
AMBIGUITY_MARGIN = 0.12

_WORD_RE = re.compile(r"[a-z0-9']+")

# Imperative verbs. A message that opens with one of these is a request to do
# something, not a question to be answered -- the single strongest signal that
# separates `task` from `analytics` ("what should I focus on" vs "focus on the
# report").
_IMPERATIVE_VERBS = frozenset(
    {
        "add",
        "block",
        "book",
        "buy",
        "cancel",
        "check",
        "clean",
        "clear",
        "complete",
        "create",
        "delete",
        "do",
        "finish",
        "fix",
        "log",
        "make",
        "mark",
        "move",
        "note",
        "plan",
        "post",
        "prepare",
        "pull",
        "push",
        "record",
        "remind",
        "remove",
        "rename",
        "reschedule",
        "review",
        "schedule",
        "send",
        "set",
        "start",
        "submit",
        "track",
        "update",
        "write",
    }
)

# Question openers. These push toward read-only intents even when an imperative
# verb appears later in the sentence ("can you check my habits").
_QUESTION_OPENERS = frozenset(
    {
        "am",
        "are",
        "did",
        "do",
        "does",
        "how",
        "is",
        "should",
        "was",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "will",
        "would",
        "can",
        "could",
    }
)

# Verbs that mean "the user is about to change data". Used for the entity hint
# that separates `scheduling` (block out time) from `task` (make a to-do).
_SCHEDULING_VERBS = frozenset({"schedule", "block", "book", "calendar", "reschedule", "slot", "meeting"})
# Tokens that mean "the user is measuring their own time". "focus" is
# deliberately absent: it is an ordinary English word ("what should I focus on
# today"), and including it made every focus-flavoured question a time-tracking
# request. Deep/focus-time only counts when a measurement word is alongside it.
_TIME_TOKENS = frozenset({"timer", "timesheet", "clock", "pomodoro", "deep", "deep-work", "focus-time", "clocked"})


class Classification(BaseModel):
    """One classified user message."""

    intent: str = "general"
    confidence: float = 0.0
    entities: Dict[str, Any] = Field(default_factory=dict)
    matched_agents: List[str] = Field(default_factory=list)
    reasoning: str = ""
    # "rule", "llm", or "llm_fallback" -- which layer produced `intent`.
    source: str = "rule"

    def model_post_init(self, __context: Any) -> None:
        if self.intent not in INTENTS:
            raise ValueError(f"unknown intent {self.intent!r}; must be one of {INTENTS}")


def tokenize(text: str) -> List[str]:
    """Lowercase word tokens, with a light singular fold so plurals match."""
    tokens = _WORD_RE.findall((text or "").lower())
    folded: List[str] = []
    for token in tokens:
        folded.append(token)
        # "tasks" -> "task", "habits" -> "habit". Only for regular -s plurals,
        # so "class" is left alone (it ends in -ss).
        if len(token) > 3 and token.endswith("s") and not token.endswith(("ss", "us", "is")):
            folded.append(token[:-1])
    return folded


def _expand(tokens: List[str]) -> set:
    """Token set for scoring: raw tokens plus singular folds.

    Synonymy lives in `KEYWORD_GROUPS`, not here. An earlier version expanded
    tokens through a synonym map *and* matched against concept groups, so a
    single word could score through three separate paths.
    """
    expanded = set(tokens)
    for token in tokens:
        if len(token) > 3 and token.endswith("s") and not token.endswith(("ss", "us", "is")):
            expanded.add(token[:-1])
    return expanded


# Concept groups. Every intent owns a list of interchangeable token sets; a group
# scores ONCE no matter how many of its members appear.
#
# The earlier flat keyword-set design double- and triple-counted: with
# `skill`/`skills`/`competency` all listed, "my skills" scored 8.0 against
# "my skill level"'s 3.0 and swamped the actual intent of the sentence. Concept
# groups make synonym expansion part of the score instead of a multiplier on it.
#
# Weights: 3.0 = the group's tokens name the thing itself. 1.0 = adjacent
# vocabulary that only implies the intent.
KEYWORD_GROUPS: Dict[str, List[Tuple[frozenset, float]]] = {
    "task": [
        (frozenset({"task", "todo", "to-do", "action-item"}), 3.0),
        (frozenset({"assignment", "homework", "submission"}), 3.0),
        (frozenset({"deadline", "due", "due-date"}), 3.0),
        (frozenset({"overdue", "backlog", "chore", "errand"}), 3.0),
        (frozenset({"reminder", "remind"}), 3.0),
        (frozenset({"add", "create", "finish", "complete", "mark", "pending", "priority", "due"}), 1.0),
    ],
    "goal": [
        (frozenset({"goal", "objective", "aim"}), 3.0),
        (frozenset({"milestone", "target"}), 3.0),
        (frozenset({"progress", "achieve", "ambition"}), 1.0),
        (frozenset({"long-term"}), 1.0),
    ],
    "course": [
        (frozenset({"course", "class", "subject", "curriculum", "syllabus"}), 3.0),
        (frozenset({"nptel", "coursera", "udemy"}), 3.0),
        (frozenset({"lecture", "semester", "module", "exam"}), 1.0),
        (frozenset({"study", "learn", "cgpa"}), 1.0),
    ],
    "habit": [
        (frozenset({"habit", "streak", "checkin"}), 3.0),
        (frozenset({"routine", "daily"}), 3.0),
        (frozenset({"consistency", "discipline", "practice"}), 1.0),
        (frozenset({"break"}), 1.0),
    ],
    "sleep": [
        (frozenset({"sleep", "slept", "sleping"}), 3.0),
        # Weighted above the other strong groups: these name sleep specifically,
        # while "routine"/"streak" are shared with habit. Without the extra
        # weight "my bedtime routine" ties and resolves to habit.
        (frozenset({"bedtime", "insomnia", "nap"}), 4.0),
        (frozenset({"tired", "fatigue", "rest", "wake"}), 1.0),
        (frozenset({"wind-down", "debt", "recovery"}), 1.0),
    ],
    "income": [
        (frozenset({"income", "salary", "earnings", "stipend", "revenue"}), 3.0),
        (frozenset({"payment", "invoice"}), 3.0),
        (frozenset({"money", "paid", "freelance", "gig"}), 1.0),
        (frozenset({"budget", "expense"}), 1.0),
    ],
    "opportunity": [
        (frozenset({"opportunity", "internship", "placement", "hiring"}), 3.0),
        (frozenset({"job", "role", "opening", "offer"}), 1.0),
        (frozenset({"application", "apply", "recruiter"}), 1.0),
    ],
    "briefing": [
        (frozenset({"briefing", "brief"}), 3.0),
        (frozenset({"morning", "agenda"}), 1.0),
        (frozenset({"today", "ahead", "overview"}), 1.0),
        (frozenset({"focus", "standup", "catch-up"}), 1.0),
    ],
    "review": [
        (frozenset({"review", "retrospective", "recap"}), 3.0),
        (frozenset({"reflection", "postmortem"}), 3.0),
        (frozenset({"weekly", "summarize"}), 1.0),
        (frozenset({"week", "month", "last"}), 1.0),
    ],
    "memory": [
        (frozenset({"memory", "memories"}), 3.0),
        (frozenset({"remember", "remembered", "recall", "recalled"}), 3.0),
        (frozenset({"previously", "last-time"}), 1.0),
        (frozenset({"context", "told", "know-about-me", "note"}), 1.0),
    ],
    "analytics": [
        (frozenset({"analytics", "insight", "insights"}), 3.0),
        (frozenset({"pattern", "patterns", "trend", "trends"}), 3.0),
        (frozenset({"anomaly", "anomalies"}), 3.0),
        (frozenset({"productivity", "metric", "metrics", "stat", "stats"}), 1.0),
        (frozenset({"analyze", "analyse", "analysis", "data"}), 1.0),
    ],
    "skill": [
        (frozenset({"skill", "competency", "competencies", "proficiency"}), 3.0),
        (frozenset({"assessment", "assess"}), 3.0),
        (frozenset({"level", "expertise", "resume", "portfolio"}), 1.0),
        (frozenset({"gap", "improve"}), 1.0),
    ],
    "roadmap": [
        (frozenset({"roadmap", "road-map"}), 3.0),
        (frozenset({"career-path"}), 3.0),
        (frozenset({"sequence", "milestone"}), 1.0),
        (frozenset({"next", "path"}), 1.0),
    ],
    "time_tracking": [
        (frozenset({"timer", "timesheet", "pomodoro"}), 3.0),
        (frozenset({"tracked", "tracking", "tracker"}), 3.0),
        (frozenset({"focus-time", "deep-work", "clocked"}), 3.0),
    ],
    "scheduling": [
        (frozenset({"schedule", "scheduled", "reschedule", "rescheduled"}), 3.0),
        (frozenset({"calendar", "meeting", "slot"}), 3.0),
        (frozenset({"book", "booking", "block"}), 1.0),
    ],
    "help": [
        (frozenset({"help", "capability", "capabilities"}), 3.0),
        (frozenset({"how-do-i", "what-can-you-do"}), 3.0),
        (frozenset({"commands", "usage", "guide"}), 1.0),
    ],
    "general": [
        (frozenset({"hello", "hi", "hey", "greetings"}), 3.0),
        (frozenset({"thanks", "thank-you"}), 3.0),
        (frozenset({"who-are-you", "how-are-you"}), 1.0),
    ],
}

# The token that names the intent outright. A literal occurrence of an intent's
# own head noun outranks weaker adjacent vocabulary, which is what makes
# "fix my roadmap milestones" a roadmap request rather than a goal one (both
# own "milestone"; only roadmap owns "roadmap").
HEAD_NOUN: Dict[str, frozenset] = {
    intent: max(groups, key=lambda g: (g[1], len(g[0])))[0] for intent, groups in KEYWORD_GROUPS.items()
}

# Multi-word keyword members ("how do i", "what can you do") cannot be produced
# by the tokenizer, which yields single words. They are matched as substrings of
# the lowercased text instead, inside `_keyword_score`. Listed here so the set
# of multi-word members is discoverable rather than buried in the groups.
MULTIWORD_KEYWORDS: frozenset = frozenset(
    word for groups in KEYWORD_GROUPS.values() for group, _ in groups for word in group if " " in word or "-" in word
)

# Course-name-ish proper nouns. In a BTech context these are course codes, and
# capturing them as an entity is what lets `scheduling` distinguish "schedule DSA
# for 3pm" from a generic scheduling request.
#
# Letter-only abbreviations are matched from an explicit allow-list rather than
# by pattern: a bare `[a-z]{2,4}` pattern would fire on "do", "is" and "ai" in
# ordinary sentences. Numbered codes (CS204, ME301, nptel 42) are pattern-matched.
_COURSE_ABBREVIATIONS = frozenset(
    {
        "dsa",
        "dbms",
        "os",
        "cn",
        "coa",
        "toc",
        "ps",
        "cg",
        "ui",
        "ml",
        "ai",
        "nlp",
        "cnc",
        "db",
        "oops",
        "dsa",
        "dm",
        "wt",
        "cc",
        "se",
        "asap",
        "hl",
    }
)
_COURSE_CODE_RE = re.compile(r"\b(d[a-z]{1,2}\d{2,4}|nptel\s*\d+|cs\d{2,4}|me\d{2,4}|btech)\b", re.IGNORECASE)
_COUNT_RE = re.compile(r"\b(\d{1,3})\s+(tasks?|goals?|habits?|courses?|items?|things?|modules?)\b", re.IGNORECASE)


def _keyword_score(intent: str, tokens: set, text_lower: str) -> Tuple[float, List[str]]:
    """Score one intent, counting each concept group at most once.

    `tokens` is the raw token set plus singular folds. Synonymy is encoded in the
    groups themselves, so there is no separate expansion step to double-count
    against.
    """
    hits: List[str] = []
    score = 0.0

    for group, weight in KEYWORD_GROUPS[intent]:
        matched = group & tokens
        phrases = {w for w in group if w in MULTIWORD_KEYWORDS and w in text_lower}
        if not matched and not phrases:
            continue
        score += weight
        hits.extend(sorted(matched))
        hits.extend(sorted(phrases))

    # A literal head noun in the raw text is a direct reference to the thing the
    # intent is about; the same word reached only by singular folding ("roadmaps"
    # -> "roadmap") is weaker evidence.
    head = HEAD_NOUN.get(intent, frozenset())
    if head and (head & tokens):
        literal = {w for w in head & tokens if w in text_lower}
        if literal and score > 0:
            score += 1.5
            hits.append(f"head:{sorted(literal)[0]}")

    return score, sorted(set(hits))


def _entity_hints(text: str, tokens: List[str], text_lower: str) -> Tuple[Dict[str, Any], Dict[str, float]]:
    """Extract entities and derive intent hints from them.

    Returns the entity dict plus a per-intent score bonus. Hints are kept small
    and explainable: a date plus an imperative verb is scheduling; a date alone
    is a task due date.
    """
    entities: Dict[str, Any] = {}

    due_date = extract_date(text)
    if due_date:
        entities["due_date"] = due_date

    priority = extract_priority(text)
    if priority:
        entities["priority"] = priority

    minutes = extract_minutes(text)
    if minutes:
        entities["duration_minutes"] = minutes

    course_codes = sorted({m.group(0).lower() for m in _COURSE_CODE_RE.finditer(text)})
    course_codes.extend(t for t in sorted(set(tokens) & _COURSE_ABBREVIATIONS) if t not in course_codes)
    if course_codes:
        entities["course_codes"] = course_codes

    counts = [{"n": int(m.group(1)), "noun": m.group(2).lower()} for m in _COUNT_RE.finditer(text)]
    if counts:
        entities["counts"] = counts

    hints: Dict[str, float] = {}
    if tokens and tokens[0] in _IMPERATIVE_VERBS:
        hints["task"] = hints.get("task", 0.0) + 1.5
    if tokens and tokens[0] in _QUESTION_OPENERS:
        # A question is a read, not a write.
        hints["analytics"] = hints.get("analytics", 0.0) + 0.75
    if expanded_time := set(tokens) & _TIME_TOKENS:
        hints["time_tracking"] = hints.get("time_tracking", 0.0) + 2.0
        if expanded_time:
            entities["time_tokens"] = sorted(expanded_time)
    if set(tokens) & _SCHEDULING_VERBS:
        hints["scheduling"] = hints.get("scheduling", 0.0) + 1.5
    if due_date and set(tokens) & _SCHEDULING_VERBS:
        # Date + a booking verb is the scheduling signature; date + any other
        # verb is a due date on a task.
        hints["scheduling"] = hints.get("scheduling", 0.0) + 1.0
    if course_codes:
        hints["course"] = hints.get("course", 0.0) + 1.0
    if counts and counts[0]["noun"].startswith("habit"):
        hints["habit"] = hints.get("habit", 0.0) + 1.0

    # "what can you do" / "help me" style capability questions.
    if "help" in tokens or "what can you do" in text_lower or "commands" in tokens:
        hints["help"] = hints.get("help", 0.0) + 3.0

    # A message that OPENS with "when" is asking for a time. The question word
    # leads the sentence and is the sentence's actual subject matter, so it
    # outweighs a noun that appears later: "when is my next class" wants a
    # schedule, not course content, even though `course` scores "class" plus a
    # head-noun bonus.
    #
    # 5.0 is chosen against the scoring ceiling: the strongest single concept
    # group (3.0) plus the head-noun bonus (1.5) tops out at 4.5, so a leading
    # temporal interrogative beats any one keyword and any tie-break.
    if tokens and tokens[0] == "when":
        hints["scheduling"] = hints.get("scheduling", 0.0) + 5.0

    return entities, hints


def classify_with_rules(message: str) -> Classification:
    """Deterministic classification. Always returns a result, never raises."""
    text = (message or "").strip()
    text_lower = text.lower()

    if not text:
        return Classification(
            intent="general",
            confidence=0.2,
            entities={},
            matched_agents=[],
            reasoning="Empty message; defaulting to general.",
            source="rule",
        )

    tokens = tokenize(text)
    expanded = _expand(tokens)
    entities, hints = _entity_hints(text, tokens, text_lower)

    scores: Dict[str, float] = {}
    hits_by_intent: Dict[str, List[str]] = {}
    for intent in INTENTS:
        score, hits = _keyword_score(intent, expanded, text_lower)
        score += hints.get(intent, 0.0)
        scores[intent] = score
        if hits:
            hits_by_intent[intent] = hits

    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    top_intent, top_score = ranked[0]
    runner_up = ranked[1][1] if len(ranked) > 1 else 0.0

    if top_score <= 0.0:
        return Classification(
            intent="general",
            confidence=0.25,
            entities=entities,
            matched_agents=[],
            reasoning="No intent keywords matched; defaulting to general.",
            source="rule",
        )

    # Confidence from the margin, not the raw score: a message matching two
    # intents equally well is genuinely uncertain even when both scores are
    # high. Scaled by absolute evidence so "task" alone is less certain than
    # "task" + "deadline" + imperative.
    margin = top_score - runner_up
    evidence = min(1.0, top_score / 5.0)
    confidence = round(min(MAX_RULE_CONFIDENCE, 0.35 + 0.25 * evidence + 0.35 * min(1.0, margin / 2.5)), 3)

    hit_words = hits_by_intent.get(top_intent, [])
    reasoning = (
        f"Rule layer: intent={top_intent} score={top_score:.1f} runner_up={runner_up:.1f} "
        f"matched={sorted(hit_words) or ['entity-hint']}"
    )

    return Classification(
        intent=top_intent,
        confidence=confidence,
        entities=entities,
        matched_agents=[],
        reasoning=reasoning,
        source="rule",
    )


async def _llm_classify(message: str, rule_result: Classification) -> Optional[Classification]:
    """Ask the LLM to classify. Returns None on any failure.

    The prompt is inline rather than a new `prompts/agents/*.md` file: the
    classifier is a classifier, not a persona, and adding a file would mean a
    new frontmatter contract for a 40-line task. It reuses the memory agent's
    prompt only for the JSON-output discipline that prompt already establishes.
    """
    try:
        base = prompts.get_agent("memory_agent")
        system = (
            f"{base.system_prompt}\n\n"
            "## Current task: intent classification\n"
            "Classify the user's message into exactly one intent. "
            f"Valid intents: {', '.join(INTENTS)}. "
            "Respond with ONLY a JSON object: "
            '{"intent": "<one valid intent>", "confidence": <0.0-1.0>, '
            '"entities": {}, "reasoning": "<one short sentence>"}. '
            "If genuinely ambiguous, use the intent the rule layer suggested "
            f"({rule_result.intent}) rather than inventing a new category."
            if base
            else "You are an intent classifier. Respond with ONLY JSON: "
            '{"intent": "...", "confidence": 0.0, "entities": {}, "reasoning": "..."}. '
            f"Valid intents: {', '.join(INTENTS)}."
        )
        user = (
            f"User message: {message}\n\n"
            f"Rule-layer guess: {rule_result.intent} (confidence {rule_result.confidence})\n"
            f"Rule-layer entities: {rule_result.entities}"
        )
        raw = await llm.generate_json(user, system=system, max_tokens=256, agent_name="aria_intent_classifier")
    except LLMProviderUnavailableError as exc:
        logger.warn("Intent LLM unavailable; keeping rule result", error=str(exc))
        return None
    except Exception as exc:  # noqa: BLE001 -- never let classification break chat
        logger.warn("Intent LLM classification failed; keeping rule result", error=str(exc))
        return None

    if not isinstance(raw, dict):
        return None

    intent = str(raw.get("intent", "")).strip().lower()
    if intent not in INTENTS:
        logger.warn("LLM returned an unknown intent; keeping rule result", intent=intent)
        return None

    try:
        confidence = float(raw.get("confidence", rule_result.confidence))
    except (TypeError, ValueError):
        confidence = rule_result.confidence
    confidence = max(0.0, min(1.0, confidence))

    raw_entities = raw.get("entities")
    entities = dict(rule_result.entities)
    if isinstance(raw_entities, dict):
        # Rule-extracted entities WIN on conflict. They were parsed out of the
        # text with regexes and cannot be hallucinated; the LLM is summarising
        # and will happily return a confident wrong date. The LLM may only add
        # keys the rule layer did not extract.
        additions = {k: v for k, v in raw_entities.items() if v is not None and k not in rule_result.entities}
        entities.update(additions)
        overridden = sorted(set(raw_entities) & set(rule_result.entities))
        if overridden:
            logger.info(
                "Kept rule-extracted entities over the LLM's",
                entities=overridden,
                intent=rule_result.intent,
            )

    return Classification(
        intent=intent,
        confidence=confidence,
        entities=entities,
        matched_agents=[],
        reasoning=f"LLM layer overrode rule guess ({rule_result.intent}): {raw.get('reasoning', 'no reasoning given')}",
        source="llm",
    )


async def classify(message: str, use_llm: bool = True) -> Classification:
    """Classify `message`, escalating to the LLM only when the rules are unsure.

    Always returns a `Classification`. The rule result is the floor: any LLM
    failure, unknown intent or malformed response leaves it untouched.
    """
    rule_result = classify_with_rules(message)

    needs_llm = use_llm and (rule_result.confidence < LLM_ESCALATION_THRESHOLD or rule_result.intent == "general")
    if not needs_llm:
        return rule_result

    llm_result = await _llm_classify(message, rule_result)
    if llm_result is None:
        rule_result.source = "llm_fallback"
        rule_result.reasoning += " | LLM escalation failed; rule result retained"
        return rule_result
    return llm_result
