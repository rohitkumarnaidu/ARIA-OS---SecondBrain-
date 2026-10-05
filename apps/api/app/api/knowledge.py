from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from database.schemas.knowledge import (
    KnowledgeExtractRequest,
    KnowledgeExtractResult,
    KnowledgeGraphResponse,
    KnowledgeNodeResponse,
    KnowledgeSearchRequest,
)
from shared.utils.logger import logger

router = APIRouter()

# Explicit column lists — never select("*"). Kept in sync with the
# knowledge_nodes / knowledge_edges DDL in migration 015 (plus the `tags`
# column added by 017).
NODE_COLUMNS = (
    "id, user_id, type, label, summary, tags, source_table, source_id, " "weight, degree, created_at, updated_at"
)
EDGE_COLUMNS = "id, user_id, source_id, target_id, relation, weight, created_at"


@router.get(
    "/",
    summary="List knowledge graph nodes and edges",
    response_model=KnowledgeGraphResponse,
)
async def list_knowledge_graph(
    current_user=Depends(get_current_user),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    node_type: Optional[str] = Query(None, alias="type"),
):
    """Return a page of nodes plus the edges between them.

    Edges are top-level siblings of nodes, not nested per node:
    knowledgeStore.fetch() reads `data.nodes` and `data.edges`
    (apps/web/lib/stores/knowledgeStore.ts:28). Edges are restricted to the
    page's own nodes so the store's client-side filter — which drops any
    edge with an endpoint outside the visible node set
    (page.tsx:86-89) — has nothing left to discard.
    """
    supabase = get_supabase_client()
    user_id = current_user.user.id

    builder = supabase.from_("knowledge_nodes").select(NODE_COLUMNS).eq("user_id", user_id)
    if node_type:
        builder = builder.eq("type", node_type)

    try:
        response = builder.order("updated_at", ascending=False).range(offset, offset + limit - 1).execute()
    except Exception as e:
        logger.error("Knowledge graph list failed", user_id=user_id, error=e)
        raise HTTPException(status_code=400, detail="Failed to load knowledge graph")

    nodes = response.data or []
    node_ids = [node["id"] for node in nodes if node.get("id")]

    edges = []
    if node_ids:
        try:
            edge_response = (
                supabase.from_("knowledge_edges")
                .select(EDGE_COLUMNS)
                .eq("user_id", user_id)
                .in_("source_id", node_ids)
                .in_("target_id", node_ids)
                .execute()
            )
            edges = edge_response.data or []
        except Exception as e:
            logger.error("Knowledge edge list failed", user_id=user_id, error=e)
            raise HTTPException(status_code=400, detail="Failed to load knowledge graph edges")

    return {
        "nodes": nodes,
        "edges": edges,
        "count": len(nodes),
        "limit": limit,
        "offset": offset,
    }


@router.get(
    "/search",
    summary="Search knowledge graph nodes",
    response_model=List[KnowledgeNodeResponse],
)
async def search_knowledge_nodes(
    q: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    node_type: Optional[str] = Query(None, alias="type"),
    current_user=Depends(get_current_user),
):
    """Search one user's nodes by label or summary.

    Returns a BARE array, not an envelope: knowledgeStore.search() assigns
    the response straight into `nodes` and page.tsx calls `.filter()` on it
    (knowledgeStore.ts:39, page.tsx:74). Declared before `/{node_id}` below
    so FastAPI matches this literal path first — otherwise "search" would be
    captured as a node_id and 404.
    """
    from ai.agents.knowledge_agent import search_nodes

    try:
        request = KnowledgeSearchRequest(query=q, limit=limit, type=node_type)
        result = await search_nodes(current_user.user.id, request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Knowledge search failed", user_id=current_user.user.id, error=e)
        raise HTTPException(status_code=400, detail="Knowledge search failed")

    # offset is applied here rather than pushed into the agent so the agent
    # stays a single-request helper; the response contract is unchanged.
    nodes = result.nodes[offset : offset + limit]
    return nodes


@router.get(
    "/{node_id}",
    summary="Get a knowledge graph node by ID",
    response_model=KnowledgeNodeResponse,
)
async def get_knowledge_node(node_id: str, current_user=Depends(get_current_user)):
    """Return a single node. 404 when it does not exist or is not the caller's."""
    supabase = get_supabase_client()
    try:
        response = (
            supabase.from_("knowledge_nodes")
            .select(NODE_COLUMNS)
            .eq("id", node_id)
            .eq("user_id", current_user.user.id)
            .execute()
        )
    except Exception as e:
        logger.error("Knowledge node fetch failed", node_id=node_id, error=e)
        raise HTTPException(status_code=400, detail="Failed to load knowledge node")

    if not response.data:
        raise HTTPException(status_code=404, detail="Knowledge node not found")
    return response.data[0]


@router.post(
    "/extract",
    summary="Extract entities and relations into the knowledge graph",
    response_model=KnowledgeExtractResult,
)
async def extract_knowledge(
    request: Optional[KnowledgeExtractRequest] = None,
    current_user=Depends(get_current_user),
):
    """Rebuild the caller's graph from their own memories, resources, ideas,
    tasks, courses and goals.

    Idempotent: a node is keyed on (user_id, type, source_table, source_id),
    so re-running converges on the same rows instead of duplicating them.
    Degrades to a deterministic extractor when no LLM provider answers.
    """
    from ai.agents.knowledge_agent import extract_knowledge_graph

    payload = request or KnowledgeExtractRequest()
    user_id = current_user.user.id
    try:
        result = await extract_knowledge_graph(
            user_id,
            sources=payload.sources,
            limit_per_source=payload.limit_per_source,
            mode=payload.mode,
        )
    except Exception as e:
        # str(e) is never returned to the client — it can carry table names,
        # SQL fragments or connection strings.
        logger.error("Knowledge extraction request failed", user_id=user_id, error=e)
        raise HTTPException(status_code=400, detail="Knowledge extraction failed")

    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail="Knowledge extraction failed, no changes made")
    return result


@router.delete(
    "/{node_id}",
    summary="Delete a knowledge graph node",
    status_code=204,
)
async def delete_knowledge_node(node_id: str, current_user=Depends(get_current_user)):
    """Delete one of the caller's nodes. Incident edges cascade in the database
    (ON DELETE CASCADE on both knowledge_edges foreign keys, migration 015)."""
    supabase = get_supabase_client()
    try:
        response = (
            supabase.from_("knowledge_nodes").delete().eq("id", node_id).eq("user_id", current_user.user.id).execute()
        )
    except Exception as e:
        logger.error("Knowledge node delete failed", node_id=node_id, error=e)
        raise HTTPException(status_code=400, detail="Failed to delete knowledge node")

    if response.error:
        logger.error("Knowledge node delete rejected", node_id=node_id, detail=response.error.message)
        raise HTTPException(status_code=400, detail="Failed to delete knowledge node")
    if not response.data:
        raise HTTPException(status_code=404, detail="Knowledge node not found")
    return None
