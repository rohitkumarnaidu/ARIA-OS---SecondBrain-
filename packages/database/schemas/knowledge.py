from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

# knowledge_nodes.type — mirrors the CHECK constraint in
# scripts/migrations/015_memory_knowledge_schema.sql:153, widened to
# include 'goal' by scripts/migrations/017_knowledge_graph_node_tags.sql.
# Kept in sync by hand: the database is the authority, this is the
# Pydantic-side copy used for validation and OpenAPI.
VALID_NODE_TYPES = ("note", "resource", "idea", "memory", "course", "task", "goal")

# Relation verbs written to knowledge_edges.relation. The frontend
# renders this value as GraphEdge.label (KnowledgeGraph.tsx:87), so it is
# a human-readable verb, not an enum the client switches on.
DEFAULT_RELATION = "related_to"


class KnowledgeNodeCreate(BaseModel):
    type: str
    label: str
    summary: Optional[str] = None
    tags: list[str] = []
    source_table: Optional[str] = None
    source_id: Optional[str] = None
    weight: float = 1.0


class KnowledgeNodeUpdate(BaseModel):
    label: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[list[str]] = None
    weight: Optional[float] = None


class KnowledgeNodeResponse(BaseModel):
    """One graph vertex, shaped for the frontend.

    The database column names are `label`, `summary` and `created_at`, but
    apps/web/components/knowledge/KnowledgeGraph.tsx:7-14 declares

        interface GraphNode {
          id: string
          title: string
          type: 'note' | 'resource' | 'idea'
          createdAt: string
          tags?: string[]
          description?: string
        }

    `serialization_alias` bridges the two without a hand-written mapper:
    validation reads the snake_case field names (which is what the Supabase
    rows contain) and FastAPI serialises with by_alias=True by default, so
    the wire format carries title/description/createdAt.
    """

    id: str
    user_id: str
    type: str
    label: str = Field(serialization_alias="title")
    summary: Optional[str] = Field(default=None, serialization_alias="description")
    tags: list[str] = Field(default_factory=list)
    source_table: Optional[str] = None
    source_id: Optional[str] = None
    weight: float = 1.0
    degree: int = 0
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class KnowledgeEdgeResponse(BaseModel):
    """One graph relationship, shaped for the frontend.

    KnowledgeGraph.tsx:16-20 declares

        interface GraphEdge {
          source: string
          target: string
          label?: string
        }

    so source_id/target_id/relation are aliased to source/target/label.
    015 line 175 documents the same mapping.
    """

    source_id: str = Field(serialization_alias="source")
    target_id: str = Field(serialization_alias="target")
    relation: str = Field(serialization_alias="label")
    weight: float = 1.0
    id: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class KnowledgeGraphResponse(BaseModel):
    """Envelope for GET /api/v1/knowledge/.

    knowledgeStore.fetch() reads `data.nodes` and `data.edges`
    (apps/web/lib/stores/knowledgeStore.ts:28), so both arrays are
    top-level siblings — edges are NOT nested inside each node.
    """

    nodes: list[KnowledgeNodeResponse] = []
    edges: list[KnowledgeEdgeResponse] = []
    count: int = 0
    limit: int = 0
    offset: int = 0


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=200)
    limit: int = Field(default=20, ge=1, le=100)
    type: Optional[str] = None


class KnowledgeSearchResponse(BaseModel):
    query: str
    nodes: list[KnowledgeNodeResponse] = []
    count: int = 0


class KnowledgeExtractRequest(BaseModel):
    """Body for POST /api/v1/knowledge/extract.

    Omitting `sources` extracts from every table the agent understands.
    `mode` pins the pipeline instead of letting it pick: "auto" tries the
    LLM and degrades to the algorithmic extractor, "algorithmic" skips the
    LLM entirely (useful when no provider is configured).
    """

    sources: Optional[list[str]] = None
    limit_per_source: int = Field(default=50, ge=1, le=200)
    mode: str = Field(default="auto")


class KnowledgeExtractResult(BaseModel):
    """Summary of one extraction run — the numbers, not the graph.

    The graph itself is read back through GET /api/v1/knowledge/, which
    keeps this response small and lets the caller confirm the upsert
    actually landed by fetching it.
    """

    status: str
    mode: str
    sources_scanned: list[str] = []
    records_scanned: int = 0
    nodes_upserted: int = 0
    edges_upserted: int = 0
    edges_skipped: int = 0
    degree_refreshed: int = 0
    summary: str
