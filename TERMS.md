# Terms of Service

## Document Control

| Field | Value |
|---|---|
| **Document ID** | LEG-TERM-001 |
| **Version** | 1.0.0 |
| **Status** | Active |
| **Classification** | External â€” Public |
| **Effective Date** | July 11, 2026 |
| **Last Updated** | 2026-07-11 |
| **Next Review** | 2026-10-11 |
| **Governing Law** | State of California, United States |
| **Provider** | Second Brain OS (ARIA OS) â€” Individual Developer |

---

## Table of Contents

1. [Introduction and Acceptance](#1-introduction-and-acceptance)
2. [The Service](#2-the-service)
3. [Account Registration and Security](#3-account-registration-and-security)
4. [Acceptable Use](#4-acceptable-use)
5. [User Content](#5-user-content)
6. [AI-Generated Content Disclaimer](#6-ai-generated-content-disclaimer)
7. [Intellectual Property](#7-intellectual-property)
8. [Third-Party Services](#8-third-party-services)
9. [Service Availability and Maintenance](#9-service-availability-and-maintenance)
10. [Limitation of Liability](#10-limitation-of-liability)
11. [Indemnification](#11-indemnification)
12. [Termination](#12-termination)
13. [Dispute Resolution](#13-dispute-resolution)
14. [General Provisions](#14-general-provisions)
15. [Contact](#15-contact)

---

## 1. Introduction and Acceptance

### 1.1 Welcome

Welcome to Second Brain OS (operating as **ARIA OS**). These Terms of Service ("Terms") govern your access to and use of the ARIA OS web application, API, and related services (collectively, the "Service").

The Service is provided by an individual developer ("we," "us," or "our"). By creating an account or using the Service, you agree to be bound by these Terms. If you do not agree to these Terms, do not use the Service.

### 1.2 Binding Agreement

These Terms constitute a legally binding agreement between you ("you" or "User") and the developer of Second Brain OS. By using the Service, you acknowledge that you have read, understood, and accept these Terms.

### 1.3 Eligibility

By using the Service, you represent and warrant that:
- You are at least 16 years of age (or the age of digital consent in your country)
- You have the legal capacity to enter into binding contracts
- You are not located in a country subject to a US government embargo or designated as a terrorist-supporting country
- You are not on any US government list of prohibited or restricted parties

### 1.4 Changes to Terms

We may update these Terms from time to time. Material changes will be communicated via email to registered users. Continued use of the Service after changes take effect constitutes acceptance of the updated Terms. If you do not agree to the changes, you must stop using the Service and delete your account.

---

## 2. The Service

### 2.1 Description

ARIA OS is a personal AI productivity system that helps you manage tasks, habits, goals, courses, projects, income, time, sleep, ideas, and resources. It includes optional AI features powered by local (Ollama) or cloud (Claude API) language models, based on your preferences.

### 2.2 Nature of the Service

The Service is a **personal productivity tool**. It is not:
- A professional, legal, medical, or financial advisory service
- A replacement for professional judgment in any field
- A guaranteed path to any specific outcome (productivity, academic, career)

AI-generated content (briefings, recommendations, insights) is for informational and motivational purposes only and should not be relied upon for decisions with legal, financial, or health consequences.

### 2.3 Beta / Pre-Release Status

The Service may undergo significant changes, including features being added, modified, or removed without notice. We do our best to maintain backward compatibility but make no guarantees about feature continuity.

---

## 3. Account Registration and Security

### 3.1 Account Creation

To use the Service, you must create an account. You can register using:
- **Email and password** (authentication handled securely by Supabase)
- **Google OAuth** (single sign-on via your Google account)

You agree to provide accurate, current, and complete information during the registration process and to update it as necessary.

### 3.2 Your Responsibilities

You are responsible for:
- **Maintaining the confidentiality** of your login credentials
- **All activity** that occurs under your account, whether or not authorized by you
- **Notifying us immediately** of any unauthorized use of your account (security@secondbrainos.app)
- **Ensuring your device and network** are secure

### 3.3 Account Security Measures

We implement industry-standard security measures (see our [Privacy Policy](PRIVACY.md)), including:
- JWT-based authentication with short-lived access tokens (1 hour) and refresh tokens (30 days)
- Row-Level Security (RLS) isolating your data from all other users
- Rate limiting to prevent brute force attacks
- No storage of plaintext passwords (bcrypt hashing via Supabase Auth)

### 3.4 Multiple Accounts

You may not create multiple accounts for the purpose of circumventing restrictions, abusing the Service, or evading termination.

---

## 4. Acceptable Use

### 4.1 You May Use the Service To:

- Manage your personal productivity data
- Use AI features (if opted in) for personal productivity assistance
- Create, edit, and export your own content
- Explore and test the Service for evaluation purposes

### 4.2 You May Not:

| Prohibited Activity | Examples |
|---|---|
| **Illegal activity** | Using the Service to plan, facilitate, or document illegal acts; storing contraband data |
| **Abuse of AI systems** | Attempting prompt injection to extract system prompts; using AI to generate harmful, abusive, or illegal content; automated AI probing |
| **Interfering with the Service** | DDoS attacks, attempting to bypass authentication or RLS, exploiting bugs for unauthorized access, reverse engineering |
| **Data scraping / crawling** | Using automated tools to extract data from the Service beyond your own content |
| **Impersonation** | Creating accounts for anyone other than yourself; impersonating others |
| **Spam** | Using the Service to generate or distribute spam, unsolicited messages, or bulk content |
| **Malware** | Uploading malicious code, viruses, or anything that could harm the Service or other users |
| **Commercial resale** | Reselling access to the Service or its features without explicit written permission |
| **Violating others' rights** | Storing or processing data that violates someone else's intellectual property, privacy, or contractual rights |

### 4.3 Enforcement

If we reasonably believe you have violated these Terms, we may:
- Issue a warning
- Restrict or suspend your access to specific features
- Temporarily or permanently suspend your account
- Delete your data (subject to applicable law)
- Report illegal activity to relevant authorities

We will attempt to notify you before taking significant enforcement action unless immediate action is necessary to prevent harm.

---

## 5. User Content

### 5.1 You Own Your Data

You retain all ownership and intellectual property rights to the content you create, upload, or store in the Service ("User Content"). We do not claim ownership of your tasks, goals, notes, chat messages, or any other data you enter.

### 5.2 License to Operate the Service

By using the Service, you grant us a limited, worldwide, non-exclusive, royalty-free license to access, use, process, copy, store, and transmit your User Content solely for the purpose of providing, maintaining, and improving the Service. This license:
- **Lasts** only as long as you use the Service
- **Ends** when you delete your data or account (subject to legal retention requirements)
- **Does not** grant us the right to sell, distribute, or sublicense your content to third parties
- **Does not** grant us the right to use your content for our own purposes (e.g., training AI models on your data)

### 5.3 Data Backup

**You are responsible for maintaining backups of your data.** While we maintain our own backups for operational continuity, we strongly recommend that you regularly export your data using the built-in Export feature (Settings â†’ Export Data). We are not responsible for data loss caused by:
- Your deletion of data
- Account termination (by you or us)
- Force majeure events affecting our infrastructure providers
- Bugs or errors in the Service (we do our best, but no guarantees)

### 5.4 Data Accuracy

You are responsible for the accuracy, quality, and legality of your User Content. We do not review, monitor, or verify User Content for accuracy.

---

## 6. AI-Generated Content Disclaimer

### 6.1 How AI Works

The Service includes optional AI features powered by:
- **Local AI (Ollama):** Runs on your machine â€” no data leaves your computer
- **Cloud AI (Claude API):** Runs on Anthropic's servers â€” only if you explicitly enable it

Both options use large language models (LLMs) to generate content based on your input and stored data.

### 6.2 No Guarantee of Accuracy

**AI-generated content may be inaccurate, incomplete, or misleading.** LLMs can "hallucinate" â€” generate plausible-sounding but factually incorrect information. You should:
- **Always verify** AI-generated information before relying on it
- **Not use** AI-generated content for medical, legal, financial, or safety-critical decisions
- **Exercise judgment** â€” AI is a tool, not a replacement for your own thinking

### 6.3 No Guarantee of Availability

AI features depend on external providers (Ollama on your machine, Claude API on Anthropic). If the provider is unavailable, the AI features may not work. We provide algorithmic fallbacks where possible, but core features (tasks, habits, goals) always work regardless of AI availability.

### 6.4 AI and Privacy

- **Local AI:** No data leaves your machine. We cannot see your AI interactions.
- **Cloud AI:** If enabled, your data is processed by Anthropic under their [Usage Policy](https://www.anthropic.com/legal). Anthropic does not train their models on your API data. See Anthropic's privacy policy for details.

### 6.5 AI Feature Changes

AI features, models, and providers may change as technology evolves. We reserve the right to add, modify, or discontinue AI features at any time. We will notify you before making material changes to AI processing practices.

---

## 7. Intellectual Property

### 7.1 Service IP

The Service â€” including the ARIA OS software, design, branding, trademarks, logos, and user interface â€” is owned by the developer. The source code is licensed under the **MIT License** (see [LICENSE](LICENSE)).

This means:
- You may view, fork, and modify the source code for personal use
- You may not use our branding, logos, or trademarks without permission
- You may not redistribute modified versions as the official ARIA OS Service

### 7.2 Feedback

If you provide feedback, suggestions, or feature requests, we may use them without compensation or attribution. You waive any moral rights in feedback you provide.

### 7.3 Copyright Complaints

If you believe content on the Service infringes your copyright, please contact us with:
- A description of the copyrighted work
- The location of the infringing content
- Your contact information
- A statement of good faith belief that the use is not authorized

We will respond to valid takedown requests in accordance with applicable law.

---

## 8. Third-Party Services

The Service integrates with third-party services that have their own terms and privacy policies. We do not control these services and are not responsible for their operation.

| Service | What It Does | Your Relationship |
|---|---|---|
| **Supabase** | Database, authentication, storage | Subject to Supabase's [Terms](https://supabase.com/terms) and [Privacy Policy](https://supabase.com/privacy) |
| **Vercel** | Frontend hosting, CDN | Subject to Vercel's [Terms](https://vercel.com/legal/terms) |
| **Railway** | Backend hosting | Subject to Railway's [Terms](https://railway.app/legal/terms) |
| **Anthropic (Claude)** | Cloud AI (opt-in only) | Subject to Anthropic's [Usage Policy](https://www.anthropic.com/legal) and [Privacy Policy](https://www.anthropic.com/privacy) |
| **Google** | OAuth authentication, (optional) Calendar | Subject to Google's [Terms of Service](https://policies.google.com/terms) and [Privacy Policy](https://policies.google.com/privacy) |
| **Resend** | Email delivery | Subject to Resend's [Terms](https://resend.com/legal/terms) |
| **Ollama** | Local AI (your machine) | Subject to Ollama's [License](https://github.com/ollama/ollama) (MIT) |
| **Sentry** | Error tracking | Subject to Sentry's [Terms](https://sentry.io/terms/) |

**We disclaim all liability** for the acts, omissions, security breaches, or data practices of these third-party services. We choose providers with strong security postures (SOC 2 Type II certified where available) but cannot guarantee their performance.

---

## 9. Service Availability and Maintenance

### 9.1 No Service Level Agreement (SLA)

The Service is provided on a **best-effort basis** with **no guaranteed uptime or availability**. As a single-developer project, we cannot commit to 99.9% availability or guaranteed response times.

### 9.2 What to Expect

- **Typical availability:** High â€” the Service runs on enterprise-grade infrastructure (Vercel + Railway + Supabase)
- **Planned maintenance:** We will notify you via email or in-app notification at least 48 hours in advance when possible
- **Emergency maintenance:** May occur without notice to address security issues or critical bugs
- **Free-tier infrastructure limits:** The Service runs on free or low-cost infrastructure tiers, which may have resource limits

### 9.3 What Could Go Down

- **Frontend (Vercel):** Rarely down; Vercel has 99.99% historical uptime
- **Backend (Railway):** May experience brief downtime during deployments; Railway has auto-restart
- **Database (Supabase):** Highly available with daily backups and point-in-time recovery
- **AI services:** Local AI depends on your machine; Claude API depends on Anthropic

### 9.4 Infrastructure Changes

We reserve the right to change hosting providers, infrastructure, or technology stack. If such changes materially affect your privacy or data security, we will notify you.

---

## 10. Limitation of Liability

### 10.1 Disclaimer of Warranties

**THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE," WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.** This includes, but is not limited to:
- No warranty that the Service will be uninterrupted, error-free, or secure
- No warranty that AI-generated content will be accurate, reliable, or useful
- No warranty that data will not be lost, corrupted, or temporarily unavailable

### 10.2 Limitation of Liability

**TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, THE DEVELOPER SHALL NOT BE LIABLE FOR:**

- **Indirect or consequential damages** (lost profits, lost data, lost opportunities, business interruption)
- **AI-related damages** (reliance on inaccurate AI-generated content, AI hallucinations)
- **Data loss** (corruption, deletion, or inability to access your data)
- **Third-party service failures** (Supabase, Vercel, Railway, Anthropic, Google, Resend outages or breaches)
- **Damages arising from unauthorized access** to your account (unless caused by our negligence)

### 10.3 Cap on Liability

**OUR TOTAL LIABILITY TO YOU FOR ANY CLAIM ARISING FROM OR RELATING TO THESE TERMS OR THE SERVICE SHALL NOT EXCEED THE GREATER OF:**

- **$100 (USD)**
- **The total amount you have paid us in the 12 months preceding the claim**

### 10.4 Exceptions

Nothing in these Terms excludes or limits liability where prohibited by law, including:
- Death or personal injury caused by negligence
- Fraud or fraudulent misrepresentation
- Willful misconduct or gross negligence

### 10.5 You Assume Risk

By using AI features, you explicitly acknowledge and assume the risk that AI-generated content may be inaccurate, incomplete, or inappropriate. AI output should always be reviewed by a human before action.

---

## 11. Indemnification

You agree to indemnify, defend, and hold harmless the developer from and against any claims, damages, losses, liabilities, costs, and expenses (including reasonable legal fees) arising out of or related to:

1. Your violation of these Terms
2. Your violation of any applicable law or regulation
3. Your User Content (including claims that your content infringes third-party rights)
4. Your misuse of the Service, including AI features
5. Your unauthorized access to or interference with the Service

We reserve the right to assume exclusive defense and control of any matter subject to indemnification by you, in which case you will cooperate with us in asserting any available defenses.

---

## 12. Termination

### 12.1 Termination by You

You may terminate these Terms at any time by deleting your account. Here is what happens:
- Your data is permanently deleted within 30 days (subject to legal retention requirements)
- Deletion is irreversible â€” we cannot recover your data after deletion
- Any outstanding obligations (e.g., payment, if applicable) survive termination

### 12.2 Termination by Us

We may terminate or suspend your access to the Service immediately, without prior notice or liability, if:

| Reason | Examples |
|---|---|
| **Material breach of Terms** | Illegal activity, abuse, scraping |
| **Violation of acceptable use** | Any prohibited use listed in Section 4 |
| **Extended inactivity** | No login for 12+ consecutive months (we will attempt to notify you first) |
| **Legal requirement** | Court order, regulatory requirement |
| **Service discontinuation** | If we decide to discontinue the Service |

### 12.3 Effect of Termination

Upon termination:
- Your right to use the Service immediately ceases
- We will delete your data within 30 days (subject to legal holds)
- Sections 5 (User Content â€” backup responsibility), 6 (AI Disclaimer), 10 (Liability), 11 (Indemnification), and 13 (Dispute Resolution) survive termination

### 12.4 Data Export Before Termination

We encourage you to export your data (Settings â†’ Export Data) before initiating or receiving termination notice. If we terminate for cause, we may not provide an export window.

---

## 13. Dispute Resolution

### 13.1 Governing Law

These Terms shall be governed by and construed in accordance with the laws of **State of California, United States**, without regard to its conflict of law provisions.

### 13.2 Informal Resolution First

Before filing any claim, you agree to try to resolve the dispute informally by contacting us at disputes@secondbrainos.app. We will respond within 15 days and work in good faith to resolve the issue. This is a condition precedent to any formal proceeding.

### 13.3 Binding Arbitration

If we cannot resolve the dispute informally within 30 days, **any dispute arising from these Terms or the Service shall be resolved by binding individual arbitration**, rather than in court, under the following terms:

- The arbitration will be conducted by **American Arbitration Association (AAA)** under its commercial arbitration rules
- The arbitration will take place in **San Francisco, California**, or virtually via video conference
- Each party bears its own costs and fees
- The arbitrator's decision is final and binding

### 13.4 Small Claims Exception

Notwithstanding the arbitration clause, either party may bring an individual action in small claims court in **San Francisco County, California** if the claim qualifies and remains in small claims court.

### 13.5 No Class Actions

**YOU AND WE AGREE THAT EACH MAY BRING CLAIMS AGAINST THE OTHER ONLY IN YOUR OR ITS INDIVIDUAL CAPACITY AND NOT AS A PLAINTIFF OR CLASS MEMBER IN ANY PURPORTED CLASS, REPRESENTATIVE, OR PRIVATE ATTORNEY GENERAL PROCEEDING.**

### 13.6 Statute of Limitations

Any claim arising under these Terms must be commenced within **one (1) year** after the cause of action accrues. Otherwise, it is permanently barred.

---

## 14. General Provisions

### 14.1 Entire Agreement

These Terms, together with our [Privacy Policy](PRIVACY.md) and [Cookie Policy](COOKIE-POLICY.md), constitute the entire agreement between you and us regarding the Service. They supersede all prior agreements, understandings, and communications.

### 14.2 Severability

If any provision of these Terms is held to be invalid or unenforceable, that provision shall be reformed to the minimum extent necessary to make it enforceable, and the remaining provisions shall remain in full force and effect.

### 14.3 Waiver

Our failure to enforce any right or provision of these Terms does not constitute a waiver of that right or provision. Waivers must be in writing and signed by us to be effective.

### 14.4 Assignment

You may not assign or transfer these Terms, by operation of law or otherwise, without our prior written consent. We may assign these Terms without restriction (e.g., if the project is transferred to a new developer or organization).

### 14.5 Force Majeure

We shall not be liable for any failure or delay in performance due to causes beyond our reasonable control, including acts of God, natural disasters, war, terrorism, riots, embargoes, acts of civil or military authorities, fire, floods, accidents, pandemics, power outages, or internet infrastructure failures.

### 14.6 Electronic Communications

By using the Service, you consent to receive electronic communications from us (account notifications, security alerts, privacy updates). You may manage notification preferences in Settings.

### 14.7 Language

These Terms are written in English. Translations may be provided for convenience, but the English version governs in case of conflict.

---

## 15. Contact

| Purpose | Contact |
|---|---|
| **General inquiries** | hello@secondbrainos.app |
| **Privacy questions** | privacy@secondbrainos.app |
| **Security issues** | security@secondbrainos.app |
| **Dispute resolution** | disputes@secondbrainos.app |
| **DMCA / copyright** | copyright@secondbrainos.app |
| **Developer (Data Controller)** | developer@secondbrain-os.com |

**Response time:** We aim to respond within 48 hours.

---

*These Terms of Service were last updated on 2026-07-11. They were written to be clear and fair, not to hide obligations in fine print. If something is unclear, please reach out.*
