# Goals & Roadmap Guide

## Document Control

| Field | Value |
|---|---|
| Document ID | UG-GOALS-001 |
| Version | 1.0.0 |
| Status | Active |
| Classification | Public - User Documentation |
| Last Updated | 2026-07-14 |

---

## Introduction

The Goals & Roadmap module helps you define long-term objectives, break them into actionable milestones, and visualize your progress on an interactive roadmap canvas.

## Creating a Goal

1. Go to **Goals** from the sidebar
2. Click **New Goal**
3. Configure the following:

| Field | Description |
|---|---|
| Title | The goal you want to achieve (required) |
| Description | Optional context or motivation |
| Category | Learning, Career, Fitness, Finance, Personal, Academic |
| Target Date | Optional deadline for completion |
| Status | Active, Completed, or Abandoned |

## Working with the Roadmap

The roadmap is an interactive drag-and-drop canvas (powered by React Flow):

- **Add milestone nodes** by clicking on the canvas
- **Connect nodes** by dragging between connection points
- **Rearrange** by dragging nodes to new positions
- **Edit** by clicking on a node to update details
- **Delete** by selecting a node and pressing Delete

Each node represents a milestone on your goal journey.

## Tracking Progress

- Goals show a progress bar updated as you complete linked tasks
- Milestones can be marked as complete individually
- The target date shows remaining time (or overdue warning)
- Status automatically tracks active, completed, or abandoned goals

## Linking Goals to Tasks

Connect goals to tasks for automatic progress tracking:

1. Open a task's detail view
2. In the **Goal** field, select the goal to link
3. Completing the task increments the goal's progress

## AI Roadmap Optimization

The Roadmap agent (A08) can help optimize your learning path:
- Suggests optimal order for milestones
- Identifies gaps in your current plan
- Recommends prerequisites and next steps
- Runs on-demand or weekly

## Managing Goals

### View and Filter Goals

The Goals page provides multiple views:
- **Card view**: Visual cards with progress bars and milestone counts
- **Roadmap view**: Interactive React Flow canvas with milestone nodes
- **Filter by category**: Show only Learning, Career, Fitness, Finance, Personal, or Academic goals
- **Filter by status**: Active, completed, or abandoned

### Editing a Goal

1. Click on any goal card to open the detail view
2. Update the title, description, category, or target date
3. Change the **Status** when a goal is completed or abandoned
4. Add or remove linked tasks and courses

### Roadmap Canvas Features

The interactive roadmap canvas (powered by React Flow) provides:
- **Add milestone**: Double-click on the canvas to create a new milestone
- **Connect milestones**: Drag between connection handles to create dependencies
- **Rearrange**: Drag nodes to any position on the canvas
- **Zoom and pan**: Scroll to zoom, click and drag to pan
- **Edit milestone**: Click a node to open the edit dialog
- **Delete milestone**: Select and press Delete, or use the context menu
- **Auto-layout**: Optional automatic arrangement of nodes

### Linking to Tasks

Connect goals to tasks for automatic progress tracking:

1. Open a task's detail view
2. In the **Goal** field, select the goal to link
3. Completing the task increments the goal's progress
4. Tasks linked to a goal appear on the goal's detail page

Multiple tasks can link to the same goal. Goal progress is calculated as:
```
Goal Progress = (Completed Linked Tasks / Total Linked Tasks) x 100
```

### Linking to Courses

Courses linked to goals also contribute:
1. Edit a course and select the **Linked Goal** field
2. Course completion percentage is factored into goal progress
3. Related courses display on the goal detail page

### AI Goal Suggestions

The AI (agent A08) can help optimize your goals:
- Suggests realistic target dates based on your workload
- Recommends prerequisite goals before starting new ones
- Identifies overlapping goals that could be merged
- Warns if you have too many active goals (recommended max: 3)

## Data Model

| Field | Type | Description |
|---|---|---|
| `title` | string | Goal name |
| `description` | text | Optional details and context |
| `category` | string | learning, career, fitness, finance, personal, academic |
| `target_date` | date | Optional deadline |
| `status` | string | active, completed, abandoned |
| `progress_pct` | integer | Auto-calculated percentage (0-100) |

## Tips

- Start with 2-3 active goals to stay focused and avoid overwhelm
- Break large goals into 4-6 milestones on the roadmap for clear steps
- Link courses and tasks to goals for automatic progress tracking
- Review goal progress during the weekly review
- Update milestone status as you make progress -- completing milestones is motivating
- Use the roadmap to visualize dependencies between milestones
- Set realistic target dates based on your current workload from tasks and courses

## Related Guides

- [Courses](courses.md) -- Link courses to learning goals
- [Tasks](tasks.md) -- Create tasks that contribute to goals
- [Weekly Review](weekly-review.md) -- Review goal progress weekly
- [Roadmap](features-overview.md) -- Skill development roadmap optimizer
- [Projects](projects.md) -- Goals can spawn projects for execution
