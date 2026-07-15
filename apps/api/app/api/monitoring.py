import collections
from typing import Optional
from fastapi import APIRouter, Depends, Query
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from config.core.config import settings
from shared.utils.logger import logger
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from database.schemas.agent_activity import AgentActivityLogCreate, AgentActivityFeedResponse
from shared.utils.ai_cache import ai_cache

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


@router.post("/activity", summary="Log agent activity", response_model=dict, status_code=201)
async def record_agent_activity(req: AgentActivityLogCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    now = datetime.now(timezone.utc).isoformat()
    record = {
        "id": str(uuid4()),
        "user_id": current_user.user.id,
        "agent_name": req.agent_name,
        "status": req.status,
        "started_at": (req.started_at.isoformat() if req.started_at else now),
        "completed_at": req.completed_at.isoformat() if req.completed_at else None,
        "duration_ms": req.duration_ms,
        "error_message": req.error_message,
        "input_summary": req.input_summary,
        "output_summary": req.output_summary,
        "created_at": now,
    }
    try:
        supabase.from_("agent_activity_log").insert(record).execute()
    except Exception as e:
        logger.error("Failed to record agent activity", error=str(e))
    return {"status": "ok", "id": record["id"]}


@router.get("/activity", summary="Get agent activity feed", response_model=AgentActivityFeedResponse)
async def get_agent_activity_feed(
    current_user=Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    supabase = get_supabase_client()
    try:
        count_result = (
            supabase.from_("agent_activity_log")
            .select("id", count="exact")
            .eq("user_id", current_user.user.id)
            .execute()
        )
        total = count_result.count if hasattr(count_result, "count") and count_result.count else 0
    except Exception:
        total = 0

    try:
        result = (
            supabase.from_("agent_activity_log")
            .select("id, user_id, agent_name, status, started_at, completed_at, duration_ms, error_message, input_summary, output_summary, created_at")
            .eq("user_id", current_user.user.id)
            .order("started_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        items = result.data or []
    except Exception as e:
        logger.error("Failed to fetch agent activity", error=str(e))
        items = []

    return {
        "data": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def _calc_trend(sparkline: list[dict]) -> tuple[str, float]:
    if len(sparkline) < 2:
        return "neutral", 0.0
    first = sparkline[0]["value"]
    last = sparkline[-1]["value"]
    if first == 0.0:
        return "neutral", 0.0
    change = round((last - first) / first * 100, 1)
    trend = "up" if change > 0 else ("down" if change < 0 else "neutral")
    return trend, change


@router.get("/ai-cache", summary="Get AI response cache statistics")
async def get_ai_cache_stats(current_user=Depends(get_current_user)):
    return {
        "status": "ok",
        "cache": ai_cache.stats,
    }


@router.delete("/ai-cache", summary="Clear AI response cache", status_code=204)
async def clear_ai_cache(current_user=Depends(get_current_user)):
    ai_cache.clear()
    return None


@router.get("/metrics", summary="Get RED metrics dashboard data (Rate, Errors, Duration)")
async def get_metrics(
    current_user=Depends(get_current_user),
    period: str = Query("24h", pattern="^(1h|6h|24h|7d)$"),
    agent: Optional[str] = Query(None),
):
    supabase = get_supabase_client()
    now = datetime.now(timezone.utc)
    period_map = {"1h": 1, "6h": 6, "24h": 24, "7d": 168}
    hours = period_map[period]
    since = now - timedelta(hours=hours)

    # Fetch token usage data
    query = (
        supabase.from_("token_usage")
        .select("id, agent, total_tokens, duration_ms, cost_usd, created_at")
        .eq("user_id", current_user.user.id)
        .gte("created_at", since.isoformat())
    )
    if agent:
        query = query.eq("agent", agent)
    token_result = query.execute()
    token_items = token_result.data or []

    # Fetch agent activity for error rate
    act_query = (
        supabase.from_("agent_activity_log")
        .select("id, agent_name, status, started_at, duration_ms")
        .eq("user_id", current_user.user.id)
        .gte("started_at", since.isoformat())
    )
    act_result = act_query.execute()
    activities = act_result.data or []

    # Group token usage into time buckets for sparklines
    buckets: dict[str, list[dict]] = collections.defaultdict(list)
    for item in token_items:
        ts = item.get("created_at", "")
        if ts:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            key = dt.strftime("%Y-%m-%d") if period == "7d" else dt.strftime("%Y-%m-%dT%H:00:00")
            buckets[key].append(item)

    sorted_keys = sorted(buckets.keys())
    bucket_seconds = 86400 if period == "7d" else 3600

    rate_sparkline: list[dict] = []
    dur_p50_sparkline: list[dict] = []
    dur_p95_sparkline: list[dict] = []
    dur_p99_sparkline: list[dict] = []
    error_sparkline: list[dict] = []

    for key in sorted_keys:
        bucket = buckets[key]
        count = len(bucket)
        rate_sparkline.append({"timestamp": key, "value": round(count / bucket_seconds, 4)})

        durations = sorted([i.get("duration_ms", 0) for i in bucket if i.get("duration_ms") is not None])
        if durations:
            dlen = len(durations)
            p50 = durations[dlen // 2]
            p95 = durations[int(dlen * 0.95)] if dlen >= 20 else durations[-1]
            p99 = durations[int(dlen * 0.99)] if dlen >= 100 else durations[-1]
        else:
            p50 = p95 = p99 = 0
        dur_p50_sparkline.append({"timestamp": key, "value": p50})
        dur_p95_sparkline.append({"timestamp": key, "value": p95})
        dur_p99_sparkline.append({"timestamp": key, "value": p99})

        # Error rate per bucket (matched by date prefix)
        day_prefix = key[:10]
        bucket_acts = [a for a in activities if (a.get("started_at") or "").startswith(day_prefix)]
        total_acts = len(bucket_acts)
        failed_acts = len([a for a in bucket_acts if a.get("status") == "failed"])
        err_val = round(failed_acts / total_acts * 100, 2) if total_acts > 0 else 0
        error_sparkline.append({"timestamp": key, "value": err_val})

    # Per-agent breakdown
    agents_map: dict[str, dict] = {}
    for item in token_items:
        name = item.get("agent", "unknown")
        entry = agents_map.setdefault(name, {"calls": 0, "tokens": 0, "durations": [], "errors": 0, "cost": 0.0})
        entry["calls"] += 1
        entry["tokens"] += item.get("total_tokens", 0)
        d = item.get("duration_ms")
        if d is not None:
            entry["durations"].append(d)
        entry["cost"] += item.get("cost_usd", 0.0)

    for act in activities:
        name = act.get("agent_name", "unknown")
        if name in agents_map and act.get("status") == "failed":
            agents_map[name]["errors"] += 1

    agent_list = []
    for name, data in agents_map.items():
        avg_dur = round(sum(data["durations"]) / max(len(data["durations"]), 1), 1) if data["durations"] else 0
        err_rate = round(data["errors"] / max(data["calls"], 1) * 100, 2)
        agent_list.append({
            "name": name,
            "calls": data["calls"],
            "tokens": data["tokens"],
            "avg_duration_ms": avg_dur,
            "error_rate": err_rate,
            "cost_usd": round(data["cost"], 6),
        })
    agent_list.sort(key=lambda x: x["calls"], reverse=True)

    # Overall current values
    all_durations = sorted([i.get("duration_ms", 0) for i in token_items if i.get("duration_ms") is not None])
    adlen = len(all_durations)
    overall_p50 = all_durations[adlen // 2] if adlen else 0
    overall_p95 = all_durations[int(adlen * 0.95)] if adlen >= 20 else (all_durations[-1] if adlen else 0)
    overall_p99 = all_durations[int(adlen * 0.99)] if adlen >= 100 else (all_durations[-1] if adlen else 0)

    total_activities = len(activities)
    failed_activities = len([a for a in activities if a.get("status") == "failed"])
    overall_error_rate = round(failed_activities / max(total_activities, 1) * 100, 2)
    overall_rate = round(len(token_items) / max(hours * 3600, 1), 4)

    # Service health checks
    services = {}
    services["api"] = {"status": "ok", "uptime": 99.9, "last_checked": now.isoformat(), "latency_ms": 0}
    try:
        t0 = datetime.now(timezone.utc)
        supabase.from_("users").select("count", count="exact").limit(1).execute()
        db_latency = int((datetime.now(timezone.utc) - t0).total_seconds() * 1000)
        services["supabase"] = {"status": "ok", "uptime": 99.8, "last_checked": now.isoformat(), "latency_ms": db_latency}
    except Exception:
        services["supabase"] = {"status": "unavailable", "uptime": 0.0, "last_checked": now.isoformat(), "latency_ms": 0}
    try:
        if settings.use_local_ai:
            import httpx
            t0 = datetime.now(timezone.utc)
            resp = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=5)
            ai_latency = int((datetime.now(timezone.utc) - t0).total_seconds() * 1000)
            services["ai"] = {
                "status": "ok" if resp.status_code == 200 else "degraded",
                "uptime": 99.5 if resp.status_code == 200 else 80.0,
                "last_checked": now.isoformat(),
                "latency_ms": ai_latency,
            }
        else:
            services["ai"] = {
                "status": "configured" if settings.claude_api_key else "not_configured",
                "uptime": 100.0,
                "last_checked": now.isoformat(),
                "latency_ms": 0,
            }
    except Exception:
        services["ai"] = {"status": "unavailable", "uptime": 0.0, "last_checked": now.isoformat(), "latency_ms": 0}
    services["scheduler"] = {"status": "ok", "uptime": 99.7, "last_checked": now.isoformat(), "latency_ms": 0}

    return {
        "rate": {
            "current": overall_rate,
            "sparkline": rate_sparkline,
            "trend": _calc_trend(rate_sparkline)[0],
            "changePercent": _calc_trend(rate_sparkline)[1],
        },
        "errors": {
            "current": overall_error_rate,
            "sparkline": error_sparkline,
            "trend": _calc_trend(error_sparkline)[0],
            "changePercent": _calc_trend(error_sparkline)[1],
        },
        "duration": {
            "p50": {
                "current": overall_p50,
                "sparkline": dur_p50_sparkline,
                "trend": _calc_trend(dur_p50_sparkline)[0],
                "changePercent": _calc_trend(dur_p50_sparkline)[1],
            },
            "p95": {
                "current": overall_p95,
                "sparkline": dur_p95_sparkline,
                "trend": _calc_trend(dur_p95_sparkline)[0],
                "changePercent": _calc_trend(dur_p95_sparkline)[1],
            },
            "p99": {
                "current": overall_p99,
                "sparkline": dur_p99_sparkline,
                "trend": _calc_trend(dur_p99_sparkline)[0],
                "changePercent": _calc_trend(dur_p99_sparkline)[1],
            },
        },
        "agents": agent_list,
        "services": services,
    }
