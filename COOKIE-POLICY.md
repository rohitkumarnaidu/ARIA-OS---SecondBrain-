# Cookie Policy

## Document Control

| Field | Value |
|---|---|
| **Document ID** | LEG-COOK-001 |
| **Version** | 1.0.0 |
| **Status** | Active |
| **Classification** | External â€” Public |
| **Effective Date** | July 11, 2026 |
| **Last Updated** | 2026-07-11 |
| **Next Review** | 2026-10-11 |
| **Jurisdiction** | State of California, United States |
| **Owner** | Second Brain OS (ARIA OS) â€” Individual Developer |

---

## Table of Contents

1. [What Are Cookies?](#1-what-are-cookies)
2. [Types of Cookies We Use](#2-types-of-cookies-we-use)
3. [Essential Cookies](#3-essential-cookies)
4. [Functional Cookies](#4-functional-cookies)
5. [Analytics Cookies](#5-analytics-cookies)
6. [Third-Party Cookies](#6-third-party-cookies)
7. [Cookie Declaration Table](#7-cookie-declaration-table)
8. [Managing Cookies](#8-managing-cookies)
9. [Do Not Track Signals](#9-do-not-track-signals)
10. [Changes to This Policy](#10-changes-to-this-policy)
11. [Contact](#11-contact)

---

## 1. What Are Cookies?

Cookies are small text files that websites store on your device (computer, tablet, phone) when you visit them. They are widely used to make websites work properly, improve your browsing experience, and provide information to the website owners.

Cookies can be:
- **First-party cookies:** Set by the website you are visiting (in this case, ARIA OS)
- **Third-party cookies:** Set by a domain other than the website you are visiting (e.g., Google for OAuth)

Cookies can also be:
- **Session cookies:** Deleted when you close your browser
- **Persistent cookies:** Remain on your device for a set period or until you delete them

**Other similar technologies** we use include:
- **Local storage:** Used to store your UI preferences and theme settings in your browser
- **Session storage:** Used to maintain temporary state during your visit

---

## 2. Types of Cookies We Use

We use cookies and similar technologies for three categories of purposes:

| Category | Purpose | Consent Required? | Impact if Disabled |
|---|---|---|---|
| **Essential** | Authentication, security, session management | No â€” strictly necessary | Service will not function |
| **Functional** | Theme preferences, UI settings | No â€” but recommended for full experience | Less personalized experience |
| **Analytics** | Usage statistics, product improvement | Yes â€” requires your consent | No impact on functionality |

### Cookie Consent Preference

When you first visit ARIA OS, we present a cookie consent banner that lets you choose which categories of non-essential cookies you accept. Your preference is stored in a cookie so we remember it on future visits. You can change your preferences at any time by clicking the "Cookie Preferences" link in the footer of the app.

---

## 3. Essential Cookies

Essential cookies are necessary for the Service to function. They cannot be disabled because without them, the Service simply will not work. These cookies do not track you, collect personal information for marketing, or remember your browsing activity outside the Service.

| Cookie Name | Purpose | Duration | Provider |
|---|---|---|---|
| `sb-*-auth-token` | Supabase authentication token â€” keeps you logged in | Session | Supabase |
| `sb-*-refresh-token` | Supabase refresh token â€” renews your session | 30 days | Supabase |
| `csrf-token` | CSRF protection â€” prevents cross-site request forgery attacks | Session | ARIA OS |
| `__session` | Session identifier for API requests | Session | ARIA OS |

**Why they are strictly necessary:**
- **Auth tokens:** Without them, you would need to log in on every page visit
- **CSRF token:** Without it, the Service would be vulnerable to cross-site request forgery attacks
- **Session cookie:** Without it, the API cannot associate requests with your authenticated session

---

## 4. Functional Cookies

Functional cookies enhance your experience by remembering your preferences. They are not strictly necessary but improve usability.

| Cookie Name | Purpose | Duration | Provider |
|---|---|---|---|
| `aria-theme` | Your selected theme (dark/light) | 1 year | ARIA OS |
| `aria-sidebar-state` | Whether the sidebar was collapsed or expanded | 1 year | ARIA OS |
| `cookie-consent` | Your cookie preference choice | 1 year | ARIA OS |

**You can disable functional cookies** in your browser settings, but this may result in a less personalized experience (e.g., defaulting to light theme on each visit).

---

## 5. Analytics Cookies

We use analytics cookies to understand how the Service is used â€” which features are popular, where users encounter errors, and how we can improve. This data is anonymized and aggregated.

### 5.1 Current Status

**As of the effective date of this policy, ARIA OS does not deploy analytics cookies.** We may add privacy-preserving analytics in the future. If we do, we will:

1. Update this Cookie Policy
2. Notify registered users via email
3. Present a consent banner requesting your opt-in
4. Use only privacy-focused analytics providers (e.g., Plausible, PostHog â€” without cookies where possible)

### 5.2 Future Analytics (If Implemented)

If we implement analytics, we will use:

| Approach | Cookie-Free? | Data Collected |
|---|---|---|
| **Cookie-less analytics** (Plausible, Fathom, Umami) | âœ… Yes â€” no cookies needed | Anonymized page views, referrers, browsers |
| **Lightweight analytics** (PostHog with cookie opt-in) | âŒ Requires consent | Feature usage, session recordings (anonymized) |

### 5.3 Current Data Collection (Without Cookies)

We currently collect limited analytics data **without cookies** on our backend:
- Anonymized request counts (endpoint, status code, duration) â€” no user identification
- Error rates and types (via Sentry) â€” no personal data in error logs where avoidable
- Aggregated feature usage (total tasks created, briefings generated, etc.) â€” no per-user tracking

This data collection is:
- **Does not use cookies**
- **Does not identify individual users**
- **Controlled by us** (not shared with third-party analytics networks)
- **Subject to your analytics opt-out** in Settings

---

## 6. Third-Party Cookies

Third-party cookies are set by domains other than the ARIA OS website. Because ARIA OS has a minimal third-party footprint, we use very few of these.

### 6.1 Google OAuth

When you choose to sign in with Google, Google may set cookies as part of the OAuth flow. These cookies are controlled by Google, not by us. They are used to:
- Authenticate your identity
- Obtain your consent for sharing basic profile information (email, name, avatar)

**Google's cookie use:** Governed by Google's [Privacy Policy](https://policies.google.com/privacy) and [Cookie Policy](https://policies.google.com/technologies/cookies). We have no control over these cookies.

**You can avoid third-party OAuth cookies** by signing up with email and password instead of Google OAuth.

### 6.2 Supabase Auth

Supabase's authentication system may set cookies as part of the login flow. These are essential for the Service to function (see Section 3) and are governed by Supabase's [Privacy Policy](https://supabase.com/privacy).

### 6.3 What We Do NOT Use

We do **not** use cookies from:
- Social media platforms (Facebook Pixel, Twitter Analytics, LinkedIn Insight)
- Advertising networks (Google Ads, Meta Ads)
- Remarketing or retargeting services
- Any third-party tracking for advertising purposes
- Any other analytics or marketing platform

---

## 7. Cookie Declaration Table

This table lists every cookie and similar technology that may be set when you use ARIA OS. It is updated whenever we make changes.

### 7.1 First-Party Cookies (Set by ARIA OS)

| Name | Purpose | Type | Duration | Data Stored |
|---|---|---|---|---|
| `csrf-token` | CSRF attack prevention | Essential â€” Session | Session | Random cryptographic token |
| `aria-theme` | Remember your dark/light mode preference | Functional â€” Persistent | 1 year | `"dark"` or `"light"` |
| `aria-sidebar-state` | Remember sidebar collapsed/expanded state | Functional â€” Persistent | 1 year | `"collapsed"` or `"expanded"` |
| `cookie-consent` | Remember your cookie preference choice | Functional â€” Persistent | 1 year | JSON with consent categories |
| `__session` | API request session identifier | Essential â€” Session | Session | Session UUID |

### 7.2 Third-Party Cookies (Set by Partners)

| Name | Purpose | Type | Duration | Provider | More Info |
|---|---|---|---|---|---|
| `__session-*` | Supabase authentication session | Essential â€” Session | Session | Supabase | [Supabase Privacy](https://supabase.com/privacy) |
| `sb-*-auth-token` | Supabase auth token (JWT) | Essential â€” Persistent | 30 days | Supabase | [Supabase Privacy](https://supabase.com/privacy) |
| `sb-*-refresh-token` | Supabase refresh token | Essential â€” Persistent | 30 days | Supabase | [Supabase Privacy](https://supabase.com/privacy) |
| `G_AUTHUSER_*` | Google OAuth session state | Essential â€” Session | Session | Google | [Google Privacy](https://policies.google.com/privacy) |
| `G_CAPTCHA_*` | Google reCAPTCHA (if enabled) | Essential â€” Persistent | 6 months | Google | [Google Privacy](https://policies.google.com/privacy) |

### 7.3 Local Storage (Similar to Cookies)

| Key | Purpose | Type | Duration |
|---|---|---|---|
| `aria-prefs` | UI preferences (font size, layout) | Functional | Persistent until cleared |
| `supabase.auth.token` | Cached authentication token | Essential | Persistent until logout |

### 7.4 Future Cookies

We will update this table if we add any new cookies. We commit to:
- Never adding advertising or tracking cookies
- Always seeking opt-in consent before adding analytics cookies
- Updating the table within 7 days of any change

---

## 8. Managing Cookies

### 8.1 Cookie Consent Banner

When you first visit the Service, you will see a cookie consent banner that allows you to:
- **Accept all** essential + functional cookies
- **Decline** non-essential cookies (functional + analytics)
- **Customize** your preferences per category

You can change your preferences at any time by clicking **"Cookie Preferences"** in the website footer.

### 8.2 Browser Controls

All major browsers let you control which cookies are stored. You can:

| Browser | How to Manage |
|---|---|
| **Google Chrome** | Settings â†’ Privacy and Security â†’ Cookies and other site data |
| **Mozilla Firefox** | Options â†’ Privacy & Security â†’ Cookies and Site Data |
| **Apple Safari** | Preferences â†’ Privacy â†’ Cookies and website data |
| **Microsoft Edge** | Settings â†’ Cookies and site permissions â†’ Cookies and site data |
| **Brave** | Settings â†’ Shields â†’ Cookies |
| **Opera** | Settings â†’ Privacy & Security â†’ Cookies |

You can typically:
- View all cookies stored on your device
- Delete individual cookies or all cookies
- Block third-party cookies
- Block all cookies (but essential cookies are required for the Service to function)
- Set your browser to notify you when a cookie is set

### 8.3 Blocking Essential Cookies

If you block essential cookies, the Service will not function. Specifically:
- **Without auth cookies:** You cannot stay logged in
- **Without CSRF token:** The API will reject your requests for security reasons
- **Without session cookie:** You will need to re-authenticate on every page load

### 8.4 Opting Out of Future Analytics

If we implement analytics cookies in the future, you will have these opt-out options:
1. **Cookie consent banner:** Decline analytics cookies
2. **Settings:** Disable analytics tracking in Settings
3. **Browser:** Block third-party cookies (if analytics are served by a third party)
4. **Opt-out links:** We will provide direct opt-out links for any analytics provider

---

## 9. Do Not Track Signals

### 9.1 What Is Do Not Track?

"Do Not Track" (DNT) is a browser setting that sends a signal to websites requesting that they do not track your browsing activity. DNT is not a standardized or legally binding signal, and there is no consensus on how websites should respond.

### 9.2 Our Response

ARIA OS **currently respects DNT signals** from browsers that send them. When DNT is enabled in your browser:

- We will not set analytics cookies (but essential and functional cookies still apply)
- We will not track your activity across third-party sites
- We will not create a browsing profile of you

If we later implement analytics, we will continue to honor DNT signals by defaulting analytics to OFF for users who have DNT enabled.

### 9.3 Global Privacy Control (GPC)

We also respect the **Global Privacy Control** (GPC) signal, where available. If your browser or extension sends a GPC signal, we will treat it as an opt-out of any non-essential data collection, including analytics.

---

## 10. Changes to This Policy

We may update this Cookie Policy from time to time. When we do:

1. We will update the "Last Updated" date at the top of this document
2. We will notify registered users via email if we add new types of cookies
3. We will present a new cookie consent banner if your existing consent does not cover the new cookies
4. For minor changes (clarifications, formatting), we may update without direct notice

**Material changes** include:
- Adding analytics cookies or other tracking technologies
- Adding third-party services that set cookies
- Changing how we use existing cookie data

We encourage you to review this policy periodically.

---

## 11. Contact

If you have questions about our use of cookies, please contact us:

| Role | Contact |
|---|---|
| **Data Protection Officer** | dpo@secondbrainos.app |
| **Cookie Policy Inquiries** | privacy@secondbrainos.app |
| **Developer** | developer@secondbrain-os.com |

**Response time:** We aim to respond within 48 hours.

---

## Cookies Explained Simply

If you are not familiar with the technical details, here is the plain-English summary:

- **Essential cookies** are like the keys to your house â€” you cannot get in without them
- **Functional cookies** are like remembering that you prefer the lights dimmed â€” nice but not essential
- **Analytics cookies** are like a shop owner noting that most customers visit on Saturdays â€” helps improve things, but no one is identified
- **We do not use advertising cookies** â€” we do not show ads and we do not track you across other websites
- **You are in control** â€” you can change your preferences at any time

---

*This Cookie Policy was last updated on 2026-07-11. We use only as few cookies as possible to make the Service work, and we will never add tracking cookies without telling you first.*
