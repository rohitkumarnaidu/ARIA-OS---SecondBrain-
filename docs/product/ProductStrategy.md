# Product Strategy — Second Brain OS (ARIA OS)

## Document Control

| Field | Value |
|---|---|
| Document ID | PRD-STG-001 |
| Version | 2.0.0 |
| Status | Active |
| Date | 2026-07-10 |
| Classification | Internal |
| Owner | Developer |

---

## 1. Strategic Vision

**Mission:** Eliminate academic chaos for BTech CSE students through an intelligent, privacy-first second brain that remembers everything, anticipates needs, and works offline for Rs. 0.

**Vision (3-Year):** The default productivity OS for every Indian engineering student — an open-source, AI-native platform that manages coursework, career preparation, projects, and personal growth from a single dashboard.

**North Star Metric:** Weekly active users (WAU) with >5 modules engaged.

---

## 2. Core Strategic Pillars

### Pillar 1: AI-First, Privacy-Preserving
- Local-first AI (Ollama) ensures zero data leaves the device
- Cloud AI is secondary, user-opt-in only
- Every AI feature has algorithmic fallback (no mandatory AI)

### Pillar 2: Free Forever for Core
- Core product (all features, all modules) perpetually free
- Monetization only through optional premium add-ons (Year 2+)

### Pillar 3: Engineering Student Specialization
- India-specific academic constructs (CGPA, SGPA, NPTEL, GATE prep)
- BTech CSE curriculum alignment (DSA, DBMS, OS, CN, System Design)
- No generic productivity — deep specialization

### Pillar 4: Offline-First Architecture
- PWA with service worker enables full functionality offline
- Supabase Realtime syncs when online
- No mandatory internet dependency

---

## 3. Market Positioning

### Primary Target
- **Who:** BTech CSE students in India (ages 18-22)
- **Where:** Tier 1-3 cities, English-medium instruction
- **Pain:** Fragmented apps (Notion + Todoist + Anki + Google Calendar + habit tracker), no unified OS, no AI memory, no offline capability for most tools

### Positioning Statement
> "For BTech CSE students overwhelmed by academic chaos, ARIA OS is the only open-source AI second brain that unifies tasks, courses, goals, habits, sleep, career prep, and project management into a single, privacy-first, offline-capable dashboard — at zero cost."

### Competitive Differentiation
| Factor | ARIA OS | Notion | Todoist | Obsidian |
|---|---|---|---|---|
| AI-first | ✅ | Limited | No | Limited |
| Offline PWA | ✅ | Limited | ✅ | ✅ |
| Academic specialization | ✅ | No | No | No |
| Open source | ✅ | No | No | ❌ |
| Rs. 0 forever | ✅ | No | No | No |
| AI memory | ✅ | No | No | Plugins |

---

## 4. Go-to-Market Strategy

### Phase 1: Distribution (Months 1-6)
- GitHub open-source launch (Show HN, Reddit r/opensource, r/developersIndia)
- College ambassador program (5-10 ambassadors across Indian engineering colleges)
- WhatsApp/Telegram community for early adopters

### Phase 2: Engagement (Months 3-9)
- Weekly feature releases (Monday deploys)
- Public roadmap board (GitHub Projects)
- Active issue triage with 48-hour SLA for bugs

### Phase 3: Monetization (Year 2+)
- Premium AI credits (Claude API pass-through, pay-per-use, .015/req)
- Enterprise licensing (colleges, coaching centers)
- GitHub Sponsors / Open Collective

---

## 5. Strategic Initiatives (Q3-Q4 2026)

| Initiative | Priority | Timeline | Success Metric |
|---|---|---|---|
| Production deploy (Vercel + Railway) | P0 | Jul 14 | URL resolves |
| AI agent frontend integration | P0 | Jul 28 | 11 agent cards live |
| Monitoring & observability | P1 | Aug 11 | RED metrics dashboard |
| Security hardening | P1 | Sep 1 | Zero critical findings |
| PWA + offline optimization | P1 | Sep 15 | Lighthouse 90+ |
| Test coverage to 90%+ | P2 | Sep 30 | 3750+ total tests |

---

## 6. Strategic Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Ollama not available in production | Medium | Claude fallback + algorithmic fallback |
| Low adoption / discoverability | High | College ambassador program |
| Feature creep | Medium | Strict scope control, 3-pillar focus |
| Solo developer burnout | High | Community contributions, scope reduction |
