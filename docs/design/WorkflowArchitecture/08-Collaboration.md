# Part VIII — Collaboration Experiences

> **Part of the Workflow Architecture (SB-WFARCH-001). See `README.md` for document control.**
> Note: Collaboration features are in **design phase** — primarily deferred to future releases. This section defines the planned UX for multi-user scenarios.

---

## 8.1 Sharing

**Trigger:** User wants to share an item with others
**Access:** Share button on detail views (Tasks, Goals, Projects, Roadmaps)

### Share Dialog

```
┌──────────────────────────────────────────────┐
│  Share: "ML Project Roadmap"                 │
│                                              │
│  Permission:                                 │
│  ○ View only    ○ Can comment    ○ Can edit  │
│                                              │
│  Share via:                                  │
│  [Copy Link]  [Email]  [WhatsApp]  [More...] │
│                                              │
│  Link Options:                               │
│  ☐ Expires in: [24 hours ▼]                 │
│  ☐ Password protect                          │
│  ☐ Allow comments                            │
│                                              │
│  Shared with:                                │
│  👤 user@email.com · View · [Remove]         │
│  👤 friend@email.com · Edit · [Remove]       │
│  👤 + Invite by email                        │
│                                              │
│  [Generate Link]                             │
└──────────────────────────────────────────────┘
```

### States

| State | UI Treatment |
|---|---|
| **Closed** | Share icon on detail view header |
| **Open** | Modal slides up with permission selector + share methods |
| **Generating** | Spinner on "Generate Link" button |
| **Link Ready** | Button changes to "Copied!" + green toast |
| **Error** | "Couldn't generate link" + retry button |
| **Expired** | "This link has expired" on attempted access (viewer-side) |
| **Revoked** | "Access revoked" confirmation toast |

---

## 8.2 Comments

**Trigger:** User opens comment thread on a shared item
**Display:** Slide-over panel (desktop), full-screen (mobile)

### Comment Thread

```
┌──────────────────────────────────────────────┐
│  Comments (3)                           [X]  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ 👤 User A · 2h ago                     │  │
│  │ "Great progress on the ML project!"    │  │
│  │ [Reply] [👍 5] [👎 0]                 │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ 👤 You · 1h ago                        │  │
│  │ "Thanks! Stuck on the deployment       │  │
│  │  phase though."                        │  │
│  │ [Edit] [Delete] [👍 2] [👎 0]          │  │
│  └────────────────────────────────────────┘  │
│    ┌────────────────────────────────────┐    │
│    │ 👤 User A · 30m ago               │    │
│    │ "Try using Docker Compose!"        │    │
│    │ [Reply] [👍 3] [👎 0]             │    │
│    └────────────────────────────────────┘    │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ Write a comment...                     │  │
│  │ [@mention] [Add file] [Send]           │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

### States

| State | UI Treatment |
|---|---|
| **Empty** | "No comments yet" + "Be the first to share your thoughts" |
| **Loading** | 3 skeleton comment cards (shimmer) |
| **Populated** | Threaded comments with reactions and nested replies (max depth: 3) |
| **Posting** | Grayed input + spinner + "Sending..." |
| **Error** | "Couldn't post comment" + retry button in toast |
| **Editing** | Inline edit field → Save / Cancel |
| **Deleting** | Confirm dialog → remove with undo (30s) |

---

## 8.3 Mentions

**Trigger:** User types @ in comment or description field
**Display:** Autocomplete dropdown

### Mention Dropdown

```
┌──────────────────────────────────────────────┐
│  Write a comment...                          │
│  Hey @                                        │
│  ┌────────────────────────────────────────┐  │
│  │ 👤 User A · user@email.com            │  │
│  │ 👤 User B · user2@email.com           │  │
│  │ 👤 User C · user3@email.com           │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  After selection:                            │
│  "Hey @User_A, check out this task!"        │
│       └── accent colored, clickable        │
└──────────────────────────────────────────────┘
```

### States

| State | UI Treatment |
|---|---|
| **Triggered** | @ character detected → dropdown appears after 2 chars |
| **Loading** | "Searching..." in dropdown |
| **Results** | Matching users with avatar + name + email |
| **No Results** | "No users found" |
| **Selected** | @username inserted with accent color formatting |
| **Notification** | Mentioned user receives push notification + bell badge |

---

## 8.4 Activity Feeds

**Trigger:** User views item detail or Dashboard
**Display:** Chronological event stream in detail slide-over or Dashboard widget

### Activity Feed

```
┌──────────────────────────────────────────────┐
│  Activity                        [Filter ▼]  │
│                                              │
│  📅 Today                                    │
│  ┌────────────────────────────────────────┐  │
│  │ 2:30 PM · ✅ You completed "Deploy"    │  │
│  │ 1:15 PM · 🤖 AI created 3 study tasks │  │
│  │ 10:00 AM · 💬 User A commented         │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  📅 Yesterday                                │
│  ┌────────────────────────────────────────┐  │
│  │ 8:00 PM · ✏️ You updated goal +10%    │  │
│  │ 6:30 PM · 🤖 Briefing generated        │  │
│  │ 3:00 PM · 🔗 User B shared link        │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  [Load more]                                 │
└──────────────────────────────────────────────┘
```

### Event Types

| Type | Icon | Color | Description |
|---|---|---|---|
| Created | ➕ | Green | Item was created |
| Updated | ✏️ | Blue | Item was edited |
| Completed | ✅ | Green | Task/goal completed |
| Commented | 💬 | Purple | New comment added |
| Shared | 🔗 | Indigo | Item was shared |
| AI Action | 🤖 | Accent (helium) | Agent performed action |
| Status Change | 🔄 | Amber | Status/phase transition |
| Deleted | 🗑️ | Red | Item removed |

---

## 8.5 History

**Trigger:** User opens version history for an item
**Display:** Version list with expandable diffs

### History Timeline

```
┌──────────────────────────────────────────────┐
│  Version History — "ML Project Roadmap"      │
│                                              │
│  v1.3 · 2h ago · You                         │
│  └─ Added "Deploy to production" phase      │
│  [Restore this version]  [View diff]         │
│                                              │
│  v1.2 · 1d ago · User A                      │
│  └─ Updated timeline: Phase 2 → 2 weeks     │
│  [Restore this version]  [View diff]         │
│                                              │
│  v1.1 · 3d ago · 🤖 AI                       │
│  └─ Generated phase breakdown               │
│  [Restore this version]                      │
│                                              │
│  v1.0 · 5d ago · You                         │
│  └─ Created project                         │
└──────────────────────────────────────────────┘
```

### States

| State | UI Treatment |
|---|---|
| **Empty** | "No version history yet" (only current version exists) |
| **Loading** | 4 skeleton version items |
| **Populated** | Reverse-chronological version timeline |
| **Restoring** | "Restoring v1.2..." + preview of restored state |
| **Restored** | "Restored to v1.2" + undo button (30s) |
| **Diff View** | Side-by-side (desktop) or inline (mobile) with additions green / deletions red |

---

## 8.6 Version Tracking

### Purpose

Auto-save snapshots of all editable content for rollback capability

### Auto-Save Interval

| Content Type | Save Trigger | Max Versions |
|---|---|---|
| Goals (description, KRs) | 30s after last keystroke | 50 |
| Projects (phases, timeline) | 30s after last keystroke | 50 |
| Roadmaps (courses, timeline) | 30s after last keystroke | 50 |
| Comments | On submit | N/A (single) |

### States

| State | UI Treatment |
|---|---|
| **Auto-Saving** | Subtle "Saving..." indicator (fades after 2s) |
| **Saved** | "All changes saved" (fades after 2s) |
| **Conflict Detected** | "Updated by another user" → resolve dialog |
| **Restoring** | "Restoring version [N]..." → reload current view |
