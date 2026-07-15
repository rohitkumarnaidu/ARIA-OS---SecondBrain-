from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from config.core.supabase import get_supabase_client
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts
from shared.utils.logger import logger


async def detect_productivity_peaks(user_id: str, days: int = 30) -> dict:
    try:
        supabase = get_supabase_client()
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        resp = supabase.from_("time_entries").select("date, duration_minutes, category, start_time").eq("user_id", user_id).gte("date", cutoff[:10]).execute()
        entries = resp.data or []
        if not entries:
            return {"has_data": False, "message": "No time entries found in the selected period."}

        hourly: Dict[int, list] = {}
        daily: Dict[str, list] = {}
        for entry in entries:
            start = entry.get("start_time", "09:00")
            try:
                hour = int(start.split(":")[0])
            except (ValueError, IndexError):
                hour = 9
            duration = entry.get("duration_minutes", 0) or 0
            hourly.setdefault(hour, []).append(duration)
            day_name = entry.get("date", "unknown")
            daily.setdefault(day_name, []).append(duration)

        peak_hour = max(hourly, key=lambda h: sum(hourly[h]) / len(hourly[h]) if hourly[h] else 0)
        peak_minutes = int(sum(hourly.get(peak_hour, [])) / len(hourly.get(peak_hour, [1])))

        day_totals: Dict[str, float] = {}
        for day, dur_list in daily.items():
            try:
                dt = datetime.fromisoformat(day) if isinstance(day, str) else day
                day_name = dt.strftime("%A")
            except (ValueError, TypeError):
                day_name = "Unknown"
            day_totals[day_name] = day_totals.get(day_name, 0) + sum(dur_list)

        peak_day = max(day_totals, key=day_totals.get) if day_totals else "Monday"

        return {
            "has_data": True,
            "peak_hour": f"{peak_hour:02d}:00",
            "peak_hour_avg_minutes": peak_minutes,
            "peak_day": peak_day,
            "hourly_breakdown": {f"{h:02d}:00": int(sum(v) / len(v)) for h, v in sorted(hourly.items())},
            "daily_totals_minutes": {d: int(t) for d, t in sorted(day_totals.items())},
            "total_entries": len(entries),
        }
    except Exception as e:
        logger.error("detect_productivity_peaks failed", user_id=user_id, error=str(e))
        return {"has_data": False, "error": str(e)}


async def analyze_trends(user_id: str, metric: str, days: int = 30) -> dict:
    try:
        supabase = get_supabase_client()
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        if metric == "tasks_completed":
            resp = supabase.from_("tasks").select("completed_at").eq("user_id", user_id).eq("status", "completed").gte("completed_at", cutoff).execute()
            items = resp.data or []
            daily = {}
            for item in items:
                day = (item.get("completed_at") or "")[:10]
                daily[day] = daily.get(day, 0) + 1
            return {"metric": metric, "daily_counts": daily, "total": len(items), "days": days}

        elif metric == "courses_progress":
            resp = supabase.from_("learning_progress").select("date, data").eq("user_id", user_id).gte("date", cutoff[:10]).order("date", ascending=True).execute()
            entries = resp.data or []
            daily = {}
            for e in entries:
                d = e.get("data", {})
                if isinstance(d, str):
                    try:
                        import json
                        d = json.loads(d)
                    except (json.JSONDecodeError, TypeError):
                        d = {}
                day = (e.get("date") or "")[:10]
                daily[day] = d.get("courses_completed", 0) if isinstance(d, dict) else 0
            return {"metric": metric, "daily_counts": daily, "total_entries": len(entries), "days": days}

        elif metric == "habits_streak":
            resp = supabase.from_("habits").select("name, current_streak").eq("user_id", user_id).execute()
            habits = resp.data or []
            return {"metric": metric, "habits": {h.get("name", "unknown"): h.get("current_streak", 0) for h in habits}, "total_habits": len(habits), "days": days}

        elif metric == "sleep_score":
            resp = supabase.from_("sleep_logs").select("date, quality").eq("user_id", user_id).gte("date", cutoff[:10]).order("date", ascending=True).execute()
            logs = resp.data or []
            daily = {}
            for log in logs:
                daily[(log.get("date") or "")[:10]] = log.get("quality", 0)
            avg = sum(daily.values()) / len(daily) if daily else 0
            return {"metric": metric, "daily_scores": daily, "average": round(avg, 1), "total": len(logs), "days": days}

        elif metric == "focus_hours":
            resp = supabase.from_("time_entries").select("date, duration_minutes, category").eq("user_id", user_id).gte("date", cutoff[:10]).execute()
            entries = resp.data or []
            daily = {}
            for e in entries:
                day = (e.get("date") or "")[:10]
                cat = (e.get("category") or "").lower()
                if cat in ("deep_work", "focus", "study", "coding"):
                    daily[day] = daily.get(day, 0) + (e.get("duration_minutes", 0) or 0)
            return {"metric": metric, "daily_focus_minutes": daily, "total_entries": len(entries), "days": days}

        return {"metric": metric, "error": f"Unknown metric: {metric}"}

    except Exception as e:
        logger.error("analyze_trends failed", user_id=user_id, metric=metric, error=str(e))
        return {"metric": metric, "error": str(e)}


async def detect_anomalies(user_id: str) -> List[dict]:
    try:
        supabase = get_supabase_client()
        anomalies = []

        cutoff_30 = (datetime.now() - timedelta(days=30)).isoformat()
        tasks_resp = supabase.from_("tasks").select("completed_at, created_at").eq("user_id", user_id).gte("created_at", cutoff_30).execute()
        tasks = tasks_resp.data or []

        daily_completion: Dict[str, int] = {}
        for t in tasks:
            day = (t.get("completed_at") or t.get("created_at") or "")[:10]
            daily_completion[day] = daily_completion.get(day, 0) + 1

        if daily_completion:
            values = list(daily_completion.values())
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            std_dev = variance ** 0.5 if variance > 0 else 1
            for day, count in daily_completion.items():
                if count == 0 and mean > 1:
                    anomalies.append({"type": "procrastination_day", "date": day, "tasks_expected": round(mean, 1), "tasks_done": 0, "severity": "high" if mean > 3 else "medium"})
                elif count > mean + 2 * std_dev:
                    anomalies.append({"type": "breakthrough_productivity", "date": day, "tasks_done": count, "tasks_avg": round(mean, 1), "severity": "positive"})

        sleep_resp = supabase.from_("sleep_logs").select("date, quality, duration_hours").eq("user_id", user_id).gte("date", cutoff_30[:10]).execute()
        sleeps = sleep_resp.data or []
        if sleeps:
            qualities = [s.get("quality", 70) for s in sleeps]
            q_mean = sum(qualities) / len(qualities)
            q_var = sum((q - q_mean) ** 2 for q in qualities) / len(qualities)
            q_std = q_var ** 0.5 if q_var > 0 else 1
            for s in sleeps:
                q = s.get("quality", 70)
                if q < q_mean - 2 * q_std:
                    anomalies.append({"type": "poor_sleep", "date": s.get("date"), "quality": q, "avg_quality": round(q_mean, 1), "severity": "high"})
                elif q > q_mean + 2 * q_std:
                    anomalies.append({"type": "great_sleep", "date": s.get("date"), "quality": q, "avg_quality": round(q_mean, 1), "severity": "positive"})

        return anomalies
    except Exception as e:
        logger.error("detect_anomalies failed", user_id=user_id, error=str(e))
        return []


async def suggest_spaced_repetition(user_id: str, course_id: Optional[str] = None) -> List[dict]:
    try:
        supabase = get_supabase_client()
        if course_id:
            courses_resp = supabase.from_("courses").select("id, title, progress, last_reviewed").eq("id", course_id).eq("user_id", user_id).execute()
        else:
            courses_resp = supabase.from_("courses").select("id, title, progress, last_reviewed").eq("user_id", user_id).eq("status", "in_progress").execute()
        courses = courses_resp.data or []
        now = datetime.now()
        schedule = []
        for course in courses:
            last_reviewed = course.get("last_reviewed")
            if last_reviewed:
                try:
                    last_dt = datetime.fromisoformat(last_reviewed) if isinstance(last_reviewed, str) else last_reviewed
                    days_since = (now - last_dt).days
                except (ValueError, TypeError):
                    days_since = 30
            else:
                days_since = 30
            progress = course.get("progress", 0) or 0
            if progress < 30:
                interval_days = 1 if days_since > 1 else 0
            elif progress < 60:
                interval_days = 3 if days_since > 3 else 0
            elif progress < 80:
                interval_days = 7 if days_since > 7 else 0
            else:
                interval_days = 14 if days_since > 14 else 0
            if interval_days > 0:
                schedule.append({
                    "course_id": course.get("id"),
                    "course_title": course.get("title"),
                    "progress_pct": progress,
                    "days_since_review": days_since,
                    "suggested_review_date": (now + timedelta(days=1)).isoformat()[:10],
                    "interval_days": interval_days,
                    "reason": f"Review needed: {days_since}d since last review, {progress}% complete",
                })
        return schedule
    except Exception as e:
        logger.error("suggest_spaced_repetition failed", user_id=user_id, error=str(e))
        return []


async def track_user_progress(user_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()
    tasks_resp = supabase.from_("tasks").select("*").eq("user_id", user_id).execute()
    courses_resp = supabase.from_("courses").select("*").eq("user_id", user_id).execute()
    habits_resp = supabase.from_("habits").select("*").eq("user_id", user_id).execute()

    tasks = tasks_resp.data or []
    courses = courses_resp.data or []
    habits = habits_resp.data or []

    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    recent_tasks = [t for t in tasks if t.get("created_at", "") >= week_ago]
    completed_tasks = [t for t in tasks if t.get("status") == "completed" and t.get("completed_at", "") >= week_ago]

    learning_progress = {
        "tasks_created": len(recent_tasks),
        "tasks_completed": len(completed_tasks),
        "completion_rate": round(len(completed_tasks) / len(recent_tasks) * 100, 1) if recent_tasks else 0,
        "courses_enrolled": len([c for c in courses if c.get("status") in ["not_started", "in_progress"]]),
        "courses_completed": len([c for c in courses if c.get("status") == "completed"]),
        "active_habits": len([h for h in habits if h.get("is_active")]),
    }

    supabase.from_("learning_progress").insert(
        {"user_id": user_id, "date": datetime.now().date().isoformat(), "data": learning_progress}
    ).execute()
    return learning_progress


async def detect_learning_patterns(user_id: str) -> List[str]:
    progress = await track_user_progress(user_id)
    learning_prompt = prompts.get_agent("learning_agent")
    if learning_prompt:
        system = learning_prompt.system_prompt
        prompt = (
            f"Analyze this student learning data and identify patterns:\n"
            f"Progress data: {progress}\n"
            f"Return a JSON array of pattern strings."
        )
    else:
        system = "You are a learning analytics AI. Be concise."
        prompt = (
            f"Student learning data: {progress}. "
            f"Identify 1-3 learning patterns or insights. Return as a JSON array of strings."
        )
    try:
        result = await llm.generate_json(prompt, system=system)
    except LLMProviderUnavailableError:
        result = {}
    if isinstance(result, list):
        return result
    return result.get("patterns", ["Keep up the consistent work"])


async def suggest_learning_focus(user_id: str) -> Dict[str, Any]:
    patterns = await detect_learning_patterns(user_id)
    learning_prompt = prompts.get_agent("learning_agent")
    system = learning_prompt.system_prompt if learning_prompt else "You are a learning coach."
    prompt = f"Based on these learning patterns: {patterns}, suggest 2 concrete recommendations. Return JSON with 'recommendations' array."
    try:
        result = await llm.generate_json(prompt, system=system)
    except LLMProviderUnavailableError:
        result = {}
    return {
        "patterns": patterns,
        "recommendations": result.get("recommendations", ["Stay consistent with your study routine"]),
    }
