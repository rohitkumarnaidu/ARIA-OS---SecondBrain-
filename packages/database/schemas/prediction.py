from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class TimeSlot(BaseModel):
    hour: int
    day_of_week: int
    productivity_score: float
    task_count: int
    completion_rate: float


class SmartSlotResponse(BaseModel):
    slots: list[TimeSlot]
    best_hour: int
    best_day: int


class BedtimePrediction(BaseModel):
    optimal_bedtime: str
    optimal_wake: str
    expected_score: float
    confidence: str
    based_on_sessions: int


class StreakPrediction(BaseModel):
    habit_id: str
    habit_name: str
    current_streak: int
    risk_level: str
    risk_probability: float
    recommendation: str


class CompletionPrediction(BaseModel):
    task_id: str
    title: str
    probability: float
    confidence: str
    due_date: Optional[str] = None
    recommendation: str


class HabitCompletionForecast(BaseModel):
    total_active: int
    at_risk_count: int
    predictions: list[StreakPrediction]


class TaskCompletionForecast(BaseModel):
    total_pending: int
    high_completion: int
    at_risk_count: int
    predictions: list[CompletionPrediction]


class SleepInsight(BaseModel):
    average_score: float
    average_duration: float
    trend: str
    recommendation: str
    bedtime_prediction: Optional[BedtimePrediction] = None
