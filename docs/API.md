# API Documentation

## Base URL
```
Production: https://your-api-domain.com
Development: http://localhost:8000
```

## Authentication
All endpoints require Bearer token authentication. Get token from Supabase Auth.

```
Authorization: Bearer <supabase_access_token>
```

## Endpoints

---

## Tasks

### GET /api/tasks
Get all tasks for current user

**Query Parameters:**
- `status` (optional): pending, in_progress, completed, cancelled
- `priority` (optional): low, medium, high, urgent
- `category` (optional): study, project, habit, personal, income

**Response:**
```json
{
  "tasks": [
    {
      "id": "uuid",
      "title": "Task title",
      "description": "Task description",
      "priority": "high",
      "category": "study",
      "status": "pending",
      "estimated_minutes": 30,
      "due_date": "2024-01-15T10:00:00Z",
      "goal_id": "uuid",
      "project_id": "uuid",
      "completed_at": null,
      "missed_count": 0,
      "created_at": "2024-01-10T10:00:00Z",
      "updated_at": "2024-01-10T10:00:00Z"
    }
  ]
}
```

### POST /api/tasks
Create a new task

**Request Body:**
```json
{
  "title": "Task title",
  "description": "Optional description",
  "priority": "medium",
  "category": "study",
  "estimated_minutes": 45,
  "due_date": "2024-01-15T10:00:00Z",
  "goal_id": "uuid (optional)",
  "project_id": "uuid (optional)"
}
```

### PUT /api/tasks/{task_id}
Update a task

### DELETE /api/tasks/{task_id}
Delete a task

### POST /api/tasks/{task_id}/complete
Mark task as completed

---

## Courses

### GET /api/courses
Get all courses

### POST /api/courses
Add a new course (deadline required)

### PUT /api/courses/{course_id}
Update course progress

### DELETE /api/courses/{course_id}
Delete a course

---

## Goals

### GET /api/goals
Get all goals with roadmap nodes

### POST /api/goals
Create a new goal with roadmap

### PUT /api/goals/{goal_id}
Update goal (including nodes)

### DELETE /api/goals/{goal_id}
Delete a goal

---

## Projects

### GET /api/projects
Get all projects

### POST /api/projects
Create a new project

### PUT /api/projects/{project_id}
Update project phase, next action, blocker

### DELETE /api/projects/{project_id}
Delete a project

---

## Resources

### GET /api/resources
Get all saved resources

**Query Parameters:**
- `q` (optional): Natural language search query
- `type` (optional): article, book, github, tool, paper
- `archived` (optional): true, false

### POST /api/resources
Save a new resource

### PUT /api/resources/{resource_id}
Update resource

### DELETE /api/resources/{resource_id}
Delete resource

---

## Ideas

### GET /api/ideas
Get all ideas

### POST /api/ideas
Capture a new idea

### PUT /api/ideas/{idea_id}
Update idea status or research

### DELETE /api/ideas/{idea_id}
Delete idea

---

## Opportunities

### GET /api/opportunities
Get scanned opportunities

**Query Parameters:**
- `type` (optional): internship, hackathon, open_source, fellowship, freelance
- `status` (optional): new, saved, applied, rejected, accepted

### POST /api/opportunities
Manually add an opportunity

### PUT /api/opportunities/{opp_id}
Update opportunity status

---

## Income

### GET /api/income
Get income entries

**Query Parameters:**
- `start_date` (optional): Start date filter
- `end_date` (optional): End date filter

### POST /api/income
Log new income entry

### GET /api/income/summary
Get income summary with hourly rates

---

## Habits

### GET /api/habits
Get all habits with streak data

### POST /api/habits
Create a new habit

### PUT /api/habits/{habit_id}
Update habit

### DELETE /api/habits/{habit_id}
Delete habit

### POST /api/habits/{habit_id}/log
Log habit completion for today

---

## Sleep

### GET /api/sleep
Get sleep logs

### POST /api/sleep
Log sleep entry (bedtime + wake time + quality)

### GET /api/sleep/stats
Get sleep statistics

---

## Time Tracking

### GET /api/time
Get time entries

**Query Parameters:**
- `date` (optional): Specific date
- `task_id` (optional): Filter by task

### POST /api/time/start
Start a timer

**Request Body:**
```json
{
  "task_id": "uuid (optional)",
  "description": "Working on..."
}
```

### POST /api/time/stop
Stop the current timer

### GET /api/time/active
Get currently running timer

---

## Chat (ARIA)

### POST /api/chat
Send message to ARIA

**Request Body:**
```json
{
  "message": "What should I focus on today?"
}
```

**Response:**
```json
{
  "response": "Based on your tasks and deadline...",
  "action_taken": "null or description of action"
}
```

### GET /api/chat/history
Get conversation history

---

## Briefings

### GET /api/briefing/today
Get today's morning briefing

### GET /api/briefing/weekly
Get weekly review

---

## Error Responses

All endpoints may return:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

**Common Status Codes:**
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Server Error
