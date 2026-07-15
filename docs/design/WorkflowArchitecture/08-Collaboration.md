## Document Control

| Field | Value |
|---|---|
| Document ID | DSG-WF08-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-07-11 |

# Part VIII â€” Collaboration Experiences

> **Part of the Workflow Architecture (SB-WFARCH-001). See `README.md` for document control.**
> Note: Collaboration features are in **design phase** â€” primarily deferred to future releases. This section defines the planned UX for multi-user scenarios.

---

## 8.1 Sharing

**Trigger:** User wants to share an item with others
**Access:** Share button on detail views (Tasks, Goals, Projects, Roadmaps)

### Share Dialog

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Share: "ML Project Roadmap"                 â”‚
â”‚                                              â”‚
â”‚  Permission:                                 â”‚
â”‚  â—‹ View only    â—‹ Can comment    â—‹ Can edit  â”‚
â”‚                                              â”‚
â”‚  Share via:                                  â”‚
â”‚  [Copy Link]  [Email]  [WhatsApp]  [More...] â”‚
â”‚                                              â”‚
â”‚  Link Options:                               â”‚
â”‚  â˜ Expires in: [24 hours â–¼]                 â”‚
â”‚  â˜ Password protect                          â”‚
â”‚  â˜ Allow comments                            â”‚
â”‚                                              â”‚
â”‚  Shared with:                                â”‚
â”‚  ðŸ‘¤ user@email.com Â· View Â· [Remove]         â”‚
â”‚  ðŸ‘¤ friend@email.com Â· Edit Â· [Remove]       â”‚
â”‚  ðŸ‘¤ + Invite by email                        â”‚
â”‚                                              â”‚
â”‚  [Generate Link]                             â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
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
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Comments (3)                           [X]  â”‚
â”‚                                              â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ ðŸ‘¤ User A Â· 2h ago                     â”‚  â”‚
â”‚  â”‚ "Great progress on the ML project!"    â”‚  â”‚
â”‚  â”‚ [Reply] [ðŸ‘ 5] [ðŸ‘Ž 0]                 â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                              â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ ðŸ‘¤ You Â· 1h ago                        â”‚  â”‚
â”‚  â”‚ "Thanks! Stuck on the deployment       â”‚  â”‚
â”‚  â”‚  phase though."                        â”‚  â”‚
â”‚  â”‚ [Edit] [Delete] [ðŸ‘ 2] [ðŸ‘Ž 0]          â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”‚
â”‚    â”‚ ðŸ‘¤ User A Â· 30m ago               â”‚    â”‚
â”‚    â”‚ "Try using Docker Compose!"        â”‚    â”‚
â”‚    â”‚ [Reply] [ðŸ‘ 3] [ðŸ‘Ž 0]             â”‚    â”‚
â”‚    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â”‚
â”‚                                              â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ Write a comment...                     â”‚  â”‚
â”‚  â”‚ [@mention] [Add file] [Send]           â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### States

| State | UI Treatment |
|---|---|
| **Empty** | "No comments yet" + "Be the first to share your thoughts" |
| **Loading** | 3 skeleton comment cards (shimmer) |
| **Populated** | Threaded comments with reactions and nested replies (max depth: 3) |
| **Posting** | Grayed input + spinner + "Sending..." |
| **Error** | "Couldn't post comment" + retry button in toast |
| **Editing** | Inline edit field â†’ Save / Cancel |
| **Deleting** | Confirm dialog â†’ remove with undo (30s) |

---

## 8.3 Mentions

**Trigger:** User types @ in comment or description field
**Display:** Autocomplete dropdown

### Mention Dropdown

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Write a comment...                          â”‚
â”‚  Hey @                                        â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ ðŸ‘¤ User A Â· user@email.com            â”‚  â”‚
â”‚  â”‚ ðŸ‘¤ User B Â· user2@email.com           â”‚  â”‚
â”‚  â”‚ ðŸ‘¤ User C Â· user3@email.com           â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                              â”‚
â”‚  After selection:                            â”‚
â”‚  "Hey @User_A, check out this task!"        â”‚
â”‚       â””â”€â”€ accent colored, clickable        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### States

| State | UI Treatment |
|---|---|
| **Triggered** | @ character detected â†’ dropdown appears after 2 chars |
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
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Activity                        [Filter â–¼]  â”‚
â”‚                                              â”‚
â”‚  ðŸ“… Today                                    â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ 2:30 PM Â· âœ… You completed "Deploy"    â”‚  â”‚
â”‚  â”‚ 1:15 PM Â· ðŸ¤– AI created 3 study tasks â”‚  â”‚
â”‚  â”‚ 10:00 AM Â· ðŸ’¬ User A commented         â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                              â”‚
â”‚  ðŸ“… Yesterday                                â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ 8:00 PM Â· âœï¸ You updated goal +10%    â”‚  â”‚
â”‚  â”‚ 6:30 PM Â· ðŸ¤– Briefing generated        â”‚  â”‚
â”‚  â”‚ 3:00 PM Â· ðŸ”— User B shared link        â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                              â”‚
â”‚  [Load more]                                 â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Event Types

| Type | Icon | Color | Description |
|---|---|---|---|
| Created | âž• | Green | Item was created |
| Updated | âœï¸ | Blue | Item was edited |
| Completed | âœ… | Green | Task/goal completed |
| Commented | ðŸ’¬ | Purple | New comment added |
| Shared | ðŸ”— | Indigo | Item was shared |
| AI Action | ðŸ¤– | Accent (helium) | Agent performed action |
| Status Change | ðŸ”„ | Amber | Status/phase transition |
| Deleted | ðŸ—‘ï¸ | Red | Item removed |

---

## 8.5 History

**Trigger:** User opens version history for an item
**Display:** Version list with expandable diffs

### History Timeline

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Version History â€” "ML Project Roadmap"      â”‚
â”‚                                              â”‚
â”‚  v1.3 Â· 2h ago Â· You                         â”‚
â”‚  â””â”€ Added "Deploy to production" phase      â”‚
â”‚  [Restore this version]  [View diff]         â”‚
â”‚                                              â”‚
â”‚  v1.2 Â· 1d ago Â· User A                      â”‚
â”‚  â””â”€ Updated timeline: Phase 2 â†’ 2 weeks     â”‚
â”‚  [Restore this version]  [View diff]         â”‚
â”‚                                              â”‚
â”‚  v1.1 Â· 3d ago Â· ðŸ¤– AI                       â”‚
â”‚  â””â”€ Generated phase breakdown               â”‚
â”‚  [Restore this version]                      â”‚
â”‚                                              â”‚
â”‚  v1.0 Â· 5d ago Â· You                         â”‚
â”‚  â””â”€ Created project                         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
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
| **Conflict Detected** | "Updated by another user" â†’ resolve dialog |
| **Restoring** | "Restoring version [N]..." â†’ reload current view |
