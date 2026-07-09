from fastapi import APIRouter, Depends
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from shared.utils.logger import logger
from uuid import uuid4
from datetime import datetime, timezone

router = APIRouter()


def _compute_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    if model.startswith("ollama/"):
        return 0.0
    if "opus" in model:
        return (prompt_tokens / 1_000_000 * 15) + (completion_tokens / 1_000_000 * 75)
    if "sonnet" in model:
        return (prompt_tokens / 1_000_000 * 3) + (completion_tokens / 1_000_000 * 15)
    if "haiku" in model:
        return (prompt_tokens / 1_000_000 * 0.25) + (completion_tokens / 1_000_000 * 1.25)
    return (prompt_tokens + completion_tokens) / 1_000_000 * 3


@router.post("/token-usage", summary="Record token usage", response_model=dict)
async def record_token_usage(req: dict, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    prompt_tokens = req.get("prompt_tokens", 0)
    completion_tokens = req.get("completion_tokens", 0)
    model = req.get("model", "ollama/mistral:7b")
    record = {
        "id": str(uuid4()),
        "user_id": current_user.user.id,
        "agent": req.get("agent", "unknown"),
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "cost_usd": _compute_cost(model, prompt_tokens, completion_tokens),
        "duration_ms": req.get("duration_ms", 0),
        "endpoint": req.get("endpoint", ""),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        supabase.from_("token_usage").insert(record).execute()
    except Exception as e:
        logger.error("Failed to record token usage", error=str(e))
    return {"status": "ok"}


@router.get("/token-usage/summary", summary="Get token usage summary", response_model=dict)
async def token_usage_summary(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    try:
        result = (
            supabase.from_("token_usage")
            .select(
                "id, user_id, agent, model, prompt_tokens, completion_tokens, total_tokens, cost_usd, duration_ms, endpoint, created_at"
            )
            .eq("user_id", current_user.user.id)
            .execute()
        )
        items = result.data or []
    except Exception as e:
        logger.error("Failed to fetch token usage", error=str(e))
        return {"total_tokens": 0, "total_cost": 0, "by_agent": {}, "avg_duration_ms": 0, "total_calls": 0}

    total_tokens = sum(i.get("total_tokens", 0) for i in items)
    total_cost = sum(i.get("cost_usd", 0) for i in items)
    total_calls = len(items)
    by_agent: dict[str, int] = {}
    durations = []
    for i in items:
        agent = i.get("agent", "unknown")
        by_agent[agent] = by_agent.get(agent, 0) + i.get("total_tokens", 0)
        d = i.get("duration_ms")
        if d is not None:
            durations.append(d)

    durations.sort()
    avg_duration = round(sum(durations) / max(len(durations), 1), 1) if durations else 0
    p50 = durations[len(durations) // 2] if durations else 0
    p95 = durations[int(len(durations) * 0.95)] if len(durations) >= 20 else (durations[-1] if durations else 0)
    p99 = durations[int(len(durations) * 0.99)] if len(durations) >= 100 else (durations[-1] if durations else 0)

    return {
        "total_tokens": total_tokens,
        "total_calls": total_calls,
        "by_agent": by_agent,
        "avg_duration_ms": avg_duration,
        "p50_ms": p50,
        "p95_ms": p95,
        "p99_ms": p99,
        "estimated_cost_usd": round(total_cost, 4),
    }
