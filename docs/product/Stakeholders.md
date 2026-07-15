# Stakeholders — Second Brain OS (ARIA OS)

## Document Control

| Field | Value |
|---|---|
| Document ID | PRD-SH-007 |
| Version | 1.0.0 |
| Status | Active |
| Date | 2026-07-10 |
| Classification | Internal |
| Owner | Developer |

---

## 1. Stakeholder Map

| Stakeholder | Role | Interest | Influence | Engagement |
|---|---|---|---|---|
| Developer | Creator, maintainer, product owner | High | High | Daily |
| BTech CSE Students | Primary users | High | Medium | Community |
| College Ambassadors | Early adopters, promoters | Medium | Medium | Weekly |
| Open Source Community | Contributors, fork authors | Medium | Low | Asynchronous |
| Anthropic / Ollama | AI providers | Low | Low | API only |
| GitHub Sponsors | Financial supporters | Low | Low | Monthly |

---

## 2. Primary Stakeholder: Developer

**Role:** Creator, sole maintainer, product owner, architect, DevOps

**Needs:**
- System should be maintainable alone (~10-15 hrs/week)
- AI should handle repetitive tasks (daily briefings, memory)
- Architecture must survive long breaks (vacation, exams)
- Must be personally useful first — dogfooding validates quality

**Success Criteria:**
- Uses ARIA OS daily for own productivity
- Code changes take < 30 min for simple feature additions
- Zero downtime during breaks (scheduler runs independently)
- Positive feedback from at least 20 external users

---

## 3. Primary Users: BTech CSE Students (18-22)

**Profile:**
- Tech-savvy, comfortable with CLI and GitHub
- English-medium instruction in Indian engineering colleges
- Own a laptop (primary device) + Android phone
- Unreliable campus WiFi, limited data plans
- Zero budget for software

**Needs:**
- Track courses, grades, CGPA across semesters
- Manage assignments, deadlines, exam prep
- Build DSA skills and project portfolio for placements
- Maintain habits (study, sleep, exercise) during academic stress
- All features must work offline

**Pain Points:**
- 5+ apps for different tasks (Notion, Todoist, Anki, Google Calendar, habit tracker)
- No unified view of academic + personal life
- AI tools are either paid or require internet
- Context switching between apps wastes study time

**Success Criteria:**
- Replaces 3+ apps within first week of use
- Grades improve or study time reduces by 20%
- AI briefings feel personalized and useful
- Zero cost for all core features

---

## 4. Secondary Stakeholder: College Ambassador (18-22)

**Profile:** Enthusiastic user who promotes ARIA OS at their college

**Needs:**
- Easy onboarding for classmates (invite links, setup guides)
- Recognition for contributions (shoutouts, GitHub stars)
- Feature requests get heard and prioritized
- Community of like-minded users

**Engagement Model:**
- Private WhatsApp/Telegram group with developer
- Monthly sync on roadmap and feedback
- Early access to new features
- GitHub organization membership for active contributors

---

## 5. Tertiary Stakeholder: Open Source Community

**Profile:** Developers who fork, contribute, or build on ARIA OS

**Needs:**
- Clear contribution guidelines and onboarding
- Well-documented codebase with tests
- Modular architecture for feature development
- Responsive issue triage

**Engagement Model:**
- GitHub Issues + Discussions for async collaboration
- CONTRIBUTING.md with setup guide
- Good First Issue labels for new contributors
- PR review within 48 hours

---

## 6. Stakeholder Communication Plan

| Stakeholder | Frequency | Channel | Content |
|---|---|---|---|
| Developer | Daily | Local dev, CLI | Code, issues, planning |
| Primary users | Weekly | GitHub releases, CHANGELOG | New features, fixes |
| Ambassadors | Weekly | WhatsApp group | Feedback, roadmap |
| Community | Per release | GitHub Discussions | Release notes, roadmap |
| Sponsors | Monthly | GitHub Sponsors dashboard | Financial updates |

---

## 7. Stakeholder Conflicts

| Conflict | Stakeholders | Resolution |
|---|---|---|
| Feature requests vs. solo dev capacity | Users vs. Developer | Public roadmap, defer non-core |
| Open source transparency vs. security privacy | Community vs. Users | Audit trail, redact PII in examples |
| Free forever vs. premium features | Users vs. Developer | Core stays free, premium = optional cloud AI |
| Quick fixes vs. architectural consistency | Users vs. Developer | Linting/CI enforced, tech debt tracked |

---

## 8. References

| Document | Location |
|---|---|
| Personas | `docs/product/Personas.md` |
| User Stories | `docs/product/06_UserStories.md` |
| Product Strategy | ProductStrategy.md |
| Value Proposition | ValueProposition.md |
