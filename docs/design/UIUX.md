# UI/UX Specification

## Design Philosophy

- **Clean & Focused** - Minimal distractions, maximum productivity
- **Mobile-First** - Works great on phone, better on desktop
- **Dark Mode Default** - Easy on eyes for late-night sessions
- **Speed Priority** - Every interaction under 100ms

## Color Palette

### Primary Colors
- **Background Dark:** #0A0A0F
- **Background Card:** #12121A
- **Background Elevated:** #1A1A24
- **Border:** #2A2A3A

### Accent Colors
- **Primary Accent:** #6366F1 (Indigo)
- **Secondary Accent:** #10B981 (Emerald - for success)
- **Warning:** #F59E0B (Amber)
- **Error:** #EF4444 (Red)
- **Info:** #3B82F6 (Blue)

### Text Colors
- **Primary Text:** #F8FAFC
- **Secondary Text:** #94A3B8
- **Muted Text:** #64748B

### Priority Colors
- **Urgent:** #EF4444 (Red)
- **High:** #F97316 (Orange)
- **Medium:** #EAB308 (Yellow)
- **Low:** #22C55E (Green)

## Typography

### Font Family
- **Primary:** Inter (system fallback: -apple-system, BlinkMacSystemFont, Segoe UI)
- **Monospace:** JetBrains Mono (for code/timers)

### Font Sizes
- **H1:** 32px / 2rem (Page titles)
- **H2:** 24px / 1.5rem (Section headers)
- **H3:** 20px / 1.25rem (Card titles)
- **Body:** 16px / 1rem (Default text)
- **Small:** 14px / 0.875rem (Secondary info)
- **Tiny:** 12px / 0.75rem (Labels, badges)

### Font Weights
- **Bold:** 700 (Page titles)
- **Semibold:** 600 (Section headers, buttons)
- **Medium:** 500 (Card titles, links)
- **Regular:** 400 (Body text)

## Spacing System

### Base Unit: 4px

- **xs:** 4px
- **sm:** 8px
- **md:** 16px
- **lg:** 24px
- **xl:** 32px
- **2xl:** 48px
- **3xl:** 64px

## Layout Structure

### App Shell
```
┌─────────────────────────────────────────┐
│ Top Navigation Bar (64px)               │
│ [Logo] [Search] [Notifications] [User] │
├────────────┬────────────────────────────┤
│            │                            │
│  Sidebar   │      Main Content          │
│  (240px)   │      (fluid)               │
│            │                            │
│  - Dashboard│                           │
│  - Tasks   │                           │
│  - Courses │                           │
│  - Goals   │                           │
│  - Ideas   │                           │
│  - ...     │                           │
│            │                           │
└────────────┴────────────────────────────┘
```

### Mobile Layout
```
┌─────────────────┐
│ Top Bar (56px) │
├─────────────────┤
│                 │
│   Main Content  │
│   (full width)  │
│                 │
├─────────────────┤
│ Bottom Nav Bar  │
│ (64px)          │
└─────────────────┘
```

## Component Specifications

### Cards
- Border radius: 12px
- Background: #12121A
- Border: 1px solid #2A2A3A
- Padding: 16px
- Hover: subtle glow with accent color

### Buttons

**Primary Button**
- Background: #6366F1
- Text: white
- Border radius: 8px
- Padding: 12px 24px
- Hover: brightness 110%
- Active: scale 0.98

**Secondary Button**
- Background: transparent
- Border: 1px solid #2A2A3A
- Text: #F8FAFC
- Hover: background #1A1A24

**Danger Button**
- Background: #EF4444
- Same as primary

### Input Fields
- Background: #0A0A0F
- Border: 1px solid #2A2A3A
- Border radius: 8px
- Padding: 12px 16px
- Focus: border #6366F1
- Placeholder: #64748B

### Badges/Tags
- Border radius: 6px
- Padding: 4px 8px
- Font size: 12px
- Font weight: 500

### Progress Bars
- Height: 8px
- Border radius: 4px
- Background: #2A2A3A
- Fill: gradient from #6366F1 to #10B981

## Navigation

### Sidebar (Desktop)
- Width: 240px
- Fixed position
- Sections: Dashboard, Productivity, Learning, Building, Money, System
- Icons with labels
- Active state: accent color left border

### Bottom Navigation (Mobile)
- 5 main items: Home, Tasks, Add (+), Chat, Profile
- Floating action button for quick add
- Active: filled icon with accent color

## Dashboard Layout

### Morning Briefing Card
- Full width at top
- Shows: greeting, top 3 tasks, quick stats
- Collapsible sections

### Stats Grid
- 2x2 grid on mobile
- 4-column on desktop
- Cards: Tasks Today, Courses Progress, Income This Month, Streak

### Activity Section
- Recent tasks
- Upcoming deadlines
- Quick actions

## Task Manager Layout

### Task List
- Swipeable on mobile
- Drag handle for reordering
- Priority indicator (colored left border)
- Category tag
- Due time
- Timer button

### Task Creation Modal
- Slide up from bottom (mobile)
- Center modal (desktop)
- Fields: title, priority, category, due date, estimated time
- Smart suggestions below

### Kanban View
- Columns: To Do, In Progress, Done
- Drag and drop between columns
- Column headers with counts

## Roadmap Builder

### Canvas
- Full-screen mode available
- Minimap in corner
- Zoom controls
- Node palette on left

### Nodes
- 8 types: Goal, Milestone, Task, Resource, Course, Project, Custom, Note
- Different shapes per type
- Color coded by status
- Connection lines with arrows

### Properties Panel
- Slide in from right
- Edit node details
- Add subtasks
- Link to other nodes

## Chat Interface

### Message Bubbles
- User: right aligned, #6366F1 background
- ARIA: left aligned, #1A1A24 background
- Max width: 70%
- Border radius: 16px
- Typing indicator animation

### Input Area
- Fixed at bottom
- Textarea auto-grows
- Voice input button
- Send button

## Animations

### Page Transitions
- Fade in: 200ms
- Slide up: 300ms ease-out

### Micro-interactions
- Button press: scale 0.98, 100ms
- Card hover: translateY -2px, shadow increase
- Checkbox: scale bounce

### Loading States
- Skeleton screens for content
- Spinner for actions
- Progress bar for uploads

## Accessibility

- All interactive elements: keyboard navigable
- Focus indicators: 2px accent color outline
- Color contrast: minimum 4.5:1
- Screen reader labels on icons
- Reduced motion option

## Responsive Breakpoints

- **Mobile:** < 640px
- **Tablet:** 640px - 1024px
- **Desktop:** > 1024px

## PWA Requirements

- Installable on mobile
- Offline functionality
- Splash screen
- App icon
- Dark theme as default
