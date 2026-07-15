from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from config.core.supabase import get_supabase_client
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts
from shared.utils.logger import logger


def _get_week_logs(supabase, user_id: str) -> List[dict]:
    week_resp = (
        supabase.from_("sleep_logs")
        .select("*")
        .eq("user_id", user_id)
        .order("date", ascending=False)
        .limit(7)
        .execute()
    )
    return week_resp.data or []


async def assign_sleep_profile(user_id: str) -> str:
    try:
        supabase = get_supabase_client()
        logs = _get_week_logs(supabase, user_id)
        if len(logs) < 3:
            return "Balanced"

        bedtimes = []
        durations = []
        qualities = []
        for log in logs:
            bedtime = log.get("bedtime") or log.get("sleep_time", "")
            duration = log.get("duration_hours", 0) or 0
            quality = log.get("quality", 70) or 0
            if bedtime:
                bedtimes.append(bedtime)
            durations.append(duration)
            qualities.append(quality)

        if not bedtimes:
            return "Balanced"

        early_count = 0
        late_count = 0
        for bt in bedtimes:
            try:
                hour = int(str(bt).split(":")[0])
                if hour < 22:
                    early_count += 1
                elif hour >= 0 or hour < 1:
                    late_count += 1
            except (ValueError, IndexError):
                pass

        avg_duration = sum(durations) / len(durations) if durations else 7
        avg_quality = sum(qualities) / len(qualities) if qualities else 70
        duration_std = (sum((d - avg_duration) ** 2 for d in durations) / len(durations)) ** 0.5 if durations else 0

        if duration_std > 2:
            return "Erratic"
        if avg_duration < 5 and avg_quality > 60:
            return "PowerNapper"
        if early_count > late_count and early_count >= 3:
            return "EarlyBird"
        if late_count > early_count and late_count >= 3:
            return "NightOwl"
        return "Balanced"

    except Exception as e:
        logger.error("assign_sleep_profile failed", user_id=user_id, error=str(e))
        return "Balanced"


async def analyze_sleep_debt(user_id: str, days: int = 14) -> dict:
    try:
        supabase = get_supabase_client()
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()[:10]
        resp = supabase.from_("sleep_logs").select("date, duration_hours, sleep_debt_hours, quality").eq("user_id", user_id).gte("date", cutoff).order("date", ascending=True).execute()
        logs = resp.data or []
        if not logs:
            return {"total_debt_hours": 0, "avg_debt_hours": 0, "trend": "stable", "logs_count": 0, "days_analyzed": days}

        total_debt = sum(l.get("sleep_debt_hours", 0) or 0 for l in logs)
        debts = [l.get("sleep_debt_hours", 0) or 0 for l in logs]
        avg_debt = total_debt / len(debts)

        if len(debts) >= 3:
            recent = debts[-3:]
            earlier = debts[:-3]
            if earlier and sum(recent) / len(recent) > sum(earlier) / len(earlier) * 1.2:
                trend = "increasing"
            elif earlier and sum(recent) / len(recent) < sum(earlier) / len(earlier) * 0.8:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return {
            "total_debt_hours": round(total_debt, 1),
            "avg_debt_hours": round(avg_debt, 1),
            "trend": trend,
            "daily_debts": {l.get("date", "unknown"): l.get("sleep_debt_hours", 0) for l in logs},
            "logs_count": len(logs),
            "days_analyzed": days,
        }
    except Exception as e:
        logger.error("analyze_sleep_debt failed", user_id=user_id, error=str(e))
        return {"total_debt_hours": 0, "avg_debt_hours": 0, "trend": "stable", "logs_count": 0, "days_analyzed": days}


async def adjust_tasks_for_energy(user_id: str, tasks: List[dict]) -> List[dict]:
    try:
        debt = await analyze_sleep_debt(user_id, 7)
        profile = await assign_sleep_profile(user_id)
        total_debt = debt.get("total_debt_hours", 0)
        adjusted = list(tasks)

        energy_multiplier = 1.0
        if total_debt > 10:
            energy_multiplier = 0.5
        elif total_debt > 5:
            energy_multiplier = 0.75
        elif total_debt > 3:
            energy_multiplier = 0.85

        adjusted.sort(key=lambda t: (
            -(t.get("priority_score", 0) or 0) * energy_multiplier,
            t.get("due_date", ""),
        ))

        for task in adjusted:
            if energy_multiplier < 0.8:
                est = task.get("estimated_minutes", 60) or 60
                task["adjusted_minutes"] = int(est * energy_multiplier)
                if est > 120:
                    task["suggestion"] = "Break this task into smaller chunks due to low energy"

        return adjusted
    except Exception as e:
        logger.error("adjust_tasks_for_energy failed", user_id=user_id, error=str(e))
        return tasks


async def generate_wind_down_routine(user_id: str) -> str:
    try:
        profile = await assign_sleep_profile(user_id)
        routines = {
            "EarlyBird": "Your wind-down starts at 8:30 PM. Dim lights, avoid screens, read a book, "
                        "drink herbal tea, and journal for 5 minutes. Lights out by 9:30 PM.",
            "NightOwl": "Your natural peak is late. Start winding down at 11 PM: put away screens, "
                       "do light stretching, listen to calm music. Aim for lights out by midnight.",
            "PowerNapper": "You thrive on short sleeps but quality matters. Wind down at 10 PM: "
                          "15 min meditation, cool room temperature, no caffeine after 6 PM.",
            "Erratic": "Your schedule varies. Establish a consistent wind-down: set a fixed bedtime "
                      "alarm, 30 min before: no screens, warm shower, calming tea. Consistency is key.",
            "Balanced": "Maintain your routine: 30 min before bed, dim lights, put away phone, "
                       "read something light, deep breathing for 2 minutes. Aim for 7-8 hours.",
        }
        return routines.get(profile, routines["Balanced"])
    except Exception as e:
        logger.error("generate_wind_down_routine failed", user_id=user_id, error=str(e))
        return "Maintain a consistent sleep schedule with a 30-minute wind-down routine."


async def generate_morning_recovery(user_id: str) -> str:
    try:
        supabase = get_supabase_client()
        latest_resp = supabase.from_("sleep_logs").select("*").eq("user_id", user_id).order("date", ascending=False).limit(1).execute()
        latest = latest_resp.data[0] if latest_resp.data else None
        if not latest:
            return "Start your day with a glass of water and some light stretching."

        quality = latest.get("quality", 70) or 70
        duration = latest.get("duration_hours", 7) or 7
        debt = latest.get("sleep_debt_hours", 0) or 0

        if quality < 50:
            return (
                f"Tough night ({quality}/100). Take it easy today: "
                "drink extra water, avoid caffeine after 2 PM, "
                "take a 15-min power nap if possible, and aim for an early bedtime tonight."
            )
        elif quality < 65:
            return (
                f"Not your best sleep ({quality}/100, {duration}h). "
                "Start with sunlight exposure, have a protein-rich breakfast, "
                "and avoid heavy meals for lunch. You'll recover by evening."
            )
        elif debt > 3:
            return (
                f"Good sleep quality ({quality}/100) but you have {debt}h of accumulated debt. "
                "Try to go to bed 30 min earlier tonight to catch up."
            )
        return (
            f"Great sleep ({quality}/100, {duration}h)! You're well-rested. "
            "Start your day with your most important task while energy is high."
        )
    except Exception as e:
        logger.error("generate_morning_recovery failed", user_id=user_id, error=str(e))
        return "Start your day with a glass of water and some light stretching."


async def analyze_sleep(user_id: str, date: Optional[str] = None) -> Dict[str, Any]:
    supabase = get_supabase_client()
    target_date = date or datetime.now().date().isoformat()

    resp = supabase.from_("sleep_logs").select("*").eq("user_id", user_id).eq("date", target_date).execute()
    logs = resp.data or []
    latest = logs[0] if logs else None

    week_logs = _get_week_logs(supabase, user_id)

    if not latest:
        return {
            "date": target_date,
            "has_data": False,
            "message": "No sleep data for this date.",
        }

    avg_quality = sum(log.get("quality", 0) for log in week_logs) / len(week_logs) if week_logs else 0

    sleep_prompt = prompts.get_agent("sleep_agent")
    if sleep_prompt:
        system = sleep_prompt.system_prompt
        user = (
            f"Analyze sleep data for {target_date}:\n"
            f"Score: {latest.get('quality')}\n"
            f"Duration: {latest.get('duration_hours')}h\n"
            f"Debt: {latest.get('sleep_debt_hours', 0)}h\n"
            f"7-day avg quality: {avg_quality:.0f}\n"
            f"Return JSON with: sleep_analysis, wind_down_routine (array of steps), "
            f"recommendations (array)."
        )
    else:
        system = "You are a sleep quality analyst. Provide concise, actionable insights."
        user = (
            f"Sleep score: {latest.get('quality')}/100, "
            f"duration: {latest.get('duration_hours')}h, "
            f"debt: {latest.get('sleep_debt_hours', 0)}h. "
            f"Return JSON with wind_down_routine and recommendations."
        )

    try:
        ai_response = await llm.generate_json(user, system=system)
    except LLMProviderUnavailableError:
        ai_response = {}

    profile = await assign_sleep_profile(user_id)
    debt_analysis = await analyze_sleep_debt(user_id, 14)
    morning_rec = await generate_morning_recovery(user_id)

    return {
        "date": target_date,
        "has_data": True,
        "score": latest.get("quality"),
        "duration_hours": latest.get("duration_hours"),
        "sleep_debt_hours": latest.get("sleep_debt_hours", 0),
        "seven_day_avg_quality": round(avg_quality, 1),
        "sleep_profile": profile,
        "sleep_debt_analysis": debt_analysis,
        "morning_recovery": morning_rec,
        "wind_down_routine": ai_response.get(
            "wind_down_routine",
            [
                "Dim lights 30 min before bed",
                "Put away phone 20 min before bed",
            ],
        ),
        "sleep_analysis": ai_response.get("sleep_analysis", "No analysis available"),
        "recommendations": ai_response.get(
            "recommendations",
            [
                "Maintain consistent sleep schedule",
            ],
        ),
    }


async def suggest_bedtime(user_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()
    resp = (
        supabase.from_("sleep_logs")
        .select("*")
        .eq("user_id", user_id)
        .order("date", ascending=False)
        .limit(3)
        .execute()
    )
    recent = resp.data or []
    scores = [log.get("quality", 0) for log in recent]
    avg = sum(scores) / len(scores) if scores else 70

    profile = "Balanced"
    try:
        profile = await assign_sleep_profile(user_id)
    except Exception:
        pass

    profile_bedtimes = {
        "EarlyBird": "21:00",
        "NightOwl": "23:30",
        "PowerNapper": "22:00",
        "Erratic": "22:00",
        "Balanced": "22:00",
    }
    suggested = profile_bedtimes.get(profile, "22:00")

    if avg < 60:
        suggested = "21:30"
    elif avg < 75:
        suggested = "22:00"
    else:
        suggested = "22:30"

    return {
        "suggested_bedtime": suggested,
        "based_on_avg_quality": round(avg, 1),
        "sleep_profile": profile,
        "message": f"Aim for bed by {suggested} to maintain or improve your sleep quality.",
    }
