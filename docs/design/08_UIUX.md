# UI/UX Specification — Second Brain OS

| Field | Value |
|---|---|
| Document ID | DSG-UIUX-008 |
| Version | 3.0.0 |
| Status | Active |
| Last Updated | 2026-06-11 |
| Classification | Internal — Design Reference |
| Target Audience | Designers, Frontend Developers, QA Engineers |

---

## 1. Executive Summary

The Second Brain OS (ARIA OS) user experience is built on a **cyberpunk dark theme** that balances aesthetic boldness with functional clarity. Every design decision serves the mission of transforming a student into a builder. This document defines the complete UX framework — from research methodology and design process through interaction patterns, micro-interactions, feedback systems, and accessibility — ensuring a cohesive, high-quality experience across all 16 modules.

**Core UX Promise:** "Your second brain should be faster than your first."

---

## 2. UX Philosophy

### 2.1 Design Principles

| # | Principle | Description | Example |
|---|---|---|---|
| 1 | **Dark by Default** | #0A0B0F base reduces eye strain during late-night study sessions. The dark canvas makes neon accent colors pop, guiding attention without visual noise. | Dashboard cards use subtle glass borders; neon green (#00FFA3) draws eye to completed streaks. |
| 2 | **Speed is a Feature** | Every interaction completes under 100ms. Skeleton screens appear in under 200ms. Animations run at 60fps. | Task completion triggers instant local state update before API confirms. |
| 3 | **Glanceable Information** | The Morning Briefing delivers critical data in under 5 seconds. Cards expose priority, status, and next action without requiring a click. | Dashboard communicates your day before you read a single word. |
| 4 | **Zero Data Loss** | The Never-Forget System means every idea, resource, and task is captured before it slips away. Quick Capture buttons are available from every screen. Auto-save prevents loss on navigation or refresh. | Draft tasks persist in localStorage even if the API call fails. |
| 5 | **Contextual Intelligence** | ARIA adapts the interface based on your sleep score, productivity patterns, and active goals. Low sleep shifts hard tasks off the main view. A stalled goal surfaces a micro-task prompt. | The UI reflects your current state, not a static layout. |
| 6 | **Progressive Disclosure** | Show essential actions first. Reveal complexity on demand. Never overwhelm the user with 20 options when they need 3. | Task detail panel expands inline; full editor is one click away. |
| 7 | **Forgiving Input** | Every destructive action has undo or confirmation. Search handles typos. Date inputs accept natural language ("tomorrow", "next Mon"). | Deleting a task shows a 5-second undo toast before finalizing. |

### 2.2 UX Quality Attributes

| Attribute | Target | Measurement Method |
|---|---|---|
| Task Success Rate | >95% | Analytics funnel tracking |
| Time on Task | <30s for core actions | Heatmap + session recording |
| Error Rate | <2% | Form validation analytics |
| Satisfaction Score | >4.2/5 | In-app NPS survey (quarterly) |
| First-Time Success | >80% complete onboarding | Onboarding funnel analytics |
| Retention (Day 7) | >60% | Cohort analysis |
| Page Load Time | <1.5s (P75) | Lighthouse CI |

---

## 3. User Research Methodology

### 3.1 Research Cadence

| Frequency | Method | Sample Size | Purpose |
|---|---|---|---|
| Weekly | In-app Micro-surveys (1-2 questions) | 50-200 respondents | Gauge satisfaction with new features, identify pain points |
| Monthly | Usability testing (remote moderated) | 5-8 participants | Validate new workflows, identify friction |
| Quarterly | Deep-dive user interviews (30-45 min) | 10-15 participants | Understand motivations, unmet needs, workflow context |
| Quarterly | Analytics review (quantitative) | All active users | Track metric trends, identify dropout funnels |
| Bi-annual | Competitive benchmarking | N/A | Compare UX quality against Notion, Todoist, Roam, Obsidian |
| Annual | Comprehensive NPS + SUS survey | All users | Measure overall experience quality |

### 3.2 Research Artifacts

#### 3.2.1 Survey Templates

**Micro-survey (post-action):**
```
How easy was it to [complete action]?
[  ] Very easy
[  ] Easy
[  ] Neutral
[  ] Difficult
[  ] Very difficult

Anything else? [free text]
```

**Quarterly NPS Survey:**
```
How likely are you to recommend ARIA OS to a friend?
0  1  2  3  4  5  6  7  8  9  10
Not at all                          Extremely likely

What is the primary benefit you get from ARIA OS? [free text]
What is the biggest frustration? [free text]
What feature would you add if you could? [free text]
```

#### 3.2.2 Interview Protocol

| Phase | Duration | Activities |
|---|---|---|
| Introduction | 3 min | Explain purpose, get consent, set expectations |
| Context | 5 min | Understand daily workflow, tools used, environment |
| Task observation | 15 min | Watch user complete 3-5 core tasks, think-aloud protocol |
| Deep dive | 10 min | Probe pain points, unmet needs, feature requests |
| Wrap-up | 2 min | Thank you, explain next steps, offer incentive |

#### 3.2.3 Analytics Framework

| Category | Events Tracked | Tools |
|---|---|---|
| Engagement | DAU/MAU, session duration, screen views per session | PostHog / Plausible |
| Adoption | Feature activation rate, time to first use of each feature | PostHog |
| Retention | Day 1/7/30 retention, weekly returning rate | Supabase analytics |
| Funnel | Onboarding completion, task creation → completion, habit start → streak | PostHog funnel analysis |
| Performance | LCP, FID, CLS, API response times (P50/P95) | Lighthouse CI, Sentry |

---

## 4. UX Design Process

### 4.1 Process Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  RESEARCH ──► DEFINE ──► IDEATE ──► PROTOTYPE ──► TEST ──► ITERATE │
│     ↑                                                        │      │
│     └──────────────────── CONTINUOUS ─────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Phase Breakdown

| Phase | Duration | Deliverables | Stakeholders |
|---|---|---|---|
| **Research** | 1-2 weeks per feature | User interviews summary, competitive analysis, analytics report | PM, Designer |
| **Define** | 3-5 days | Problem statement, user stories, acceptance criteria, UX goals | PM, Designer, Dev lead |
| **Ideate** | 2-3 days | Sketches (10+ per designer), concept diagrams, Crazy 8s | Design team |
| **Prototype** | 1-2 weeks | Figma interactive prototype (high-fidelity), micro-interactions spec | Designer |
| **Test** | 3-5 days | Usability test report, issue severity matrix, recommendations | Designer, PM |
| **Iterate** | 1 week | Revised prototype, updated specs, design approval | All |

### 4.3 Fidelity Levels

| Level | Description | When Used |
|---|---|---|
| Low-fidelity (lo-fi) | Paper sketches, wireframes, Balsamiq | Ideation, early concept validation |
| Mid-fidelity (mid-fi) | Grey-box mockups, basic layout, no styling | Layout validation, content structure |
| High-fidelity (hi-fi) | Full design with colors, typography, icons, animations | Usability testing, dev handoff |
| Production-ready | Hi-fi + design tokens, responsive specs, interaction specs | Final approval, development |

### 4.4 Design Review Gates

| Gate | Participants | Criteria |
|---|---|---|
| **UX Review** (peer) | 2+ designers | Flow completeness, consistency, edge cases covered |
| **Design Review** (lead) | Design lead | Quality bar, brand alignment, accessibility compliance |
| **Engineering Review** | Lead frontend dev | Technical feasibility, implementation effort, design token usage |
| **PM Sign-off** | Product manager | Requirements met, timeline alignment, scope confirmed |
| **QA Review** | QA engineer | All states handled (loading, empty, error, edge cases) |

---

## 5. User Journey Maps

### 5.1 Core Personas

| Persona | Role | Goals | Pain Points |
|---|---|---|---|
| **Aarav** — BTech CSE Sophomore | Student | Manage courses, tasks, projects; track habits; stay organized | Overwhelmed by multiple tools; forgets deadlines; poor time management |
| **Priya** — BTech CSE Junior | Student + Intern | Balance academics, internship, side projects; track opportunities | Misses application deadlines; can't prioritize across work/school/life |
| **Rohan** — BTech CSE Senior | Student + Job Seeker | Prepare for placements, track opportunities, manage learning | Scattered resources; no structured prep; interview tracking chaos |

### 5.2 Aarav's Daily Journey Map

| Time | Activity | Touchpoints | Goals | Pain Points | Opportunity |
|---|---|---|---|---|---|
| 7:00 AM | Wake up, check schedule | Mobile — Morning Briefing notification | See today's tasks and deadlines quickly | Wants a single glance at what matters | Briefing card shows top 3 tasks, weather, sleep score |
| 8:00 AM | Attend lectures | Mobile — Course view | Track attendance, view upcoming assignments | Forgets which courses have deliverables | Course card shows next assignment deadline with countdown |
| 12:00 PM | Lunch break, catch up | Mobile — Quick Capture | Save ideas/links from social media | Ideas get lost in chat apps | Share-to-ARIA extension captures directly |
| 3:00 PM | Study session | Desktop — Tasks + Pomodoro timer | Complete assignments with focus | Gets distracted, loses track of time | Integrated Pomodoro with task linking |
| 6:00 PM | Coursework | Desktop — Course detail | Watch recorded lectures, track progress | No way to track lecture progress | Course progress bar per module |
| 9:00 PM | Wind down | Mobile — Sleep log + Reflection | Log sleep, reflect on the day | Forgets to track sleep | Bedtime reminder with wind-down prompt |
| 10:00 PM | Review tomorrow | Desktop/Mobile — Dashboard | Preview next day's schedule | Doesn't plan ahead | Evening briefing card shows tomorrow's top tasks |

### 5.3 Priya's Weekly Journey Map (Internship + Academics)

| Day | Focus | ARIA OS Modules Used | Key Interactions |
|---|---|---|---|
| Mon-Fri | Internship (9-5) | Time tracking, Tasks, Projects | Log time entries, track project tasks, Pomodoro sessions |
| Mon/Wed evening | College assignments | Courses, Tasks, Goals | Mark course progress, create assignment tasks, check goal milestones |
| Tue/Thu evening | Side project | Projects, Ideas, Resources | Update project board, log new ideas, save resources |
| Fri evening | Weekly review | Weekly Review, Goals | Review week's accomplishments, adjust goals |
| Sat | Career prep | Opportunities, Learning | Apply to opportunities, complete learning modules |
| Sun | Planning + Rest | Habits, Sleep, Goals | Plan next week, review sleep data, set weekly intentions |

### 5.4 Rohan's Placement Prep Journey

| Phase | Activities | Success Metrics | ARIA Touchpoints |
|---|---|---|---|
| **Awareness** | Discover opportunities, understand requirements | 10+ relevant opportunities identified | Opportunity radar daily scan |
| **Preparation** | Study DSA, company-specific prep, projects | 50+ hours tracked, 5+ projects completed | Learning modules, time tracking, projects |
| **Application** | Apply to companies, track status | 20+ applications submitted | Opportunity tracking with status pipeline |
| **Interview** | Schedule interviews, practice | 5+ interviews completed, offers received | Calendar sync, interview prep checklist |
| **Selection** | Compare offers, make decision | 1+ offer accepted | Decision matrix, pro-con comparison |

### 5.5 User Journey for Task Creation

```
Step 1: Trigger        Step 2: Capture       Step 3: Enrich        Step 4: Organize        Step 5: Execute
┌──────────┐           ┌──────────┐          ┌──────────┐          ┌────────────┐           ┌──────────┐
│ Quick     │──►        │ Task     │──►       │ Select   │──►       │ Task auto   │──►       │ Work on  │
│ Capture   │           │ Form     │          │ Category │          │ appears in │          │ task     │
│ (Cmd+K)   │           │ (inline) │          │ + Prio   │          │ Dashboard  │          │ (Pomo)   │
└──────────┘           └──────────┘          └──────────┘          └────────────┘           └──────────┘
   • 1 click               • Title            • Priority              • Filtered view       • Timer starts
   • Keyboard              • Due date         • Category              • Notified             • Focus mode
   • Share extension       • Notes (optional) • Goal link             • Streak updated       • Tracks time
```

---

## 6. Information Architecture

### 6.1 Site Map

```
Home (Dashboard)
├── Tasks                     [List/Kanban view]
│   ├── Task Detail (/tasks/:id)
│   └── Task Filter (/tasks?status=pending)
├── Courses                   [Grid view]
│   ├── Course Detail (/courses/:id)
│   └── Course Progress (/courses/:id/progress)
├── Goals                     [Canvas/Grid view]
│   ├── Goal Detail (/goals/:id)
│   └── Goal Roadmap (/goals/:id/roadmap)
├── Habits                    [Grid view]
│   └── Habit Detail (/habits/:id)
├── Sleep                     [Dashboard view]
├── Income                    [Dashboard view]
│   └── Income Entry (/income/new)
├── Projects                  [Kanban view]
│   └── Project Detail (/projects/:id)
├── Ideas                     [Pipeline view]
│   └── Idea Detail (/ideas/:id)
├── Resources                 [Grid view]
│   ├── Resource Detail (/resources/:id)
│   └── Resource Collection (/resources/collections/:id)
├── Opportunities             [List view]
│   └── Opportunity Detail (/opportunities/:id)
├── Time                      [List/Dashboard view]
│   └── Time Stats (/time/stats)
├── Chat                      [Full view]
├── Automation                [List view]
│   ├── Briefing (/automation/briefing)
│   ├── Radar (/automation/radar)
│   └── Weekly Review (/automation/weekly-review)
└── Settings (modal/overlay)
    ├── Profile
    ├── Preferences
    ├── Notifications
    ├── Integrations
    └── Account
```

### 6.2 Navigation Hierarchy

| Level | Component | Purpose | Persistence |
|---|---|---|---|
| **Primary** | Sidebar (w-60) | Module navigation, 16 items | Always visible on desktop |
| **Secondary** | Navbar (h-16) | Search, notifications, user menu | Always visible |
| **Tertiary** | Breadcrumbs | Context within nested pages | Module detail pages |
| **Quaternary** | Tab bars / Sub-nav | Module-specific views (e.g., Tasks: List | Kanban | Calendar) | Module pages |
| **Utility** | Command Palette (Cmd+K) | Global search and actions | Overlay / modal |
| **Mobile** | Bottom Nav (h-16) | 5 core destinations | Always visible on mobile |

### 6.3 Global Navigation Items

| # | Item | Icon (lucide-react) | Route | Category |
|---|---|---|---|---|
| 1 | Dashboard | LayoutDashboard | /dashboard | Core |
| 2 | Tasks | CheckSquare | /tasks | Core |
| 3 | Courses | BookOpen | /courses | Academic |
| 4 | Goals | Target | /goals | Core |
| 5 | Habits | Flame | /habits | Wellness |
| 6 | Sleep | Moon | /sleep | Wellness |
| 7 | Income | DollarSign | /income | Finance |
| 8 | Projects | FolderKanban | /projects | Work |
| 9 | Ideas | Lightbulb | /ideas | Creative |
| 10 | Resources | Library | /resources | Knowledge |
| 11 | Opportunities | Briefcase | /opportunities | Career |
| 12 | Time | Clock | /time | Productivity |
| 13 | Chat | MessageSquare | /chat | AI |
| 14 | Automation | Zap | /automation | System |

---

## 7. Interaction Design Patterns

### 7.1 Task Interaction Pattern

| Action | Trigger | Response | Feedback |
|---|---|---|---|
| Create task | Cmd+K or + button | Inline form slides down below trigger | Auto-focus title input |
| Complete task | Checkbox click | Strike-through text, fade-out, move to completed | Confetti burst (first daily task), streak update |
| Edit task | Click on title | Inline edit mode or slide-in panel | Save indicator |
| Delete task | Trash icon (visible on hover/row action) | Confirmation required (undo toast for 5s) | Card collapses, toast "Task deleted" + undo |
| Reorder tasks | Drag handle | Visual lift, drop zone highlight | Spring animation on drop |
| Filter tasks | Filter button / keyboard shortcut | Dropdown with multi-select chips | Badge count on filter button |

### 7.2 Course Browsing Pattern

| Action | Trigger | Response | Feedback |
|---|---|---|---|
| View courses | Sidebar click | Card grid loads with skeleton | Staggered card reveal |
| Select course | Card click | Slide transition to detail view | Breadcrumb appears |
| Track progress | Module completion toggle | Progress bar animates forward | Dim completion animation |
| View syllabus | "Syllabus" tab | Accordion sections, expandable | Section count badge |

### 7.3 Habit Tracking Pattern

| Action | Trigger | Response | Feedback |
|---|---|---|---|
| Log habit | Today's checkbox click | Checkbox fills with accent-primary | Scale bounce animation |
| View streak | Navigate to habits module | Streak counter with flame icon | Flame glow intensifies with streak length |
| Missed habit | End of day auto-check | Remaining unlogged habits dim | Notification: "You missed: [habit]" |
| Calendar view | Toggle to calendar mode | Month grid with completion dots | Dot color gradient from dim → bright |

### 7.4 Data Visualization Interaction

| Element | Interaction | Visual Feedback |
|---|---|---|
| Chart hover | Hover over data point | Tooltip with exact values, vertical guide line |
| Chart click | Click on data point | Drill-down to detail view |
| Progress bar | Automatic | Gradient fill, width transition at 500ms |
| Heatmap cell | Hover | Color intensity increases, value tooltip |
| Calendar day | Click | Opens daily log for that date |

### 7.5 Keyboard Shortcuts

| Shortcut | Action | Scope |
|---|---|---|
| `Cmd+K` / `Ctrl+K` | Open Command Palette | Global |
| `N` | New item (task/note/resource) | Context-aware |
| `/` | Focus search bar | Global |
| `Escape` | Close modal / panel / palette | Global |
| `Enter` | Confirm / submit | Form |
| `Tab` / `Shift+Tab` | Navigate between fields | Form |
| `↑` / `↓` | Navigate list items | List view |
| `Space` | Toggle checkbox / play-pause | Context-aware |
| `Cmd+Z` | Undo | Within 5s of action |
| `Cmd+Enter` | Quick save and close | Form |

---

## 8. Micro-Interactions Catalog

### 8.1 Definition

Micro-interactions are single-purpose, trigger-response animations that provide feedback, guide the user, and make the interface feel alive.

### 8.2 Catalog

| # | Micro-interaction | Trigger | Animation | Duration | Timing |
|---|---|---|---|---|---|
| 1 | **Button Press** | Click/tap | `scale(0.97)` with `box-shadow` dim | 100ms | Immediate on pointer down |
| 2 | **Checkbox Toggle** | Click/tap | Scale 1.0 → 1.15 → 1.0 with fill sweep | 250ms | On toggle |
| 3 | **Card Hover** | Mouse enter | `translateY(-3px)`, glow shadow intensifies | 300ms | 50ms delay on enter |
| 4 | **Toast Slide-in** | Action completes | `translateY(-20px)` → `translateY(0)`, opacity 0 → 1 | 300ms | 100ms delay |
| 5 | **Modal Enter** | Trigger click | Backdrop fade 0→0.5 (200ms), modal scale 0.9→1 (300ms) | 300ms | Parallel |
| 6 | **Sidebar Hover** (collapsed) | Mouse enter | Width expands from w-16 to w-60 | 200ms | On hover |
| 7 | **Progress Fill** | Value change | Width animates from previous to new value | 500ms | On update |
| 8 | **Notification Badge** | New notification | Scale 0 → 1.2 → 1 + pulse glow | 400ms | On receive |
| 9 | **Skeleton Fade** | Content loads | Opacity 1 → 0 (skeleton), 0 → 1 (content) | 200ms | On data ready |
| 10 | **Page Transition** | Route change | Current page opacity 1→0 (150ms), new page 0→1 (200ms) | 350ms | On route |
| 11 | **Drag Handle** | Mouse down on drag | Scale 1 → 1.05, shadow elevates | 150ms | On grab |
| 12 | **Drop Target** | Drag over | Background pulse highlight | Continuous | While dragging |
| 13 | **Delete Undo** | Delete action | Card collapses (300ms), toast appears (300ms) | 600ms | On delete |
| 14 | **Search Type** | Key press in search | Debounced results appear below with stagger | 200ms delay | On input |
| 15 | **Streak Flame** | New day streak | Flame icon flickers, counter increments | 500ms | On streak update |
| 16 | **Pomodoro Complete** | Timer ends | Bell ring sound, pulsing notification | 2s | On timer end |
| 17 | **Confetti Burst** | First task of day | 30-particle confetti from center | 800ms | On check |
| 18 | **Focus Ring** | Tab to element | `ring-2 ring-accent-primary` appears with 100ms delay | 100ms | On focus |
| 19 | **Error Shake** | Form validation fail | Input shakes horizontally 3px amplitude, 3 cycles | 300ms | On submit |
| 20 | **Dropdown Open** | Click trigger | Content scales from 0.95→1, opacity 0→1 | 200ms | On click |

### 8.3 Motion Guidelines

| Property | Recommendation | Rationale |
|---|---|---|
| Duration | 100ms-500ms | Fast enough to feel responsive, slow enough to perceive |
| Easing | `cubic-bezier(0.4, 0, 0.2, 1)` for exits, `cubic-bezier(0, 0, 0.2, 1)` for entrances | Material Design-inspired, natural feel |
| Stagger delay | 50ms increments, max 8 children | Creates wave effect without excessive wait |
| Overlap | 80% overlap between enter/exit transitions | Smoother feel than sequential |
| Reduced motion | Set all durations to 0.01ms, disable keyframes | Accessibility compliance |

---

## 9. Feedback Systems

### 9.1 Feedback Type Hierarchy

| Type | Priority | Usage | Dismissal |
|---|---|---|---|
| **Toast** | Medium | Success, info, warning messages | Auto-dismiss 4s / manual close |
| **Alert Banner** | High | System errors, connectivity loss, important updates | Manual close only |
| **Confirmation Dialog** | Critical | Destructive actions (delete, irreversible changes) | Explicit confirm/cancel |
| **Inline Validation** | Medium | Form field errors | Resolves on valid input |
| **Tooltip** | Low | Helper text, feature explanations | Hover out / tap away |
| **Progress Indicator** | Medium | Loading states, long operations | Auto-hides on completion |
| **Badge Notification** | High | Unread count, reminders | Resolves on action |

### 9.2 Toast Notification System

```
┌────────────────────────────────────────────┐
│  Position: Top-right (desktop), Top (mobile)│
│  Stack: Max 3 visible, newest on top       │
│  Z-index: z-toast (1060)                   │
└────────────────────────────────────────────┘
```

| Variant | Icon | Background | Border | Duration |
|---|---|---|---|---|
| Success | CheckCircle | #065F46 / 90% | #10B981 | 4s |
| Error | AlertCircle | #7F1D1D / 90% | #EF4444 | 6s |
| Warning | AlertTriangle | #78350F / 90% | #F59E0B | 5s |
| Info | Info | #1E3A5F / 90% | #3B82F6 | 4s |
| Undo | Undo2 | #1E293B / 95% | #6366F1 | 5s (includes undo action) |

**Implementation Example:**
```tsx
// Toast component props
interface ToastProps {
  variant: 'success' | 'error' | 'warning' | 'info' | 'undo'
  title: string
  description?: string
  action?: { label: string; onClick: () => void }
  duration?: number // ms, default varies by variant
  onDismiss: () => void
}
```

### 9.3 Confirmation Dialogs

| Scenario | Title | Message | Actions |
|---|---|---|---|
| Delete task | "Delete Task?" | "This action can be undone for 5 seconds." | [Cancel] [Delete] |
| Delete habit | "Delete Habit?" | "All associated logs will be permanently deleted." | [Cancel] [Delete] |
| Discard changes | "Discard Changes?" | "You have unsaved changes. Are you sure?" | [Keep Editing] [Discard] |
| Logout | "Sign Out?" | "You'll need to sign in again to access your data." | [Cancel] [Sign Out] |

### 9.4 Empty States

Every list, grid, and detail page includes an empty state when no data exists. Structure:

1. **Icon** — Module-specific illustration (64x64, stroke-width 1.5, accent-primary)
2. **Headline** — Action-oriented message: "No tasks yet. Start your first one."
3. **Description** — Brief guidance: "Tasks are the building blocks of your day. Create one to begin tracking your progress."
4. **CTA Button** — Primary action to create the first item
5. **Optional: Example prompts** — "Try: 'Complete DSA assignment' or 'Review PR #42'"

**Empty State Registry:**

| Module | Icon | Headline | CTA |
|---|---|---|---|
| Tasks | ClipboardList | "No tasks yet. Start your first one." | "+ Create Task" |
| Courses | BookOpen | "Your course library is empty." | "+ Add Course" |
| Goals | Target | "What do you want to achieve?" | "+ Create Goal" |
| Habits | Flame | "Build your first habit." | "+ New Habit" |
| Sleep | Moon | "Start tracking your sleep." | "Log Tonight" |
| Income | DollarSign | "Track your first income entry." | "+ Add Income" |
| Projects | FolderKanban | "Start your first project." | "+ New Project" |
| Ideas | Lightbulb | "Capture your first idea." | "+ New Idea" |
| Resources | Library | "Save your first resource." | "+ Add Resource" |
| Opportunities | Briefcase | "Find your first opportunity." | "+ Scan" |
| Time entries | Clock | "Start tracking your time." | "+ Log Entry" |
| Chat messages | MessageSquare | "Start a conversation with ARIA." | "Say Hello" |

### 9.5 Loading States

| State | Implementation | Duration |
|---|---|---|
| Initial page load | Full-page skeleton matching component layout | Until data resolves |
| Section load | Card-sized skeleton with shimmer (3 pill shapes) | Until section data resolves |
| Action load | Inline spinner (20px) replaces action icon | Until action completes |
| Background refresh | Silent update, no visual indicator | N/A |
| File upload | Progress bar with percentage + filename | Until upload completes |
| AI generation | Streaming text / skeleton with pulsing glow | Until generation completes |

### 9.6 Error States

| Scenario | Handling | User Message | Recovery Action |
|---|---|---|---|
| Network failure | Toast notification | "Could not load. Check your connection." | Retry button |
| API error (4xx) | Inline error banner | "Something went wrong. [specific message]" | Retry / Go Back |
| API error (5xx) | Inline error banner | "ARIA hit a glitch. Give me a moment." | Retry / Refresh |
| Auth expired | Redirect + toast | "Your session expired. Please sign in again." | Sign In |
| Rate limited | Toast notification | "Too many requests. Try again in 60 seconds." | Countdown timer |
| Form validation | Inline field error | "[Field] is required / invalid" | Auto-focus on error field |
| File upload fail | Per-file error card | "[filename] failed to upload" | Retry / Remove |
| Offline mode | Banner at top | "You're offline. Showing cached data." | None (auto-resolves) |

---

## 10. Error Prevention and Recovery

### 10.1 Prevention Strategies

| Strategy | Implementation | Modules |
|---|---|---|
| **Constraint validation** | Required fields marked, character limits enforced, format validation | Task form, Course form, all inputs |
| **Confirmation before destruction** | Modal dialog for delete, archive, bulk actions | All CRUD modules |
| **Undo capability** | 5-second undo toast after delete/move | Tasks, Ideas, Resources |
| **Auto-save** | Debounced save (1.5s after last input) on forms | Task detail, Goal editor |
| **Graceful degradation** | Every feature works without AI or network | All modules |
| **Input suggestions** | Typeahead for categories, tags, related items | Task creation, Resource tagging |
| **Natural language parsing** | "tomorrow", "next week", "every day" → structured dates | Task due date, Habit frequency |

### 10.2 Recovery Flows

| Failure | Recovery Pattern |
|---|---|
| Network lost during task creation | Save to localStorage queue, sync on reconnect |
| API error on task completion | Optimistic update (show completed), queue for retry |
| Form navigation with unsaved changes | "Discard changes?" confirmation dialog |
| Session timeout during active use | Save current state, redirect to login, restore on return |
| AI generation timeout | Fallback to algorithmic response, notify user |
| Concurrent edit conflict | Last-write-wins, notify with "Updated by another session" toast |

### 10.3 Undo System Architecture

```typescript
interface UndoAction {
  id: string
  type: 'delete' | 'update' | 'move' | 'archive'
  timestamp: number
  entity: { table: string; id: string; data: any }
  expiry: number // Date.now() + 5000
}

// Undo stack maintained in Zustand store
interface UndoStore {
  stack: UndoAction[]
  push: (action: UndoAction) => void
  pop: () => UndoAction | undefined
  clear: () => void
}
```

---

## 11. Onboarding UX

### 11.1 First-Run Experience

| Step | Screen | Duration | Actions |
|---|---|---|---|
| 1 | **Welcome** — Brand animation + tagline | 3s auto | Click "Get Started" |
| 2 | **Goal Setting** — "What do you want to achieve?" — Multiple choice | User-paced | Select 1-3 goals, click "Continue" |
| 3 | **Quick Start** — Create first task | ~30s | Enter task title, optional due date |
| 4 | **Module Tour** — Highlight 5 key modules (Tasks, Courses, Habits, Goals, Chat) | ~2 min | Swipe through tooltips, try each module |
| 5 | **ARIA Introduction** — "Hi! I'm ARIA. Ask me anything." — Sample prompt shown | ~30s | Send first message to ARIA |
| 6 | **Dashboard** — First look at personalized dashboard | — | Automatic transition |

### 11.2 Feature Discovery

| Strategy | Implementation | Frequency |
|---|---|---|
| **Feature spotlight** | Tooltip on new feature, "New" badge for 7 days | Upon feature release |
| **Keyboard shortcut hints** | Shown in tooltip on hover, Command Palette shows all | Always available |
| **Contextual nudges** | "Did you know you can..." type prompts in empty states | On first visit to empty module |
| **Progressive disclosure** | Advanced features hidden behind "Show more" / settings gear | Always |
| **ARIA suggestions** | AI suggests features based on usage patterns: "I notice you've been logging tasks. Want to try Pomodoro?" | Weekly |
| **What's New modal** | Changelog shown after app update with feature highlights | On version update |

### 11.3 Onboarding Metrics

| Metric | Target | Measurement |
|---|---|---|
| Onboarding completion rate | >80% | Funnel: Step 1 → Step 6 |
| Time to first task | <2 min | From sign-up to first task creation |
| Time to first habit | <1 day | From sign-up to first habit log |
| Time to first ARIA chat | <3 days | From sign-up to first message |
| Feature activation (Day 7) | >60% using 3+ modules | Weekly active modules |

---

## 12. Mobile UX Considerations

### 12.1 Mobile-First Design Approach

Every screen is designed **mobile-first** in Figma, then expanded to tablet and desktop. This ensures the core experience is never compromised at smaller viewports.

### 12.2 Breakpoints

| Name | Width | Layout | Navigation |
|---|---|---|---|
| xs | < 375px | Single column, minimal padding | Bottom nav |
| sm | 375-640px | Single column, full-width cards | Bottom nav |
| md | 640-768px | 2-column grids | Bottom nav + hamburger |
| lg | 768-1024px | 2-3 column grids | Sidebar overlay |
| xl | 1024-1280px | Full desktop, 3-4 columns | Fixed sidebar |
| 2xl | > 1280px | Max-width containers, spacious | Fixed sidebar |

### 12.3 Touch Target Requirements

| Element | Minimum Size | Additional Requirements |
|---|---|---|
| Buttons | 44x44px | Adequate spacing between touch targets (>=8px) |
| Icon-only buttons | 44x44px | `aria-label` for accessibility |
| Input fields | 44px height | — |
| List items | 44px height per row | — |
| Bottom nav items | 56x48px (h-14, flex-1) | Active indicator, icon + label |
| FAB | 56x56px | Elevated shadow, bottom-right position |
| Sliders | 44px touch area | Visual track can be thinner |
| Links in text | 44px minimum touch area | Padding added via `inline-block` |

### 12.4 Mobile Gestures

| Gesture | Action | Feedback |
|---|---|---|
| Swipe left on task | Complete task | Strike-through, fade |
| Swipe right on task | Reschedule / move to "Tomorrow" | Slide reveal action |
| Swipe down on list | Pull to refresh | Spinner at top, haptic on refresh |
| Long press on card | Context menu | Haptic feedback, menu appears at touch point |
| Double tap on chart | Toggle full-screen | Chart expands with animation |
| Pinch on dashboard | No action (prevent accidental zoom) | `touch-action: manipulation` |
| Tap status bar | Scroll to top | Smooth scroll to top of page |

### 12.5 Mobile-Specific UI Patterns

| Pattern | Implementation | Rationale |
|---|---|---|
| Bottom sheet for forms | Slide-up panel with handle | Better one-handed reach than full-screen |
| Floating Action Button | 56px circle, bottom-right (+16px from edge) | Quick capture without navigating |
| Tab bar at bottom | 5 tabs max, always visible | Thumb-friendly zone |
| Search via header tap | Tap search bar → full-screen search | Maximize input space |
| Modal as full screen | Slide-up from bottom (100% height) | Avoids modal-on-modal confusion |
| Swipeable tabs | Horizontal swipe between views | Natural mobile interaction |
| Pull-to-refresh | Standard pull gesture | Familiar pattern |

### 12.6 Mobile Constraints and Workarounds

| Constraint | Workaround |
|---|---|
| No hover state | Use long-press for context actions |
| Limited screen space | Progressive disclosure, collapsible sections |
| Network instability | Offline cache, queue failed mutations |
| Keyboard covering inputs | `scrollIntoView()` on focus, `inputmode` attribute |
| Small touch targets | Minimum 44x44px, enforced by `.touch-target` class |
| Accidental back gesture | Confirmation for forms with unsaved data |
| Battery drain | Disable background animations, reduce polling |

### 12.7 PWA Support

| Feature | Implementation |
|---|---|
| Manifest | `manifest.json` with theme_color #0A0B0F |
| Service Worker | Cache-first for static assets, network-first for API |
| Offline fallback | Cached dashboard, queued mutations |
| Install prompt | Shown after 2 visits within 5 minutes |
| Splash screen | Brand logo + "Second Brain OS" on dark background |
| Push notifications | Enabled for reminders, briefings |

---

## 13. Accessibility Integration in UX

### 13.1 Standards Compliance

| Standard | Target | Verification Method |
|---|---|---|
| WCAG 2.1 AA | Minimum compliance | Automated (axe-core) + manual audit |
| WCAG 2.1 AAA | Stretch goal for core flows | Manual audit quarterly |
| Section 508 | US federal compliance | VPAT documentation |
| EN 301 549 | EU accessibility standard | Cross-reference with WCAG |

### 13.2 Accessibility by UX Phase

| UX Phase | Accessibility Activities |
|---|---|
| **Research** | Include 2+ participants with disabilities in usability testing |
| **Definition** | Write accessibility acceptance criteria alongside user stories |
| **Design** | Annotate focus order, ARIA labels, keyboard interactions in Figma |
| **Prototype** | Test with screen reader (VoiceOver / NVDA) |
| **Development** | Lint with `eslint-plugin-jsx-a11y`, use accessible components |
| **Testing** | axe-core automated scan, manual keyboard audit, screen reader test |
| **Release** | Accessibility regression checklist passes |

### 13.3 Specific Accessibility Patterns

| Pattern | Implementation |
|---|---|
| **Skip to content** | First focusable element, visible on focus |
| **Focus order** | Logical DOM order, matches visual reading order |
| **Focus indicator** | `ring-2 ring-accent-primary ring-offset-2 ring-offset-background` |
| **Color contrast** | >=4.5:1 for normal text, >=3:1 for large text (18px+ bold or 24px+) |
| **Reduced motion** | `prefers-reduced-motion` disables all animations (set to 0.01ms) |
| **Screen reader** | ARIA labels on all icons, `aria-live="polite"` on dynamic content |
| **Keyboard navigation** | Tab through all interactive elements, arrow keys for lists/tables |
| **Focus trap** | Modal open: trap focus, close on Escape, return focus on close |
| **Form labels** | Every input has visible `<label>` or `aria-label` |
| **Error announcements** | `aria-live="assertive"` on form validation errors |
| **Status announcements** | `aria-live="polite"` on toast notifications |
| **Heading hierarchy** | Single `<h1>`, logical h2-h4 nesting |

### 13.4 Color Contrast Compliance Table

| Combination | Ratio | AA (normal) | AA (large) | AAA (normal) |
|---|---|---|---|---|
| text-primary (#F0F2F5) on bg-background (#0A0B0F) | 15.2:1 | ✅ | ✅ | ✅ |
| text-primary (#F0F2F5) on bg-card (#12141C) | 14.8:1 | ✅ | ✅ | ✅ |
| text-secondary (#8B92A5) on bg-background (#0A0B0F) | 7.1:1 | ✅ | ✅ | ✅ |
| text-secondary (#8B92A5) on bg-card (#12141C) | 6.8:1 | ✅ | ✅ | ✅ |
| text-tertiary (#5A6075) on bg-background (#0A0B0F) | 4.6:1 | ✅ | ✅ | ❌ |
| text-disabled (#475569) on bg-background (#0A0B0F) | 3.5:1 | ❌ | ✅ | ❌ |
| accent-primary (#6366F1) on bg-background (#0A0B0F) | 5.2:1 | ✅ | ✅ | ❌ |
| accent-neon (#00FFA3) on bg-background (#0A0B0F) | 12.1:1 | ✅ | ✅ | ✅ |

---

## 14. UX Metrics and Measurement

### 14.1 Core UX Metrics (HEART Framework)

| Category | Metric | Target | Collection |
|---|---|---|---|
| **Happiness** | Satisfaction (CSAT) | >4.0/5.0 | Post-interaction survey (10% sampled) |
| **Happiness** | Net Promoter Score (NPS) | >40 | Quarterly survey |
| **Engagement** | Daily Active Users (DAU) | >80% of registered users | Analytics |
| **Engagement** | Sessions per user per day | >3 | Analytics |
| **Engagement** | Feature adoption rate | >50% for core features | Feature activation tracking |
| **Adoption** | Time to first value (TTFV) | <5 min from sign-up | Onboarding funnel |
| **Adoption** | Module activation (Day 7) | >60% using 3+ modules | Weekly cohort analysis |
| **Retention** | Day 1 / Day 7 / Day 30 retention | >70% / >60% / >40% | Cohort analysis |
| **Task Success** | Task completion rate | >95% | Funnel analytics |
| **Task Success** | Time on task | <30s for core actions | Session recording |
| **Task Success** | Error rate | <2% | Form validation analytics |

### 14.2 Task-Specific Metrics

| Task | Success Rate Target | Time Target | Error Rate Target |
|---|---|---|---|
| Create a task | >98% | <15s | <1% |
| Complete a task | >99% | <5s | <0.5% |
| Add a course | >95% | <30s | <2% |
| Log a habit | >99% | <3s | <0.5% |
| View daily briefing | >95% | <10s | <1% |
| Search across modules | >90% | <20s | <5% |
| Set a goal | >90% | <60s | <3% |
| Chat with ARIA | >95% | N/A | <1% |

### 14.3 Measurement Tools

| Tool | Purpose | Integration |
|---|---|---|
| PostHog | Product analytics, session recording, feature flags | Self-hosted / cloud |
| Lighthouse CI | Performance monitoring, accessibility scoring | GitHub Actions |
| Sentry | Error tracking, performance monitoring | Backend + frontend SDK |
| Supabase Analytics | Retention, engagement, funnels | Built-in |
| Custom events | Task-specific metrics | PostHog custom events |

### 14.4 UX Research Cadence

| Week | Activity | Participants | Output |
|---|---|---|---|
| Week 1-2 | Feature usability test | 5-8 users per feature | Report with severity matrix |
| Week 3-4 | Analytics deep dive | All users | Trend report, funnel analysis |
| Week 5-6 | User interviews (10-15) | 10-15 users | Affinity map, themes |
| Week 7-8 | Competitive review | N/A | Gap analysis |
| Week 9-10 | Accessibility audit | 2+ users with disabilities | Issue list, severity ratings |
| Week 11-12 | NPS / SAT survey | All users | Quarterly report |

---

## 15. Design Handoff Process

### 15.1 Handoff Artifacts

| Artifact | Format | Description | Owner |
|---|---|---|---|
| Figma file | `.fig` | Production-ready designs with all states | Designer |
| Design spec | Markdown in docs/ | Interaction details, edge cases, copy | Designer |
| Component documentation | Storybook | Props, variants, examples | Designer + Developer |
| Design token changes | PR to tailwind.config.js | New colors, spacing, typography | Designer |
| Asset exports | SVG / PNG | Icons, illustrations, images | Designer |

### 15.2 Figma File Structure

```
Project: ARIA OS — Second Brain
├── 🎨 Design System
│   ├── Colors
│   ├── Typography
│   ├── Spacing
│   ├── Icons
│   ├── Components
│   │   ├── Button
│   │   ├── Card
│   │   ├── Input
│   │   ├── Modal
│   │   └── ...
│   └── Patterns
├── 🖥️ Screens
│   ├── Dashboard
│   │   ├── v1.0 — Default
│   │   ├── v1.0 — Empty State
│   │   ├── v1.0 — Loading
│   │   └── v1.0 — Error State
│   ├── Tasks
│   │   ├── v1.0 — List View
│   │   ├── v1.0 — Kanban View
│   │   ├── v1.0 — Task Detail
│   │   └── v1.0 — Create Task
│   └── ...
├── 🧪 Prototypes
│   ├── Onboarding Flow
│   ├── Task Creation Flow
│   └── Weekly Review Flow
└── 📝 Research
    ├── User Personas
    ├── User Journey Maps
    └── Usability Test Reports
```

### 15.3 Handoff Checklist

Before marking a design as "Ready for Dev", the designer must verify:

- [ ] All variants/states designed (default, hover, active, disabled, error, loading, empty)
- [ ] Responsive behavior specified (mobile, tablet, desktop)
- [ ] Design tokens used instead of hardcoded values
- [ ] Accessibility annotations added (focus order, ARIA labels)
- [ ] Micro-interactions described (animation, duration, easing)
- [ ] Edge cases documented (long text, missing data, overflow)
- [ ] Error states defined (validation messages, error recovery)
- [ ] Copy approved by PM
- [ ] Figma layers named and organized
- [ ] Components use auto-layout with constraints

### 15.4 Dev-Design Collaboration

| Phase | Designer | Developer |
|---|---|---|
| **Design review** | Present designs, explain rationale | Review for feasibility, ask questions |
| **Component development** | Provide specs, answer questions | Build components, reference design system |
| **Integration** | Review implemented screens | Implement layouts, connect data |
| **QA** | Visual QA pass, note deviations | Fix issues, refine implementation |
| **Sign-off** | Final approval on deployed feature | Demo working feature |

---

## 16. Accessibility-In-Process Integration

### 16.1 Accessibility Checklist by Design Stage

**Wireframe Stage:**
- [ ] Content hierarchy clear without visual styling
- [ ] Tab order matches visual reading order
- [ ] All interactive elements are keyboard accessible

**Mid-fidelity Stage:**
- [ ] Color not sole indicator of meaning (add icons, text)
- [ ] Text alternatives for non-decorative images planned
- [ ] Heading structure documented (h1 → h2 → h3)

**High-fidelity Stage:**
- [ ] Color contrast verified (4.5:1 minimum)
- [ ] Focus indicators designed for every interactive element
- [ ] Touch targets meet minimum size (44x44px)
- [ ] Reduced motion alternatives specified

**Pre-development:**
- [ ] ARIA labels annotated for icons and interactive elements
- [ ] Form error handling and announcements specified
- [ ] Keyboard interaction flow documented

### 16.2 Accessibility Testing Cadence

| Frequency | Test Type | Tool / Method | Responsible |
|---|---|---|---|
| Every PR | Automated | axe-core (CI) | Developer |
| Weekly | Keyboard audit | Manual Tab navigation | Developer |
| Bi-weekly | Screen reader test | VoiceOver / NVDA | QA |
| Monthly | Color contrast audit | Contrast checker | Designer |
| Quarterly | WCAG 2.1 AA full audit | Manual + axe-core | QA + Accessibility specialist |
| Per release | User testing with PwD | 2+ participants | UX Researcher |

---

## Reference

| Document | Link |
|---|---|
| Design Architecture | `docs/design/09_Design.md` |
| Design System | `docs/design/10_DesignSystem.md` |
| Design Tokens | `docs/design/35_DesignTokens.md` |
| Accessibility Design | `docs/design/Accessibility.md` |
| Branding Guide | `docs/design/Branding.md` |
| Motion System | `docs/design/MotionSystem.md` |
| Responsive Design | `docs/design/ResponsiveRules.md` |
| UI Component Library | `apps/web/components/` |
| Tailwind Configuration | `apps/web/tailwind.config.js` |
| Global CSS | `apps/web/app/globals.css` |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-05-15 | Design Team | Initial UI/UX specification |
| 2.0.0 | 2026-06-01 | Design Team | Added user research methodology, metrics framework, accessibility integration |
| 3.0.0 | 2026-06-11 | Design Team | Enterprise upgrade: 16 sections, micro-interactions catalog, feedback systems, onboarding UX, mobile UX patterns, design handoff process |
