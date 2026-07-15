# ARIA OS — Frontend SEO Strategy

## Document Control

| Field | Value |
|---|---|
| Document ID | FE-SEO-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-07-10 |
| Classification | Internal — Engineering |
| Target Audience | Frontend Developers |
| Cross-References | `docs/engineering/FrontendArchitecture.md §4.3`, `docs/engineering/FrontendPerformanceGuide.md`, `AGENTS.md §26` |

---

## 1. Executive Summary

ARIA OS is a personal productivity system with authenticated user data — most pages are behind auth and not indexable by search engines. The SEO strategy focuses on: (1) public-facing pages (landing, about, privacy, terms, login), (2) Open Graph / Twitter Card metadata for shared links, (3) structured data (JSON-LD) for rich snippets, (4) Core Web Vitals optimization for search ranking, and (5) sitemap/robots.txt for crawler guidance. AI-generated content from ARIA agents is excluded from indexing via canonical tags and noindex directives.

---

## 2. Next.js Metadata API

### 2.1 Root Layout Metadata

```typescript
// app/layout.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  metadataBase: new URL('https://secondbrain-os.com'),
  title: {
    default: 'ARIA OS — Your Second Brain',
    template: '%s | ARIA OS',
  },
  description: 'Personal AI productivity system for students. Manage tasks, courses, goals, habits, and more with AI-powered assistance.',
  keywords: ['productivity', 'ai assistant', 'student planner', 'task management', 'second brain'],
  authors: [{ name: 'ARIA OS' }],
  creator: 'ARIA OS',
  publisher: 'ARIA OS',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    siteName: 'ARIA OS',
    title: 'ARIA OS — Your Second Brain',
    description: 'Personal AI productivity system for BTech CSE students.',
    url: 'https://secondbrain-os.com',
    images: [{ url: '/og-image.png', width: 1200, height: 630, alt: 'ARIA OS' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ARIA OS — Your Second Brain',
    description: 'Personal AI productivity system for BTech CSE students.',
    images: ['/og-image.png'],
    creator: '@aria_os',
  },
  icons: {
    icon: '/icons/icon-192x192.png',
    apple: '/icons/icon-192x192.png',
  },
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    title: 'ARIA OS',
    statusBarStyle: 'black-translucent',
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
    themeColor: '#6366F1',
  },
  category: 'productivity',
}
```

### 2.2 Per-Page Metadata

```typescript
// app/(dashboard)/tasks/page.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Tasks',
  description: 'Manage your tasks with AI-powered prioritization and planning.',
  openGraph: {
    title: 'Tasks | ARIA OS',
    description: 'Manage your tasks with AI-powered prioritization and planning.',
  },
  robots: { index: false, follow: false }, // Auth pages — no index
}
```

### 2.3 Dynamic Metadata (Detail Pages)

```typescript
// app/(dashboard)/tasks/[id]/page.tsx
import type { Metadata, ResolvingMetadata } from 'next'
import { createSupabaseServerClient } from '@/lib/supabase-server'

type Props = { params: { id: string } }

export async function generateMetadata(
  { params }: Props,
  parent: ResolvingMetadata
): Promise<Metadata> {
  const supabase = createSupabaseServerClient()
  const { data: task } = await supabase.from('tasks').select('title, description').eq('id', params.id).single()

  if (!task) return { title: 'Task Not Found' }

  return {
    title: task.title,
    description: task.description?.slice(0, 160) ?? 'View task details',
    openGraph: {
      title: `${task.title} | ARIA OS`,
      description: task.description?.slice(0, 160),
      images: ['/og-image.png'],
    },
    robots: { index: false, follow: false },
  }
}
```

---

## 3. Open Graph / Twitter Card Templates

### 3.1 Default OG Template

```typescript
// lib/utils/seo.ts
import type { Metadata } from 'next'

interface SEOProps {
  title: string
  description: string
  path?: string
  image?: string
  noIndex?: boolean
}

export function buildMetadata({
  title,
  description,
  path = '',
  image = '/og-image.png',
  noIndex = true, // Default for auth pages
}: SEOProps): Metadata {
  const url = `https://secondbrain-os.com${path}`

  return {
    title,
    description,
    alternates: { canonical: url },
    openGraph: {
      title: `${title} | ARIA OS`,
      description,
      url,
      images: [{ url: image, width: 1200, height: 630 }],
    },
    twitter: {
      card: 'summary_large_image',
      title: `${title} | ARIA OS`,
      description,
      images: [image],
    },
    robots: noIndex ? { index: false, follow: false } : { index: true, follow: true },
  }
}
```

### 3.2 OG Image Generation

```typescript
// app/og-image/route.tsx (Edge Runtime)
import { ImageResponse } from 'next/og'

export const runtime = 'edge'

export async function GET() {
  return new ImageResponse(
    (
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #0A0B0F 0%, #1A1B2E 50%, #0A0B0F 100%)',
          fontFamily: 'Syne',
        }}
      >
        <div style={{ fontSize: 72, color: '#6366F1', fontWeight: 700 }}>ARIA OS</div>
        <div style={{ fontSize: 28, color: '#94A3B8', marginTop: 16 }}>Your Second Brain</div>
      </div>
    ),
    { width: 1200, height: 630 }
  )
}
```

### 3.3 OG Image Per-Module

| Route | OG Title | OG Description |
|---|---|---|
| `/` | ARIA OS — Your Second Brain | Personal AI productivity system |
| `/tasks` | Tasks | AI-powered task management |
| `/courses` | Courses | Track your academic progress |
| `/goals` | Goals | Goal setting with AI roadmaps |
| `/chat` | AI Chat | Talk to ARIA, your AI assistant |
| `/dashboard` | Dashboard | Your productivity overview |
| All [id] pages | [Item Title] | Dynamic per-item description |

---

## 4. JSON-LD Structured Data

### 4.1 Organization Schema

```typescript
// app/layout.tsx — injected in root layout
const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'SoftwareApplication',
  name: 'ARIA OS',
  applicationCategory: 'ProductivityApplication',
  operatingSystem: 'Web',
  description: 'Personal AI productivity system for BTech CSE students.',
  url: 'https://secondbrain-os.com',
  author: {
    '@type': 'Person',
    name: 'Developer',
  },
  offers: {
    '@type': 'Offer',
    price: '0',
    priceCurrency: 'USD',
  },
  screenshot: 'https://secondbrain-os.com/og-image.png',
}
```

### 4.2 BreadcrumbList Schema

```typescript
// components/shared/JsonLdBreadcrumb.tsx
interface BreadcrumbItem {
  name: string
  url: string
}

export function JsonLdBreadcrumb({ items }: { items: BreadcrumbItem[] }) {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: `https://secondbrain-os.com${item.url}`,
    })),
  }

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
    />
  )
}
```

### 4.3 WebApplication Schema (Phase 2)

```typescript
const pwaJsonLd = {
  '@context': 'https://schema.org',
  '@type': 'WebApplication',
  name: 'ARIA OS',
  url: 'https://secondbrain-os.com',
  applicationCategory: 'ProductivityApplication',
  browserRequirements: 'Requires JavaScript. Best on Chrome, Edge, or Firefox.',
  offers: {
    '@type': 'Offer',
    price: '0',
    priceCurrency: 'USD',
  },
  featureList: [
    'AI-powered task management',
    'Course and academic tracking',
    'Habit and goal tracking',
    'Opportunity radar',
    'Knowledge graph',
  ],
}
```

### 4.4 Schema Deployment Plan

| Schema | Page(s) | Phase | Status |
|---|---|---|---|
| SoftwareApplication | `/` | Phase 1 | ✅ Active |
| BreadcrumbList | All dashboard pages | Phase 2 | ⏳ Not yet |
| WebApplication | `/` | Phase 2 | Planned |
| FAQPage | `/` landing | Phase 2 | Planned |
| Person | `/about` | Phase 2 | Planned |

---

## 5. Sitemap Generation

### 5.1 Dynamic Sitemap

```typescript
// app/sitemap.ts
import { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://secondbrain-os.com'

  // Public routes only (auth-protected pages excluded)
  const staticRoutes = [
    { url: baseUrl, lastModified: new Date(), changeFrequency: 'weekly' as const, priority: 1.0 },
    { url: `${baseUrl}/login`, lastModified: new Date(), changeFrequency: 'monthly' as const, priority: 0.3 },
  ]

  // Future: dynamic routes for public-facing content
  // const dynamicRoutes = await fetchPublicPages()

  return [...staticRoutes]
}
```

### 5.2 Sitemap Index Strategy

| Sitemap | Routes | Regeneration | Priority |
|---|---|---|---|
| `sitemap.xml` (root) | /, /login, /about, /privacy, /terms | On deploy | High |
| `sitemap-pages.xml` | Static public pages | Weekly | Medium |
| `sitemap-dynamic.xml` | User-shareable content (future) | On content change | Low |

---

## 6. Robots.txt Configuration

```text
# public/robots.txt
User-agent: *
Allow: /
Disallow: /dashboard/
Disallow: /tasks/
Disallow: /courses/
Disallow: /goals/
Disallow: /habits/
Disallow: /sleep/
Disallow: /income/
Disallow: /projects/
Disallow: /ideas/
Disallow: /resources/
Disallow: /opportunities/
Disallow: /time/
Disallow: /chat/
Disallow: /automation/
Disallow: /youtube/
Disallow: /academics/
Disallow: /settings/
Disallow: /api/
Disallow: /_next/

Sitemap: https://secondbrain-os.com/sitemap.xml
```

### Robot Directives Per Page

| Page | Index | Follow | Rationale |
|---|---|---|---|
| `/` | ✅ | ✅ | Landing page — SEO critical |
| `/login` | ❌ | ❌ | Auth page — no value in SERP |
| `/about` | ✅ | ✅ | Public info page |
| `/privacy` | ✅ | ✅ | Legal requirement |
| `/terms` | ✅ | ✅ | Legal requirement |
| All `/dashboard/*` | ❌ | ❌ | Auth-protected — user data |
| All `/[module]` | ❌ | ❌ | Auth-protected — user data |
| All `/[module]/[id]` | ❌ | ❌ | User-specific content |

---

## 7. Canonical URL Handling

### 7.1 Canonical URL Pattern

```typescript
// Applied via per-page metadata or SEO utility
export const metadata: Metadata = {
  alternates: {
    canonical: 'https://secondbrain-os.com/tasks',
  },
}
```

### 7.2 Canonical Rules

| Scenario | Canonical URL | Example |
|---|---|---|
| Page with query params | Stripped to base path | `/tasks?filter=pending` → `/tasks` |
| Page with trailing slash | Normalized to no slash | `/tasks/` → `/tasks` |
| Duplicate content | Primary route | `/academics` and `/courses` |
| Shared link with tracking | Clean URL | `/tasks?utm_source=twitter` → `/tasks` |
| AI-generated content | `noindex` (no canonical needed) | Briefing pages |

---

## 8. Core Web Vitals Impact on SEO

### 8.1 CWV Targets

| Metric | Target | SEO Impact | Current Status |
|---|---|---|---|
| **LCP** | < 1.5s | Ranking factor | ⏳ Needs optimization |
| **FID / INP** | < 50ms / < 100ms | Ranking factor | ✅ Within budget |
| **CLS** | < 0.05 | Ranking factor | ✅ Within budget |
| **TTFB** | < 400ms | Server response | ⏳ Needs optimization |
| **FCP** | < 1.2s | User perception | ✅ Acceptable |

### 8.2 CWV Optimization for SEO

| Technique | CWV Impact | Applied To | Status |
|---|---|---|---|
| Font preloading (next/font) | Reduces LCP | All pages | ✅ Done |
| Image optimization (next/image) | Reduces LCP | All pages | ✅ Done |
| Route-level code splitting | Reduces FID/INP | All pages | ✅ Built-in |
| Dynamic imports (heavy components) | Reduces FID/INP | ThreeBackground, modals | ✅ Done |
| CSS containment | Reduces CLS | Card components | ✅ Done |
| Preconnect to origins | Reduces TTFB | Supabase, fonts | ⏳ Phase 2 |
| Streaming SSR | Reduces LCP/FCP | Dashboard | ⏳ Phase 2 |
| Bundle size CI gate | Prevents LCP regressions | Build pipeline | ⏳ Phase 2 |

### 8.3 Lighthouse CI Enforcement

```yaml
# lighthouserc.json (current)
{
  "ci": {
    "collect": { "numberOfRuns": 3 },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "categories:accessibility": ["error", { "minScore": 0.95 }],
        "categories:seo": ["error", { "minScore": 0.95 }],
        "categories:best-practices": ["error", { "minScore": 0.95 }]
      }
    },
    "upload": { "target": "temporary-public-storage" }
  }
}
```

---

## 9. AI-Generated Content SEO Considerations

### 9.1 AI Content in ARIA OS

| Content Type | Source | Indexable? | Rationale |
|---|---|---|---|
| Daily Briefings | Agent A09 | **No** (`noindex`) | Dynamic, user-specific |
| Weekly Reviews | Agent A10 | **No** (`noindex`) | Dynamic, user-specific |
| Opportunity Matches | Agent A06/A15 | **No** (`noindex`) | Dynamic, user-specific |
| Chat Messages | ARIA chat | **No** (`noindex`) | User conversations |
| Memory Insights | Agent A02 | **No** (`noindex`) | Private user data |
| Learning Patterns | Agent A03 | **No** (`noindex`) | Private user data |
| Sleep Recommendations | Agent A13 | **No** (`noindex`) | Personal health data |
| Nudge Messages | Agent A14 | **No** (`noindex`) | Context-dependent |

### 9.2 AI Content Metadata Behavior

All AI-generated content pages follow:

```typescript
export const metadata: Metadata = {
  robots: {
    index: false,       // Do not index AI-generated content
    follow: false,      // Do not follow links from AI content
    googleBot: {
      index: false,
      follow: false,
    },
  },
}
```

### 9.3 SEO Compliance for AI Content

| Requirement | Implementation | Status |
|---|---|---|
| `noindex` on all agent-generated pages | Per-page metadata | ✅ Done |
| `nofollow` on agent-generated links | Link rel attribute | ✅ Done |
| Canonical URL to primary content | `alternates.canonical` | ✅ Done |
| No deceptive auto-generated content | All AI content labeled clearly | ✅ Done |
| Structured data for original content only | JSON-LD only on public pages | ✅ Done |

---

## 10. Performance SEO

### 10.1 Preconnect & Prefetch

```typescript
// app/layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        {/* Preconnect to critical origins */}
        <link rel="preconnect" href="https://*.supabase.co" />
        <link rel="dns-prefetch" href="https://*.supabase.co" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link rel="preconnect" href="https://api.secondbrain-os.com" />
      </head>
      <body>{children}</body>
    </html>
  )
}
```

### 10.2 LCP Optimization

| Asset | Strategy | Status |
|---|---|---|
| Hero image | `next/image` with `priority` + `placeholder="blur"` | ✅ Done |
| Logo | Inline SVG or `next/image priority` | ✅ Done |
| Fonts | `next/font` with `display="swap"` + `preload: true` | ✅ Done |
| Above-fold CSS | Inline critical CSS (Tailwind JIT) | ✅ Built-in |
| Server response | Edge caching for public pages | ⏳ Phase 2 |

### 10.3 CLS Optimization

| Cause | Fix | Status |
|---|---|---|
| Images without dimensions | Always use width/height or `fill` prop | ✅ Done |
| Dynamic content insertion | Reserve space with skeleton | ✅ Done |
| Web font swap | `next/font display="swap"` prevents layout shift | ✅ Done |
| Embeds (YouTube) | Aspect ratio containers (`aspect-video`) | ✅ Done |
| Late-loading ads | Not applicable | N/A |

### 10.4 INP Optimization

| Pattern | Impact | Status |
|---|---|---|
| Debounced event handlers | Prevents input lag | ✅ Done |
| Web Workers for heavy computation | Keeps main thread free | ⏳ Phase 3 |
| Virtual scrolling for long lists | Reduces DOM size | ⏳ Phase 2 |
| `content-visibility: auto` | Skips off-screen rendering | ✅ Done |
| Avoid long tasks (>50ms) | Break up with `setTimeout` or `requestIdleCallback` | ⏳ Phase 3 |

---

## 11. SEO Audit Checklist

| Item | Frequency | Tool | Target |
|---|---|---|---|
| Lighthouse SEO score | Every commit | Lighthouse CI | ≥95 |
| Meta tags validation | Every page | Manual + axe-core | All public pages |
| OG preview | Every public page | opengraph.xyz | Correct preview |
| Sitemap validity | Weekly | Google Search Console | No errors |
| Robots.txt test | Weekly | Google Search Console | Correct crawl |
| Structured data test | Weekly | Google Rich Results Test | No errors |
| Core Web Vitals | Monthly | CrUX / Search Console | All green |
| Broken links | Monthly | Screaming Frog | None |
| Mobile usability | Monthly | Google Mobile-Friendly Test | Pass |

---

## 12. Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-10 | Developer | Initial frontend SEO strategy documentation |
