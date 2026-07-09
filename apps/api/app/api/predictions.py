from fastapi import APIRouter, Depends, HTTPException
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from shared.utils.logger import logger
from database.schemas.prediction import (
    TaskCompletionForecast,
    CompletionPrediction,
    HabitCompletionForecast,
    StreakPrediction,
    SleepInsight,
    BedtimePrediction,
    SmartSlotResponse,
    TimeSlot,
)

router = APIRouter()


@router.get("/tasks", summary="Predict task completion probabilities", response_model=TaskCompletionForecast)
async def predict_task_completion(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    try:
        resp = (
            supabase.from_("tasks")
            .select(
                "id, user_id, title, status, priority, due_date, created_at, updated_at, completed_at, estimated_minutes, category, description, project_id, goal_id, is_recurring, recurring_frequency, dependency_id, missed_count"
            )
            .eq("user_id", current_user.user.id)
            .order("created_at", ascending=False)
            .execute()
        )
        tasks = resp.data or []
    except Exception as e:
        logger.error("Failed to fetch tasks for prediction", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch tasks")

    total = len(tasks)
    if total == 0:
        return TaskCompletionForecast(total_pending=0, high_completion=0, at_risk_count=0, predictions=[])

    completed = sum(1 for t in tasks if t.get("status") == "completed")
    overall_rate = completed / max(total, 1)

    pending = [t for t in tasks if t.get("status") == "pending"]
    predictions = []
    high_count = 0
    at_risk_count = 0

    for t in pending:
        prob = overall_rate * 100
        priority = t.get("priority", "medium")
        if priority == "high":
            prob += 15
        elif priority == "low":
            prob -= 10

        due = t.get("due_date")
        if due:
            try:
                from datetime import datetime

                due_date = datetime.fromisoformat(due.replace("Z", "+00:00"))
                days_left = (due_date - datetime.now(due_date.tzinfo)).days
                if days_left < 0:
                    prob = max(5, prob - 30)
                elif days_left == 0:
                    prob = max(10, prob - 15)
                elif days_left <= 3:
                    prob = min(100, prob + 5)
            except (ValueError, TypeError):
                pass

        prob = max(0, min(100, prob))
        confidence = "High" if completed > 20 else "Medium" if completed > 5 else "Low"
        if prob >= 70:
            high_count += 1
        elif prob < 40:
            at_risk_count += 1

        predictions.append(
            CompletionPrediction(
                task_id=t.get("id", ""),
                title=t.get("title", "Untitled"),
                probability=round(prob, 1),
                confidence=confidence,
                due_date=due,
                recommendation=(
                    "On track"
                    if prob >= 70
                    else "Needs attention" if prob >= 40 else "High risk — prioritize this task"
                ),
            )
        )

    return TaskCompletionForecast(
        total_pending=len(pending),
        high_completion=high_count,
        at_risk_count=at_risk_count,
        predictions=predictions,
    )


@router.get("/habits", summary="Predict habit streak risks", response_model=HabitCompletionForecast)
async def predict_habits(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    try:
        resp = (
            supabase.from_("habits")
            .select(
                "id, user_id, name, frequency, is_active, current_streak, best_streak, consistency_percentage, created_at"
            )
            .eq("user_id", current_user.user.id)
            .execute()
        )
        habits = resp.data or []
    except Exception as e:
        logger.error("Failed to fetch habits for prediction", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch habits")

    predictions = []
    at_risk_count = 0

    for h in habits:
        if not h.get("is_active", True):
            continue
        streak = h.get("current_streak", 0) or 0
        consistency = h.get("consistency_percent", 50) or 50

        if streak > 20 and consistency > 80:
            risk = 10
            risk_level = "Low"
        elif streak > 10 and consistency > 60:
            risk = 25
            risk_level = "Low"
        elif streak > 5 and consistency > 40:
            risk = 45
            risk_level = "Medium"
        else:
            risk = 65
            risk_level = "High"

        if risk >= 50:
            at_risk_count += 1

        predictions.append(
            StreakPrediction(
                habit_id=h.get("id", ""),
                habit_name=h.get("name", "Unnamed Habit"),
                current_streak=streak,
                risk_level=risk_level,
                risk_probability=risk,
                recommendation=(
                    "Keep up the momentum!"
                    if risk < 30
                    else (
                        "Try to stay consistent — short sessions beat skipped days"
                        if risk < 50
                        else "This habit needs attention — set a daily reminder"
                    )
                ),
            )
        )

    return HabitCompletionForecast(
        total_active=len(predictions),
        at_risk_count=at_risk_count,
        predictions=predictions,
    )


@router.get("/sleep", summary="Predict sleep insights", response_model=SleepInsight)
async def predict_sleep(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    try:
        resp = (
            supabase.from_("sleep_logs")
            .select(
                "id, user_id, date, bedtime, wake_time, duration_hours, sleep_score, sleep_debt, quality_rating, created_at"
            )
            .eq("user_id", current_user.user.id)
            .order("date", ascending=False)
            .limit(30)
            .execute()
        )
        logs = resp.data or []
    except Exception as e:
        logger.error("Failed to fetch sleep logs for prediction", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch sleep logs")

    if not logs:
        return SleepInsight(
            average_score=0,
            average_duration=0,
            trend="insufficient_data",
            recommendation="Start logging your sleep to get personalized insights",
        )

    score_sum = 0
    duration_sum = 0.0
    score_count = 0
    best_bedtime = None
    best_score = 0

    for entry in logs:
        score = entry.get("sleep_score")
        if score is not None:
            score_sum += score
            score_count += 1
        dur = entry.get("duration_hours")
        if dur is not None:
            duration_sum += dur
        bedtime = entry.get("bedtime")
        if bedtime and score and score > best_score:
            best_score = score
            best_bedtime = bedtime

    avg_score = round(score_sum / max(score_count, 1), 1)
    avg_duration = round(duration_sum / max(len(logs), 1), 1)

    recent = logs[:7]
    recent_avg = 0
    if recent:
        r_sum = sum(e.get("sleep_score", 0) or 0 for e in recent)
        recent_avg = r_sum / len(recent)

    trend = "stable"
    if score_count >= 14:
        older = logs[-14:-7]
        if older:
            older_avg = sum(e.get("sleep_score", 0) or 0 for e in older) / len(older)
            if recent_avg > older_avg + 5:
                trend = "improving"
            elif recent_avg < older_avg - 5:
                trend = "declining"

    bedtime_prediction = None
    if best_bedtime:
        from datetime import datetime, timedelta

        try:
            bt = datetime.fromisoformat(best_bedtime.replace("Z", "+00:00"))
            optimal = (bt + timedelta(hours=8)).isoformat()
            bedtime_prediction = BedtimePrediction(
                optimal_bedtime=best_bedtime[:16],
                optimal_wake=optimal[:16],
                expected_score=min(100, avg_score + 5),
                confidence="Medium" if score_count >= 10 else "Low",
                based_on_sessions=score_count,
            )
        except (ValueError, TypeError):
            pass

    rec = (
        "Great sleep quality! Keep your consistent schedule."
        if avg_score >= 80
        else (
            "Good sleep habits. Try winding down 30 min earlier."
            if avg_score >= 65
            else "Your sleep needs improvement. Aim for 7-8 hours consistently."
        )
    )

    return SleepInsight(
        average_score=avg_score,
        average_duration=avg_duration,
        trend=trend,
        recommendation=rec,
        bedtime_prediction=bedtime_prediction,
    )


@router.get("/slots", summary="Predict optimal productivity slots", response_model=SmartSlotResponse)
async def predict_smart_slots(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    try:
        resp = (
            supabase.from_("time_entries")
            .select(
                "id, user_id, start_time, end_time, duration_minutes, category, is_deep_work, description, created_at"
            )
            .eq("user_id", current_user.user.id)
            .execute()
        )
        entries = resp.data or []
    except Exception as e:
        logger.error("Failed to fetch time entries for slot prediction", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch time entries")

    from collections import defaultdict

    slot_map: dict[tuple[int, int], list[int]] = defaultdict(list)

    for e in entries:
        dur = e.get("duration_minutes", 0) or 0
        start = e.get("start_time")
        if not start:
            continue
        try:
            from datetime import datetime

            dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            hour = dt.hour
            day = dt.weekday()
            slot_map[(day, hour)].append(dur)
        except (ValueError, TypeError):
            pass

    slots = []
    best_hour = 9
    best_day = 0
    best_score = 0

    for (day, hour), durs in slot_map.items():
        total_minutes = sum(durs)
        count = len(durs)
        score = round(total_minutes / max(count, 1) / 60 * 10, 1)
        if score > best_score:
            best_score = score
            best_hour = hour
            best_day = day

        statuses = supabase.from_("tasks").select("status").eq("user_id", current_user.user.id).execute()
        tasks = statuses.data or []
        completed = sum(1 for t in tasks if t.get("status") == "completed")
        total = max(len(tasks), 1)

        slots.append(
            TimeSlot(
                hour=hour,
                day_of_week=day,
                productivity_score=score,
                task_count=count,
                completion_rate=round(completed / total * 100, 1),
            )
        )

    slots.sort(key=lambda s: s.productivity_score, reverse=True)

    return SmartSlotResponse(
        slots=slots[:20],
        best_hour=best_hour,
        best_day=best_day,
    )
