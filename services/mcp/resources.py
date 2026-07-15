"""MCP resource definitions — exposes ARIA OS data as MCP resources via aria:// URIs."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "packages"))

import mcp.types as types
from mcp.types import Resource, ResourceContents, TextResourceContents

from shared.utils.logger import logger


class MCPResourceRegistry:
    """Registry of ARIA OS resources accessible via MCP.

    Resources use the aria:// URI scheme:
      aria://tasks              → All user tasks
      aria://tasks/{id}         → Single task by ID
      aria://courses             → All courses
      aria://goals               → All goals
      aria://habits              → All habits
      aria://briefing/today      → Today's briefing
      aria://review/current      → Current weekly review
      aria://memory              → All memory entries
    """

    def __init__(self):
        self._resources: list[Resource] = []
        self._discovered = False

    def discover(self):
        """Register all available resources."""
        self._resources = [
            Resource(
                uri="aria://tasks",
                name="All Tasks",
                description="List all tasks for the authenticated user",
                mimeType="application/json",
            ),
            Resource(
                uri="aria://tasks/{task_id}",
                name="Task by ID",
                description="Retrieve a single task by its UUID",
                mimeType="application/json",
            ),
            Resource(
                uri="aria://courses",
                name="All Courses",
                description="List all courses for the authenticated user",
                mimeType="application/json",
            ),
            Resource(
                uri="aria://courses/{course_id}",
                name="Course by ID",
                description="Retrieve a single course by its UUID",
                mimeType="application/json",
            ),
            Resource(
                uri="aria://goals",
                name="All Goals",
                description="List all goals for the authenticated user",
                mimeType="application/json",
            ),
            Resource(
                uri="aria://goals/{goal_id}",
                name="Goal by ID",
                description="Retrieve a single goal by its UUID",
                mimeType="application/json",
            ),
            Resource(
                uri="aria://habits",
                name="All Habits",
                description="List all habits for the authenticated user",
                mimeType="application/json",
            ),
            Resource(
                uri="aria://habits/{habit_id}",
                name="Habit by ID",
                description="Retrieve a single habit by its UUID",
                mimeType="application/json",
            ),
            Resource(
                uri="aria://briefing/today",
                name="Today's Briefing",
                description="Get the daily briefing for the current date",
                mimeType="application/json",
            ),
            Resource(
                uri="aria://review/current",
                name="Current Weekly Review",
                description="Get the current weekly review",
                mimeType="application/json",
            ),
            Resource(
                uri="aria://memory",
                name="All Memory Entries",
                description="List all memory entries for the authenticated user",
                mimeType="application/json",
            ),
            Resource(
                uri="aria://memory/{key}",
                name="Memory by Key",
                description="Retrieve a single memory entry by key",
                mimeType="application/json",
            ),
        ]
        self._discovered = True
        logger.info("MCP resources discovered", count=len(self._resources))

    def list_resources(self) -> list[Resource]:
        if not self._discovered:
            self.discover()
        return self._resources

    async def read_resource(self, uri: str) -> list[ResourceContents]:
        """Resolve an aria:// URI to its resource content.

        In a production deployment, this would query Supabase.
        Returns structured metadata about the resource template.
        """
        if not uri.startswith("aria://"):
            return [
                TextResourceContents(
                    uri=uri,
                    mimeType="application/json",
                    text=json.dumps({"error": f"Unsupported URI scheme: {uri}"}),
                )
            ]

        path = uri[7:]  # strip "aria://"

        if path == "tasks":
            description = "List of all tasks. Use aria_list_tasks tool to fetch."
        elif path.startswith("tasks/"):
            task_id = path.split("/")[1]
            description = f"Task with ID: {task_id}. Use aria_get_task tool to fetch."
        elif path == "courses":
            description = "List of all courses. Use aria_list_courses tool to fetch."
        elif path.startswith("courses/"):
            course_id = path.split("/")[1]
            description = f"Course with ID: {course_id}. Use aria_get_course tool to fetch."
        elif path == "goals":
            description = "List of all goals. Use aria_list_goals tool to fetch."
        elif path.startswith("goals/"):
            goal_id = path.split("/")[1]
            description = f"Goal with ID: {goal_id}. Use aria_get_goal tool to fetch."
        elif path == "habits":
            description = "List of all habits. Use aria_list_habits tool to fetch."
        elif path.startswith("habits/"):
            habit_id = path.split("/")[1]
            description = f"Habit with ID: {habit_id}. Use aria_get_habit tool to fetch."
        elif path == "briefing/today":
            description = "Today's briefing. Use aria_get_briefing tool to fetch."
        elif path == "review/current":
            description = "Current weekly review. Use aria_get_review tool to fetch."
        elif path == "memory":
            description = "All memory entries. Use aria_get_memory tool to fetch."
        elif path.startswith("memory/"):
            key = path.split("/")[1]
            description = f"Memory entry with key: {key}. Use aria_get_memory tool to fetch."
        else:
            description = f"Unknown resource: {uri}"

        return [
            TextResourceContents(
                uri=uri,
                mimeType="application/json",
                text=json.dumps({
                    "uri": uri,
                    "description": description,
                    "note": "This resource is a template. Use the corresponding MCP tool to fetch live data.",
                    "resolved_at": datetime.now(timezone.utc).isoformat(),
                }, indent=2),
            )
        ]
