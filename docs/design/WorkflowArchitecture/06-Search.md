## Document Control

| Field | Value |
|---|---|
| Document ID | DSG-WF06-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-07-11 |

# Part VI â€” Search Experience

> **Part of the Workflow Architecture (SB-WFARCH-001). See `README.md` for document control.**
> Related: `SearchArchitecture.md` (backend FTS â†’ pgvector â†’ hybrid), `InformationArchitecture.md` (search IA), `02-FeatureFlows.md` Â§2.14 (search feature flow).

---

## 6.1 Search Entry

### Entry Points

| Entry | Trigger | Behavior |
|---|---|---|
| Cmd+K | Global shortcut | Opens command/search hybrid overlay from any screen |
| Search bar | Click in TopBar | Expand inline search with suggestions |
| Module search | Per-module search input | Client-side filter within module |
| Mobile | Tap search icon in bottom tab | Full-screen search overlay |
| Slash key | / from any screen | Focus search bar if visible |

### States

| State | UI Treatment |
|---|---|
| **Idle** | Blinking cursor + placeholder: "Search tasks, courses, goals, ideas..." |
| **Recent** | Focus without input â†’ show 5 most recent searches (time-stamped) |
| **Suggestions** | Typing (debounced 150ms) â†’ dropdown with 5-7 inline suggestions |
| **Empty Input** | Backspace to clear â†’ return to recent searches |

---

## 6.2 Search Results

### Layout by Platform

| Platform | Layout |
|---|---|
| **Desktop** | Full-page overlay with results grouped by module in columns |
| **Tablet** | Slide-over panel, 70% width, results stacked |
| **Mobile** | Full-screen with back button, results single-column |

### Result Card Anatomy

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ [Icon] Title                          [Meta] â”‚
â”‚        Snippet of content with highlight...  â”‚
â”‚        Module Tag Â· Date Â· Status badge      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Result Types

| Type | Icon | Metadata | Primary Action |
|---|---|---|---|
| Task | Checklist | Status Â· Priority Â· Due date | Navigate to /tasks/{id} |
| Course | Book | Platform Â· Progress % | Navigate to /courses/{id} |
| Goal | Target | Category Â· Deadline | Navigate to /goals/{id} |
| Habit | Cycle | Frequency Â· Streak | Log today |
| Idea | Lightbulb | Stage Â· Date created | Navigate to /ideas/{id} |
| Resource | Link | Tags Â· Date saved | Open URL in new tab |
| Project | Folder | Phase Â· Status | Navigate to /projects/{id} |
| Opportunity | Star | Match % Â· Company | Navigate to /opportunities/{id} |
| Memory | Brain | Category Â· Confidence | Navigate to /memory/{id} |
| Chat | Message | Date Â· Preview snippet | Navigate to /chat |
| Command | Cmd | Shortcut hint | Execute command |
| Setting | Gear | Section path | Navigate to /settings/{section} |

---

## 6.3 Search Suggestions

### Behavior

- Displayed after 150ms debounce
- Max 7 suggestions
- Sources: fuzzy title match, recent searches, frequent searches, AI predicted

### Suggestion Types

| Type | Source | Display |
|---|---|---|
| **Title Match** | Fuzzy match on item titles | Icon + title + "in [module]" |
| **Recent** | Last 5 searches | Clock icon + query text |
| **Frequent** | Most repeated queries | Trending icon + query text |
| **AI Predicted** | @memory_agent predicts intent | Sparkle icon + "Are you looking for [X]?" |

---

## 6.4 No Results

**Trigger:** Query returns 0 results across all scopes

### UI Treatment

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                                              â”‚
â”‚           ðŸ” No results for "xyz"            â”‚
â”‚                                              â”‚
â”‚    Try:                                      â”‚
â”‚    â€¢ Different keywords                      â”‚
â”‚    â€¢ Check spelling                          â”‚
â”‚    â€¢ Use fewer filters                       â”‚
â”‚    â€¢ Broaden your search scope               â”‚
â”‚                                              â”‚
â”‚    Or create what you're looking for:        â”‚
â”‚    [Create Task] [Create Goal] [Save Idea]   â”‚
â”‚                                              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### AI Fallback

If semantic search is enabled and FTS returns 0 results:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  âœ¨ ARIA couldn't find exact matches but     â”‚
â”‚     found related items you might want:      â”‚
â”‚                                              â”‚
â”‚  â€¢ [Related item 1] (from [module])          â”‚
â”‚  â€¢ [Related item 2] (from [module])          â”‚
â”‚  â€¢ [Related item 3] (from [module])          â”‚
â”‚                                              â”‚
â”‚  Ask ARIA: "I'm looking for..."              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## 6.5 Semantic Search

**Trigger:** User toggles "Semantic" pill or search has 0 FTS results
**Backend:** pgvector cosine similarity on `search_documents` view

### UI Indicators

| Element | Design |
|---|---|
| Toggle pill | "Semantic" / "Keyword" in filter bar |
| Active state | Accent purple glow on pill |
| Result badge | "Semantic match â€” 85%" confidence indicator |
| Tooltip | "Searching by meaning, not just keywords" |

### States

| State | UI Treatment |
|---|---|
| **Idle** | Pill shows "Semantic" with info tooltip on hover |
| **Loading** | Pill pulses with "Searching by meaning..." |
| **Results** | Cards show match percentage badge |
| **No Results** | "No semantic matches" + "Try keyword search instead" |
| **Error** | "Semantic search unavailable" â†’ silent fallback to FTS |

---

## 6.6 AI Search

**Trigger:** User clicks "Ask ARIA" in search bar or types a natural language question
**Backend:** Chat endpoint with search context

### UI Treatment

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Ask ARIA                                     â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚ "find all high priority tasks due      â”‚   â”‚
â”‚  â”‚ this week related to ML project"       â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â”‚                                              â”‚
â”‚  âœ¨ ARIA found 3 items:                       â”‚
â”‚  â€¢ Complete ML project report (Due: Fri)     â”‚
â”‚  â€¢ Review model accuracy (Due: Thu)          â”‚
â”‚  â€¢ Deploy to staging (Due: Sat)              â”‚
â”‚                                              â”‚
â”‚  "These are your ML project tasks sorted     â”‚
â”‚   by urgency."                               â”‚
â”‚                                              â”‚
â”‚  [Ask another question]                      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## 6.7 Search Filters

### Filter Panel

| Platform | Layout |
|---|---|
| **Desktop** | Slide-over from right (320px) |
| **Tablet** | Bottom sheet, 70% height |
| **Mobile** | Full-screen, scrollable |

### Filter Types

| Filter | Type | Options |
|---|---|---|
| Module | Multi-select checkboxes | Tasks, Courses, Goals, Habits, Ideas, Resources, Projects, Opportunities, Memory, Chat |
| Status | Multi-select | Active, Completed, Archived, Pending |
| Date Range | Date picker (from/to) | Any date range |
| Priority | Multi-select | Urgent, High, Medium, Low |
| Tags | Autocomplete input | User-defined tags from all modules |
| Match Score | Range slider (0-100%) | Opportunities only |

### States

| State | UI Treatment |
|---|---|
| **Closed** | Filter icon in search bar with count badge ("2") |
| **Open** | Panel slides in with active filter count badge |
| **Active Filters** | Chips below search bar, removable individually |
| **No Filters** | "No filters applied" message |
| **Clear All** | Button in panel header, clears all filters |
| **Save** | "Save as..." â†’ name input â†’ saved search (see 6.8) |

---

## 6.8 Saved Searches

### Purpose

Persist filter + query combinations for quick access without re-entering.

### Storage Location

| Platform | Location |
|---|---|
| **Desktop** | Sidebar under "Saved Searches" section |
| **Tablet** | Search page, collapsible section |
| **Mobile** | Search page, accordion panel |

### Schema

| Field | Type | Description |
|---|---|---|
| Name | Text (max 50 chars) | User-defined label |
| Query | String | Original search query |
| Filters | JSON | Active filters at time of save |
| Scope | String | Search scope (all / module / semantic) |
| Auto-refresh | Boolean | Periodically fetch new results |
| Notify on New | Boolean | Alert when new results match |
| Created | Timestamp | When saved |
| Last Run | Timestamp | Last auto-refresh time |

### States

| State | UI Treatment |
|---|---|
| **Empty** | "No saved searches yet" + "Save current search" CTA |
| **List** | Named items with match count badge |
| **Refreshing** | Rotating icon + "Checking for new results" |
| **New Matches** | Badge: "+3 new" on saved search item |
| **Expired** | "This search may have new results" â†’ Refresh CTA |

---

## 6.9 Search Settings

**Route:** `/settings/search`

| Setting | Type | Default | Description |
|---|---|---|---|
| Default Scope | Select | All modules | Default search scope |
| Semantic Search | Toggle | On | Enable vector similarity search |
| Include AI in Results | Toggle | On | Show AI-powered suggestions |
| Save Recent Searches | Toggle | On | Store last 50 searches locally |
| Clear Recent | Danger button | â€” | Clear all recent search history |
| Saved Searches | List | â€” | Manage saved searches |
| Search History Privacy | Toggle | On | Store locally only (never sync) |
| Result Count | Select | 20 / 50 / 100 | Results per page |
