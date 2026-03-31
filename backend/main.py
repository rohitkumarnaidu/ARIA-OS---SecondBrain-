from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import (
    tasks,
    courses,
    goals,
    ideas,
    chat,
    projects,
    resources,
    opportunities,
    income,
    habits,
    sleep,
    time,
)

app = FastAPI(
    title="Second Brain OS API",
    description="Personal AI productivity system for BTech CSE students",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])
app.include_router(goals.router, prefix="/api/goals", tags=["goals"])
app.include_router(ideas.router, prefix="/api/ideas", tags=["ideas"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(resources.router, prefix="/api/resources", tags=["resources"])
app.include_router(
    opportunities.router, prefix="/api/opportunities", tags=["opportunities"]
)
app.include_router(income.router, prefix="/api/income", tags=["income"])
app.include_router(habits.router, prefix="/api/habits", tags=["habits"])
app.include_router(sleep.router, prefix="/api/sleep", tags=["sleep"])
app.include_router(time.router, prefix="/api/time", tags=["time"])


@app.get("/")
async def root():
    return {"message": "Second Brain OS API is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
