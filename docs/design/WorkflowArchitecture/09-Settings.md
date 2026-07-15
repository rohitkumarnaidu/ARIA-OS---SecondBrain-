## Document Control

| Field | Value |
|---|---|
| Document ID | DSG-WF09-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-07-11 |

# Part IX â€” Settings

> **Part of the Workflow Architecture (SB-WFARCH-001). See `README.md` for document control.**
> Related: `04-MultiStepExperiences.md` (setup wizards), `02-FeatureFlows.md` Â§2.18 (settings flow), wireframes `06_ANALYTICS_AI_SETTINGS_STATES_WIREFRAMES.md`.

---

## Settings Shell

**Route:** `/settings`
**Layout:** Sidebar + content (desktop), tabs (tablet), accordion (mobile)

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'background': '#0A0B0F', 'primaryColor': '#13151A', 'primaryBorderColor': '#6366F1', 'primaryTextColor': '#F1F5F9', 'lineColor': '#818CF8', 'secondaryColor': '#1A1D24', 'tertiaryColor': '#00FFA3', 'fontFamily': 'DM Sans'}}}%%
flowchart TD
    A[Settings Nav] --> B[Profile]
    A --> C[Account]
    A --> D[Notifications]
    A --> E[Privacy]
    A --> F[AI Preferences]
    A --> G[Appearance]
    A --> H[Integrations]
    A --> I[Connected Apps]

    B --> J[Content area: Profile form]
    C --> K[Content area: Account management]
    D --> L[Content area: Notification toggles]
    E --> M[Content area: Privacy controls]
    F --> N[Content area: AI personality + model]
    G --> O[Content area: Theme picker]
    H --> P[Content area: Integration list]
    I --> Q[Content area: Connected apps grid]
```

### Per-Setting State Matrix

| State | Trigger | UI Treatment | Recovery |
|---|---|---|---|
| **Default** | Page load | Current saved value displayed | N/A |
| **Modified** | User changes value | Orange indicator dot on field | N/A |
| **Saving** | Save triggered | Mini spinner on field / button | N/A |
| **Saved** | API confirms | Green check animation + "Saved" toast (2s) | N/A |
| **Error** | Save fails | Red border + inline error message | Retry or revert |
| **Conflict** | Sync conflict detected | "Updated on another device" dialog | Keep theirs / Keep mine |
| **Disabled** | Dependencies not met | Grayed out + tooltip explanation | Resolve dependency |
| **Offline** | No connection | Amber "Will sync when online" | Auto-sync on reconnect |

---

## 9.1 Profile Settings

**Route:** `/settings/profile`

| Field | Type | Validation | Default |
|---|---|---|---|
| Avatar | Image upload (PNG/JPEG, max 2MB) | Dimension > 100px | Initials fallback |
| Display Name | Text input | 2-50 characters | Google profile name |
| Email | Read-only display | Valid email format | Google account email |
| College | Text input | 2-100 characters | â€” |
| Semester | Select dropdown | 1-8 | â€” |
| Timezone | Searchable select (IANA list) | Valid IANA timezone | Browser Intl API |
| Bio | Textarea | 0-500 characters | â€” |

---

## 9.2 Account Settings

**Route:** `/settings/account`

| Section | Control | Description |
|---|---|---|
| Email | Display (read-only) | Connected Google account email |
| Password | "Change Password" link | â†’ Email reset link (OAuth-based) |
| Connected Accounts | List with status tags | Google (primary), GitHub, (future: Outlook, Notion) |
| Active Sessions | List with device info + revoke button | Current session highlighted |
| Delete Account | Danger button (red) | â†’ Type "DELETE" to confirm â†’ 30-day grace period |

---

## 9.3 Notification Settings

**Route:** `/settings/notifications`

| Category | In-App | Push | Email | Default |
|---|---|---|---|---|
| Task Reminders | âœ… Toggle | âœ… Toggle | âŒ | All On |
| Course Nudges | âœ… Toggle | âœ… Toggle | âŒ | All On |
| Opportunity Alerts | âœ… Toggle | âœ… Toggle | âœ… (weekly) | All On |
| Goal Milestones | âœ… Toggle | âŒ | âŒ | On |
| Habit Reminders | âœ… Toggle | âœ… Toggle | âŒ | All On |
| AI Digests | âœ… Toggle | âŒ | âœ… | On |
| System Alerts | âœ… Toggle (forced) | âœ… Toggle (forced) | âœ… (P0 only) | All On |
| Social (collab) | âœ… Toggle | âœ… Toggle | âŒ | All On |

**Quiet Hours:**

| Setting | Type | Default |
|---|---|---|
| Quiet Hours Start | Time picker (30min intervals) | 22:00 |
| Quiet Hours End | Time picker (30min intervals) | 08:00 |
| Allow Critical (P0) | Toggle | On (bypasses quiet hours) |

---

## 9.4 Privacy Settings

**Route:** `/settings/privacy`

| Setting | Type | Options / Control | Default |
|---|---|---|---|
| Data Storage | Select | Local (Ollama only) / Cloud (Ollama + Claude) | Local |
| Anonymize Data | Toggle | Strip personal info from AI training data | On |
| Export All Data | Button | â†’ Generates JSON download of all user data | â€” |
| Delete All Data | Danger button | â†’ Confirm â†’ Type "DELETE" â†’ 30-day grace | â€” |
| Memory Retention | Select | 30 days / 90 days / 1 year / Forever | 90 days |
| Session Learning | Toggle | Allow ARIA to learn from usage patterns | On |

---

## 9.5 AI Preferences

**Route:** `/settings/ai`

### Personality Sliders

| Trait | Left Label | Right Label | Default |
|---|---|---|---|
| Tone | Formal | Casual | 60% Casual |
| Style | Professional | Friendly | 50% |
| Detail | Brief | Detailed | 70% Detailed |

### Proactivity

| Level | Description |
|---|---|
| Low | Only respond when asked directly |
| Medium | Suggest occasionally (â‰¤ 2/day per agent) |
| High | Proactive suggestions, briefings, nudges (default) |

### AI Features Toggles

All 8 AI features are individually togglable:
- Daily Briefing, Weekly Review, Opportunity Scanning, Memory & Learning
- Sleep Analysis, Course Nudges, Task Suggestions, Skill Roadmap

### Model Configuration

| Setting | Type | Default |
|---|---|---|
| Primary Model | Select | Ollama (Mistral 7B) |
| Fallback Model | Select | Claude Sonnet 4 |
| Auto-fallback | Toggle | On |
| Monthly Token Budget | Slider (10K - 500K) | 100K |
| Budget Alert % | Slider (50% - 95%) | 80% |
| Usage Meter | Display | "42,500 / 100,000 tokens used this month" |

---

## 9.6 Appearance Settings

**Route:** `/settings/appearance`

| Setting | Type | Options | Default |
|---|---|---|---|
| Theme | Visual card picker | Dark, Light, Cyberpunk, High Contrast | Dark |
| Accent Color | Color swatch picker | Indigo, Neon Green, Amber, Rose, Cyan, Custom | Indigo (#6366F1) |
| Sidebar Mode | Select | Icon + Label (full) / Icons Only (collapsed) | Icon + Label |
| Font Size | Slider | Small / Medium / Large | Medium |
| Compact Mode | Toggle | On/Off | Off |
| Reduced Motion | Toggle | Disables all animations | Off |
| Glass Morphism | Toggle | Backdrop blur on cards/modals | On |

---

## 9.7 Integration Settings

**Route:** `/settings/integrations`

| Integration | Status | Actions |
|---|---|---|
| Google Calendar | âœ… Connected | Sync events, view schedule, auto-create tasks |
| GitHub | ðŸ”— Connect | Fetch repos, stars, activity feed |
| YouTube | âœ… Connected | Fetch watch later, subscriptions |
| Resend (Email) | âœ… Connected | Send briefing, weekly review, alerts |
| Notion | ðŸ”œ Coming soon | â€” |
| Obsidian | ðŸ”œ Coming soon | â€” |
| Todoist | ðŸ”œ Coming soon | â€” |
| Browser Extension | ðŸ“‹ Setup guide | Install link + pairing code |

---

## 9.8 Connected Apps

**Route:** `/settings/connected-apps`

| App | Status | Permissions | Last Sync | Actions |
|---|---|---|---|---|
| Google | âœ… Connected | Profile, Calendar (read) | 2m ago | Disconnect |
| GitHub | âœ… Connected | Repos (read) | 1h ago | Disconnect |
| YouTube | âš ï¸ Token expiring | Watch Later (read) | â€” | Reconnect |
| Resend | âœ… Connected | Email (send only) | Active | Disconnect |
