# Idea Vault Guide

## Document Control

| Field | Value |
|---|---|
| Document ID | UG-IDEAS-001 |
| Version | 1.0.0 |
| Status | Active |
| Classification | Public - User Documentation |
| Last Updated | 2026-07-14 |

---

## Introduction

The Idea Vault is your creative idea pipeline. Capture ideas as they come, develop them through validation, and convert them into actionable projects. Ideas move through three stages: Raw, Validating, and Building.

## Capturing an Idea

1. Go to **Ideas** from the sidebar
2. Click **New Idea**
3. Fill in:

| Field | Description |
|---|---|
| Title | A concise name for your idea (required) |
| Description | Expand on the concept |
| Stage | Raw, Validating, or Building |
| Tags | Optional categorization tags |

## The Idea Pipeline

Ideas progress through three stages:

| Stage | Description | What to Do |
|---|---|---|
| **Raw** | Fresh idea, just captured | Write down the basic concept, no filtering |
| **Validating** | Researching feasibility | Market research, talk to people, build MVP plan |
| **Building** | Actively working on it | Convert to a project, start execution |

## Moving Ideas Through Stages

- Drag an idea card between pipeline columns
- Update the stage field when your idea progresses
- Use the **Promote to Project** action to convert a validated idea into a full project

## Managing Ideas

### View and Filter Ideas

The Idea Vault page provides:
- **Pipeline view**: Three columns (Raw, Validating, Building) with draggable cards
- **List view**: Compact table with all ideas across stages
- **Filter by stage**: Show ideas from a specific pipeline stage
- **Filter by tag**: Show ideas with specific tags
- **Search**: Find ideas by title or description

### Editing an Idea

1. Click on any idea card to open the detail view
2. Update the title, description, stage, or tags
3. The **Stage** field controls which pipeline column the idea appears in
4. Add notes as you develop the concept

### Promoting Ideas to Projects

When an idea is ready to execute:
1. Open the validated idea
2. Click **Promote to Project**
3. A new project is created with the idea's title and description pre-filled
4. The idea's status updates to indicate it has been promoted
5. The original idea remains in your vault for reference

### AI Idea Analysis (Planned)

Future versions will include:
- AI-powered market check for similar ideas
- Feasibility scoring based on your skills and resources
- Related idea discovery (connecting complementary concepts)
- Idea description enhancement suggestions

### Idea Development Workflow

A recommended workflow for taking an idea from raw to project:

1. **Raw**: Capture the spark immediately. One sentence is enough. Do not filter.
2. **Validating**: Research the market. Talk to potential users. Define what success looks like.
3. **Building**: Create an MVP plan. Break into tasks. Start the smallest possible version.
4. **Project**: Promote to the Project Tracker with full phase management.

## Data Model

| Field | Type | Description |
|---|---|---|
| `title` | string | Idea name |
| `description` | text | Full concept description |
| `stage` | string | raw, validating, building |
| `tags` | string[] | Categorization tags |
| `linked_project_id` | uuid | Optional link to promoted project |

## Common Questions

**Q: How many ideas should I keep in Raw?**
There is no limit. Raw is your capture space. Review weekly and move promising ideas to Validating.

**Q: What if an idea never leaves Raw?**
That is fine. Not every idea needs to become a project. The capture itself has value -- you can revisit later.

**Q: Can I move an idea backward?**
Yes. You can set any stage at any time. If validation reveals the idea is not ready, move it back to Raw.

## Tips

- Capture ideas immediately -- do not judge them on first entry
- Review raw ideas weekly during the weekly review
- Use tags to categorize ideas (app, content, business, research, side-project)
- Set aside dedicated time for validation research (e.g., Sunday afternoons)
- An idea can stay in Raw indefinitely -- not every idea needs to become a project
- Validate with the smallest possible effort (a 5-minute Google search counts)
- Link validated ideas to goals if they contribute to a larger objective

## Related Guides

- [Projects](projects.md) -- Convert validated ideas into projects
- [Weekly Review](weekly-review.md) -- Review and prioritize your idea pipeline
- [Tasks](tasks.md) -- Create action items for idea validation
- [Goals](goals.md) -- Align ideas with long-term goals
