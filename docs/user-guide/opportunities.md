# Opportunity Radar Guide

## Document Control

| Field | Value |
|---|---|
| Document ID | UG-OPPORTUNITIES-001 |
| Version | 1.0.0 |
| Status | Active |
| Classification | Public - User Documentation |
| Last Updated | 2026-07-14 |

---

## Introduction

The Opportunity Radar automatically scans and matches opportunities (internships, scholarships, hackathons, open-source projects, grants, competitions) to your skills, goals, and preferences. It runs daily at 6 AM and scores each opportunity by relevance.

## How the Radar Works

1. **Profile matching**: The AI analyzes your skills, courses, goals, and preferences
2. **Search queries**: Generates targeted search queries for 8 opportunity categories
3. **Brave Search**: Searches the web for relevant opportunities
4. **AI parsing**: Extracts structured data from search results
5. **Scoring**: Each opportunity receives a match score from 0-100

## Viewing Opportunities

1. Go to **Opportunities** from the sidebar
2. The radar displays matched opportunities sorted by score
3. Each card shows:
   - Title and source URL
   - Match score (color-coded badge)
   - Deadline (if available)
   - Opportunity type
   - Skills matched

## Understanding Match Scores

| Score | Color | Meaning |
|---|---|---|
| 85-100 | Green (neon) | Highly relevant -- strong match with your profile |
| 60-84 | Amber | Moderately relevant -- some skills align |
| Below 60 | Red | Low relevance -- may not be a good fit |

## Taking Action on Opportunities

- Click on an opportunity to view full details
- Visit the source link to apply or learn more
- Use **Save** to bookmark for later review
- Opportunities with deadlines under 48 hours trigger a push notification

## On-Demand Matching

For specific opportunities you find yourself, use the Opportunity Matching feature (A15):

1. Open the ARIA chat
2. Paste or describe the opportunity
3. ARIA's matching engine scores it against your profile
4. Get an instant relevance assessment with reasoning

## Managing Opportunities

### View and Filter

The Opportunities page provides:
- **Score view**: Cards sorted by match score (highest first)
- **Category filter**: Filter by internship, scholarship, hackathon, open-source, grant, competition, job, fellowship
- **Score range filter**: Set minimum match score threshold
- **Deadline filter**: Show only opportunities with upcoming deadlines
- **Search**: Find opportunities by title or source

### Reading Opportunity Details

Each opportunity card displays:
- Clear title and source organization
- Match score badge (color-coded: green/amber/red)
- Opportunity type badge
- Urgency indicator if deadline is within 48 hours
- Matched skills from your profile
- Direct link to the application or details page

Click on any card to see:
- Full description parsed from the source
- Requirements and eligibility
- Deadline with countdown
- Match reasoning (why this opportunity matches your profile)
- Application status (saved, applied, interview, accepted, rejected)

### Tracking Applications

Track your progress for each opportunity:
1. Open the opportunity detail
2. Set the **Application Status**: saved, applied, interview, accepted, rejected
3. Add notes about your application or next steps
4. The status appears on the opportunity card for quick reference

### On-Demand Matching

When you find an opportunity outside the radar scan:
1. Open the ARIA chat
2. Paste the opportunity URL or description
3. Type "match this opportunity" or similar
4. ARIA's matching engine (agent A15) evaluates it against your profile
5. Receive a match score with reasoning

This is useful for:
- Opportunities you find through personal networks
- Niche opportunities the automated scan might miss
- Getting a second opinion on fit

## Opportunity Sources

The radar scans 8 categories:

| Category | Examples | Scan Query Pattern |
|---|---|---|
| Internships | Summer internships, remote internships | "internship [your skills] [year]" |
| Scholarships | Merit-based, need-based, full-ride | "scholarship [your field] [year]" |
| Hackathons | Online, in-person, themed | "hackathon [your field] [month]" |
| Open Source | GSOC, LF, community projects | "open source contribution [your skills]" |
| Grants | Research, project, startup grants | "grant [your field] students [year]" |
| Competitions | Coding, design, case competitions | "[field] competition [your level]" |
| Jobs | Entry-level, part-time, remote | "entry level [your field] [year]" |
| Fellowships | Research, teaching, leadership | "fellowship [your field] [year]" |

## Tips

- Keep your skills and goals up to date for better matches -- the radar depends on accurate profile data
- Check the radar daily after the 6 AM scan for fresh opportunities
- Review low-scoring matches too -- they may reveal new interests you had not considered
- Use the on-demand matcher for opportunities you discover independently
- Track your application status to avoid applying to the same opportunity twice
- Set a weekly goal for applications to make consistent progress
- Opportunities with deadlines under 48 hours trigger push notifications -- respond promptly

## Related Guides

- [Goals](goals.md) -- Opportunities can trigger new goal creation
- [Chat & AI](chat-and-ai.md) -- On-demand opportunity matching via ARIA
- [Dashboard](features-overview.md) -- Top opportunities appear on dashboard
- [Weekly Review](weekly-review.md) -- Review opportunity pipeline during weekly review
