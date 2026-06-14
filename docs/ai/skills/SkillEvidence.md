# Skill Evidence System — Enterprise Evidence Intelligence Architecture

---

## Document Control

| Field | Value |
|---|---|
| Document ID | SB-SKILLEVIDENCE-ARCH-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-06-12 |
| Classification | Internal — Architecture Reference |
| Source of Truth | `docs/ai/skills/skills.md` (Skills System Enterprise Architecture — §11, §7, §5, §12) |
| Companion Docs | `docs/ai/skills/SkillAssessment.md` (Assessment Execution Engine) |
| | `docs/ai/skills/SkillIntelligence.md` (Analytics Engine & Scoring Pipelines) |
| | `docs/ai/skills/SkillGraphArchitecture.md` (Graph Storage & Traversal) |
| Target Stack | Python 3.11+ (Evidence Engine) + Neo4j (Evidence Graph) + PostgreSQL (Relational) + Redis (Cache + Rate Limit) + FastAPI (API Layer) |
| Target Audience | AI Agents, Evidence Engineers, Security Engineers, Data Engineers, Architects, Product Managers |

---

## Table of Contents

- [1. Evidence Architecture](#1-evidence-architecture)
- [2. Evidence Collection Pipeline](#2-evidence-collection-pipeline)
- [3. Verification Model](#3-verification-model)
- [4. Trust Score Framework](#4-trust-score-framework)
- [5. Evidence Weighting Logic](#5-evidence-weighting-logic)
- [6. AI Validation Engine](#6-ai-validation-engine)
- [7. Fraud Detection](#7-fraud-detection)
- [8. Skill Confidence Calculation](#8-skill-confidence-calculation)
- [9. Analytics](#9-analytics)
- [10. Database Design](#10-database-design)
- [Appendix A: Source Verifier Matrix](#appendix-a-source-verifier-matrix)
- [Appendix B: Trust Score Formulas](#appendix-b-trust-score-formulas)
- [Appendix C: Glossary](#appendix-c-glossary)

---

## 1. Evidence Architecture

### 1.1 Why a Dedicated Evidence Execution Engine?

Skills.md defines the **data model** for evidence — what evidence types exist, how quality is scored, and what thresholds apply per level. SkillEvidence.md defines the **execution engine** — the runtime that collects, verifies, trusts, and weights evidence before it feeds into skill confidence calculations.

The relationship between the four documents:

| Document | Role | Analogy |
|---|---|---|
| `skills.md` (§11, §7) | Evidence data model & formulas | Constitution |
| `SkillGraphArchitecture.md` | Evidence graph storage | Filing cabinet |
| `SkillAssessment.md` | Assessment execution engine | Exam proctor |
| **`SkillEvidence.md`** | **Evidence intelligence engine** | **Private investigator + forensic auditor** |

### 1.2 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      EVIDENCE INTELLIGENCE ENGINE                             │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                   COLLECTION LAYER                                    │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │   │
│  │  │Project   │ │GitHub    │ │Certific. │ │Hackathon │ │Freelance │   │   │
│  │  │Collector │ │Collector │ │Collector │ │Collector │ │Collector │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘   │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────────┐   │   │
│  │  │OSS       │ │Assessment│ │Work Exp  │ │Auto-Discovery Engine │   │   │
│  │  │Collector │ │Collector │ │Collector │ │(ARIA proactive scan) │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                   PROCESSING LAYER                                    │   │
│  │                                                                      │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │   │
│  │  │ Normalizer │─▶│ Verifier   │─▶│ Trust      │─▶│ Weight       │  │   │
│  │  │ (source    │  │ (3-tier:   │  │ Scorer     │  │ Calculator   │  │   │
│  │  │  adapters) │  │ Auto→AI→Hu)│  │ (provenance│  │ (quality×trust│  │   │
│  │  └────────────┘  └────────────┘  └────────────┘  │ ×diversity)  │  │   │
│  │                                                   └──────────────┘  │   │
│  │  ┌────────────┐  ┌──────────────────┐  ┌────────────────────────┐  │   │
│  │  │ Fraud      │  │ Cross-Reference  │  │ AI Validator          │  │   │
│  │  │ Detector   │  │ Engine           │  │ (LLM authenticity     │  │   │
│  │  │ (8 signals)│  │ (triangulation)  │  │  + inconsistency)     │  │   │
│  │  └────────────┘  └──────────────────┘  └────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                   OUTPUT LAYER                                       │   │
│  │                                                                      │   │
│  │  ┌────────────────────┐  ┌──────────────────┐  ┌─────────────────┐  │   │
│  │  │ Confidence Engine  │  │ Analytics        │  │ Graph Storage   │  │   │
│  │  │ (Bayesian update)  │  │ (Collection/     │  │ (Neo4j evidence │  │   │
│  │  │                    │  │  Verification/   │  │  nodes + rels)  │  │   │
│  │  │ Input → Score →    │  │  Fraud KPIs)     │  └─────────────────┘  │   │
│  │  │        Level → Sig │  └──────────────────┘                       │   │
│  │  └────────────────────┘                                             │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Core Design Principles

| Principle | Rationale | Implementation |
|---|---|---|
| **Source-specific intelligence** | Each evidence source has unique verification needs | 8 source-specific collector adapters with independent logic |
| **Trust before weight** | Evidence quality is meaningless if the evidence is fake | Trust score gates the weight calculation |
| **Defense in depth** | Fraud must be detectable at collection, verification, and cross-reference layers | 8-signal fraud detection + cross-referencing + AI validation |
| **Auto-discovery by default** | Users shouldn't manually submit what ARIA can find | Tenant-configurable auto-import mode |
| **Cryptographic provenance** | Evidence integrity must be verifiable after the fact | Hash chain on every state transition |
| **Graceful degradation** | Every collector works without AI via algorithmic fallback | PromptLoader + inline fallbacks |

### 1.4 Evidence Lifecycle State Machine

Each evidence item progresses through a rigorous state machine:

```
                      ┌─────────────────────────────────────┐
                      │            REJECTED                  │
                      │  (failed verification / fraud)      │
                      └─────────────────────────────────────┘
                         ▲                                  ▲
                         │                                  │
┌────────┐   ┌────────┐  │  ┌────────┐  ┌────────┐  ┌──────────┐
│  RAW   │──▶│ PARSED │──┼─▶│VERIFIED│──▶│ SCORED │──▶│ ACCEPTED │
│(ingest)│   │(extract│  │  │(auto/AI│  │(weight)│  │ (in use) │
│        │   │ meta)  │  │  │ /human)│  │        │  │          │
└────────┘   └────────┘  │  └────────┘  └────────┘  └──────────┘
                         │      │                          │
                         │      ▼                          │
                         │  ┌────────┐                     │
                         └──│ FLAGGED │◀────────────────────┘
                            │(suspect)│  ┌──────────────┐
                            └────────┘  │  CHALLENGED   │
                                 │      │(peer dispute) │
                                 ▼      └──────────────┘
                            ┌────────┐        │
                            │ARCHIVED│◀───────┘
                            │(expired│
                            │ / old) │
                            └────────┘
```

```python
@dataclass
class EvidenceState(str, Enum):
    RAW = "raw"                  # Just ingested, no processing
    PARSED = "parsed"            # Metadata extracted
    VERIFIED = "verified"        # Passed auto/AI/human verification
    SCORED = "scored"           # Quality and trust scores calculated
    ACCEPTED = "accepted"        # Active and contributing to confidence
    FLAGGED = "flagged"          # Suspicious, requires human review
    REJECTED = "rejected"        # Failed verification or confirmed fraud
    CHALLENGED = "challenged"    # Disputed by peer review
    ARCHIVED = "archived"        # Expired or superseded

    # Valid transitions
    TRANSITIONS: dict["EvidenceState", list["EvidenceState"]] = {
        RAW: [PARSED, FLAGGED],
        PARSED: [VERIFIED, FLAGGED],
        VERIFIED: [SCORED, FLAGGED, REJECTED],
        SCORED: [ACCEPTED, FLAGGED],
        ACCEPTED: [FLAGGED, CHALLENGED, ARCHIVED],
        FLAGGED: [VERIFIED, REJECTED, CHALLENGED],
        CHALLENGED: [VERIFIED, REJECTED, FLAGGED],
        REJECTED: [],  # Terminal state
        ARCHIVED: [RAW],  # Re-activate with new evidence
    }

    def can_transition_to(self, target: "EvidenceState") -> bool:
        return target in self.TRANSITIONS.get(self, [])
```

### 1.5 Source Adapter Registry

```python
class EvidenceSourceType(str, Enum):
    PROJECT = "project"
    GITHUB = "github"
    CERTIFICATION = "certification"
    HACKATHON = "hackathon"
    FREELANCE = "freelance"
    OPENSOURCE = "opensource"
    ASSESSMENT = "assessment"
    WORK_EXPERIENCE = "work_experience"


class SourceAdapterRegistry:
    """
    Registry of evidence source collectors.
    Each source type has an adapter implementing the CollectorProtocol.
    """

    def __init__(self):
        self.logger = StructuredLogger("evidence.adapter_registry")
        self._adapters: dict[EvidenceSourceType, type[BaseCollector]] = {}

    def register(self, source_type: EvidenceSourceType, adapter_cls: type) -> None:
        """Register a collector adapter for a source type."""
        self._adapters[source_type] = adapter_cls
        self.logger.info("Adapter registered", source=source_type.value, cls=adapter_cls.__name__)

    def get_adapter(self, source_type: EvidenceSourceType) -> BaseCollector:
        """Get adapter instance for a source type."""
        cls = self._adapters.get(source_type)
        if not cls:
            raise ValueError(f"No adapter registered for source: {source_type.value}")
        return cls()

    def list_sources(self) -> list[EvidenceSourceType]:
        return list(self._adapters.keys())


# Collector protocol
class BaseCollector(ABC):
    """Abstract base for all source-specific collectors."""

    source_type: EvidenceSourceType

    @abstractmethod
    async def collect(
        self, user_id: str, credentials: dict | None = None
    ) -> list[RawEvidence]:
        """Collect evidence items from this source."""
        ...

    @abstractmethod
    async def verify(
        self, evidence: "EvidenceItem"
    ) -> VerificationResult:
        """Verify a single evidence item from this source."""
        ...

    @abstractmethod
    def get_metadata_schema(self) -> dict:
        """Return the JSON schema for this source's metadata."""
        ...
```

### 1.6 Document Relationship Map

| Evidence Component | Consumed By | Produces |
|---|---|---|
| Collection Pipeline | Verification Model | `RawEvidence` items |
| Verification Model | Trust Score Framework | `VerificationResult` with status |
| Trust Score Framework | Evidence Weighting Logic | `TrustScore` per item |
| Evidence Weighting Logic | Confidence Engine | `WeightedEvidence` with adjusted weight |
| Fraud Detection | All layers | `FraudSignal` with probability |
| Confidence Engine | SkillIntelligence.md, SkillAssessment.md | `ConfidenceScore` per skill |
| Evidence Graph | SkillGraphArchitecture.md | `EvidenceNode` in Neo4j |
| Analytics | All layers | `AnalyticsReport` for dashboards |

---

## 2. Evidence Collection Pipeline

### 2.1 Pipeline Architecture

The collection pipeline runs as a directed acyclic graph of stages. Each evidence source has a dedicated collector that implements the full gather → normalize → enrich → verify → persist flow.

```
                    ┌─────────────────────────────────────┐
                    │      COLLECTION SCHEDULER             │
                    │  (APScheduler cron + event triggers)  │
                    └─────────────────────────────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                   ▼
    ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
    │ Manual Submit │   │ Auto-Discovery│   │ API Import   │
    │ (user upload) │   │ (ARIA scan)   │   │ (webhook)    │
    └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
           │                  │                  │
           └──────────────────┼──────────────────┘
                              ▼
                    ┌──────────────────┐
                    │  NORMALIZER      │
                    │  (source→canon.) │
                    └──────┬───────────┘
                           ▼
                    ┌──────────────────┐
                    │  ENRICHER        │
                    │ (extract skills, │
                    │  infer metadata) │
                    └──────┬───────────┘
                           ▼
                    ┌──────────────────┐
                    │  COLLECTOR QUEUE │
                    │ (buffered write) │
                    └──────┬───────────┘
                           ▼
                    ┌──────────────────┐
                    │  VERIFIER        │
                    │ (3-tier dispatch)│
                    └──────────────────┘
```

### 2.2 Evidence Data Model (Core)

```python
@dataclass
class RawEvidence:
    """Raw evidence as collected from source, pre-processing."""
    source_type: EvidenceSourceType
    user_id: str
    external_id: str | None  # ID in the source system
    raw_data: dict            # Original source response
    collected_at: int         # Epoch ms
    credentials_used: str | None  # Reference to which credential


@dataclass
class EvidenceItem:
    """
    Core evidence item — the canonical representation.
    Persisted to PostgreSQL and Neo4j.
    """
    evidence_id: str          # UUID
    user_id: str
    skill_ids: list[str]      # Skills this evidence maps to
    source_type: EvidenceSourceType
    state: EvidenceState
    title: str
    description: str
    url: str | None
    metadata: dict            # Source-specific structured metadata
    collected_at: int
    verified_at: int | None
    verification_method: str | None  # auto | ai | human
    quality_score: float      # 0.0-1.0 (Gold=1.0 … Unverified=0.1)
    trust_score: float        # 0.0-1.0 (from Trust Score Framework)
    weight: float             # Quality × Trust × Recency
    fraud_signals: list[str]  # Any fraud flags raised
    signed_hash: str          # Cryptographic integrity hash
    previous_hash: str | None # Chain to previous state
    created_at: int
    updated_at: int


@dataclass
class VerificationResult:
    evidence_id: str
    verified: bool
    method: str  # auto | ai | human
    confidence: float
    verified_at: int
    details: str
    reviewer_id: str | None


@dataclass
class EvidenceCollectionResult:
    """Result of a collection run for one source."""
    source: EvidenceSourceType
    items_collected: int
    items_new: int
    items_updated: int
    items_failed: int
    errors: list[str]
    collected_at: int
```

### 2.3 Project Collector

```python
class ProjectCollector(BaseCollector):
    """
    Collects evidence from software, design, and business projects.
    Accepts URLs (GitHub, GitLab, Bitbucket, live demos) or direct uploads.

    Verification signals:
    - Repository exists and is accessible
    - Last commit is within reasonable timeframe
    - README and documentation exist
    - Code quality heuristics (structure, tests, dependencies)
    """

    source_type = EvidenceSourceType.PROJECT

    def __init__(self):
        self.logger = StructuredLogger("evidence.collector.project")

    async def collect(
        self, user_id: str, credentials: dict | None = None
    ) -> list[RawEvidence]:
        """
        In production: called with user-submitted URL or uploaded archive.
        For auto-discovery: scans user's linked GitHub repos for new projects.
        """
        # Manual submission path — user provides URL
        repo_url = credentials.get("repo_url") if credentials else None
        if repo_url:
            return [await self._collect_single(user_id, repo_url)]

        # Auto-discovery path — scan user's GitHub for new repos
        github_token = credentials.get("github_token") if credentials else None
        if github_token:
            return await self._auto_discover(user_id, github_token)

        return []

    async def _collect_single(
        self, user_id: str, repo_url: str
    ) -> RawEvidence:
        """Collect evidence from a single project URL."""
        normalized = self._normalize_url(repo_url)
        repo_data = await self._fetch_repo_metadata(normalized)

        return RawEvidence(
            source_type=self.source_type,
            user_id=user_id,
            external_id=repo_data.get("id"),
            raw_data=repo_data,
            collected_at=int(time.time() * 1000),
            credentials_used=None,
        )

    async def _auto_discover(
        self, user_id: str, github_token: str
    ) -> list[RawEvidence]:
        """
        Auto-discover new projects from user's GitHub.
        Only returns repos that haven't been collected before.
        """
        existing = await self._get_existing_repo_ids(user_id)
        repos = await self._fetch_user_repos(github_token)
        new_repos = [r for r in repos if r["id"] not in existing]

        results = []
        for repo in new_repos:
            if self._is_meaningful_project(repo):
                results.append(RawEvidence(
                    source_type=self.source_type,
                    user_id=user_id,
                    external_id=repo["id"],
                    raw_data=repo,
                    collected_at=int(time.time() * 1000),
                    credentials_used="github_auto_discover",
                ))
        return results

    async def verify(self, evidence: EvidenceItem) -> VerificationResult:
        """
        Verify a project evidence item.
        Checks: repo exists, has recent activity, has content.
        """
        repo_url = evidence.url or evidence.metadata.get("url")
        if not repo_url:
            return VerificationResult(
                evidence_id=evidence.evidence_id,
                verified=False, method="auto", confidence=0.0,
                verified_at=int(time.time() * 1000),
                details="No URL to verify", reviewer_id=None,
            )

        try:
            repo_data = await self._fetch_repo_metadata(repo_url)
            if not repo_data:
                return self._fail("Repository not found or inaccessible")

            checks = []
            # Check 1: Repository exists and is accessible
            checks.append(repo_data.get("exists", False))

            # Check 2: Has recent commit (< 2 years)
            last_push = repo_data.get("pushed_at")
            if last_push:
                days_since = (time.time() - last_push) / 86400
                checks.append(days_since < 730)

            # Check 3: Has content (README, code files)
            has_readme = repo_data.get("has_readme", False)
            has_code = repo_data.get("size", 0) > 1000
            checks.append(has_readme or has_code)

            # Check 4: Not empty or template
            is_template = repo_data.get("is_template", False)
            is_empty = repo_data.get("size", 0) == 0
            checks.append(not (is_template or is_empty))

            pass_count = sum(1 for c in checks if c)
            confidence = pass_count / len(checks)
            verified = confidence >= 0.75

            return VerificationResult(
                evidence_id=evidence.evidence_id,
                verified=verified,
                method="auto",
                confidence=confidence,
                verified_at=int(time.time() * 1000),
                details=f"Passed {pass_count}/{len(checks)} checks",
                reviewer_id=None,
            )

        except Exception as e:
            self.logger.error("Project verification failed", error=str(e))
            return self._fail(f"Verification error: {str(e)[:200]}")

    def _normalize_url(self, url: str) -> str:
        """Normalize URL to canonical form."""
        url = url.strip().rstrip("/")
        if url.startswith("github.com"):
            url = f"https://{url}"
        if not url.startswith("http"):
            url = f"https://{url}"
        return url

    async def _fetch_repo_metadata(self, url: str) -> dict:
        """Fetch repository metadata from API."""
        # In production: use GitHub/GitLab/Bitbucket API
        # Placeholder returns representative structure
        return {
            "id": "repo_123",
            "exists": True,
            "name": "project-name",
            "description": "A full-stack web application",
            "url": url,
            "language": "Python",
            "size": 50000,
            "stars": 42,
            "forks": 10,
            "has_readme": True,
            "has_wiki": True,
            "has_tests": True,
            "is_template": False,
            "is_fork": False,
            "pushed_at": time.time() - 86400 * 30,
            "created_at": time.time() - 86400 * 180,
            "license": "MIT",
            "topics": ["python", "fastapi", "react"],
        }

    def _is_meaningful_project(self, repo: dict) -> bool:
        """Filter out trivial repos (forks, templates, empty)."""
        return (
            not repo.get("fork", False)
            and not repo.get("is_template", False)
            and repo.get("size", 0) > 1000
        )

    async def _get_existing_repo_ids(self, user_id: str) -> set[str]:
        """Get IDs of already-collected repos to avoid duplicates."""
        # In production: query PostgreSQL
        return set()

    async def _fetch_user_repos(self, token: str) -> list[dict]:
        """Fetch user's GitHub repositories."""
        # In production: call GitHub API with OAuth token
        return []

    def get_metadata_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "language": {"type": "string"},
                "stars": {"type": "integer"},
                "has_tests": {"type": "boolean"},
                "description": {"type": "string"},
            },
            "required": ["url"],
        }

    def _fail(self, reason: str) -> VerificationResult:
        return VerificationResult(
            evidence_id="", verified=False, method="auto", confidence=0.0,
            verified_at=int(time.time() * 1000), details=reason, reviewer_id=None,
        )
```

### 2.4 GitHub Contribution Collector

```python
class GitHubCollector(BaseCollector):
    """
    Collects evidence from GitHub activity — commits, PRs, issues, reviews.
    Zero user effort beyond OAuth authentication.

    Data collected:
    - Commit frequency, recency, and distribution
    - Pull request volume, merge rate, review participation
    - Issue creation and commentary
    - Repository diversity (languages, ownership)
    - Contribution graphs (streaks, consistency)
    """

    source_type = EvidenceSourceType.GITHUB

    def __init__(self):
        self.logger = StructuredLogger("evidence.collector.github")

    async def collect(
        self, user_id: str, credentials: dict | None = None
    ) -> list[RawEvidence]:
        token = credentials.get("github_token") if credentials else None
        if not token:
            self.logger.warning("No GitHub token provided", user=user_id)
            return []

        try:
            user_profile = await self._fetch_user_profile(token)
            repos = await self._fetch_repos(token)
            contributions = await self._fetch_contributions(token)

            # Structure into raw evidence items
            evidences = []

            # Profile evidence
            evidences.append(RawEvidence(
                source_type=self.source_type,
                user_id=user_id,
                external_id=user_profile.get("login"),
                raw_data=user_profile,
                collected_at=int(time.time() * 1000),
                credentials_used="github_oauth",
            ))

            # Per-repo contribution evidence
            for repo in repos[:20]:  # Top 20 repos
                repo_contribs = await self._fetch_repo_contributions(token, repo["name"])
                if self._has_meaningful_contribution(repo_contribs):
                    evidences.append(RawEvidence(
                        source_type=self.source_type,
                        user_id=user_id,
                        external_id=f"{repo['name']}_{user_profile.get('login')}",
                        raw_data={**repo, "contributions": repo_contribs},
                        collected_at=int(time.time() * 1000),
                        credentials_used="github_oauth",
                    ))

            # Aggregate contribution graph evidence
            if contributions:
                evidences.append(RawEvidence(
                    source_type=self.source_type,
                    user_id=user_id,
                    external_id=f"contributions_{user_profile.get('login')}",
                    raw_data={"contributions": contributions, "profile": user_profile},
                    collected_at=int(time.time() * 1000),
                    credentials_used="github_oauth",
                ))

            return evidences

        except Exception as e:
            self.logger.error("GitHub collection failed", error=str(e))
            return []

    async def verify(self, evidence: EvidenceItem) -> VerificationResult:
        """
        Verify GitHub evidence by re-fetching the data.
        For commits: check they still exist in the repo history.
        For PRs: check they're still merged.
        """
        metadata = evidence.metadata
        if not metadata:
            return VerificationResult(
                evidence_id=evidence.evidence_id, verified=False,
                method="auto", confidence=0.0,
                verified_at=int(time.time() * 1000),
                details="No metadata to verify", reviewer_id=None,
            )

        checks = []
        profile = metadata.get("profile", {})

        # Check 1: Profile still exists
        checks.append(bool(profile.get("login")))

        # Check 2: Has public repos
        checks.append(profile.get("public_repos", 0) > 0)

        # Check 3: Recent activity (< 1 year)
        repos = metadata.get("repos", [])
        has_recent = any(
            repo.get("pushed_at") and
            (time.time() - repo["pushed_at"]) < 86400 * 365
            for repo in repos
        )
        checks.append(has_recent)

        # Check 4: Not a new/empty account
        created = profile.get("created_at")
        if created:
            account_age_days = (time.time() - created) / 86400
            checks.append(account_age_days > 30)

        pass_count = sum(1 for c in checks if c)
        confidence = pass_count / len(checks) if checks else 0.0
        verified = confidence >= 0.75

        return VerificationResult(
            evidence_id=evidence.evidence_id,
            verified=verified,
            method="auto",
            confidence=confidence,
            verified_at=int(time.time() * 1000),
            details=f"GitHub profile checks: {pass_count}/{len(checks)} passed",
            reviewer_id=None,
        )

    def _has_meaningful_contribution(self, contribs: dict) -> bool:
        return contribs.get("total_commits", 0) > 5 or contribs.get("total_prs", 0) > 2

    async def _fetch_user_profile(self, token: str) -> dict:
        return {"login": "user", "public_repos": 15, "public_gists": 3,
                "followers": 42, "following": 30, "created_at": time.time() - 86400 * 500}

    async def _fetch_repos(self, token: str) -> list[dict]:
        return []

    async def _fetch_contributions(self, token: str) -> list[dict]:
        return []

    async def _fetch_repo_contributions(self, token: str, repo: str) -> dict:
        return {"total_commits": 50, "total_prs": 10, "reviews": 5}

    def get_metadata_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "total_commits": {"type": "integer"},
                "total_prs": {"type": "integer"},
                "languages": {"type": "array", "items": {"type": "string"}},
                "contribution_streak_days": {"type": "integer"},
            },
        }
```

### 2.5 Certification Collector

```python
class CertificationCollector(BaseCollector):
    """
    Collects and verifies professional certifications.
    Supports major providers: Credly, Acclaim, Coursera, edX, AWS, Google, Microsoft, etc.

    Verification:
    - Credential ID lookup via provider API
    - Badge URL metadata scraping (Open Badges standard)
    - Expiry date validation
    - Issuer domain authentication
    """

    source_type = EvidenceSourceType.CERTIFICATION

    # Known certification provider API endpoints
    PROVIDER_APIS: dict[str, str] = {
        "credly": "https://api.credly.com/v1",
        "acclaim": "https://api.acclaim.com/v1",
        "coursera": "https://api.coursera.com/api/certifications/v1",
        "edx": "https://api.edx.org/certificates/v1",
        "aws": "https://api.aws.com/certifications/v1",
        "google": "https://www.googleapis.com/oauth2/v1",
        "microsoft": "https://learn.microsoft.com/api/certifications",
    }

    def __init__(self):
        self.logger = StructuredLogger("evidence.collector.certification")

    async def collect(
        self, user_id: str, credentials: dict | None = None
    ) -> list[RawEvidence]:
        """
        Collect certification evidence.
        User provides: credential ID + provider + (optional) badge URL.
        """
        credential_id = credentials.get("credential_id") if credentials else None
        provider = credentials.get("provider") if credentials else None
        badge_url = credentials.get("badge_url") if credentials else None

        if not credential_id:
            return []

        api_url = self.PROVIDER_APIS.get(provider)
        if not api_url and not badge_url:
            return []

        # Try API verification first
        if api_url:
            cert_data = await self._verify_via_api(api_url, credential_id)
            if cert_data:
                return [RawEvidence(
                    source_type=self.source_type,
                    user_id=user_id,
                    external_id=credential_id,
                    raw_data=cert_data,
                    collected_at=int(time.time() * 1000),
                    credentials_used=None,
                )]

        # Fallback: badge URL scraping
        if badge_url:
            badge_data = await self._scrape_badge(badge_url)
            if badge_data:
                return [RawEvidence(
                    source_type=self.source_type,
                    user_id=user_id,
                    external_id=credential_id,
                    raw_data=badge_data,
                    collected_at=int(time.time() * 1000),
                    credentials_used=None,
                )]

        return []

    async def verify(self, evidence: EvidenceItem) -> VerificationResult:
        """Re-verify certification by checking with issuer API."""
        metadata = evidence.metadata
        credential_id = metadata.get("credential_id")
        provider = metadata.get("provider")
        badge_url = metadata.get("badge_url")
        expiry = metadata.get("expiry_date")

        # Check expiry first
        if expiry:
            if time.time() > expiry:
                return VerificationResult(
                    evidence_id=evidence.evidence_id, verified=False,
                    method="auto", confidence=0.0,
                    verified_at=int(time.time() * 1000),
                    details="Certification has expired", reviewer_id=None,
                )

        # Re-verify with provider API
        api_url = self.PROVIDER_APIS.get(provider)
        if api_url and credential_id:
            result = await self._verify_via_api(api_url, credential_id)
            if result:
                return VerificationResult(
                    evidence_id=evidence.evidence_id, verified=True,
                    method="auto", confidence=0.95,
                    verified_at=int(time.time() * 1000),
                    details="Verified via provider API", reviewer_id=None,
                )

        # Badge URL fallback
        if badge_url:
            badge_data = await self._scrape_badge(badge_url)
            if badge_data and badge_data.get("verified"):
                return VerificationResult(
                    evidence_id=evidence.evidence_id, verified=True,
                    method="auto", confidence=0.80,
                    verified_at=int(time.time() * 1000),
                    details="Verified via badge URL metadata", reviewer_id=None,
                )

        return VerificationResult(
            evidence_id=evidence.evidence_id, verified=False,
            method="auto", confidence=0.0,
            verified_at=int(time.time() * 1000),
            details="Could not verify with provider API or badge URL",
            reviewer_id=None,
        )

    async def _verify_via_api(self, api_url: str, credential_id: str) -> dict | None:
        """Verify credential via provider API."""
        # In production: HTTP GET with API key
        return {
            "credential_id": credential_id,
            "verified": True,
            "issued_at": time.time() - 86400 * 100,
            "expiry_date": time.time() + 86400 * 265,
            "credential_name": "AWS Solutions Architect Associate",
            "issuer": "Amazon Web Services",
            "skills": ["aws", "cloud_architecture", "vpc", "ec2", "s3"],
        }

    async def _scrape_badge(self, url: str) -> dict | None:
        """Scrape badge metadata using Open Badges standard."""
        return {
            "badge_url": url,
            "verified": True,
            "issued_on": "2025-01-15",
            "expires": "2028-01-15",
            "badge_name": "AWS Certified Solutions Architect",
        }

    def get_metadata_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "credential_id": {"type": "string"},
                "provider": {"type": "string", "enum": list(self.PROVIDER_APIS.keys())},
                "badge_url": {"type": "string", "format": "uri"},
                "issue_date": {"type": "string", "format": "date"},
                "expiry_date": {"type": "string", "format": "date"},
                "credential_name": {"type": "string"},
            },
            "required": ["credential_id", "provider"],
        }
```

### 2.6 Hackathon Collector

```python
class HackathonCollector(BaseCollector):
    """
    Collects evidence from hackathon participation and wins.
    Sources: Devpost API, certificate uploads, manual entry.

    Verification:
    - Devpost API project lookup
    - Certificate authenticity (template + issuer check)
    - Winner list cross-referencing
    - Team member corroboration
    """

    source_type = EvidenceSourceType.HACKATHON

    def __init__(self):
        self.logger = StructuredLogger("evidence.collector.hackathon")

    async def collect(
        self, user_id: str, credentials: dict | None = None
    ) -> list[RawEvidence]:
        devpost_url = credentials.get("devpost_url") if credentials else None
        cert_image = credentials.get("certificate") if credentials else None

        evidences = []

        if devpost_url:
            project_data = await self._fetch_devpost_project(devpost_url)
            if project_data:
                evidences.append(RawEvidence(
                    source_type=self.source_type, user_id=user_id,
                    external_id=project_data.get("id"),
                    raw_data=project_data,
                    collected_at=int(time.time() * 1000),
                    credentials_used=None,
                ))

        if cert_image:
            cert_data = await self._parse_certificate(cert_image)
            if cert_data:
                evidences.append(RawEvidence(
                    source_type=self.source_type, user_id=user_id,
                    external_id=cert_data.get("certificate_id", uuid.uuid4().hex),
                    raw_data=cert_data,
                    collected_at=int(time.time() * 1000),
                    credentials_used=None,
                ))

        return evidences

    async def verify(self, evidence: EvidenceItem) -> VerificationResult:
        """Verify hackathon evidence."""
        url = evidence.url or evidence.metadata.get("devpost_url")
        if url:
            project = await self._fetch_devpost_project(url)
            if project:
                return VerificationResult(
                    evidence_id=evidence.evidence_id, verified=True,
                    method="auto", confidence=0.9,
                    verified_at=int(time.time() * 1000),
                    details="Verified via Devpost API", reviewer_id=None,
                )

        return VerificationResult(
            evidence_id=evidence.evidence_id, verified=False,
            method="auto", confidence=0.0,
            verified_at=int(time.time() * 1000),
            details="Could not verify hackathon evidence", reviewer_id=None,
        )

    async def _fetch_devpost_project(self, url: str) -> dict | None:
        return {
            "id": "hp_123", "title": "AI Chat Assistant",
            "url": url, "prize": "First Place",
            "event": "HackMIT 2025", "date": "2025-09-15",
            "team_size": 4, "technologies": ["python", "fastapi", "react"],
        }

    async def _parse_certificate(self, image: str) -> dict | None:
        # In production: OCR + template matching
        return {"certificate_id": "cert_123", "event": "HackMIT 2025",
                "rank": "1st Place", "issued_by": "MIT"}

    def get_metadata_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "event_name": {"type": "string"},
                "date": {"type": "string"},
                "prize": {"type": "string"},
                "devpost_url": {"type": "string"},
                "team_size": {"type": "integer"},
                "technologies": {"type": "array", "items": {"type": "string"}},
            },
        }
```

### 2.7 Freelance Collector

```python
class FreelanceCollector(BaseCollector):
    """
    Collects evidence from freelance and contract work.
    Sources: Upwork API, Fiverr API, contract uploads, invoice validation.

    Verification:
    - Platform API verification (Upwork contract status)
    - Client reference checks
    - Invoice payment verification
    - Contract document authenticity
    """

    source_type = EvidenceSourceType.FREELANCE

    PLATFORM_APIS: dict[str, str] = {
        "upwork": "https://www.upwork.com/api/v3",
        "fiverr": "https://api.fiverr.com/v1",
        "freelancer": "https://api.freelancer.com/v1",
        "toptal": "https://api.toptal.com/v1",
    }

    def __init__(self):
        self.logger = StructuredLogger("evidence.collector.freelance")

    async def collect(
        self, user_id: str, credentials: dict | None = None
    ) -> list[RawEvidence]:
        """Collect freelance evidence from platform API or manual entry."""
        platform = credentials.get("platform") if credentials else None
        platform_token = credentials.get("platform_token") if credentials else None
        contract_id = credentials.get("contract_id") if credentials else None

        evidences = []

        # Platform API collection
        if platform and platform_token and contract_id:
            contract_data = await self._fetch_contract(
                platform, platform_token, contract_id
            )
            if contract_data:
                evidences.append(RawEvidence(
                    source_type=self.source_type, user_id=user_id,
                    external_id=contract_id,
                    raw_data=contract_data,
                    collected_at=int(time.time() * 1000),
                    credentials_used=f"{platform}_token",
                ))

        # Manual entry with invoice
        invoice_data = credentials.get("invoice") if credentials else None
        if invoice_data:
            evidences.append(RawEvidence(
                source_type=self.source_type, user_id=user_id,
                external_id=uuid.uuid4().hex,
                raw_data=invoice_data,
                collected_at=int(time.time() * 1000),
                credentials_used=None,
            ))

        return evidences

    async def verify(self, evidence: EvidenceItem) -> VerificationResult:
        """Verify freelance evidence via platform API or client reference."""
        metadata = evidence.metadata
        platform = metadata.get("platform")
        contract_id = metadata.get("contract_id")
        client_contact = metadata.get("client_reference")

        # Platform API verification
        if platform and contract_id:
            api_url = self.PLATFORM_APIS.get(platform)
            if api_url:
                result = await self._check_contract_status(api_url, contract_id)
                if result:
                    return VerificationResult(
                        evidence_id=evidence.evidence_id, verified=True,
                        method="auto", confidence=0.9,
                        verified_at=int(time.time() * 1000),
                        details=f"Verified via {platform} API", reviewer_id=None,
                    )

        # Client reference verification (AI or human)
        if client_contact:
            return VerificationResult(
                evidence_id=evidence.evidence_id, verified=True,
                method="ai", confidence=0.6,
                verified_at=int(time.time() * 1000),
                details="Awaiting client reference confirmation", reviewer_id=None,
            )

        return VerificationResult(
            evidence_id=evidence.evidence_id, verified=False,
            method="auto", confidence=0.0,
            verified_at=int(time.time() * 1000),
            details="Could not verify freelance evidence", reviewer_id=None,
        )

    async def _fetch_contract(self, platform: str, token: str, contract_id: str) -> dict | None:
        return {"contract_id": contract_id, "title": "Web App Development",
                "client": "Acme Corp", "amount": 5000, "currency": "USD",
                "status": "completed", "skills": ["react", "node", "postgresql"],
                "start_date": "2025-01-15", "end_date": "2025-04-15"}

    async def _check_contract_status(self, api_url: str, contract_id: str) -> dict | None:
        return {"status": "completed", "payment_verified": True}

    def get_metadata_schema(self) -> dict:
        return {"type": "object", "properties": {
            "platform": {"type": "string", "enum": list(self.PLATFORM_APIS.keys())},
            "contract_id": {"type": "string"},
            "client_name": {"type": "string"},
            "amount": {"type": "number"},
            "start_date": {"type": "string"}, "end_date": {"type": "string"},
            "skills_used": {"type": "array", "items": {"type": "string"}},
        }, "required": ["platform", "contract_id"]}
```

### 2.8 Open Source Collector

```python
class OSSCollector(BaseCollector):
    """
    Collects evidence from open source contributions.
    Extends GitHub collector with OSS-specific analysis.

    Metrics:
    - Merged PRs with review quality
    - Maintainer status (owner, committer, contributor)
    - Repository popularity (stars, forks, dependents)
    - Code review participation
    - Issue triage and community management
    - Longevity and consistency of contributions
    """

    source_type = EvidenceSourceType.OPENSOURCE

    def __init__(self):
        self.logger = StructuredLogger("evidence.collector.oss")

    async def collect(
        self, user_id: str, credentials: dict | None = None
    ) -> list[RawEvidence]:
        token = credentials.get("github_token") if credentials else None
        if not token:
            return []

        oss_repos = await self._identify_oss_repos(token)
        evidences = []

        for repo in oss_repos[:30]:
            contribs = await self._analyze_oss_contribution(token, repo)
            if self._is_significant_contribution(contribs):
                evidences.append(RawEvidence(
                    source_type=self.source_type, user_id=user_id,
                    external_id=f"{repo['name']}_{user_id}",
                    raw_data={**repo, "contribution_analysis": contribs},
                    collected_at=int(time.time() * 1000),
                    credentials_used="github_oauth",
                ))

        return evidences

    async def verify(self, evidence: EvidenceItem) -> VerificationResult:
        """Verify OSS contribution via GitHub API."""
        metadata = evidence.metadata
        repo = metadata.get("name")

        if not repo:
            return VerificationResult(evidence_id=evidence.evidence_id,
                verified=False, method="auto", confidence=0.0,
                verified_at=int(time.time() * 1000),
                details="No repository name", reviewer_id=None)

        checks = []
        checks.append(metadata.get("fork_count", 0) >= 0)
        checks.append(metadata.get("merged_prs", 0) > 0)
        checks.append(metadata.get("contribution_period_days", 0) > 30)
        pass_count = sum(1 for c in checks if c)
        confidence = pass_count / len(checks)

        return VerificationResult(evidence_id=evidence.evidence_id,
            verified=confidence >= 0.5, method="auto", confidence=confidence,
            verified_at=int(time.time() * 1000),
            details=f"OSS checks: {pass_count}/{len(checks)}", reviewer_id=None)

    def _is_significant_contribution(self, contribs: dict) -> bool:
        return (contribs.get("merged_prs", 0) >= 3
                or contribs.get("role") in ("maintainer", "committer")
                or contribs.get("total_commits", 0) >= 20)

    async def _identify_oss_repos(self, token: str) -> list[dict]:
        return []

    async def _analyze_oss_contribution(self, token: str, repo: dict) -> dict:
        return {"merged_prs": 15, "total_commits": 100, "reviews_given": 30,
                "role": "committer", "contribution_period_days": 365,
                "issues_closed": 20, "code_reviews": 25}

    def get_metadata_schema(self) -> dict:
        return {"type": "object", "properties": {
            "repo_name": {"type": "string"}, "role": {"type": "string"},
            "merged_prs": {"type": "integer"}, "total_commits": {"type": "integer"},
            "stars": {"type": "integer"}, "forks": {"type": "integer"},
            "first_contribution": {"type": "string"},
            "last_contribution": {"type": "string"},
        }, "required": ["repo_name"]}
```

### 2.9 Assessment Collector

```python
class AssessmentCollector(BaseCollector):
    """
    Collects evidence from the SkillAssessment Engine (§ SkillAssessment.md).
    Assessment results are automatically imported as evidence.

    This is the bridge between assessment and evidence systems.
    Every completed assessment generates a structured evidence item.
    """

    source_type = EvidenceSourceType.ASSESSMENT

    def __init__(self):
        self.logger = StructuredLogger("evidence.collector.assessment")

    async def collect(
        self, user_id: str, credentials: dict | None = None
    ) -> list[RawEvidence]:
        """
        Import assessment results as evidence.
        Called by webhook when an assessment completes (§ SkillAssessment.md 9.2).
        """
        assessment_result = credentials.get("validation_result") if credentials else None
        if not assessment_result:
            return []

        return [RawEvidence(
            source_type=self.source_type,
            user_id=user_id,
            external_id=assessment_result.get("session_id"),
            raw_data=assessment_result,
            collected_at=int(time.time() * 1000),
            credentials_used="assessment_engine",
        )]

    async def verify(self, evidence: EvidenceItem) -> VerificationResult:
        """
        Assessment evidence is already verified by the validation pipeline.
        Re-verify: check the cryptographic signature from the assessment engine.
        """
        signature = evidence.metadata.get("signature")
        session_id = evidence.metadata.get("session_id")
        score = evidence.metadata.get("final_score")
        level = evidence.metadata.get("final_level")

        if not signature or not session_id:
            return VerificationResult(evidence_id=evidence.evidence_id,
                verified=False, method="auto", confidence=0.0,
                verified_at=int(time.time() * 1000),
                details="Missing signature or session ID", reviewer_id=None)

        # Verify the assessment engine signature
        # In production: verify HMAC-SHA256
        is_valid = self._verify_signature(session_id, score, level, signature)

        return VerificationResult(evidence_id=evidence.evidence_id,
            verified=is_valid, method="auto", confidence=1.0 if is_valid else 0.0,
            verified_at=int(time.time() * 1000),
            details="Assessment signature verified" if is_valid else "Invalid signature",
            reviewer_id=None)

    def _verify_signature(self, session_id: str, score: float, level: int, signature: str) -> bool:
        """Verify the cryptographic signature from the assessment engine."""
        import hashlib
        expected = hashlib.sha256(f"{session_id}|{score}|{level}".encode()).hexdigest()[:16]
        return signature == expected

    def get_metadata_schema(self) -> dict:
        return {"type": "object", "properties": {
            "session_id": {"type": "string"}, "method": {"type": "string"},
            "final_score": {"type": "number"}, "final_level": {"type": "integer"},
            "confidence": {"type": "number"}, "signature": {"type": "string"},
            "rubric_scores": {"type": "object"},
        }, "required": ["session_id", "final_score", "signature"]}
```

### 2.10 Work Experience Collector

```python
class WorkExperienceCollector(BaseCollector):
    """
    Collects evidence from professional work experience.
    Sources: LinkedIn API, resume upload, offer letter verification.

    Verification:
    - LinkedIn profile employment history API
    - Offer letter document verification
    - Company email domain verification
    - LinkedIn endorsement cross-check
    - Employment verification service (e.g., TrueWork)
    """

    source_type = EvidenceSourceType.WORK_EXPERIENCE

    def __init__(self):
        self.logger = StructuredLogger("evidence.collector.work_exp")

    async def collect(
        self, user_id: str, credentials: dict | None = None
    ) -> list[RawEvidence]:
        linkedin_token = credentials.get("linkedin_token") if credentials else None
        resume_data = credentials.get("resume") if credentials else None

        evidences = []

        # LinkedIn API collection
        if linkedin_token:
            positions = await self._fetch_linkedin_positions(linkedin_token)
            for pos in positions:
                evidences.append(RawEvidence(
                    source_type=self.source_type, user_id=user_id,
                    external_id=pos.get("id"),
                    raw_data=pos, collected_at=int(time.time() * 1000),
                    credentials_used="linkedin_oauth",
                ))

        # Resume parsing
        if resume_data:
            parsed = await self._parse_resume(resume_data)
            for exp in parsed.get("experiences", []):
                evidences.append(RawEvidence(
                    source_type=self.source_type, user_id=user_id,
                    external_id=uuid.uuid4().hex,
                    raw_data=exp, collected_at=int(time.time() * 1000),
                    credentials_used=None,
                ))

        return evidences

    async def verify(self, evidence: EvidenceItem) -> VerificationResult:
        """Verify work experience via LinkedIn API or company verification."""
        metadata = evidence.metadata
        company = metadata.get("company")
        title = metadata.get("title")

        if not company:
            return VerificationResult(evidence_id=evidence.evidence_id,
                verified=False, method="auto", confidence=0.0,
                verified_at=int(time.time() * 1000),
                details="No company name", reviewer_id=None)

        # LinkedIn API check
        if metadata.get("linkedin_id"):
            return VerificationResult(evidence_id=evidence.evidence_id,
                verified=True, method="auto", confidence=0.85,
                verified_at=int(time.time() * 1000),
                details="Confirmed via LinkedIn API", reviewer_id=None)

        # Company email domain verification
        work_email = metadata.get("work_email")
        if work_email and self._verify_email_domain(work_email, company):
            return VerificationResult(evidence_id=evidence.evidence_id,
                verified=True, method="auto", confidence=0.75,
                verified_at=int(time.time() * 1000),
                details=f"Verified email domain: {work_email.split('@')[1]}", reviewer_id=None)

        # Fallback to AI review
        return VerificationResult(evidence_id=evidence.evidence_id,
            verified=False, method="ai", confidence=0.5,
            verified_at=int(time.time() * 1000),
            details="Pending AI review of supporting documents", reviewer_id=None)

    def _verify_email_domain(self, email: str, company: str) -> bool:
        """Verify that email domain matches known company domains."""
        known_domains = {
            "google": ["google.com", "gmail.com"],
            "microsoft": ["microsoft.com"],
            "amazon": ["amazon.com"],
            # In production: maintain a domain→company lookup table
        }
        domain = email.split("@")[1].lower() if "@" in email else ""
        company_key = company.lower().replace(" ", "")
        return any(
            domain == d
            for c, domains in known_domains.items()
            if c in company_key
            for d in domains
        )

    async def _fetch_linkedin_positions(self, token: str) -> list[dict]:
        return [{"id": "pos_1", "company": "Acme Corp", "title": "Software Engineer",
                 "start_date": "2023-01", "end_date": "2025-06",
                 "description": "Built microservices architecture",
                 "skills_used": ["python", "aws", "kubernetes"]}]

    async def _parse_resume(self, resume: str) -> dict:
        return {"experiences": []}

    def get_metadata_schema(self) -> dict:
        return {"type": "object", "properties": {
            "company": {"type": "string"}, "title": {"type": "string"},
            "start_date": {"type": "string"}, "end_date": {"type": "string"},
            "linkedin_id": {"type": "string"},
            "work_email": {"type": "string", "format": "email"},
            "description": {"type": "string"},
        }, "required": ["company", "title"]}
```

### 2.11 Auto-Discovery Engine

```python
class AutoDiscoveryEngine:
    """
    ARIA proactively discovers evidence without user submission.

    Discovery modes (per-tenant configurable):
    - AUTO_IMPORT: ARIA discovers, imports, and notifies. User can reject within 7 days.
    - CONFIRM_FIRST: ARIA discovers and notifies. Only imports after user approves.

    Discovery sources:
    1. GitHub: new repos, new contributions, new stars
    2. LinkedIn: new position, new endorsements
    3. Certification platforms: new badges (via webhook or periodic check)
    4. Upwork/Fiverr: new completed contracts
    5. Devpost: new hackathon participations
    6. Package registries: npm, PyPI, crates.io — new package publications
    7. Blog/Publication platforms: Medium, Dev.to, Substack — new articles
    """

    def __init__(self, tenant_config: TenantConfig | None = None):
        self.logger = StructuredLogger("evidence.auto_discovery")
        self.mode = (
            tenant_config.settings.evidence_auto_discovery_mode
            if tenant_config else AutoDiscoveryMode.CONFIRM_FIRST
        )
        self.discovery_schedule = {
            "github": 3600,       # Every hour
            "linkedin": 86400,    # Daily
            "certifications": 86400,
            "freelance": 43200,   # Twice daily
            "hackathons": 86400,
            "registries": 43200,  # npm, PyPI, etc.
        }

    async def scan(self, user_id: str, linked_accounts: dict) -> list[DiscoveredEvidence]:
        """
        Run a full auto-discovery scan for a user.
        Called by cron schedule or on-demand.
        """
        discovered: list[DiscoveredEvidence] = []

        # GitHub scan
        if "github" in linked_accounts:
            gh_evidence = await self._scan_github(
                user_id, linked_accounts["github"]["token"],
                linked_accounts["github"].get("last_scan"),
            )
            discovered.extend(gh_evidence)

        # LinkedIn scan
        if "linkedin" in linked_accounts:
            li_evidence = await self._scan_linkedin(
                user_id, linked_accounts["linkedin"]["token"],
            )
            discovered.extend(li_evidence)

        # Certification scan (check for new badges)
        if "certifications" in linked_accounts:
            cert_evidence = await self._scan_certifications(
                user_id, linked_accounts["certifications"],
            )
            discovered.extend(cert_evidence)

        # Filter out already-collected evidence
        new_evidence = await self._filter_existing(discovered)

        if self.mode == AutoDiscoveryMode.AUTO_IMPORT:
            return await self._auto_import(user_id, new_evidence)
        else:
            return await self._notify_for_approval(user_id, new_evidence)

    async def _scan_github(
        self, user_id: str, token: str, last_scan: int | None
    ) -> list[DiscoveredEvidence]:
        """Scan GitHub for new contributions since last scan."""
        collector = GitHubCollector()
        raw = await collector.collect(user_id, {"github_token": token})

        discovered = []
        for item in raw:
            # Check if this is new since last scan
            repo_created = item.raw_data.get("created_at", 0)
            if last_scan and repo_created < last_scan:
                continue
            discovered.append(DiscoveredEvidence(
                source=EvidenceSourceType.GITHUB,
                user_id=user_id,
                title=item.raw_data.get("name", "GitHub Activity"),
                description=f"Auto-discovered GitHub activity",
                suggested_skills=self._infer_skills_from_repo(item.raw_data),
                confidence=0.7,
                raw_data=item.raw_data,
            ))

        return discovered

    async def _scan_linkedin(
        self, user_id: str, token: str
    ) -> list[DiscoveredEvidence]:
        """Scan LinkedIn for new positions."""
        collector = WorkExperienceCollector()
        raw = await collector.collect(user_id, {"linkedin_token": token})
        return [
            DiscoveredEvidence(
                source=EvidenceSourceType.WORK_EXPERIENCE,
                user_id=user_id,
                title=f"{r.raw_data.get('title', 'Position')} @ {r.raw_data.get('company', 'Company')}",
                description=r.raw_data.get("description", ""),
                suggested_skills=r.raw_data.get("skills_used", []),
                confidence=0.8,
                raw_data=r.raw_data,
            )
            for r in raw
        ]

    async def _scan_certifications(
        self, user_id: str, cert_accounts: dict
    ) -> list[DiscoveredEvidence]:
        """Check for new certifications from connected accounts."""
        discovered = []
        collector = CertificationCollector()

        for provider, account_data in cert_accounts.items():
            raw = await collector.collect(user_id, {
                "provider": provider,
                "credential_id": account_data.get("last_credential_id"),
            })
            discovered.extend([
                DiscoveredEvidence(
                    source=EvidenceSourceType.CERTIFICATION,
                    user_id=user_id,
                    title=r.raw_data.get("credential_name", "Certification"),
                    description=f"Auto-discovered {provider} certification",
                    suggested_skills=r.raw_data.get("skills", []),
                    confidence=0.9,
                    raw_data=r.raw_data,
                )
                for r in raw
            ])

        return discovered

    async def _filter_existing(
        self, discovered: list[DiscoveredEvidence]
    ) -> list[DiscoveredEvidence]:
        """Remove evidence that's already been collected."""
        # In production: query PostgreSQL for existing evidence
        return discovered

    async def _auto_import(
        self, user_id: str, evidence: list[DiscoveredEvidence]
    ) -> list[DiscoveredEvidence]:
        """Auto-import mode: immediately create EvidenceItems."""
        for item in evidence:
            await self._create_evidence_item(user_id, item)
            self.logger.info("Auto-imported evidence", user=user_id, title=item.title)
        return evidence

    async def _notify_for_approval(
        self, user_id: str, evidence: list[DiscoveredEvidence]
    ) -> list[DiscoveredEvidence]:
        """Confirm-first mode: notify and wait for approval."""
        for item in evidence:
            # Create notification with accept/reject/remind buttons
            item.status = "pending_approval"
            item.notification_id = await self._send_approval_notification(user_id, item)
            self.logger.info("Pending approval notification sent", user=user_id, title=item.title)
        return evidence

    def _infer_skills_from_repo(self, repo: dict) -> list[str]:
        """Infer skills from repository metadata."""
        skills = []
        language = repo.get("language")
        if language:
            skills.append(language.lower())
        topics = repo.get("topics", [])
        skills.extend(t.lower() for t in topics)
        return skills

    async def _create_evidence_item(self, user_id: str, discovered: DiscoveredEvidence) -> str:
        """Create a new EvidenceItem in the database."""
        # In production: INSERT into PostgreSQL
        return uuid.uuid4().hex

    async def _send_approval_notification(self, user_id: str, item: DiscoveredEvidence) -> str:
        """Send push/email notification asking user to approve evidence."""
        return f"notif_{uuid.uuid4().hex[:8]}"


class AutoDiscoveryMode(str, Enum):
    AUTO_IMPORT = "auto_import"
    CONFIRM_FIRST = "confirm_first"


@dataclass
class DiscoveredEvidence:
    source: EvidenceSourceType
    user_id: str
    title: str
    description: str
    suggested_skills: list[str]
    confidence: float
    raw_data: dict
    status: str = "discovered"
    notification_id: str | None = None
```

### 2.12 Collection Scheduler

```python
class CollectionScheduler:
    """
    Manages the schedule for evidence collection runs.
    Each source type has a configurable collection frequency.
    Supports backpressure and rate limiting per source API.
    """

    def __init__(self, registry: SourceAdapterRegistry):
        self.registry = registry
        self.logger = StructuredLogger("evidence.scheduler")
        self.collectors: dict[EvidenceSourceType, BaseCollector] = {}
        self.last_run: dict[str, float] = {}
        self.default_schedule: dict[EvidenceSourceType, int] = {
            EvidenceSourceType.GITHUB: 3600,           # Every hour
            EvidenceSourceType.PROJECT: 86400,          # Daily
            EvidenceSourceType.CERTIFICATION: 43200,    # Twice daily
            EvidenceSourceType.HACKATHON: 86400,
            EvidenceSourceType.FREELANCE: 43200,
            EvidenceSourceType.OPENSOURCE: 3600,
            EvidenceSourceType.ASSESSMENT: 0,           # Event-triggered, not scheduled
            EvidenceSourceType.WORK_EXPERIENCE: 86400,
        }

    async def run_collection(
        self, user_id: str, source_type: EvidenceSourceType,
        credentials: dict | None = None
    ) -> EvidenceCollectionResult:
        """Run collection for a specific source type."""
        collector = self.registry.get_adapter(source_type)
        source_key = f"{user_id}:{source_type.value}"

        # Rate limit check
        last = self.last_run.get(source_key, 0)
        min_interval = self.default_schedule.get(source_type, 3600)
        if time.time() - last < min_interval:
            return EvidenceCollectionResult(
                source=source_type, items_collected=0, items_new=0,
                items_updated=0, items_failed=0, errors=["Rate limited"],
                collected_at=int(time.time() * 1000),
            )

        self.last_run[source_key] = time.time()

        try:
            raw_items = await collector.collect(user_id, credentials)
            processed = await self._process_raw_items(raw_items, collector)

            return EvidenceCollectionResult(
                source=source_type,
                items_collected=len(raw_items),
                items_new=processed["new"],
                items_updated=processed["updated"],
                items_failed=processed["failed"],
                errors=processed["errors"],
                collected_at=int(time.time() * 1000),
            )

        except Exception as e:
            self.logger.error("Collection failed", source=source_type.value, error=str(e))
            return EvidenceCollectionResult(
                source=source_type, items_collected=0, items_new=0,
                items_updated=0, items_failed=0, errors=[str(e)],
                collected_at=int(time.time() * 1000),
            )

    async def _process_raw_items(
        self, raw_items: list[RawEvidence], collector: BaseCollector
    ) -> dict:
        """Process raw items through normalizer and enricher."""
        new = 0
        updated = 0
        failed = 0
        errors = []

        for item in raw_items:
            try:
                # Normalize: convert source-specific format to canonical
                normalized = await self._normalize(item, collector)
                # Enrich: infer skills, extract metadata
                enriched = await self._enrich(normalized)
                # Persist to database
                await self._persist(enriched)
                new += 1
            except Exception as e:
                failed += 1
                errors.append(str(e)[:200])

        return {"new": new, "updated": updated, "failed": failed, "errors": errors}

    async def _normalize(self, raw: RawEvidence, collector: BaseCollector) -> EvidenceItem:
        """Normalize raw evidence to canonical EvidenceItem."""
        return EvidenceItem(
            evidence_id=uuid.uuid4().hex,
            user_id=raw.user_id,
            skill_ids=[],
            source_type=raw.source_type,
            state=EvidenceState.RAW,
            title=raw.raw_data.get("title") or raw.raw_data.get("name") or raw.source_type.value,
            description=raw.raw_data.get("description", ""),
            url=raw.raw_data.get("url") or raw.raw_data.get("html_url"),
            metadata=raw.raw_data,
            collected_at=raw.collected_at,
            verified_at=None,
            verification_method=None,
            quality_score=0.0,
            trust_score=0.0,
            weight=0.0,
            fraud_signals=[],
            signed_hash=self._hash(raw),
            previous_hash=None,
            created_at=int(time.time() * 1000),
            updated_at=int(time.time() * 1000),
        )

    async def _enrich(self, item: EvidenceItem) -> EvidenceItem:
        """Enrich evidence with inferred data (skills, quality estimate)."""
        # Infer skills from metadata
        inferred_skills = self._infer_skills(item)
        item.skill_ids = inferred_skills
        # Estimate initial quality score from metadata signals
        item.quality_score = self._estimate_base_quality(item)
        return item

    def _infer_skills(self, item: EvidenceItem) -> list[str]:
        """Infer skills from evidence metadata."""
        skills = []
        meta = item.metadata
        if item.source_type == EvidenceSourceType.GITHUB:
            lang = meta.get("language")
            if lang:
                skills.append(lang.lower())
            skills.extend(t.lower() for t in meta.get("topics", []))
        elif item.source_type == EvidenceSourceType.CERTIFICATION:
            skills.extend(s.lower() for s in meta.get("skills", []))
        elif item.source_type == EvidenceSourceType.PROJECT:
            skills.extend(s.lower() for s in meta.get("technologies", []))
        return skills

    def _estimate_base_quality(self, item: EvidenceItem) -> float:
        """Estimate initial quality score from metadata signals."""
        # In production: use more sophisticated heuristics
        return 0.5

    def _hash(self, raw: RawEvidence) -> str:
        import hashlib
        payload = f"{raw.user_id}|{raw.source_type.value}|{raw.external_id}|{raw.collected_at}|{json.dumps(raw.raw_data, sort_keys=True)}"
        return hashlib.sha256(payload.encode()).hexdigest()

    async def _persist(self, item: EvidenceItem) -> None:
        """Persist EvidenceItem to PostgreSQL."""
        # In production: INSERT into evidence_items table
        pass
```


---
## 3. Verification Model

### 3.1 Verification Architecture

The Verification Model is the second stage of the Evidence Processing Layer. After collection normalizes raw evidence into canonical `EvidenceItem` objects, the Verification Model determines **authenticity, accuracy, and completeness** through a three-tier escalation system.

```
                        ┌─────────────────────────┐
                        │   COLLECTED EVIDENCE      │
                        │   (state: RAW)            │
                        └──────────┬────────────────┘
                                   ▼
                    ┌──────────────────────────────┐
                    │    TIER 1: AUTO VERIFICATION  │
                    │  (algorithmic checks, no AI)  │
                    │  • Source accessibility       │
                    │  • Metadata consistency        │
                    │  • Format validation           │
                    │  • Signature verification     │
                    │  • Anti-tamper hash check     │
                    └──────────┬───────────────────┘
                               │
                    ┌──────────▼───────────────────┐
                    │  Auto confidence ≥ threshold? │
                    └──────────┬───────────────────┘
                    YES        │        NO
                    ┌──────────▼──────────┐
                    │  VERIFIED (auto)    │
                    │  state: VERIFIED    │
                    └─────────────────────┘
                               │
                               ▼
                    ┌──────────────────────────────┐
                    │    TIER 2: AI VERIFICATION    │
                    │  (LLM-based authenticity)     │
                    │  • Content analysis           │
                    │  • Anomaly detection          │
                    │  • Cross-reference checks     │
                    │  • Inconsistency flagging     │
                    └──────────┬───────────────────┘
                               │
                    ┌──────────▼───────────────────┐
                    │  AI confidence ≥ threshold?   │
                    └──────────┬───────────────────┘
                    YES        │        NO
                    ┌──────────▼──────────┐
                    │  VERIFIED (ai)      │
                    │  state: VERIFIED    │
                    └─────────────────────┘
                               │
                               ▼
                    ┌──────────────────────────────┐
                    │  TIER 3: HUMAN VERIFICATION   │
                    │  (expert review queue)        │
                    │  • Manual document check      │
                    │  • Source contact verification│
                    │  • Domain expert review       │
                    └──────────┬───────────────────┘
                               │
                    ┌──────────▼───────────────────┐
                    │  VERIFIED (human) / REJECTED  │
                    └───────────────────────────────┘
```

### 3.2 Verification State Machine

Evidence transitions through verification states independently of the main evidence lifecycle:

```python
@dataclass
class VerificationState:
    """Verification-specific state machine (orthogonal to EvidenceState)."""
    evidence_id: str
    current_tier: int                  # 1=auto, 2=ai, 3=human
    auto_result: VerificationAttempt | None = None
    ai_result: VerificationAttempt | None = None
    human_result: VerificationAttempt | None = None
    final_status: VerificationStatus = VerificationStatus.PENDING
    escalations: int = 0               # Number of tier escalations
    last_verified_at: int | None = None
    expires_at: int | None = None      # Re-verification deadline


class VerificationStatus(str, Enum):
    PENDING = "pending"                 # Not yet verified
    VERIFIED_AUTO = "verified_auto"     # Passed Tier 1
    VERIFIED_AI = "verified_ai"        # Passed Tier 2
    VERIFIED_HUMAN = "verified_human"   # Passed Tier 3
    REJECTED_AUTO = "rejected_auto"     # Failed Tier 1
    REJECTED_AI = "rejected_ai"        # Failed Tier 2
    REJECTED_HUMAN = "rejected_human"   # Failed Tier 3
    EXPIRED = "expired"                # Needs re-verification
    INCONCLUSIVE = "inconclusive"       # Needs human review


@dataclass
class VerificationAttempt:
    """Record of a single verification attempt at one tier."""
    tier: int
    status: VerificationStatus
    confidence: float                   # 0.0-1.0
    checks_passed: int
    checks_total: int
    details: str
    performed_by: str                  # "auto" | "ai:model_name" | "human:user_id"
    performed_at: int
    duration_ms: int
    evidence_hash: str                 # Hash of evidence at time of verification
```

### 3.3 Verification Dispatcher

The dispatcher routes each evidence item through the appropriate verification pipeline based on source type, quality tier, and tenant configuration.

```python
class VerificationDispatcher:
    """
    Routes evidence through the 3-tier verification pipeline.
    Each tier is attempted; if confidence is insufficient, it escalates.
    """

    def __init__(self, config: VerificationConfig | None = None):
        self.logger = StructuredLogger("evidence.verifier.dispatcher")
        self.config = config or VerificationConfig()
        self.auto_verifiers: dict[EvidenceSourceType, AutoVerifier] = {}
        self.ai_validator: AIEvidenceValidator | None = None
        self.human_review_queue: HumanReviewQueue | None = None

    async def verify(
        self, item: EvidenceItem, context: VerificationContext
    ) -> VerificationState:
        """
        Execute the full verification pipeline for one evidence item.
        Returns the final VerificationState after all applicable tiers.
        """
        state = VerificationState(evidence_id=item.evidence_id)
        start = time.time()

        # Tier 1: Auto verification (always attempted first)
        state.auto_result = await self._run_auto_verification(item, context)
        state.current_tier = 1

        if state.auto_result.confidence >= self.config.auto_threshold:
            state.final_status = VerificationStatus.VERIFIED_AUTO
            state.last_verified_at = int(time.time() * 1000)
            state.expires_at = self._compute_expiry(item, state.final_status)
            return state

        # Tier 2: AI verification (if auto inconclusive and AI available)
        if self.ai_validator and context.ai_enabled:
            state.ai_result = await self._run_ai_verification(item, context)
            state.current_tier = 2
            state.escalations += 1

            if state.ai_result.confidence >= self.config.ai_threshold:
                state.final_status = VerificationStatus.VERIFIED_AI
                state.last_verified_at = int(time.time() * 1000)
                state.expires_at = self._compute_expiry(item, state.final_status)
                return state

        # Tier 3: Human review (if AI unavailable or inconclusive)
        if self.human_review_queue:
            state.human_result = await self._queue_human_review(item, context)
            state.current_tier = 3
            state.escalations += 1
            state.final_status = VerificationStatus.PENDING  # Awaiting human
        else:
            state.final_status = VerificationStatus.INCONCLUSIVE

        duration = int((time.time() - start) * 1000)

        self.logger.info(
            "Verification pipeline completed",
            evidence_id=item.evidence_id,
            final_status=state.final_status.value,
            tier=state.current_tier,
            escalations=state.escalations,
            duration_ms=duration,
        )

        return state

    async def _run_auto_verification(
        self, item: EvidenceItem, context: VerificationContext
    ) -> VerificationAttempt:
        """
        Run automated algorithmic checks against the evidence.
        No LLM involved — purely deterministic verification.
        """
        start = time.time()
        verifier = self.auto_verifiers.get(item.source_type, GenericAutoVerifier())
        result = await verifier.verify(item, context)
        duration = int((time.time() - start) * 1000)

        return VerificationAttempt(
            tier=1,
            status=VerificationStatus.VERIFIED_AUTO if result.verified
                   else VerificationStatus.REJECTED_AUTO,
            confidence=result.confidence,
            checks_passed=result.checks_passed,
            checks_total=result.checks_total,
            details=result.details,
            performed_by="auto",
            performed_at=int(time.time() * 1000),
            duration_ms=duration,
            evidence_hash=item.signed_hash,
        )

    async def _run_ai_verification(
        self, item: EvidenceItem, context: VerificationContext
    ) -> VerificationAttempt:
        """Run AI-based authenticity and consistency verification."""
        start = time.time()
        result = await self.ai_validator.authenticate(item, context)
        duration = int((time.time() - start) * 1000)

        return VerificationAttempt(
            tier=2,
            status=VerificationStatus.VERIFIED_AI if result.verified
                   else VerificationStatus.REJECTED_AI,
            confidence=result.confidence,
            checks_passed=result.checks_passed if hasattr(result, 'checks_passed') else 1,
            checks_total=result.checks_total if hasattr(result, 'checks_total') else 1,
            details=result.explanation,
            performed_by=f"ai:{self.config.ai_model}",
            performed_at=int(time.time() * 1000),
            duration_ms=duration,
            evidence_hash=item.signed_hash,
        )

    async def _queue_human_review(
        self, item: EvidenceItem, context: VerificationContext
    ) -> VerificationAttempt:
        """Queue evidence for human expert review."""
        review_id = await self.human_review_queue.enqueue(
            evidence_id=item.evidence_id,
            reason=f"Auto (conf={context.auto_confidence:.2f}) and AI verification insufficient" if context.ai_enabled
                   else f"Auto verification insufficient (conf={context.auto_confidence:.2f})",
            priority=self._compute_human_priority(item),
            context=context,
        )
        return VerificationAttempt(
            tier=3,
            status=VerificationStatus.PENDING,
            confidence=0.0,
            checks_passed=0,
            checks_total=0,
            details=f"Queued for human review: {review_id}",
            performed_by="human:queue",
            performed_at=int(time.time() * 1000),
            duration_ms=0,
            evidence_hash=item.signed_hash,
        )

    def _compute_expiry(
        self, item: EvidenceItem, status: VerificationStatus
    ) -> int | None:
        """Compute when this evidence needs re-verification."""
        base_expiry_days = {
            VerificationStatus.VERIFIED_HUMAN: 365,
            VerificationStatus.VERIFIED_AI: 180,
            VerificationStatus.VERIFIED_AUTO: 90,
        }
        days = base_expiry_days.get(status, 90)
        return int(time.time() * 1000) + days * 86400 * 1000

    def _compute_human_priority(self, item: EvidenceItem) -> int:
        """Compute priority for human review queue (1-5, 5=highest)."""
        # Higher priority for high-value evidence
        priority = 3  # Default medium
        if item.quality_score >= 0.8:
            priority = 5
        elif item.quality_score >= 0.6:
            priority = 4
        return priority


@dataclass
class VerificationConfig:
    """Tenant-configurable verification thresholds."""
    auto_threshold: float = 0.85      # Auto passes if confidence >= 0.85
    ai_threshold: float = 0.90        # AI passes if confidence >= 0.90
    human_threshold: float = 0.95     # Human decision threshold
    auto_enabled: bool = True
    ai_enabled: bool = True
    human_enabled: bool = True
    ai_model: str = "claude-sonnet-4"
    max_escalations: int = 2
    re_verify_interval_days: dict[str, int] = None  # Per-status expiry
    re_verify_on_skill_change: bool = True


@dataclass
class VerificationContext:
    """Context passed through the verification pipeline."""
    evidence_id: str
    user_id: str
    tenant_id: str
    auto_confidence: float = 0.0
    ai_enabled: bool = True
    cross_ref_data: dict | None = None
    linked_accounts: list[str] | None = None
```

### 3.4 Auto Verifiers (Tier 1)

Each evidence source type has a dedicated auto-verifier with source-specific checks. These are **fully deterministic** — no AI, no external API calls beyond source validation.

```python
class AutoVerifier(ABC):
    """Base class for source-specific auto verifiers."""

    @abstractmethod
    async def verify(
        self, item: EvidenceItem, context: VerificationContext
    ) -> AutoVerificationResult:
        ...


@dataclass
class AutoVerificationResult:
    verified: bool
    confidence: float
    checks_passed: int
    checks_total: int
    details: str
    failed_checks: list[str]


class GenericAutoVerifier(AutoVerifier):
    """
    Fallback verifier for source types without a dedicated verifier.
    Runs basic integrity checks applicable to all evidence.
    """

    async def verify(
        self, item: EvidenceItem, context: VerificationContext
    ) -> AutoVerificationResult:
        checks = []
        failed = []

        # Check 1: Evidence has a valid ID
        id_ok = bool(item.evidence_id) and len(item.evidence_id) >= 8
        checks.append(id_ok)
        if not id_ok:
            failed.append("Invalid evidence ID")

        # Check 2: Evidence has a user_id
        user_ok = bool(item.user_id)
        checks.append(user_ok)
        if not user_ok:
            failed.append("Missing user_id")

        # Check 3: Has at least a title
        title_ok = bool(item.title) and len(item.title.strip()) > 0
        checks.append(title_ok)
        if not title_ok:
            failed.append("Missing or empty title")

        # Check 4: Has a source type
        source_ok = item.source_type is not None
        checks.append(source_ok)
        if not source_ok:
            failed.append("Missing source_type")

        # Check 5: Timestamps are in the past
        now = int(time.time() * 1000)
        ts_ok = item.collected_at <= now
        checks.append(ts_ok)
        if not ts_ok:
            failed.append("Collected_at is in the future")

        # Check 6: Hash integrity
        hash_ok = bool(item.signed_hash)
        checks.append(hash_ok)
        if not hash_ok:
            failed.append("Missing signed hash")

        # Check 7: Cryptographic chain integrity (if previous hash exists)
        chain_ok = True
        if item.previous_hash and item.state != EvidenceState.RAW:
            chain_ok = await self._verify_hash_chain(item)
        checks.append(chain_ok)
        if not chain_ok:
            failed.append("Hash chain broken — evidence tampered")

        pass_count = sum(1 for c in checks if c)
        total = len(checks)
        confidence = pass_count / total if total > 0 else 0.0
        verified = confidence >= 0.75

        return AutoVerificationResult(
            verified=verified,
            confidence=confidence,
            checks_passed=pass_count,
            checks_total=total,
            details=f"Generic checks: {pass_count}/{total} passed",
            failed_checks=failed,
        )

    async def _verify_hash_chain(self, item: EvidenceItem) -> bool:
        """Verify that the hash chain from previous state is intact."""
        # In production: re-compute hash from previous state stored in DB
        return True


class ProjectAutoVerifier(AutoVerifier):
    """Auto-verifier for project evidence with source-specific checks."""

    async def verify(
        self, item: EvidenceItem, context: VerificationContext
    ) -> AutoVerificationResult:
        metadata = item.metadata
        checks = []
        failed = []

        # Check 1: URL is reachable
        url = item.url or metadata.get("url")
        if url:
            reachable = await self._check_url_reachability(url)
            checks.append(reachable)
            if not reachable:
                failed.append(f"URL not reachable: {url}")
        else:
            checks.append(False)
            failed.append("No URL provided")

        # Check 2: Repository has meaningful content
        size = metadata.get("size", 0)
        has_content = size > 1000
        checks.append(has_content)
        if not has_content:
            failed.append("Repository is empty or trivial")

        # Check 3: Not a fork or template (if applicable)
        is_fork = metadata.get("is_fork", False)
        is_template = metadata.get("is_template", False)
        not_derivative = not (is_fork or is_template)
        checks.append(not_derivative)
        if not not_derivative:
            failed.append("Repository is a fork or template")

        # Check 4: Has README or documentation
        has_docs = metadata.get("has_readme", False) or metadata.get("has_wiki", False)
        checks.append(has_docs)
        if not has_docs:
            failed.append("No documentation found")

        # Check 5: Has recent activity (< 2 years)
        pushed_at = metadata.get("pushed_at")
        if pushed_at:
            recent = (time.time() - pushed_at) < 86400 * 730
            checks.append(recent)
            if not recent:
                failed.append("No activity in 2+ years")

        # Check 6: Commit count sufficient for claimed effort
        commits = metadata.get("total_commits", 0)
        if commits > 0:
            sufficient_commits = commits >= 5
            checks.append(sufficient_commits)
            if not sufficient_commits:
                failed.append("Too few commits for claimed project")

        # Check 7: Multiple contributors signal real project (optional)
        contributors = metadata.get("contributors", 0)
        if contributors > 0:
            multi_contributor = contributors >= 1  # At least the owner
            checks.append(multi_contributor)

        pass_count = sum(1 for c in checks if c)
        total = len(checks)
        confidence = pass_count / total if total > 0 else 0.0
        verified = confidence >= 0.75

        return AutoVerificationResult(
            verified=verified,
            confidence=confidence,
            checks_passed=pass_count,
            checks_total=total,
            details=f"Project verification: {pass_count}/{total} checks passed",
            failed_checks=failed,
        )

    async def _check_url_reachability(self, url: str) -> bool:
        """Check if URL is reachable (HEAD request)."""
        # In production: HTTP HEAD with timeout=5s
        try:
            from httpx import AsyncClient
            async with AsyncClient() as client:
                resp = await client.head(url, follow_redirects=True, timeout=5.0)
                return resp.status_code < 500
        except Exception:
            return False


class GitHubAutoVerifier(AutoVerifier):
    """Auto-verifier for GitHub contribution evidence."""

    async def verify(
        self, item: EvidenceItem, context: VerificationContext
    ) -> AutoVerificationResult:
        metadata = item.metadata
        checks = []
        failed = []

        # Check 1: GitHub profile exists
        profile = metadata.get("profile", {})
        login = profile.get("login")
        checks.append(bool(login))
        if not login:
            failed.append("No GitHub profile found")

        # Check 2: Account is not brand new
        created = profile.get("created_at")
        if created:
            age_days = (time.time() - created) / 86400
            mature_account = age_days > 90
            checks.append(mature_account)
            if not mature_account:
                failed.append(f"GitHub account is only {age_days:.0f} days old")
        else:
            checks.append(False)
            failed.append("Cannot determine account age")

        # Check 3: Has public repositories
        repos = metadata.get("repos", []) or metadata.get("public_repos", 0)
        if isinstance(repos, list):
            has_repos = len(repos) > 0
        else:
            has_repos = repos > 0
        checks.append(has_repos)
        if not has_repos:
            failed.append("No public repositories")

        # Check 4: Recent activity
        contributions = metadata.get("contributions", {})
        total_commits = contributions.get("total_commits", 0) if isinstance(contributions, dict) else 0
        has_recent_contributions = total_commits > 0
        checks.append(has_recent_contributions)
        if not has_recent_contributions:
            failed.append("No recent contributions")

        # Check 5: Contribution streak indicates genuine activity
        streak = contributions.get("streak_days", 0) if isinstance(contributions, dict) else 0
        if streak > 0:
            meaningful_streak = streak >= 3
            checks.append(meaningful_streak)
            if not meaningful_streak:
                failed.append("Contribution streak too short (< 3 days)")

        # Check 6: Multiple languages suggests varied skill set
        languages = metadata.get("languages", [])
        if len(languages) > 0:
            diverse = len(languages) >= 2
            checks.append(diverse)

        # Check 7: PRs merged vs open ratio
        repos_data = metadata.get("repos", [])
        total_prs = sum(r.get("prs_merged", 0) for r in repos_data if isinstance(r, dict))
        if total_prs > 0:
            meaningful_prs = total_prs >= 3
            checks.append(meaningful_prs)
            if not meaningful_prs:
                failed.append("Too few merged PRs")

        pass_count = sum(1 for c in checks if c)
        total = len(checks)
        confidence = pass_count / total if total > 0 else 0.0
        verified = confidence >= 0.75

        return AutoVerificationResult(
            verified=verified,
            confidence=confidence,
            checks_passed=pass_count,
            checks_total=total,
            details=f"GitHub verification: {pass_count}/{total} checks passed",
            failed_checks=failed,
        )


class CertificationAutoVerifier(AutoVerifier):
    """Auto-verifier for certification evidence with provider API lookups."""

    PROVIDER_LOOKUP_FUNCTIONS: dict[str, str] = {
        "credly": "https://api.credly.com/v1/badges/",
        "acclaim": "https://api.acclaim.com/v1/badge/",
        "coursera": "https://www.coursera.org/api/certificate/",
        "edx": "https://credentials.edx.org/records/",
        "aws": "https://aws.amazon.com/verification/",
        "google": "https://cloud.google.com/learn/certification/",
        "microsoft": "https://learn.microsoft.com/api/certifications/",
    }

    async def verify(
        self, item: EvidenceItem, context: VerificationContext
    ) -> AutoVerificationResult:
        metadata = item.metadata
        checks = []
        failed = []

        # Check 1: Has a credential ID
        credential_id = metadata.get("credential_id") or metadata.get("certificate_id")
        checks.append(bool(credential_id))
        if not credential_id:
            failed.append("No credential ID provided")

        # Check 2: Has a recognizable provider
        provider = metadata.get("provider", "")
        recognized = provider.lower() in self.PROVIDER_LOOKUP_FUNCTIONS
        checks.append(recognized)
        if not recognized:
            failed.append(f"Unknown certification provider: {provider}")

        # Check 3: Has a verification URL
        verify_url = metadata.get("verify_url") or metadata.get("url")
        checks.append(bool(verify_url))
        if not verify_url:
            failed.append("No verification URL")

        # Check 4: Credential URL is from the legitimate provider domain
        if verify_url:
            url_domain = self._extract_domain(verify_url)
            expected_domains = {
                "credly": "credly.com",
                "acclaim": "acclaim.com",
                "coursera": "coursera.org",
                "edx": "edx.org",
                "aws": "aws.amazon.com",
                "google": "google.com",
                "microsoft": "microsoft.com",
            }
            expected = expected_domains.get(provider.lower(), "")
            correct_domain = expected and expected in url_domain
            checks.append(correct_domain)
            if not correct_domain:
                failed.append(f"Verification URL domain mismatch: expected {expected}, got {url_domain}")

        # Check 5: Certificate is not expired
        expires = metadata.get("expires_at") or metadata.get("expiration_date")
        if expires:
            if isinstance(expires, (int, float)):
                not_expired = time.time() < expires
            else:
                not_expired = True  # No expiration date = no renewal needed
            checks.append(not_expired)
            if not not_expired:
                failed.append("Certification has expired")

        # Check 6: Issuer is legitimate
        issuer = metadata.get("issuer", "").lower()
        known_issuers = [
            "aws", "amazon", "google", "microsoft", "coursera", "edx",
            "credly", "acclaim", "ibm", "oracle", "cisco", "comptia",
            "pmi", "scrum alliance", "sans", "isc2",
        ]
        if issuer:
            known = any(known in issuer for known in known_issuers)
            checks.append(known)
            if not known:
                failed.append(f"Unknown certification issuer: {issuer}")

        # Check 7: Has a date issued (not just a future promise)
        issued = metadata.get("issued_at") or metadata.get("issue_date")
        if issued:
            if isinstance(issued, (int, float)):
                has_real_date = issued > 0 and issued < time.time()
            else:
                has_real_date = True
            checks.append(has_real_date)

        pass_count = sum(1 for c in checks if c)
        total = len(checks)
        confidence = pass_count / total if total > 0 else 0.0
        verified = confidence >= 0.80

        return AutoVerificationResult(
            verified=verified,
            confidence=confidence,
            checks_passed=pass_count,
            checks_total=total,
            details=f"Certification verification: {pass_count}/{total} checks passed",
            failed_checks=failed,
        )

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc or parsed.hostname or ""


class AssessmentAutoVerifier(AutoVerifier):
    """Auto-verifier for assessment evidence (imported from SkillAssessment.md)."""

    async def verify(
        self, item: EvidenceItem, context: VerificationContext
    ) -> AutoVerificationResult:
        metadata = item.metadata
        checks = []
        failed = []

        # Check 1: Has a valid assessment session ID
        session_id = metadata.get("session_id")
        checks.append(bool(session_id))
        if not session_id:
            failed.append("No assessment session ID")

        # Check 2: Assessment result is signed by the assessment engine
        signature = metadata.get("assessment_signature")
        checks.append(bool(signature))
        if not signature:
            failed.append("Missing assessment signature")

        # Check 3: Verify the cryptographic signature
        if signature and session_id:
            sig_valid = await self._verify_assessment_signature(session_id, signature)
            checks.append(sig_valid)
            if not sig_valid:
                failed.append("Assessment signature verification failed — result may be tampered")

        # Check 4: Assessment was completed, not abandoned
        status = metadata.get("status", "")
        completed = status == "completed"
        checks.append(completed)
        if not completed:
            failed.append(f"Assessment not completed (status: {status})")

        # Check 5: Has a score
        score = metadata.get("score")
        has_score = score is not None and isinstance(score, (int, float))
        checks.append(has_score)
        if not has_score:
            failed.append("No assessment score")

        # Check 6: Score is within valid range
        if has_score:
            valid_range = 0.0 <= score <= 1.0
            checks.append(valid_range)
            if not valid_range:
                failed.append(f"Assessment score outside valid range: {score}")

        # Check 7: Duration is reasonable (not too fast)
        duration_min = metadata.get("duration_minutes", 0)
        if duration_min > 0:
            questions = metadata.get("questions_count", 1)
            reasonable_time = duration_min >= questions * 0.5  # At least 30s per question
            checks.append(reasonable_time)
            if not reasonable_time:
                failed.append(f"Assessment completed too quickly: {duration_min}min for {questions} questions")

        pass_count = sum(1 for c in checks if c)
        total = len(checks)
        confidence = pass_count / total if total > 0 else 0.0
        verified = confidence >= 0.80

        return AutoVerificationResult(
            verified=verified,
            confidence=confidence,
            checks_passed=pass_count,
            checks_total=total,
            details=f"Assessment verification: {pass_count}/{total} checks passed",
            failed_checks=failed,
        )

    async def _verify_assessment_signature(self, session_id: str, signature: str) -> bool:
        """Verify the assessment result cryptographic signature."""
        # In production: use the assessment engine's public key to verify
        return True
```

### 3.5 Cross-Reference Engine

The Cross-Reference Engine triangulates evidence by checking if the same skill claim is supported by **multiple independent sources**. This is a powerful trust multiplier: a skill backed by 3+ independent evidence sources requires less verification scrutiny per source.

```python
class CrossReferenceEngine:
    """
    Triangulates evidence by finding overlapping skill claims
    across different evidence sources for the same user.

    When the same skill is evidenced by 3+ independent sources,
    a trust synergy bonus is applied, and each individual source's
    verification threshold can be lowered.
    """

    def __init__(self, evidence_store: EvidenceStore):
        self.store = evidence_store
        self.logger = StructuredLogger("evidence.cross_reference")

    async def compute_cross_references(
        self, user_id: str, skill_id: str | None = None
    ) -> CrossReferenceResult:
        """
        Compute cross-references for all of a user's evidence.
        Optionally scope to a specific skill.
        """
        evidence = await self.store.get_evidence_by_user(user_id)
        if skill_id:
            evidence = [e for e in evidence if skill_id in e.skill_ids]

        # Group evidence by skill
        skill_evidence: dict[str, list[EvidenceItem]] = {}
        for item in evidence:
            for skill in item.skill_ids:
                if skill not in skill_evidence:
                    skill_evidence[skill] = []
                skill_evidence[skill].append(item)

        cross_refs = []
        for skill, items in skill_evidence.items():
            xref = await self._compute_for_skill(skill, items)
            cross_refs.append(xref)

        return CrossReferenceResult(
            user_id=user_id,
            skill_cross_refs=cross_refs,
            overall_synergy_score=self._compute_overall_synergy(cross_refs),
            computed_at=int(time.time() * 1000),
        )

    async def _compute_for_skill(
        self, skill: str, items: list[EvidenceItem]
    ) -> SkillCrossReference:
        """Compute cross-reference data for a single skill."""
        source_types = set(item.source_type.value for item in items)
        source_count = len(source_types)
        total_items = len(items)

        # Determine source independence
        independent_sources = self._classify_independence(items)

        # Synergy score: more independent sources = higher score
        # 1 source: 1.0, 2 sources: 1.25, 3+: 1.5
        if source_count >= 3:
            synergy_multiplier = 1.5
            confidence_boost = 0.15
        elif source_count == 2:
            synergy_multiplier = 1.25
            confidence_boost = 0.08
        else:
            synergy_multiplier = 1.0
            confidence_boost = 0.0

        # Temporal diversity: evidence spread over time adds credibility
        timestamps = [item.collected_at for item in items if item.collected_at]
        if len(timestamps) >= 2:
            span_days = (max(timestamps) - min(timestamps)) / 86400000
            temporal_diversity = min(span_days / 365, 1.0)  # Cap at 1 year
        else:
            temporal_diversity = 0.0

        return SkillCrossReference(
            skill=skill,
            source_count=source_count,
            source_types=list(source_types),
            total_items=total_items,
            independent_sources=independent_sources,
            synergy_multiplier=synergy_multiplier,
            confidence_boost=confidence_boost,
            temporal_diversity=temporal_diversity,
            requires_less_verification=source_count >= 3,
        )

    def _classify_independence(self, items: list[EvidenceItem]) -> int:
        """
        Count truly independent sources.
        Two sources are independent if they come from different platforms
        or were collected at significantly different times.
        """
        # Group by platform/domain
        source_groups: dict[str, set[str]] = {}
        for item in items:
            domain = self._get_source_domain(item)
            if domain not in source_groups:
                source_groups[domain] = set()
            source_groups[domain].add(item.evidence_id)

        # Count domains as independent if they have evidence
        return len(source_groups)

    def _get_source_domain(self, item: EvidenceItem) -> str:
        """Extract the independent domain from a source type."""
        domain_map = {
            EvidenceSourceType.GITHUB: "github.com",
            EvidenceSourceType.PROJECT: "github.com",  # Same domain as GitHub
            EvidenceSourceType.CERTIFICATION: "credential_provider",
            EvidenceSourceType.HACKATHON: "devpost.com",
            EvidenceSourceType.FREELANCE: "upwork.com",
            EvidenceSourceType.OPENSOURCE: "pypi.org",
            EvidenceSourceType.ASSESSMENT: "assessment_engine",
            EvidenceSourceType.WORK_EXPERIENCE: "linkedin.com",
        }
        return domain_map.get(item.source_type, "unknown")

    def _compute_overall_synergy(
        self, cross_refs: list[SkillCrossReference]
    ) -> float:
        """Compute overall synergy score across all skills."""
        if not cross_refs:
            return 1.0
        synergy_scores = [
            cr.synergy_multiplier * (1 + cr.temporal_diversity * 0.5)
            for cr in cross_refs
        ]
        return sum(synergy_scores) / len(synergy_scores)

    async def get_verification_recommendation(
        self, evidence_ids: list[str]
    ) -> VerificationRecommendation:
        """
        Given a list of evidence items for a skill, recommend whether
        to verify each item or rely on cross-referencing for trust.
        """
        items = []
        for eid in evidence_ids:
            item = await self.store.get_evidence(eid)
            if item:
                items.append(item)

        skill = items[0].skill_ids[0] if items else None
        if not skill:
            return VerificationRecommendation(
                evidence_ids=evidence_ids,
                recommended_tier=1,
                reason="Cannot determine skill",
            )

        xref = await self._compute_for_skill(skill, items)

        # If 3+ independent sources, reduce verification tier
        if xref.source_count >= 3:
            return VerificationRecommendation(
                evidence_ids=evidence_ids,
                recommended_tier=1,  # Auto only is sufficient
                reason=f"Skill '{skill}' has {xref.source_count} independent sources — cross-referencing provides sufficient trust",
                synergy_applied=True,
                reduced_verification=True,
            )
        elif xref.source_count == 2:
            return VerificationRecommendation(
                evidence_ids=evidence_ids,
                recommended_tier=1,  # Auto may be sufficient with synergy bonus
                reason=f"Skill '{skill}' has 2 sources — synergy bonus reduces verification burden",
                synergy_applied=True,
                reduced_verification=True,
            )
        else:
            return VerificationRecommendation(
                evidence_ids=evidence_ids,
                recommended_tier=2,  # AI verification recommended
                reason=f"Skill '{skill}' has only 1 source — full verification required",
                synergy_applied=False,
                reduced_verification=False,
            )


@dataclass
class CrossReferenceResult:
    user_id: str
    skill_cross_refs: list[SkillCrossReference]
    overall_synergy_score: float
    computed_at: int


@dataclass
class SkillCrossReference:
    skill: str
    source_count: int
    source_types: list[str]
    total_items: int
    independent_sources: int
    synergy_multiplier: float
    confidence_boost: float
    temporal_diversity: float
    requires_less_verification: bool


@dataclass
class VerificationRecommendation:
    evidence_ids: list[str]
    recommended_tier: int
    reason: str
    synergy_applied: bool = False
    reduced_verification: bool = False
```

### 3.6 Human Review Queue

When both auto and AI verification are inconclusive, evidence is queued for human expert review with priority scoring, SLA tracking, and reviewer assignment.

```python
class HumanReviewQueue:
    """
    Manages the queue of evidence items requiring human expert verification.

    Reviewers are domain-tagged for appropriate assignment:
    - A Python certification goes to a Python expert reviewer
    - A project goes to a tech lead reviewer
    - A work experience claim goes to an HR-domain reviewer
    """

    def __init__(self, db_session, config: HumanReviewConfig):
        self.db = db_session
        self.config = config
        self.logger = StructuredLogger("evidence.human_review")

    async def enqueue(
        self,
        evidence_id: str,
        reason: str,
        priority: int,
        context: VerificationContext,
    ) -> str:
        """Add an evidence item to the human review queue."""
        review_id = f"rev_{uuid.uuid4().hex[:12]}"

        review = HumanReviewTask(
            review_id=review_id,
            evidence_id=evidence_id,
            reason=reason,
            priority=priority,
            status="pending",
            assigned_to=None,
            sla_deadline=int(time.time() * 1000) + self.config.sla_hours * 3600000,
            escalation_level=0,
            created_at=int(time.time() * 1000),
            context=context,
        )

        await self._persist(review)
        await self._notify_reviewers(evidence_id, priority)

        self.logger.info(
            "Evidence queued for human review",
            review_id=review_id,
            evidence_id=evidence_id,
            priority=priority,
            sla=self.config.sla_hours,
        )

        return review_id

    async def assign(self, review_id: str, reviewer_id: str) -> bool:
        """Assign a review task to a specific reviewer."""
        review = await self._get_review(review_id)
        if not review or review.status != "pending":
            return False
        review.assigned_to = reviewer_id
        review.status = "in_progress"
        review.assigned_at = int(time.time() * 1000)
        await self._update(review)
        return True

    async def resolve(
        self, review_id: str, reviewer_id: str,
        decision: HumanReviewDecision
    ) -> VerificationAttempt:
        """
        Resolve a human review with a decision.
        Returns the VerificationAttempt for the verification state.
        """
        review = await self._get_review(review_id)
        if not review:
            raise ValueError(f"Review not found: {review_id}")

        # Validate reviewer assignment
        if review.assigned_to and review.assigned_to != reviewer_id:
            raise PermissionError(f"Review {review_id} is assigned to {review.assigned_to}")

        review.status = "resolved"
        review.resolved_at = int(time.time() * 1000)
        review.decision = decision
        await self._update(review)

        verification_status = (
            VerificationStatus.VERIFIED_HUMAN if decision.approved
            else VerificationStatus.REJECTED_HUMAN
        )

        attempt = VerificationAttempt(
            tier=3,
            status=verification_status,
            confidence=decision.confidence,
            checks_passed=1 if decision.approved else 0,
            checks_total=1,
            details=decision.notes or f"Human review: {'approved' if decision.approved else 'rejected'}",
            performed_by=f"human:{reviewer_id}",
            performed_at=int(time.time() * 1000),
            duration_ms=review.resolved_at - review.assigned_at if review.assigned_at else 0,
            evidence_hash="",  # In production: re-hash evidence
        )

        return attempt

    async def escalate(self, review_id: str) -> bool:
        """Escalate a review to a higher authority (senior reviewer)."""
        review = await self._get_review(review_id)
        if not review:
            return False

        review.escalation_level += 1
        if review.escalation_level > self.config.max_escalations:
            review.status = "escalated_max"
            self.logger.warning("Review at max escalation", review_id=review_id)
        else:
            review.status = "pending"
            review.assigned_to = None
            review.sla_deadline = int(time.time() * 1000) + self.config.escalation_sla_hours * 3600000
            self.logger.info("Review escalated", review_id=review_id, level=review.escalation_level)

        await self._update(review)
        return True

    async def get_next_pending(self, reviewer_capabilities: list[str]) -> HumanReviewTask | None:
        """Get the next pending review matching the reviewer's capabilities."""
        # In production: query PostgreSQL with priority ordering
        return None

    async def _persist(self, review: HumanReviewTask) -> None:
        pass

    async def _get_review(self, review_id: str) -> HumanReviewTask | None:
        return None

    async def _update(self, review: HumanReviewTask) -> None:
        pass

    async def _notify_reviewers(self, evidence_id: str, priority: int) -> None:
        """Notify available reviewers of a new review task."""
        pass


@dataclass
class HumanReviewConfig:
    sla_hours: int = 48           # Standard SLA for human review
    escalation_sla_hours: int = 24  # Faster SLA for escalated items
    max_escalations: int = 3
    auto_assign: bool = True
    require_two_factor: bool = True
    reviewer_domains: list[str] = None


@dataclass
class HumanReviewTask:
    review_id: str
    evidence_id: str
    reason: str
    priority: int
    status: str                    # pending | in_progress | resolved | escalated_max
    assigned_to: str | None
    assigned_at: int | None
    sla_deadline: int
    escalation_level: int
    decision: HumanReviewDecision | None = None
    resolved_at: int | None = None
    created_at: int
    context: VerificationContext


@dataclass
class HumanReviewDecision:
    approved: bool
    confidence: float              # Human's confidence in their decision (0.0-1.0)
    notes: str | None = None
    supporting_evidence: list[str] = None
    reviewer_credentials: str | None = None
```

### 3.7 Verification Expiration and Renewal

Evidence verification is not permanent. Each verification tier has a different expiration window, and certain events trigger re-verification.

```python
class VerificationExpiryManager:
    """
    Manages verification expiration and renewal cycles.

    Verification tiers have different lifetimes:
    - Human-verified: 365 days
    - AI-verified: 180 days
    - Auto-verified: 90 days

    Events that trigger early re-verification:
    - User changes linked accounts
    - Fraud alert is raised for the evidence or user
    - Source platform API changes
    - Scheduled random audit (stochastic verification)
    """

    def __init__(self, store: EvidenceStore, config: VerificationConfig):
        self.store = store
        self.config = config
        self.logger = StructuredLogger("evidence.verification_expiry")
        self.default_expiry_days = {
            VerificationStatus.VERIFIED_HUMAN: 365,
            VerificationStatus.VERIFIED_AI: 180,
            VerificationStatus.VERIFIED_AUTO: 90,
        }

    async def check_expiry(self, evidence_id: str) -> ExpiryStatus:
        """Check whether an evidence item needs re-verification."""
        item = await self.store.get_evidence(evidence_id)
        if not item or not item.verified_at:
            return ExpiryStatus(
                evidence_id=evidence_id,
                expired=True,
                reason="Never verified",
                days_until_expiry=0,
            )

        status = await self._get_verification_status(evidence_id)
        expiry_days = self.default_expiry_days.get(status, 90)
        expiry_ms = expiry_days * 86400 * 1000
        age_ms = int(time.time() * 1000) - item.verified_at
        days_old = age_ms / 86400000

        expired = age_ms > expiry_ms
        days_remaining = expiry_days - days_old

        return ExpiryStatus(
            evidence_id=evidence_id,
            expired=expired,
            reason=f"Past {expiry_days}-day expiry window" if expired else f"Expires in {days_remaining:.0f} days",
            days_until_expiry=max(0, days_remaining),
        )

    async def get_expired_batch(self, batch_size: int = 100) -> list[str]:
        """Get all evidence items that need re-verification."""
        # In production: query PostgreSQL WHERE expires_at < now()
        return []

    async def renew(self, evidence_id: str, new_verification: VerificationState) -> bool:
        """Renew verification for an evidence item."""
        item = await self.store.get_evidence(evidence_id)
        if not item:
            return False

        item.verified_at = new_verification.last_verified_at
        item.verification_method = new_verification.final_status.value
        item.state = EvidenceState.VERIFIED

        await self.store.update(item)
        self.logger.info("Verification renewed", evidence_id=evidence_id, tier=new_verification.current_tier)
        return True

    async def trigger_reverification(
        self, evidence_ids: list[str], reason: str
    ) -> int:
        """Trigger re-verification for a batch of evidence items."""
        count = 0
        for eid in evidence_ids:
            item = await self.store.get_evidence(eid)
            if item and item.state not in (EvidenceState.REJECTED, EvidenceState.EXPIRED):
                item.state = EvidenceState.PENDING_VERIFICATION
                await self.store.update(item)
                count += 1
        self.logger.info("Re-verification triggered", count=count, reason=reason)
        return count

    async def schedule_random_audit(
        self, user_id: str, fraction: float = 0.05
    ) -> list[str]:
        """
        Schedule a random fraction of a user's evidence for re-verification.
        Stochastic verification keeps the system honest.
        """
        evidence = await self.store.get_evidence_by_user(user_id)
        import random
        random.seed(int(time.time() / 86400))  # Deterministic per day
        audit_sample = random.sample(
            evidence, max(1, int(len(evidence) * fraction))
        )
        return await self.trigger_reverification(
            [e.evidence_id for e in audit_sample],
            f"Random audit ({fraction*100:.0f}% sample)"
        )


@dataclass
class ExpiryStatus:
    evidence_id: str
    expired: bool
    reason: str
    days_until_expiry: float
```

### 3.8 Verification Alerts and Notifications

When verification fails or expires, the system raises appropriate alerts for both the user and the system administrators.

```python
@dataclass
class VerificationAlert:
    """Alert raised when verification encounters an issue."""
    alert_id: str
    evidence_id: str
    alert_type: str  # verification_failed | expired | tampered | fraud_suspected
    severity: str    # info | warning | critical
    message: str
    tier: int
    created_at: int
    resolved_at: int | None = None
    action_required: str | None = None


class VerificationAlertManager:
    """Manages verification alerts and user notifications."""

    def __init__(self):
        self.logger = StructuredLogger("evidence.verification_alerts")

    async def raise_alert(
        self,
        evidence_id: str,
        alert_type: str,
        severity: str,
        message: str,
        tier: int,
        action_required: str | None = None,
    ) -> VerificationAlert:
        alert = VerificationAlert(
            alert_id=f"valert_{uuid.uuid4().hex[:8]}",
            evidence_id=evidence_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            tier=tier,
            created_at=int(time.time() * 1000),
            action_required=action_required,
        )

        await self._persist(alert)

        if severity in ("warning", "critical"):
            await self._notify_user(evidence_id, alert)
            await self._notify_admin(alert)

        self.logger.warning(
            "Verification alert raised",
            alert_id=alert.alert_id,
            alert_type=alert_type,
            severity=severity,
        )

        return alert

    async def resolve(self, alert_id: str, resolution: str) -> bool:
        alert = await self._get_alert(alert_id)
        if not alert:
            return False
        alert.resolved_at = int(time.time() * 1000)
        return True

    async def _persist(self, alert: VerificationAlert) -> None:
        pass

    async def _get_alert(self, alert_id: str) -> VerificationAlert | None:
        return None

    async def _notify_user(self, evidence_id: str, alert: VerificationAlert) -> None:
        """Notify the evidence owner about the verification issue."""
        self.logger.info("User notified of verification alert", alert_id=alert.alert_id)

    async def _notify_admin(self, alert: VerificationAlert) -> None:
        """Notify system administrators about critical verification alerts."""
        self.logger.info("Admin notified of critical alert", alert_id=alert.alert_id)
```


---
## 4. Trust Score Framework

### 4.1 Trust Score Philosophy

Trust is the **gate** that evidence weight must pass through. Before any quality or recency calculation matters, the system must answer: *"Can we trust that this evidence is authentic and belongs to this user?"*

Trust is computed as a **multiplicative** score — if any single trust component is zero, the entire trust score is zero. This is by design: a forged credential cannot be partially trusted.

```
Trust_Score = Provenance_Integrity × Source_Reputation × Chain_of_Custody × Identity_Binding

Where:
  Provenance_Integrity  = Can we verify where this came from?   [0.0, 1.0]
  Source_Reputation     = How trustworthy is the source?        [0.0, 1.0]
  Chain_of_Custody      = Has the evidence chain been intact?   [0.0, 1.0]
  Identity_Binding      = Is this firmly tied to the user?      [0.0, 1.0]
```

If any factor is 0.0, the trust score is 0.0 — the evidence is rejected regardless of quality.

### 4.2 Trust Score Computation

```python
class TrustScoreFramework:
    """
    Computes the trust score for each evidence item.
    Trust is multiplicative: one zero factor zeroes the entire score.
    """

    def __init__(self, config: TrustScoreConfig | None = None):
        self.config = config or TrustScoreConfig()
        self.logger = StructuredLogger("evidence.trust_score")
        self.provenance_verifier = ProvenanceVerifier()
        self.reputation_service = SourceReputationService()
        self.custody_tracker = ChainOfCustodyTracker()
        self.identity_binder = IdentityBindingService()

    async def compute_trust_score(
        self, item: EvidenceItem
    ) -> TrustScoreResult:
        """
        Compute the full trust score for an evidence item.

        Steps:
        1. Verify provenance integrity (where did this come from?)
        2. Evaluate source reputation (how trustworthy is the platform?)
        3. Validate chain of custody (has it been tampered with?)
        4. Confirm identity binding (does this belong to this user?)
        5. Multiply all factors for final trust score
        """
        start = time.time()

        # Step 1: Provenance Integrity
        provenance = await self.provenance_verifier.verify(item)
        if provenance.score == 0.0:
            return TrustScoreResult(
                evidence_id=item.evidence_id,
                trust_score=0.0,
                provenance_score=0.0,
                source_reputation_score=0.0,
                chain_of_custody_score=0.0,
                identity_binding_score=0.0,
                broken_factor="provenance",
                reason=provenance.failure_reason or "Provenance integrity check failed",
                details=provenance.details,
                computed_at=int(time.time() * 1000),
                duration_ms=int((time.time() - start) * 1000),
            )

        # Step 2: Source Reputation
        reputation = await self.reputation_service.get_reputation(
            item.source_type, item.metadata
        )

        # Step 3: Chain of Custody
        custody = await self.custody_tracker.validate(item)

        # Step 4: Identity Binding
        identity = await self.identity_binder.bind(item)

        # Step 5: Multiplicative trust score
        trust_score = (
            provenance.score *
            reputation.score *
            custody.score *
            identity.score
        )

        # Identify the weakest factor for diagnosis
        factors = {
            "provenance": provenance.score,
            "source_reputation": reputation.score,
            "chain_of_custody": custody.score,
            "identity_binding": identity.score,
        }
        weakest = min(factors, key=factors.get)

        duration = int((time.time() - start) * 1000)

        self.logger.info(
            "Trust score computed",
            evidence_id=item.evidence_id,
            trust_score=round(trust_score, 4),
            weakest_factor=weakest,
            duration_ms=duration,
        )

        return TrustScoreResult(
            evidence_id=item.evidence_id,
            trust_score=trust_score,
            provenance_score=provenance.score,
            source_reputation_score=reputation.score,
            chain_of_custody_score=custody.score,
            identity_binding_score=identity.score,
            broken_factor=weakest if trust_score == 0.0 else None,
            reason=f"Trust score: {trust_score:.2f} (weakest: {weakest})",
            details={
                "provenance": provenance.details,
                "reputation": reputation.details,
                "custody": custody.details,
                "identity": identity.details,
            },
            computed_at=int(time.time() * 1000),
            duration_ms=duration,
        )


@dataclass
class TrustScoreResult:
    evidence_id: str
    trust_score: float                # 0.0-1.0
    provenance_score: float           # 0.0-1.0
    source_reputation_score: float    # 0.0-1.0
    chain_of_custody_score: float     # 0.0-1.0
    identity_binding_score: float     # 0.0-1.0
    broken_factor: str | None         # Which factor caused zero trust
    reason: str
    details: dict
    computed_at: int
    duration_ms: int


@dataclass
class TrustScoreConfig:
    min_trust_threshold: float = 0.3   # Below this, evidence is rejected
    require_provenance: bool = True
    require_identity_binding: bool = True
    reputation_ttl_hours: int = 24     # Cache source reputation for 24h
    custody_max_gap_seconds: int = 86400 * 30  # Max 30 days between chain links
```

### 4.3 Provenance Integrity

Provenance answers: *"Where did this evidence originate, and can we trace it back to its source?"*

```python
class ProvenanceVerifier:
    """
    Verifies the provenance chain of evidence.

    Provenance signals:
    - Source type is recognized and verified
    - External ID can be looked up at source
    - Collection timestamp is consistent with source metadata
    - Evidence URL resolves to the claimed source
    - Metadata contains expected fields for the source type
    """

    def __init__(self):
        self.logger = StructuredLogger("evidence.provenance")
        self.url_resolver = URLChecker()

    async def verify(self, item: EvidenceItem) -> ProvenanceResult:
        """Verify the provenance of an evidence item."""
        checks = []
        failures = []

        # Check 1: Source type is valid
        source_valid = item.source_type in EvidenceSourceType
        checks.append(source_valid)
        if not source_valid:
            failures.append("Invalid or unrecognized source type")

        # Check 2: Has an external ID from the source
        ext_id = item.metadata.get("id") or item.metadata.get("external_id")
        has_external_id = bool(ext_id)
        checks.append(has_external_id)
        if not has_external_id:
            failures.append("Missing external ID from source system")

        # Check 3: URL resolves to a real page (if provided)
        if item.url:
            url_valid = await self.url_resolver.check(item.url)
            checks.append(url_valid)
            if not url_valid:
                failures.append(f"URL not reachable: {item.url}")

        # Check 4: Collected_at is not in the future
        ts_valid = item.collected_at <= int(time.time() * 1000)
        checks.append(ts_valid)
        if not ts_valid:
            failures.append("Collection timestamp is in the future")

        # Check 5: Source-specific metadata completeness
        schema = self._get_expected_fields(item.source_type)
        if schema:
            has_fields = all(
                field in item.metadata for field in schema["required"]
            )
            checks.append(has_fields)
            if not has_fields:
                missing = [
                    f for f in schema["required"] if f not in item.metadata
                ]
                failures.append(f"Missing required fields: {missing}")

        # Check 6: External ID matches source provider patterns
        if ext_id and item.source_type:
            id_format_valid = self._validate_external_id_format(
                ext_id, item.source_type
            )
            checks.append(id_format_valid)
            if not id_format_valid:
                failures.append(f"External ID format doesn't match {item.source_type.value} pattern")

        pass_count = sum(1 for c in checks if c)
        total = len(checks)
        score = pass_count / total if total > 0 else 0.0

        # Zero score if critical checks fail
        if not source_valid or not has_external_id:
            score = 0.0
            return ProvenanceResult(
                score=0.0,
                source_validated=source_valid,
                external_id_valid=has_external_id,
                url_validated=item.url and await self.url_resolver.check(item.url) if item.url else False,
                timestamp_valid=ts_valid,
                metadata_complete=score >= 0.7,
                failure_reason="; ".join(failures) if failures else None,
                details={"checks_passed": pass_count, "checks_total": total, "failures": failures},
            )

        return ProvenanceResult(
            score=score,
            source_validated=source_valid,
            external_id_valid=has_external_id,
            url_validated=item.url and await self.url_resolver.check(item.url) if item.url else False,
            timestamp_valid=ts_valid,
            metadata_complete=score >= 0.7,
            failure_reason=None,
            details={"checks_passed": pass_count, "checks_total": total, "failures": failures},
        )

    def _get_expected_fields(self, source_type: EvidenceSourceType) -> dict | None:
        """Return the required metadata schema for a given source type."""
        schemas = {
            EvidenceSourceType.GITHUB: {
                "required": ["login", "id"],
            },
            EvidenceSourceType.CERTIFICATION: {
                "required": ["credential_id", "provider", "credential_name"],
            },
            EvidenceSourceType.PROJECT: {
                "required": ["url"],
            },
            EvidenceSourceType.HACKATHON: {
                "required": ["event_name", "date"],
            },
            EvidenceSourceType.FREELANCE: {
                "required": ["platform", "contract_id"],
            },
            EvidenceSourceType.OPENSOURCE: {
                "required": ["package_name", "registry"],
            },
            EvidenceSourceType.ASSESSMENT: {
                "required": ["session_id", "assessment_signature"],
            },
            EvidenceSourceType.WORK_EXPERIENCE: {
                "required": ["company", "title"],
            },
        }
        return schemas.get(source_type)

    def _validate_external_id_format(
        self, ext_id: str, source_type: EvidenceSourceType
    ) -> bool:
        """Validate that external ID matches expected format for source."""
        format_rules = {
            EvidenceSourceType.GITHUB: lambda x: len(x) > 0 and not x.startswith("!"),
            EvidenceSourceType.CERTIFICATION: lambda x: len(x) >= 8,
            EvidenceSourceType.PROJECT: lambda x: "/" in x or len(x) > 10,
            EvidenceSourceType.HACKATHON: lambda x: len(x) > 0,
            EvidenceSourceType.FREELANCE: lambda x: x.startswith("contract_") or x.startswith("job_"),
            EvidenceSourceType.OPENSOURCE: lambda x: "/" in x or len(x) > 3,
            EvidenceSourceType.ASSESSMENT: lambda x: x.startswith("session_") or len(x) >= 16,
            EvidenceSourceType.WORK_EXPERIENCE: lambda x: len(x) > 0,
        }
        validator = format_rules.get(source_type, lambda x: len(x) > 0)
        return validator(ext_id)


@dataclass
class ProvenanceResult:
    score: float
    source_validated: bool
    external_id_valid: bool
    url_validated: bool
    timestamp_valid: bool
    metadata_complete: bool
    failure_reason: str | None
    details: dict


class URLChecker:
    """Validates that URLs are reachable and from legitimate domains."""

    SUSPICIOUS_TLDS = {".tk", ".ml", ".ga", ".cf", ".gq"}  # Free TLDs

    async def check(self, url: str) -> bool:
        """Check if a URL is reachable and appears legitimate."""
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            # Check domain exists
            if not parsed.netloc:
                return False
            # Check for suspicious TLDs
            tld = "." + parsed.netloc.rsplit(".", 1)[-1] if "." in parsed.netloc else ""
            if tld in self.SUSPICIOUS_TLDS:
                return False
            # In production: HTTP HEAD request
            return True
        except Exception:
            return False
```

### 4.4 Source Reputation

Source reputation evaluates how trustworthy the *platform* or *provider* is for each evidence type. Different source types have vastly different trust baselines.

```python
class SourceReputationService:
    """
    Evaluates and caches the reputation of evidence sources.

    Factors:
    - Platform credibility (domain authority)
    - Verification mechanisms the platform provides
    - Historical reliability (has this platform had data breaches?)
    - Anti-fraud measures the platform has in place
    - Whether the platform does identity verification
    """

    def __init__(self, cache: TTLCache | None = None):
        self.cache = cache or TTLCache(maxsize=1000, ttl=86400)
        self.logger = StructuredLogger("evidence.source_reputation")

        # Base reputation scores per source type
        # These are static baselines that can be overridden by tenant config
        self.base_reputation: dict[EvidenceSourceType, SourceReputation] = {
            EvidenceSourceType.GITHUB: SourceReputation(
                base_score=0.95,
                platform="GitHub",
                trust_level="high",
                has_identity_verification=False,
                has_anti_fraud=True,
                known_breaches=[],
                verification_methods=["OAuth", "SSH key", "GP2"],
                notes="Industry standard for code contributions. Email verification required.",
            ),
            EvidenceSourceType.CERTIFICATION: SourceReputation(
                base_score=0.85,
                platform="Certification Provider",
                trust_level="high",
                has_identity_verification=True,
                has_anti_fraud=True,
                known_breaches=[],
                verification_methods=["Badge API", "Open Badges", "Credential ID lookup"],
                notes="Varies by provider. Credly/Acclaim are gold standard. Self-hosted certs are lower trust.",
            ),
            EvidenceSourceType.PROJECT: SourceReputation(
                base_score=0.70,
                platform="Project Hosting",
                trust_level="medium",
                has_identity_verification=False,
                has_anti_fraud=False,
                known_breaches=[],
                verification_methods=["URL verification", "Git metadata"],
                notes="Trust depends on hosting platform. GitHub-hosted projects inherit GitHub trust.",
            ),
            EvidenceSourceType.HACKATHON: SourceReputation(
                base_score=0.60,
                platform="Devpost / Hackathon Platform",
                trust_level="medium",
                has_identity_verification=False,
                has_anti_fraud=False,
                known_breaches=[],
                verification_methods=["Devpost API", "Submission URL"],
                notes="Hackathons vary widely in verification rigor. Major ones (Devpost, MLH) are more reliable.",
            ),
            EvidenceSourceType.FREELANCE: SourceReputation(
                base_score=0.65,
                platform="Upwork / Fiverr / Freelance",
                trust_level="medium",
                has_identity_verification=True,
                has_anti_fraud=True,
                known_breaches=[],
                verification_methods=["Platform API", "Contract records", "Payment verification"],
                notes="Upwork has stronger verification than Fiverr. Payment data is reliable signal.",
            ),
            EvidenceSourceType.OPENSOURCE: SourceReputation(
                base_score=0.80,
                platform="Package Registry",
                trust_level="high",
                has_identity_verification=False,
                has_anti_fraud=True,
                known_breaches=[],
                verification_methods=["Registry API", "Package metadata", "Download stats"],
                notes="npm, PyPI, crates.io have different verification levels. PyPI has minimal identity check.",
            ),
            EvidenceSourceType.ASSESSMENT: SourceReputation(
                base_score=0.90,
                platform="ARIA Assessment Engine",
                trust_level="high",
                has_identity_verification=True,
                has_anti_fraud=True,
                known_breaches=[],
                verification_methods=["Cryptographic signature", "Session audit", "Proctoring logs"],
                notes="Assessment engine has built-in anti-cheating (SkillAssessment.md §7). Highest trust source.",
            ),
            EvidenceSourceType.WORK_EXPERIENCE: SourceReputation(
                base_score=0.50,
                platform="LinkedIn / Resume",
                trust_level="low",
                has_identity_verification=False,
                has_anti_fraud=False,
                known_breaches=["LinkedIn 2021 data scrape"],
                verification_methods=["LinkedIn API", "Work email verification", "Manager reference"],
                notes="LinkedIn experience claims are notoriously unreliable. Requires additional verification.",
            ),
        }

    async def get_reputation(
        self, source_type: EvidenceSourceType, metadata: dict
    ) -> SourceReputationResult:
        """Get the reputation score for a source, with runtime adjustments."""
        cache_key = f"source_reputation:{source_type.value}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        base = self.base_reputation.get(
            source_type,
            SourceReputation(base_score=0.5, platform="Unknown", trust_level="unknown")
        )

        # Runtime adjustments based on metadata
        adjusted_score = base.base_score

        # Adjust for known providers within a source type
        if source_type == EvidenceSourceType.CERTIFICATION:
            provider = (metadata.get("provider") or "").lower()
            provider_adjustments = {
                "credly": 0.05,
                "acclaim": 0.05,
                "aws": 0.03,
                "google": 0.03,
                "microsoft": 0.03,
                "coursera": 0.02,
                "edx": 0.02,
                "udemy": -0.10,  # Udemy certs are less trusted
                "unknown": -0.10,
            }
            adjusted_score += provider_adjustments.get(provider, -0.05)

        elif source_type == EvidenceSourceType.FREELANCE:
            platform = (metadata.get("platform") or "").lower()
            platform_adjustments = {
                "upwork": 0.05,
                "toptal": 0.10,
                "fiverr": -0.05,
                "freelancer": -0.05,
            }
            adjusted_score += platform_adjustments.get(platform, 0.0)

        elif source_type == EvidenceSourceType.PROJECT:
            url = (metadata.get("url") or "").lower()
            if "github.com" in url:
                adjusted_score += 0.10  # Inherits GitHub trust
            elif "gitlab.com" in url:
                adjusted_score += 0.08
            elif "bitbucket.org" in url:
                adjusted_score += 0.05

        # Clamp to [0.0, 1.0]
        adjusted_score = max(0.0, min(1.0, adjusted_score))

        result = SourceReputationResult(
            score=adjusted_score,
            platform=base.platform,
            trust_level=base.trust_level,
            has_identity_verification=base.has_identity_verification,
            has_anti_fraud=base.has_anti_fraud,
            details={
                "base_score": base.base_score,
                "adjustment": round(adjusted_score - base.base_score, 4),
                "adjustment_reason": "Provider/domain adjustment" if adjusted_score != base.base_score else "None",
            },
        )

        self.cache.set(cache_key, result)
        return result


@dataclass
class SourceReputation:
    base_score: float
    platform: str
    trust_level: str                    # low | medium | high
    has_identity_verification: bool
    has_anti_fraud: bool
    known_breaches: list[str]
    verification_methods: list[str]
    notes: str


@dataclass
class SourceReputationResult:
    score: float
    platform: str
    trust_level: str
    has_identity_verification: bool
    has_anti_fraud: bool
    details: dict
```

### 4.5 Chain of Custody

Chain of custody ensures that evidence hasn't been tampered with since collection. Every state transition is cryptographically hashed and linked.

```python
class ChainOfCustodyTracker:
    """
    Tracks and validates the cryptographic chain of custody for evidence.

    Each evidence state transition creates a hash link:
    previous_hash = hash(previous_state)
    current_hash  = hash(current_state + previous_hash)

    This creates an immutable chain that proves:
    1. The evidence hasn't been tampered with since collection
    2. Every state transition is recorded and auditable
    3. Any tampering breaks the chain and is immediately detectable
    """

    def __init__(self):
        self.logger = StructuredLogger("evidence.chain_of_custody")

    async def validate(self, item: EvidenceItem) -> CustodyResult:
        """
        Validate the chain of custody for an evidence item.
        Checks the hash chain integrity.
        """
        checks = []
        failures = []

        # Check 1: Current hash exists
        has_current_hash = bool(item.signed_hash)
        checks.append(has_current_hash)
        if not has_current_hash:
            failures.append("Evidence has no signed hash")

        # Check 2: Current hash is valid (re-compute and compare)
        if has_current_hash:
            expected_hash = self._compute_hash(item)
            hash_valid = item.signed_hash == expected_hash
            checks.append(hash_valid)
            if not hash_valid:
                failures.append("Current hash mismatch — evidence may be tampered")

        # Check 3: Previous hash forms a valid chain (if not the first state)
        if item.previous_hash:
            previous_valid = await self._verify_previous_hash(
                item.evidence_id, item.previous_hash
            )
            checks.append(previous_valid)
            if not previous_valid:
                failures.append("Previous hash mismatch — chain broken")
        else:
            # First state — no previous hash expected
            checks.append(True)

        # Check 4: Timestamps are monotonic (created <= updated)
        ts_ordered = item.created_at <= item.updated_at if item.updated_at else True
        checks.append(ts_ordered)
        if not ts_ordered:
            failures.append("Timestamp inconsistency: created_at > updated_at")

        # Check 5: State transitions are valid
        if item.state:
            state_valid = await self._validate_state_transition(item)
            checks.append(state_valid)
            if not state_valid:
                failures.append(f"Invalid state transition to {item.state.value}")

        # Check 6: Evidence hasn't been altered after finalization
        if item.state in (EvidenceState.VERIFIED, EvidenceState.REJECTED, EvidenceState.ACTIVE):
            not_altered = await self._check_not_modified_since_finalization(item)
            checks.append(not_altered)
            if not not_altered:
                failures.append("Evidence modified after finalization")

        pass_count = sum(1 for c in checks if c)
        total = len(checks)
        score = pass_count / total if total > 0 else 0.0

        # Zero score if critical hash checks fail
        if not has_current_hash or (has_current_hash and hash_valid is False):
            score = 0.0

        return CustodyResult(
            score=score,
            hash_integrity=not failures or "Current hash mismatch" not in str(failures),
            chain_intact="chain broken" not in str(failures).lower(),
            timestamp_consistent=ts_ordered,
            state_transition_valid="Invalid state transition" not in str(failures),
            failure_reason="; ".join(failures) if failures else None,
            details={
                "checks_passed": pass_count,
                "checks_total": total,
                "failures": failures,
                "evidence_state": item.state.value if item.state else "unknown",
                "hash_algorithm": "SHA-256",
            },
        )

    def _compute_hash(self, item: EvidenceItem) -> str:
        """
        Compute the cryptographic hash for an evidence item.
        Uses all meaningful fields to detect any tampering.
        """
        import hashlib
        payload = (
            f"{item.evidence_id}|"
            f"{item.user_id}|"
            f"{item.source_type.value}|"
            f"{item.state.value if item.state else ''}|"
            f"{item.title}|"
            f"{item.description}|"
            f"{item.url}|"
            f"{json.dumps(item.metadata, sort_keys=True)}|"
            f"{item.collected_at}|"
            f"{item.verified_at}|"
            f"{item.previous_hash or ''}|"
            f"{item.quality_score}|"
            f"{item.trust_score}|"
            f"{item.weight}"
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    async def _verify_previous_hash(self, evidence_id: str, previous_hash: str) -> bool:
        """Verify that the previous hash matches the stored previous state."""
        # In production: fetch previous state from DB and recompute
        return True

    async def _validate_state_transition(self, item: EvidenceItem) -> bool:
        """Validate that the current state is reachable from the previous state."""
        valid_transitions = {
            EvidenceState.RAW: [EvidenceState.PENDING_VERIFICATION, EvidenceState.REJECTED],
            EvidenceState.PENDING_VERIFICATION: [
                EvidenceState.VERIFIED, EvidenceState.REJECTED,
                EvidenceState.FLAGGED, EvidenceState.VERIFIED_AUTO,
                EvidenceState.VERIFIED_AI,
            ],
            EvidenceState.VERIFIED: [EvidenceState.ACTIVE, EvidenceState.EXPIRED, EvidenceState.FLAGGED],
            EvidenceState.VERIFIED_AUTO: [EvidenceState.ACTIVE, EvidenceState.VERIFIED_AI, EvidenceState.EXPIRED],
            EvidenceState.VERIFIED_AI: [EvidenceState.ACTIVE, EvidenceState.VERIFIED_HUMAN, EvidenceState.EXPIRED],
            EvidenceState.VERIFIED_HUMAN: [EvidenceState.ACTIVE, EvidenceState.EXPIRED],
            EvidenceState.ACTIVE: [EvidenceState.EXPIRED, EvidenceState.FLAGGED, EvidenceState.REJECTED],
            EvidenceState.REJECTED: [EvidenceState.PENDING_VERIFICATION],  # Appeal
            EvidenceState.FLAGGED: [EvidenceState.PENDING_VERIFICATION, EvidenceState.REJECTED],
            EvidenceState.EXPIRED: [EvidenceState.PENDING_VERIFICATION, EvidenceState.REJECTED],
        }
        # In production: fetch previous state
        return True

    async def _check_not_modified_since_finalization(self, item: EvidenceItem) -> bool:
        """Check that evidence wasn't modified after reaching a final state."""
        # In production: compare current hash with hash at finalization time
        return True


@dataclass
class CustodyResult:
    score: float
    hash_integrity: bool
    chain_intact: bool
    timestamp_consistent: bool
    state_transition_valid: bool
    failure_reason: str | None
    details: dict
```

### 4.6 Identity Binding

Identity binding answers: *"Does this evidence truly belong to this user?"* It's the most critical trust component — even authentic evidence from a trustworthy source is worthless if it belongs to someone else.

```python
class IdentityBindingService:
    """
    Verifies that evidence is cryptographically and contextually bound
    to the user claiming it.

    Binding methods (in order of strength):
    1. OAuth identity match — the evidence came from an OAuth-linked account
    2. Email domain match — the user's email domain matches the evidence context
    3. Profile cross-reference — the evidence subject matches user's profile data
    4. Cryptographic signature — the user signed the evidence submission
    5. Behavioral consistency — the evidence pattern matches user's history
    """

    def __init__(self):
        self.logger = StructuredLogger("evidence.identity_binding")

    async def bind(self, item: EvidenceItem) -> IdentityBindingResult:
        """
        Compute identity binding strength for an evidence item.
        """
        checks = []
        failures = []
        binding_methods_used = []

        # Check 1: OAuth identity link (strongest signal)
        oauth_linked = await self._check_oauth_link(item)
        checks.append(oauth_linked)
        if oauth_linked:
            binding_methods_used.append("oauth")
        else:
            failures.append("No OAuth identity link found")

        # Check 2: Email domain consistency
        email_match = await self._check_email_domain(item)
        checks.append(email_match)
        if email_match:
            binding_methods_used.append("email_domain")
        else:
            failures.append("Email domain does not match evidence context")

        # Check 3: Profile cross-reference
        profile_match = await self._check_profile_cross_reference(item)
        checks.append(profile_match)
        if profile_match:
            binding_methods_used.append("profile_cross_ref")
        else:
            failures.append("Evidence subject doesn't match user profile")

        # Check 4: Cryptographic submission signature
        has_signature = bool(item.metadata.get("submission_signature"))
        checks.append(has_signature)
        if has_signature:
            sig_valid = await self._verify_submission_signature(
                item.user_id, item.metadata["submission_signature"]
            )
            checks.append(sig_valid)
            binding_methods_used.append("crypto_signature")
            if not sig_valid:
                failures.append("Submission signature invalid")
        else:
            failures.append("No cryptographic submission signature")

        # Check 5: Collection account ownership verification
        if item.credentials_used:
            owns_account = await self._verify_account_ownership(
                item.user_id, item.credentials_used, item.source_type
            )
            checks.append(owns_account)
            if owns_account:
                binding_methods_used.append("account_ownership")
            else:
                failures.append("Account ownership verification failed")
        else:
            checks.append(False)
            failures.append("No credentials reference for account ownership check")

        pass_count = sum(1 for c in checks if c)
        total = len(checks)

        # Score: higher weight for stronger binding methods
        score_weights = {
            "oauth": 0.35,
            "crypto_signature": 0.25,
            "account_ownership": 0.20,
            "email_domain": 0.10,
            "profile_cross_ref": 0.10,
        }
        weighted_score = sum(
            score_weights.get(method, 0.0) for method in binding_methods_used
        )

        # Bonus for multiple binding methods
        if len(binding_methods_used) >= 3:
            weighted_score = min(1.0, weighted_score * 1.2)
        elif len(binding_methods_used) >= 2:
            weighted_score = min(1.0, weighted_score * 1.1)

        # Zero score if no binding methods at all
        if not binding_methods_used:
            weighted_score = 0.0

        return IdentityBindingResult(
            score=weighted_score,
            oauth_linked=oauth_linked,
            email_domain_match=email_match,
            profile_matches=profile_match,
            has_submission_signature=has_signature,
            binding_methods=binding_methods_used,
            failure_reason="; ".join(failures) if failures else None,
            details={
                "binding_methods_used": binding_methods_used,
                "binding_methods_count": len(binding_methods_used),
                "weighted_score": round(weighted_score, 4),
                "total_checks": total,
                "passed_checks": pass_count,
            },
        )

    async def _check_oauth_link(self, item: EvidenceItem) -> bool:
        """Check if the evidence came from an OAuth-linked account."""
        # In production: verify that the credentials_used reference points
        # to a valid OAuth token linked to this user
        return bool(item.credentials_used)

    async def _check_email_domain(self, item: EvidenceItem) -> bool:
        """Check if the user's email domain matches evidence context."""
        # In production: extract domain from user's primary email
        # and check if it matches the evidence platform or organization
        return True

    async def _check_profile_cross_reference(self, item: EvidenceItem) -> bool:
        """Check if evidence subject matches user's profile data."""
        # In production: compare names, locations, URLs, etc.
        return True

    async def _verify_submission_signature(self, user_id: str, signature: str) -> bool:
        """Verify the user's cryptographic submission signature."""
        # In production: use user's public key to verify signature
        return True

    async def _verify_account_ownership(
        self, user_id: str, credential_ref: str, source_type: EvidenceSourceType
    ) -> bool:
        """Verify that the user still owns the linked account."""
        # In production: check that the OAuth token is still valid
        # and the account is still linked to this user
        return True


    binding_methods: list[str]
    failure_reason: str | None
    details: dict
```


---
## 5. Evidence Weighting Logic

### 5.1 Weight Formula

Evidence weight determines how much a piece of evidence contributes to the skill confidence calculation. The weight is **not** simply the quality score — it's a composite of quality, trust, recency, and context.

```
Evidence_Weight = Base_Quality × Trust_Score × Recency_Multiplier × Context_Adjustment

Where:
  Base_Quality         = skills.md §11 Gold/Silver/Bronze tier mapping  [0.1, 1.0]
  Trust_Score          = Multiplicative trust from §4                   [0.0, 1.0]
  Recency_Multiplier   = Decay based on evidence age                    [0.3, 1.0]
  Context_Adjustment   = Skill-level cap, diversity bonus, dep. weight  [0.5, 1.5]
```

The weight is always gated by trust: if `Trust_Score < min_trust_threshold (0.3)`, the weight is forced to zero regardless of quality.

### 5.2 Weight Calculator

```python
class EvidenceWeightCalculator:
    """
    Computes the final weight for each evidence item.
    Weight determines how much this evidence contributes to
    the skill confidence calculation.
    """

    def __init__(self, config: WeightConfig | None = None):
        self.config = config or WeightConfig()
        self.logger = StructuredLogger("evidence.weight")

    async def compute_weight(
        self,
        item: EvidenceItem,
        trust_result: TrustScoreResult,
        skill_level: str | None = None,
        cross_ref_data: SkillCrossReference | None = None,
    ) -> WeightedEvidence:
        """
        Compute the final weight for an evidence item.

        Pipeline:
        1. Validate trust threshold (gate)
        2. Map base quality
        3. Apply recency decay
        4. Apply context adjustments (level cap, diversity bonus, dependency)
        5. Multiply all factors
        6. Apply per-source max weight cap
        """
        start = time.time()

        # Step 1: Trust gate
        if trust_result.trust_score < self.config.min_trust_threshold:
            return WeightedEvidence(
                evidence_id=item.evidence_id,
                base_quality=item.quality_score,
                trust_score=trust_result.trust_score,
                recency_multiplier=0.0,
                context_adjustment=0.0,
                final_weight=0.0,
                broken_at="trust_gate",
                reason=f"Trust score {trust_result.trust_score:.2f} below threshold",
                computed_at=int(time.time() * 1000),
                duration_ms=int((time.time() - start) * 1000),
            )

        if trust_result.trust_score == 0.0:
            return WeightedEvidence(
                evidence_id=item.evidence_id,
                base_quality=item.quality_score,
                trust_score=0.0,
                recency_multiplier=0.0,
                context_adjustment=0.0,
                final_weight=0.0,
                broken_at="trust_zero",
                reason=trust_result.reason,
                computed_at=int(time.time() * 1000),
                duration_ms=int((time.time() - start) * 1000),
            )

        # Step 2: Base quality
        base_quality = item.quality_score if item.quality_score > 0.0 else self.config.default_base_quality

        # Step 3: Recency decay
        recency = self._compute_recency_multiplier(item)

        # Step 4: Context adjustments
        context = await self._compute_context_adjustment(item, skill_level, cross_ref_data)

        # Step 5: Final weight
        final_weight = base_quality * trust_result.trust_score * recency * context.adjustment

        # Step 6: Source-specific max cap
        max_cap = self.config.max_weight_per_source.get(item.source_type, self.config.default_max_weight)
        final_weight = min(final_weight, max_cap)
        final_weight = max(0.0, final_weight)

        duration = int((time.time() - start) * 1000)

        return WeightedEvidence(
            evidence_id=item.evidence_id,
            base_quality=base_quality,
            trust_score=trust_result.trust_score,
            recency_multiplier=recency,
            context_adjustment=context.adjustment,
            adjustment_reasons=context.reasons,
            final_weight=final_weight,
            computed_at=int(time.time() * 1000),
            duration_ms=duration,
        )

    def _compute_recency_multiplier(self, item: EvidenceItem) -> float:
        """Compute recency decay using exponential half-life decay."""
        age_days = (time.time() - item.collected_at / 1000) / 86400 if item.collected_at else 0
        if age_days <= 0:
            return 1.0

        half_life_days = self.config.recency_half_life.get(item.source_type, self.config.default_half_life_days)

        # No decay for lifetime certifications
        if item.source_type == EvidenceSourceType.CERTIFICATION:
            if not item.metadata.get("expires_at"):
                return 1.0

        half_lives = age_days / half_life_days
        return max(self.config.min_recency_multiplier, 2.0 ** (-half_lives))

    async def _compute_context_adjustment(
        self, item: EvidenceItem, skill_level: str | None, cross_ref_data: SkillCrossReference | None
    ) -> ContextAdjustment:
        reasons = []
        adjustment = 1.0

        if skill_level:
            level_cap = self.config.level_weight_caps.get(skill_level, self.config.default_level_cap)
            if adjustment > level_cap:
                adjustment = level_cap
                reasons.append(f"level_cap({skill_level}): {level_cap}")

        if cross_ref_data and cross_ref_data.source_count >= 2:
            diversity_bonus = 1.0 + (cross_ref_data.synergy_multiplier - 1.0) * self.config.diversity_bonus_weight
            adjustment *= diversity_bonus
            reasons.append(f"diversity_bonus({cross_ref_data.source_count}sources): {diversity_bonus:.3f}")

        dependency_bonus = self._check_dependency_bonus(item)
        if dependency_bonus > 1.0:
            adjustment *= dependency_bonus
            reasons.append(f"dependency_bonus: {dependency_bonus:.3f}")

        return ContextAdjustment(adjustment=min(adjustment, self.config.max_context_adjustment), reasons=reasons)

    def _check_dependency_bonus(self, item: EvidenceItem) -> float:
        """Foundational skills get weight bonus."""
        return 1.0


@dataclass
class WeightConfig:
    min_trust_threshold: float = 0.3
    min_recency_multiplier: float = 0.3
    default_base_quality: float = 0.3
    default_half_life_days: float = 365.0
    default_max_weight: float = 1.0
    max_context_adjustment: float = 1.5
    diversity_bonus_weight: float = 0.5
    recency_half_life: dict[EvidenceSourceType, float] = None
    level_weight_caps: dict[str, float] = None
    max_weight_per_source: dict[EvidenceSourceType, float] = None

    def __post_init__(self):
        if self.recency_half_life is None:
            self.recency_half_life = {
                EvidenceSourceType.GITHUB: 180.0, EvidenceSourceType.PROJECT: 365.0,
                EvidenceSourceType.CERTIFICATION: 730.0, EvidenceSourceType.HACKATHON: 365.0,
                EvidenceSourceType.FREELANCE: 365.0, EvidenceSourceType.OPENSOURCE: 365.0,
                EvidenceSourceType.ASSESSMENT: 90.0, EvidenceSourceType.WORK_EXPERIENCE: 365.0,
            }
        if self.level_weight_caps is None:
            self.level_weight_caps = {
                "beginner": 0.5, "intermediate": 0.75, "advanced": 1.0, "expert": 1.0, "master": 1.0,
            }
        if self.max_weight_per_source is None:
            self.max_weight_per_source = {
                EvidenceSourceType.GITHUB: 0.9, EvidenceSourceType.PROJECT: 1.0,
                EvidenceSourceType.CERTIFICATION: 0.85, EvidenceSourceType.HACKATHON: 0.7,
                EvidenceSourceType.FREELANCE: 0.8, EvidenceSourceType.OPENSOURCE: 0.75,
                EvidenceSourceType.ASSESSMENT: 1.0, EvidenceSourceType.WORK_EXPERIENCE: 0.8,
            }


@dataclass
class WeightedEvidence:
    evidence_id: str
    base_quality: float
    trust_score: float
    recency_multiplier: float
    context_adjustment: float
    adjustment_reasons: list[str] = None
    final_weight: float = 0.0
    broken_at: str | None = None
    reason: str = ""
    computed_at: int = 0
    duration_ms: int = 0


@dataclass
class ContextAdjustment:
    adjustment: float
    reasons: list[str]
```

### 5.3 Quality Tier Mapper

Maps evidence quality scores to Gold/Silver/Bronze from skills.md §11.

```python
class QualityTierMapper:
    """Maps evidence quality scores to Gold/Silver/Bronze tier system."""

    def __init__(self):
        self.tier_ranges = {"gold": (0.85, 1.0), "silver": (0.60, 0.85), "bronze": (0.30, 0.60), "unverified": (0.0, 0.30)}

    def assign_tier(self, item: EvidenceItem) -> str:
        score = item.quality_score
        if score >= 0.85 and item.verification_method == "human":
            return "gold"
        if score >= 0.60 and item.verification_method in ("ai", "human"):
            return "silver"
        if score >= 0.30 and item.verification_method == "auto":
            return "bronze"
        return "unverified"

    def meets_minimum_for_level(self, item: EvidenceItem, target_skill_level: str) -> bool:
        tier = self.assign_tier(item)
        min_tier = {"beginner": "bronze", "intermediate": "silver", "advanced": "silver", "expert": "gold", "master": "gold"}
        required = min_tier.get(target_skill_level, "bronze")
        tier_order = ["unverified", "bronze", "silver", "gold"]
        return tier_order.index(tier) >= tier_order.index(required)
```

### 5.4 Evidence Aggregator

```python
class EvidenceAggregator:
    """Aggregates weighted evidence into combined strength per skill."""

    def __init__(self):
        self.logger = StructuredLogger("evidence.aggregator")

    async def aggregate_for_skill(self, skill_id: str, items: list[WeightedEvidence]) -> SkillEvidenceSummary:
        valid = [e for e in items if e.final_weight > 0.0]
        if not valid:
            return SkillEvidenceSummary(skill_id=skill_id, total_evidence_count=0, primary_evidence_count=0,
                total_weight=0.0, effective_strength=0.0, source_diversity=0, top_evidence=[], estimated_tier="unverified")

        valid.sort(key=lambda e: e.final_weight, reverse=True)
        top_k = valid[:5]
        total_weight = sum(e.final_weight for e in valid)
        effective_strength = self._compute_effective_strength(valid, top_k)
        estimated_tier = self._estimate_tier(effective_strength)

        return SkillEvidenceSummary(skill_id=skill_id, total_evidence_count=len(valid),
            primary_evidence_count=len(top_k), total_weight=total_weight, effective_strength=effective_strength,
            source_diversity=0, top_evidence=[e.evidence_id for e in top_k], estimated_tier=estimated_tier)

    def _compute_effective_strength(self, all_items: list[WeightedEvidence], top_items: list[WeightedEvidence]) -> float:
        primary_sum = sum(e.final_weight for e in top_items)
        additional = all_items[5:]
        extra_contribution = math.log(1 + sum(e.final_weight for e in additional)) * 0.5 if additional else 0.0
        return min(primary_sum + extra_contribution, 10.0)

    def _estimate_tier(self, strength: float) -> str:
        if strength >= 5.0: return "gold"
        if strength >= 3.0: return "silver"
        if strength >= 1.0: return "bronze"
        return "unverified"


@dataclass
class SkillEvidenceSummary:
    skill_id: str
    total_evidence_count: int
    primary_evidence_count: int
    total_weight: float
    effective_strength: float
    source_diversity: int
    top_evidence: list[str]
    estimated_tier: str
```


---
## 6. AI Validation Engine

### 6.1 Overview

The AI Validation Engine uses LLMs to validate evidence authenticity and detect inconsistencies that algorithmic checks miss. It follows the PromptLoader pattern from SkillAssessment.md — prompts live in `prompts/agents/evidence_validator.md` with inline fallbacks.

AI validation is **Tier 2** verification — it kicks in when auto-verification is inconclusive, and can be bypassed entirely if cross-referencing provides sufficient trust.

```python
class AIEvidenceValidator:
    """
    AI-powered evidence validation using LLM classification.

    Capabilities:
    1. Authenticity classification — real or fabricated?
    2. Inconsistency detection — does the evidence contradict itself?
    3. Exaggeration detection — are claims inflated?
    4. Cross-source coherence — matches other evidence for this user?
    5. Anomaly flagging — deviates from expected patterns?

    Uses PromptLoader with graceful fallback to inline defaults.
    """

    def __init__(self, config: AIValidatorConfig | None = None):
        self.config = config or AIValidatorConfig()
        self.logger = StructuredLogger("evidence.ai_validator")
        self.llm_client = self._init_llm_client()
        self.prompt_loader = None
        self.metrics = AIValidatorMetrics()

    def _init_llm_client(self):
        return None

    async def authenticate(self, item: EvidenceItem, context: VerificationContext) -> AIValidationResult:
        start = time.time()
        prompt = await self._build_validation_prompt(item, context)
        llm_result = await self._call_llm(prompt, context)
        parsed = self._parse_response(llm_result)
        calibrated = self._calibrate_confidence(parsed)
        duration = int((time.time() - start) * 1000)
        self.metrics.record(item.evidence_id, parsed.confidence, calibrated.confidence, duration, self.config.model)
        return calibrated

    async def _build_validation_prompt(self, item: EvidenceItem, context: VerificationContext) -> str:
        try:
            if self.prompt_loader:
                loaded = self.prompt_loader.get_agent("evidence_validator")
                if loaded:
                    return loaded.render(source_type=item.source_type.value, title=item.title,
                        description=item.description, url=item.url or "N/A",
                        metadata=json.dumps(item.metadata, indent=2)[:2000], user_id=item.user_id)
        except Exception:
            pass

        return f"""You are an evidence authenticity validator.

EVIDENCE TYPE: {item.source_type.value}
TITLE: {item.title}
DESCRIPTION: {item.description[:500] if item.description else 'N/A'}
URL: {item.url or 'N/A'}

METADATA:
{json.dumps(item.metadata, indent=2)[:2000]}

Analyze: Is this authentic or fabricated? Are there inconsistencies?
Respond as JSON:
{{
  "authentic": true/false,
  "confidence": 0.0-1.0,
  "authenticity_score": 0.0-1.0,
  "reasoning": "...",
  "inconsistencies": ["..."],
  "warning_signals": ["..."],
  "verification_suggestions": ["..."]
}}"""

    async def _call_llm(self, prompt: str, context: VerificationContext) -> dict:
        return {"authentic": True, "confidence": 0.85, "authenticity_score": 0.85,
                "reasoning": "Evidence appears authentic.", "inconsistencies": [],
                "warning_signals": [], "verification_suggestions": []}

    def _parse_response(self, result: dict) -> AIValidationResult:
        return AIValidationResult(evidence_id="", authentic=result.get("authentic", False),
            authenticity_score=min(1.0, max(0.0, float(result.get("authenticity_score", 0.0)))),
            confidence=min(1.0, max(0.0, float(result.get("confidence", 0.0)))),
            inconsistencies=result.get("inconsistencies", []),
            warning_signals=result.get("warning_signals", []),
            reasoning=result.get("reasoning", ""),
            verification_suggestions=result.get("verification_suggestions", []),
            calibrated_confidence=0.0, raw_response=result)

    def _calibrate_confidence(self, result: AIValidationResult) -> AIValidationResult:
        calibration_factor = self.metrics.get_calibration_factor()
        result.confidence = min(1.0, max(0.0, 0.5 + (result.confidence - 0.5) * calibration_factor))
        result.authenticity_score = min(1.0, max(0.0, 0.5 + (result.authenticity_score - 0.5) * calibration_factor))
        result.calibrated_confidence = result.confidence
        result.calibrated = True
        return result


@dataclass
class AIValidatorConfig:
    model: str = "claude-sonnet-4"
    temperature: float = 0.1
    max_tokens: int = 2048
    min_confidence_to_accept: float = 0.85
    retry_on_failure: bool = True
    max_retries: int = 2
    calibration_window_size: int = 100
    enable_calibration: bool = True


@dataclass
class AIValidationResult:
    evidence_id: str
    authentic: bool
    authenticity_score: float
    confidence: float
    inconsistencies: list[str]
    warning_signals: list[str]
    reasoning: str
    verification_suggestions: list[str]
    calibrated_confidence: float
    raw_response: dict
    calibrated: bool = False


class AIValidatorMetrics:
    """Tracks accuracy for confidence calibration using ECE."""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.predictions: list[dict] = []

    def record(self, evidence_id: str, raw_confidence: float, calibrated_confidence: float,
               duration_ms: int, model: str) -> None:
        self.predictions.append({"evidence_id": evidence_id, "raw_confidence": raw_confidence,
            "calibrated_confidence": calibrated_confidence, "duration_ms": duration_ms,
            "model": model, "timestamp": time.time()})
        if len(self.predictions) > self.window_size:
            self.predictions.pop(0)

    def get_calibration_factor(self) -> float:
        if len(self.predictions) < 10:
            return 0.8
        return 0.85  # In production: compute ECE


### 6.2 Source-Specific Prompt Templates

The AI validator uses different prompt templates per evidence source type. Each template is optimized for the specific fraud signals and authenticity markers relevant to that source.

```python
class SourceSpecificPromptBuilder:
    """
    Builds source-specific validation prompts for the AI validator.
    Each source type has unique authenticity markers and fraud patterns
    that the LLM should check.
    """

    SOURCE_PROMPTS: dict[EvidenceSourceType, str] = {
        EvidenceSourceType.CERTIFICATION: """
You are validating a professional certification credential.

CERTIFICATION: {title}
PROVIDER: {provider}
CREDENTIAL ID: {credential_id}
ISSUER: {issuer}
ISSUE DATE: {issue_date}
EXPIRY: {expiry}
VERIFICATION URL: {verify_url}

Check these specific authenticity markers:
1. Is the provider a legitimate certification authority?
2. Does the credential ID format match the provider's standard format?
3. Is the issuer name spelled correctly (not a misspelling of a known issuer)?
4. Does the verification URL domain belong to the legitimate provider?
5. Is the issue date plausible (not in the future, not >20 years ago)?
6. Does the credential name follow the provider's naming convention?
""",
        EvidenceSourceType.GITHUB: """
You are validating GitHub contribution evidence.

GITHUB USER: {username}
ACCOUNT AGE: {account_age_days} days
PUBLIC REPOS: {public_repos}
FOLLOWERS: {followers}
CONTRIBUTION STREAK: {streak_days} days
LANGUAGES: {languages}

Check these specific authenticity markers:
1. Does the contribution pattern look organic (not bot-like)?
2. Are the number of contributions proportional to account age?
3. Is the language distribution consistent with someone learning?
4. Are there signs of automated or systematically fake contributions?
5. Does the follower/following ratio appear natural?
""",
        EvidenceSourceType.PROJECT: """
You are validating a project submission.

PROJECT: {title}
DESCRIPTION: {description}
URL: {url}
LANGUAGE: {language}
STARS: {stars}
SIZE: {size} bytes
LAST UPDATED: {last_updated}

Check these specific authenticity markers:
1. Is this a real, substantive project or a template/starter repo?
2. Are the project metrics (stars, forks) proportional to content?
3. Does the description match the apparent scope of the project?
4. Is the project recent enough to be relevant?
5. Does the project demonstrate the claimed skill level?
""",
        EvidenceSourceType.WORK_EXPERIENCE: """
You are validating a work experience claim.

COMPANY: {company}
TITLE: {title}
DATES: {start_date} - {end_date}
DESCRIPTION: {description}
INDUSTRY: {industry}

Check these specific authenticity markers:
1. Is the company a legitimate organization?
2. Is the job title realistic for the described responsibilities?
3. Are the employment dates reasonable (not overlapping implausibly)?
4. Does the description use authentic industry language?
5. Are the claimed skills and technologies consistent with the role?
""",
        EvidenceSourceType.ASSESSMENT: """
You are validating an assessment result from the ARIA assessment engine.

SKILL: {skill}
SCORE: {score}
DURATION: {duration_minutes} min
QUESTIONS: {questions_count}
COMPLETED: {completed_at}

Check these specific authenticity markers:
1. Is the score consistent with the time taken?
2. Is the completion time realistic for the question count?
3. Does the score distribution look natural?
4. Is the assessment signature valid?
""",
    }

    def build(self, source_type: EvidenceSourceType, metadata: dict) -> str | None:
        """Build a source-specific prompt or return None for generic fallback."""
        template = self.SOURCE_PROMPTS.get(source_type)
        if not template:
            return None
        try:
            return template.format(**metadata)
        except KeyError:
            return None
```

### 6.3 Multi-LLM Router

The AI validator supports multiple LLM providers with automatic failover. If the primary model is unavailable or returns low-confidence results, secondary models are tried.

```python
class MultiLLMRouter:
    """
    Routes validation requests across multiple LLM providers with failover.

    Provider priority:
    1. Claude Sonnet 4 (primary — best accuracy for evidence validation)
    2. GPT-4o (fallback — comparable quality)
    3. Ollama/Mistral (last resort — local, free, lower quality)
    """

    PROVIDER_CONFIG = [
        {"name": "claude-sonnet-4", "provider": "anthropic", "max_retries": 2, "timeout_s": 30},
        {"name": "gpt-4o", "provider": "openai", "max_retries": 1, "timeout_s": 30},
        {"name": "ollama/mistral:7b", "provider": "ollama", "max_retries": 1, "timeout_s": 60},
    ]

    def __init__(self):
        self.logger = StructuredLogger("evidence.ai_router")
        self.current_provider_index = 0

    async def route(
        self, prompt: str, context: VerificationContext
    ) -> tuple[dict, str]:
        """
        Route prompt to the best available LLM with failover.
        Returns (response, model_name).
        """
        errors = []
        for i in range(self.current_provider_index, len(self.PROVIDER_CONFIG)):
            config = self.PROVIDER_CONFIG[i]
            try:
                response = await self._call_provider(prompt, config, context)
                self.current_provider_index = i
                return response, config["name"]
            except Exception as e:
                errors.append(f"{config['name']}: {str(e)}")
                self.logger.warning("Provider failed, trying next", provider=config["name"], error=str(e))
                continue

        self.logger.error("All LLM providers failed", errors=errors)
        return {"authentic": False, "confidence": 0.0, "authenticity_score": 0.0,
                "reasoning": f"All providers failed: {'; '.join(errors)}",
                "inconsistencies": ["LLM unavailable"], "warning_signals": ["All providers failed"],
                "verification_suggestions": ["Queue for human review"]}, "none"

    async def _call_provider(self, prompt: str, config: dict, context: VerificationContext) -> dict:
        """Call a specific LLM provider. In production: use provider SDK."""
        return {"authentic": True, "confidence": 0.85, "authenticity_score": 0.85,
                "reasoning": "Auto-approved (production placeholder)", "inconsistencies": [],
                "warning_signals": [], "verification_suggestions": []}
```

### 6.4 Validation Retry Logic

```python
class ValidationRetryHandler:
    """Handles retry logic for AI validation with exponential backoff."""

    def __init__(self, max_retries: int = 3, base_delay_ms: int = 1000):
        self.max_retries = max_retries
        self.base_delay_ms = base_delay_ms

    async def execute_with_retry(
        self, item: EvidenceItem, validator: AIEvidenceValidator, context: VerificationContext
    ) -> AIValidationResult:
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                result = await validator.authenticate(item, context)
                if result.confidence >= validator.config.min_confidence_to_accept:
                    return result
                if attempt < self.max_retries:
                    delay = self.base_delay_ms * (2 ** attempt) + random.randint(0, 500)
                    await asyncio.sleep(delay / 1000)
            except Exception as e:
                last_error = e
                if attempt < self.max_retries:
                    delay = self.base_delay_ms * (2 ** attempt)
                    await asyncio.sleep(delay / 1000)

        return AIValidationResult(evidence_id=item.evidence_id, authentic=False, authenticity_score=0.0,
            confidence=0.0, inconsistencies=["Max retries exceeded"],
            warning_signals=[f"Validation failed after {self.max_retries} retries: {last_error}"],
            reasoning="Validation unavailable", verification_suggestions=["Queue for human review"],
            calibrated_confidence=0.0, raw_response={})
```
---
## 7. Fraud Detection

### 7.1 Fraud Detection Philosophy

Fraud detection in SkillEvidence.md targets **evidence fraud** — faking credentials, inflating contributions, forging certificates, stealing identity. This is completely separate from SkillAssessment.md §7 Anti-Cheating (assessment-taking fraud).

| Dimension | SkillAssessment.md §7 | SkillEvidence.md §7 |
|---|---|---|
| **Target** | Assessment-taking behavior | Evidence claims |
| **Fraud types** | Copying, impersonation, AI use | Forged credentials, fake repos, cert fraud |
| **Detection** | Behavioral, keystroke, plagiarism | Source verification, cross-ref, AI auth |
| **Output** | Invalid assessment session | Flagged evidence item |

### 7.2 Fraud Detection Engine

```python
class FraudSignalType(str, Enum):
    FORGED_CREDENTIAL = "forged_credential"
    REPO_INFLATION = "repo_inflation"
    CERT_TEMPLATE_FRAUD = "cert_template_fraud"
    IDENTITY_FRAUD = "identity_fraud"
    TEMPORAL_ANOMALY = "temporal_anomaly"
    CROSS_PLATFORM_MISMATCH = "cross_platform_mismatch"
    DUPLICATE_EVIDENCE = "duplicate_evidence"
    PATTERN_ANOMALY = "pattern_anomaly"


@dataclass
class FraudSignal:
    evidence_id: str
    signal_type: FraudSignalType
    confidence: float
    severity_weight: float
    description: str
    details: dict
    detected_at: int


@dataclass
class FraudScanResult:
    evidence_id: str
    signals: list[FraudSignal]
    signal_count: int
    risk_score: float
    is_suspicious: bool
    is_blocked: bool
    scanned_at: int
    duration_ms: int


@dataclass
class FraudContext:
    user_id: str
    tenant_id: str | None = None
    peer_group_data: dict | None = None
    cross_platform_data: dict | None = None


@dataclass
class FraudConfig:
    suspicious_threshold: float = 0.3
    block_threshold: float = 0.7
    enable_all_detectors: bool = True
    notify_on_suspicious: bool = True
    auto_block_on_high_risk: bool = True


class BaseFraudDetector(ABC):
    @abstractmethod
    async def detect(self, item: EvidenceItem, context: FraudContext) -> FraudSignal | None:
        ...

    @abstractmethod
    def applicable_sources(self) -> list[EvidenceSourceType]:
        ...


class FraudDetectionEngine:
    """Detects fraudulent evidence across 8 signal categories."""

    def __init__(self, config: FraudConfig | None = None):
        self.config = config or FraudConfig()
        self.logger = StructuredLogger("evidence.fraud_detection")
        self.detectors: dict[FraudSignalType, BaseFraudDetector] = {
            FraudSignalType.FORGED_CREDENTIAL: ForgedCredentialDetector(),
            FraudSignalType.REPO_INFLATION: RepoInflationDetector(),
            FraudSignalType.CERT_TEMPLATE_FRAUD: CertTemplateFraudDetector(),
            FraudSignalType.IDENTITY_FRAUD: IdentityFraudDetector(),
            FraudSignalType.TEMPORAL_ANOMALY: TemporalAnomalyDetector(),
            FraudSignalType.CROSS_PLATFORM_MISMATCH: CrossPlatformMismatchDetector(),
            FraudSignalType.DUPLICATE_EVIDENCE: DuplicateEvidenceDetector(),
            FraudSignalType.PATTERN_ANOMALY: PatternAnomalyDetector(),
        }

    async def scan(self, item: EvidenceItem, context: FraudContext) -> FraudScanResult:
        start = time.time()
        signals: list[FraudSignal] = []
        for signal_type, detector in self.detectors.items():
            if item.source_type not in detector.applicable_sources():
                continue
            result = await detector.detect(item, context)
            if result:
                signals.append(result)

        risk_score = sum(s.severity_weight for s in signals) / max(len(self.detectors), 1)
        risk_score = min(risk_score, 1.0)

        return FraudScanResult(evidence_id=item.evidence_id, signals=signals, signal_count=len(signals),
            risk_score=risk_score, is_suspicious=risk_score >= self.config.suspicious_threshold,
            is_blocked=risk_score >= self.config.block_threshold,
            scanned_at=int(time.time() * 1000), duration_ms=int((time.time() - start) * 1000))

    async def scan_user(self, user_id: str, all_evidence: list[EvidenceItem]) -> UserFraudProfile:
        signals, flagged = [], []
        for item in all_evidence:
            result = await self.scan(item, FraudContext(user_id=user_id))
            if result.signal_count > 0:
                signals.extend(result.signals)
                flagged.append(item.evidence_id)

        overall_risk = min(sum(s.severity_weight for s in signals) / max(len(signals), 1), 1.0) if signals else 0.0
        return UserFraudProfile(user_id=user_id, total_evidence_flagged=len(flagged), total_signals=len(signals),
            signal_types=list(set(s.signal_type.value for s in signals)), overall_risk_score=overall_risk,
            cross_evidence_patterns=[], flagged_evidence_ids=flagged)


@dataclass
class UserFraudProfile:
    user_id: str
    total_evidence_flagged: int
    total_signals: int
    signal_types: list[str]
    overall_risk_score: float
    cross_evidence_patterns: list
    flagged_evidence_ids: list[str]
```

### 7.3 Forged Credential Detector

```python
class ForgedCredentialDetector(BaseFraudDetector):
    """Detects credentials that don't exist at the source."""

    async def detect(self, item: EvidenceItem, context: FraudContext) -> FraudSignal | None:
        if item.source_type not in self.applicable_sources():
            return None
        metadata = item.metadata
        warnings = []

        credential_id = metadata.get("credential_id") or metadata.get("certificate_id", "")
        provider = (metadata.get("provider") or "").lower()

        if credential_id and provider:
            if not self._validate_format(credential_id, provider):
                warnings.append(f"ID format doesn't match {provider}")

        issue_date = metadata.get("issued_at") or metadata.get("issue_date")
        if isinstance(issue_date, (int, float)):
            if issue_date > time.time() * 1000:
                warnings.append("Issue date is in the future")
            elif issue_date < (time.time() - 86400 * 365 * 20) * 1000:
                warnings.append("Issue date implausibly old")

        if not warnings:
            return None

        return FraudSignal(evidence_id=item.evidence_id, signal_type=FraudSignalType.FORGED_CREDENTIAL,
            confidence=0.8 if len(warnings) >= 2 else 0.5, severity_weight=0.8,
            description="; ".join(warnings), details={"warnings": warnings}, detected_at=int(time.time() * 1000))

    def _validate_format(self, cred_id: str, provider: str) -> bool:
        patterns = {"credly": lambda x: len(x) >= 8, "acclaim": lambda x: len(x) >= 10,
            "coursera": lambda x: x.startswith(("C", "X")), "aws": lambda x: len(x) >= 10,
            "microsoft": lambda x: len(x) >= 10}
        return patterns.get(provider, lambda x: len(x) >= 6)(cred_id)

    def applicable_sources(self) -> list[EvidenceSourceType]:
        return [EvidenceSourceType.CERTIFICATION]
```

### 7.4 Repo Inflation Detector

```python
class RepoInflationDetector(BaseFraudDetector):
    """Detects artificially inflated GitHub statistics."""

    async def detect(self, item: EvidenceItem, context: FraudContext) -> FraudSignal | None:
        if item.source_type not in self.applicable_sources():
            return None
        metadata = item.metadata
        warnings = []
        stars = metadata.get("stars", 0)
        size = metadata.get("size", 0)
        forks = metadata.get("forks", 0)
        commits = metadata.get("total_commits", 0)

        if stars > 0 and size > 0 and stars / size > 0.1:
            warnings.append(f"Suspicious star/size ratio")
        if stars > 0 and forks > 0 and forks / stars < 0.01:
            warnings.append(f"Suspicious fork/star ratio")
        if stars > 10 and size < 10000:
            warnings.append("Stars without content")

        created = metadata.get("created_at")
        if isinstance(created, (int, float)) and stars > 0:
            age_days = (time.time() - created) / 86400
            if age_days < 7 and stars > 50:
                warnings.append(f"Rapid star growth: {stars} in {age_days:.0f}d")

        if stars > 100 and commits < 10:
            warnings.append(f"Stars ({stars}) but few commits ({commits})")

        if not warnings:
            return None
        return FraudSignal(evidence_id=item.evidence_id, signal_type=FraudSignalType.REPO_INFLATION,
            confidence=0.9 if len(warnings) >= 3 else 0.6, severity_weight=0.8,
            description="; ".join(warnings), details={"warnings": warnings}, detected_at=int(time.time() * 1000))

    def applicable_sources(self) -> list[EvidenceSourceType]:
        return [EvidenceSourceType.PROJECT, EvidenceSourceType.GITHUB, EvidenceSourceType.OPENSOURCE]
```

### 7.5 Cert Template Fraud Detector

```python
class CertTemplateFraudDetector(BaseFraudDetector):
    """Detects template-based fake certifications."""

    KNOWN = {"credly", "acclaim", "coursera", "edx", "aws", "google", "microsoft",
             "ibm", "oracle", "cisco", "comptia", "pmi", "sans", "isc2"}
    SUSPICIOUS_DOMAINS = {"certificate.net", "verify-cert.com", "credential.net", "cert-template.com"}

    async def detect(self, item: EvidenceItem, context: FraudContext) -> FraudSignal | None:
        if item.source_type not in self.applicable_sources():
            return None
        metadata = item.metadata
        warnings = []

        provider = (metadata.get("provider") or "").lower()
        if provider and not any(k in provider for k in self.KNOWN):
            warnings.append(f"Unknown provider: {provider}")

        verify_url = metadata.get("verify_url") or metadata.get("url", "")
        if verify_url:
            from urllib.parse import urlparse
            domain = urlparse(verify_url).netloc.lower()
            if any(s in domain for s in self.SUSPICIOUS_DOMAINS):
                warnings.append(f"Suspicious domain: {domain}")

        issuer = (metadata.get("issuer") or "").lower()
        misspellings = {"microsft": "microsoft", "googel": "google", "amzon": "amazon", "orcle": "oracle"}
        for wrong, correct in misspellings.items():
            if wrong in issuer:
                warnings.append(f"Misspelled issuer: '{issuer}'")
                break

        if not metadata.get("credential_id") and not metadata.get("certificate_id"):
            warnings.append("No credential ID")

        if not metadata.get("issued_at") and not metadata.get("issue_date"):
            warnings.append("No issue date")

        if not warnings:
            return None
        return FraudSignal(evidence_id=item.evidence_id, signal_type=FraudSignalType.CERT_TEMPLATE_FRAUD,
            confidence=min(0.95, len(warnings) * 0.2), severity_weight=0.9,
            description="; ".join(warnings), details={"warnings": warnings}, detected_at=int(time.time() * 1000))

    def applicable_sources(self) -> list[EvidenceSourceType]:
        return [EvidenceSourceType.CERTIFICATION]
```

### 7.6 Identity Fraud Detector

```python
class IdentityFraudDetector(BaseFraudDetector):
    """Detects evidence claimed under false identity."""

    async def detect(self, item: EvidenceItem, context: FraudContext) -> FraudSignal | None:
        metadata = item.metadata
        warnings = []

        created = metadata.get("created_at") or metadata.get("account_created")
        if isinstance(created, (int, float)):
            age_days = (time.time() - created) / 86400
            if age_days < 7:
                warnings.append(f"Account only {age_days:.0f} days old")
            elif age_days < 30:
                warnings.append(f"Account relatively new ({age_days:.0f}d)")

        if context.cross_platform_data and item.metadata.get("name"):
            name = (item.metadata["name"] or "").lower()
            for platform, data in context.cross_platform_data.items():
                other = (data.get("name") or "").lower()
                if name and other and name != other:
                    warnings.append(f"Name mismatch with {platform}")

        if not warnings:
            return None
        return FraudSignal(evidence_id=item.evidence_id, signal_type=FraudSignalType.IDENTITY_FRAUD,
            confidence=min(0.9, len(warnings) * 0.25), severity_weight=1.0,
            description="; ".join(warnings), details={"warnings": warnings}, detected_at=int(time.time() * 1000))

    def applicable_sources(self) -> list[EvidenceSourceType]:
        return list(EvidenceSourceType)


class TemporalAnomalyDetector(BaseFraudDetector):
    """Detects suspicious timing patterns."""

    async def detect(self, item: EvidenceItem, context: FraudContext) -> FraudSignal | None:
        metadata = item.metadata
        warnings = []

        created = metadata.get("created_at")
        if isinstance(created, (int, float)):
            hour = datetime.fromtimestamp(created).hour
            if 2 <= hour <= 5:
                warnings.append(f"Created at unusual hour: {hour}:00")

        dates = [metadata.get(k) for k in ["created_at", "issued_at", "collected_at"] if metadata.get(k)]
        if len(dates) >= 3 and len(set(dates)) == 1:
            warnings.append("All dates identical — batch creation")

        for key in ["created_at", "issued_at"]:
            val = metadata.get(key)
            if isinstance(val, (int, float)) and val > 1000000000000 and val % 10000 == 0:
                warnings.append(f"Round timestamp for {key}")

        if not warnings:
            return None
        return FraudSignal(evidence_id=item.evidence_id, signal_type=FraudSignalType.TEMPORAL_ANOMALY,
            confidence=0.6, severity_weight=0.4, description="; ".join(warnings),
            details={"warnings": warnings}, detected_at=int(time.time() * 1000))

    def applicable_sources(self) -> list[EvidenceSourceType]:
        return list(EvidenceSourceType)


class CrossPlatformMismatchDetector(BaseFraudDetector):
    """Detects conflicting identity across platforms."""

    async def detect(self, item: EvidenceItem, context: FraudContext) -> FraudSignal | None:
        if not context.cross_platform_data:
            return None
        warnings = []
        name = (item.metadata.get("name") or item.metadata.get("login", "")).lower()
        for platform, data in context.cross_platform_data.items():
            if platform == item.source_type.value:
                continue
            other = (data.get("name") or "").lower()
            if name and other and not set(name.split()) & set(other.split()):
                warnings.append(f"Name differs on {platform}")
        if not warnings:
            return None
        return FraudSignal(evidence_id=item.evidence_id, signal_type=FraudSignalType.CROSS_PLATFORM_MISMATCH,
            confidence=0.7, severity_weight=0.6, description="; ".join(warnings),
            details={"warnings": warnings}, detected_at=int(time.time() * 1000))

    def applicable_sources(self) -> list[EvidenceSourceType]:
        return list(EvidenceSourceType)


class DuplicateEvidenceDetector(BaseFraudDetector):
    """Detects same evidence claimed multiple times."""

    def __init__(self):
        self.seen: dict[str, set[str]] = {}

    async def detect(self, item: EvidenceItem, context: FraudContext) -> FraudSignal | None:
        if context.user_id not in self.seen:
            self.seen[context.user_id] = set()
        ext_id = item.metadata.get("id") or item.metadata.get("external_id")
        if ext_id and ext_id in self.seen[context.user_id]:
            return FraudSignal(evidence_id=item.evidence_id, signal_type=FraudSignalType.DUPLICATE_EVIDENCE,
                confidence=1.0, severity_weight=0.5, description=f"Duplicate external ID: {ext_id}",
                details={}, detected_at=int(time.time() * 1000))
        if ext_id:
            self.seen[context.user_id].add(ext_id)
        return None

    def applicable_sources(self) -> list[EvidenceSourceType]:
        return list(EvidenceSourceType)


class PatternAnomalyDetector(BaseFraudDetector):
    """Detects statistical outliers in evidence patterns."""

    async def detect(self, item: EvidenceItem, context: FraudContext) -> FraudSignal | None:
        warnings = []
        if len(item.skill_ids) > 10:
            warnings.append(f"Unusually broad: {len(item.skill_ids)} skills")
        stars = item.metadata.get("stars", 0)
        if isinstance(stars, (int, float)) and stars > 10000:
            warnings.append(f"Exceptionally high stars: {stars}")
        if not warnings:
            return None
        return FraudSignal(evidence_id=item.evidence_id, signal_type=FraudSignalType.PATTERN_ANOMALY,
            confidence=0.5, severity_weight=0.3, description="; ".join(warnings),
            details={"warnings": warnings}, detected_at=int(time.time() * 1000))

    def applicable_sources(self) -> list[EvidenceSourceType]:
        return list(EvidenceSourceType)
```


---
## 8. Skill Confidence Calculation

### 8.1 Confidence Formula

Integrates evidence weights, assessment results, and prior knowledge into calibrated confidence per skill.

```
Confidence(skill) = Evidence_Contribution + Assessment_Contribution + Prior

Evidence_Contribution  = Σ(Weight × Impact) / Max_Possible × Evidence_Weight_Pct
Assessment_Contribution = Σ(Assessment_Score) / Count × Assessment_Weight_Pct
Prior                  = Base_Probability × Prior_Weight_Pct
```

### 8.2 Confidence Engine

```python
class SkillConfidenceEngine:
    """Computes calibrated skill confidence using evidence + assessments + priors."""

    def __init__(self, config: ConfidenceConfig | None = None):
        self.config = config or ConfidenceConfig()
        self.logger = StructuredLogger("evidence.confidence")
        self.aggregator = EvidenceAggregator()
        self.classifier = SkillLevelClassifier()

    async def compute(self, user_id: str, skill_id: str,
                      weighted_evidence: list[WeightedEvidence],
                      assessment_results: list[AssessmentResult] | None = None,
                      prior: PriorData | None = None) -> SkillConfidence:
        start = time.time()

        # Evidence contribution
        summary = await self.aggregator.aggregate_for_skill(skill_id, weighted_evidence)
        ev_contrib = summary.effective_strength / 10.0 * self.config.evidence_weight

        # Assessment contribution
        as_contrib = 0.0
        as_count = 0
        if assessment_results:
            valid = [a for a in assessment_results if a.skill_id == skill_id and a.passed]
            if valid:
                as_contrib = sum(a.score for a in valid) / len(valid) * self.config.assessment_weight
                as_count = len(valid)

        # Prior contribution
        prior_prob = prior.base_probability if prior else 0.1
        prior_contrib = prior_prob * self.config.prior_weight

        # Normalize
        max_possible = self.config.evidence_weight + self.config.assessment_weight + self.config.prior_weight
        raw = ev_contrib + as_contrib + prior_contrib
        confidence = min(raw / max_possible, 1.0) if max_possible > 0 else 0.0

        # Recency
        recency = self._recency_factor(weighted_evidence, assessment_results)
        confidence *= recency

        # Level
        level = self.classifier.classify(confidence, summary.estimated_tier)

        # Interval
        total_points = summary.total_evidence_count + as_count * 3
        half = max(0.05, 0.35 - total_points * 0.015)

        return SkillConfidence(skill_id=skill_id, confidence_score=confidence, level=level,
            evidence_contribution=ev_contrib, assessment_contribution=as_contrib, prior_contribution=prior_contrib,
            evidence_summary=summary, assessment_summary={"score": as_contrib, "count": as_count},
            confidence_interval=ConfidenceInterval(lower=max(0, confidence - half), upper=min(1, confidence + half),
                confidence_level=0.95, data_points=total_points),
            computed_at=int(time.time() * 1000), duration_ms=int((time.time() - start) * 1000))

    def _recency_factor(self, evidence: list[WeightedEvidence], assessments: list | None) -> float:
        latest = max([e.computed_at for e in evidence] + [0])
        if assessments:
            for a in assessments:
                if hasattr(a, 'completed_at') and a.completed_at and a.completed_at > latest:
                    latest = a.completed_at
        if latest == 0:
            return 1.0
        age_days = (time.time() - latest / 1000) / 86400
        if age_days < 30: return 1.0
        if age_days < 90: return 0.95
        if age_days < 180: return 0.85
        if age_days < 365: return 0.70
        return 0.50


@dataclass
class ConfidenceConfig:
    evidence_weight: float = 0.50
    assessment_weight: float = 0.35
    prior_weight: float = 0.15
    min_evidence_for_confidence: int = 1


@dataclass
class SkillConfidence:
    skill_id: str
    confidence_score: float
    level: str
    evidence_contribution: float
    assessment_contribution: float
    prior_contribution: float
    evidence_summary: SkillEvidenceSummary
    assessment_summary: dict
    confidence_interval: ConfidenceInterval
    computed_at: int
    duration_ms: int


@dataclass
class ConfidenceInterval:
    lower: float
    upper: float
    confidence_level: float
    data_points: int


@dataclass
class AssessmentResult:
    skill_id: str
    score: float
    passed: bool
    completed_at: int


@dataclass
class PriorData:
    base_probability: float
    current_level: str | None = None


class SkillLevelClassifier:
    """Classifies confidence scores into skill levels."""

    THRESHOLDS = [("master", 0.95), ("expert", 0.80), ("advanced", 0.60), ("intermediate", 0.35), ("beginner", 0.0)]

    def classify(self, confidence: float, evidence_tier: str, assessment_score: float = 0.0, prior_level: str = "beginner") -> str:
        for level, threshold in self.THRESHOLDS:
            if confidence >= threshold:
                return level
        return "beginner"


### 8.3 Confidence Trend Analyzer

Tracks confidence changes over time for trend detection and regression alerting.

```python
class ConfidenceTrendAnalyzer:
    """Analyzes confidence score trends over time for regression detection."""

    SIGNIFICANCE_THRESHOLD = 0.10  # 10% change is considered significant

    async def analyze(
        self, user_id: str, skill_id: str, history: list[SkillConfidence]
    ) -> ConfidenceTrend:
        if len(history) < 2:
            return ConfidenceTrend(skill_id=skill_id, trend="insufficient_data",
                change=0.0, significant=False, recommendation="Collect more data points")

        sorted_history = sorted(history, key=lambda h: h.computed_at)
        first = sorted_history[0]
        last = sorted_history[-1]
        change = last.confidence_score - first.confidence_score
        change_pct = change / max(first.confidence_score, 0.01)

        # Determine trend direction
        if change_pct > self.SIGNIFICANCE_THRESHOLD:
            trend = "improving"
        elif change_pct < -self.SIGNIFICANCE_THRESHOLD:
            trend = "declining"
        else:
            trend = "stable"

        # Compute velocity (change per 30 days)
        time_span_days = (last.computed_at - first.computed_at) / 86400000
        velocity_per_month = change / max(time_span_days, 1) * 30 if time_span_days > 0 else 0.0

        # Generate recommendation
        if trend == "declining":
            rec = "New evidence or assessment recommended to reverse decline"
        elif trend == "improving" and velocity_per_month > 0.1:
            rec = "Consider reclassification to higher skill level"
        else:
            rec = "No action needed — skill level is stable"

        return ConfidenceTrend(skill_id=skill_id, trend=trend, change=round(change, 4),
            change_pct=round(change_pct, 4), significant=abs(change_pct) > self.SIGNIFICANCE_THRESHOLD,
            velocity_per_month=round(velocity_per_month, 4), current_level=last.level,
            previous_level=first.level if len(sorted_history) > 1 else last.level,
            recommendation=rec, data_points=len(sorted_history))

    async def detect_regression(self, user_id: str, all_skills: dict[str, list[SkillConfidence]]) -> list[RegressionAlert]:
        """Detect skills with significant regression across all user skills."""
        alerts = []
        for skill_id, history in all_skills.items():
            trend = await self.analyze(user_id, skill_id, history)
            if trend.trend == "declining" and trend.significant:
                alerts.append(RegressionAlert(skill_id=skill_id, current_confidence=trend.change,
                    previous_confidence=trend.change - trend.change if len(history) >= 2 else 0.0,
                    decline_amount=abs(trend.change), recommendation=trend.recommendation,
                    detected_at=int(time.time() * 1000)))
        return alerts


@dataclass
class ConfidenceTrend:
    skill_id: str
    trend: str
    change: float
    change_pct: float
    significant: bool
    velocity_per_month: float
    current_level: str
    previous_level: str
    recommendation: str
    data_points: int


@dataclass
class RegressionAlert:
    skill_id: str
    current_confidence: float
    previous_confidence: float
    decline_amount: float
    recommendation: str
    detected_at: int
```

### 8.4 Batch Confidence Processor

Processes confidence calculations for multiple skills/users efficiently with batching.

```python
class BatchConfidenceProcessor:
    """Processes confidence calculations for multiple skills in batch."""

    def __init__(self, engine: SkillConfidenceEngine, batch_size: int = 50):
        self.engine = engine
        self.batch_size = batch_size
        self.logger = StructuredLogger("evidence.batch_confidence")

    async def process_user_skills(self, user_id: str, skill_ids: list[str],
                                    evidence_map: dict[str, list[WeightedEvidence]],
                                    assessment_map: dict[str, list[AssessmentResult]] | None = None) -> dict[str, SkillConfidence]:
        """Compute confidence for all of a user's skills in parallel batches."""
        results = {}
        for i in range(0, len(skill_ids), self.batch_size):
            batch = skill_ids[i:i + self.batch_size]
            tasks = []
            for skill_id in batch:
                task = self.engine.compute(
                    user_id, skill_id,
                    evidence_map.get(skill_id, []),
                    assessment_map.get(skill_id) if assessment_map else None,
                )
                tasks.append(task)

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            for skill_id, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    self.logger.error("Batch confidence failed", skill=skill_id, error=str(result))
                    results[skill_id] = None
                else:
                    results[skill_id] = result

        return results

    async def process_all_users(self, user_ids: list[str], skill_registry: dict) -> dict[str, dict[str, SkillConfidence]]:
        """Process confidence for all users. In production: triggered by cron."""
        all_results = {}
        for user_id in user_ids:
            all_results[user_id] = await self.process_user_skills(
                user_id, skill_registry.get(user_id, [])
            )
        return all_results
```

### 8.5 Confidence Decay Manager

Manages automatic confidence decay when evidence hasn't been refreshed.

```python
class ConfidenceDecayManager:
    """Applies automatic confidence decay for stale skills."""

    DECAY_INTERVALS = [
        (90, 0.95),   # 3 months: 5% decay
        (180, 0.85),  # 6 months: 15% decay
        (365, 0.70),  # 1 year: 30% decay
        (730, 0.50),  # 2 years: 50% decay
    ]

    async def apply_decay(self, confidence: SkillConfidence) -> SkillConfidence:
        latest = confidence.computed_at
        age_days = (time.time() - latest / 1000) / 86400
        factor = 1.0
        for days, multiplier in self.DECAY_INTERVALS:
            if age_days >= days:
                factor = multiplier
        confidence.confidence_score *= factor
        return confidence

    async def get_stale_skills(self, user_id: str, threshold_days: int = 90) -> list[str]:
        """Get skills that haven't been refreshed within threshold."""
        return []
```


---
## 9. Analytics

### 9.1 Analytics Architecture

The Analytics layer collects and surfaces KPIs across the entire evidence pipeline: collection, verification, trust, weighting, AI validation, and fraud detection. It feeds dashboards, alerts, and the SkillIntelligence.md analytics engine.

```
                  ┌─────────────────────────────────────────┐
                  │         EVIDENCE ANALYTICS ENGINE          │
                  │                                           │
                  │  ┌──────────┐ ┌──────────┐ ┌──────────┐  │
                  │  │Collection│ │Verific.  │ │Trust     │  │
                  │  │KPIs      │ │KPIs      │ │KPIs      │  │
                  │  └──────────┘ └──────────┘ └──────────┘  │
                  │  ┌──────────┐ ┌──────────┐ ┌──────────┐  │
                  │  │Fraud     │ │Confidence│ │Pipeline  │  │
                  │  │KPIs      │ │KPIs      │ │Health    │  │
                  │  └──────────┘ └──────────┘ └──────────┘  │
                  └─────────────────────────────────────────┘
                              │            │
                    ┌─────────▼──┐  ┌──────▼──────────┐
                    │ Dashboards │  │ Alerts &        │
                    │ (Real-time)│  │ Notifications   │
                    └────────────┘  └─────────────────┘
```

### 9.2 Collection Analytics

```python
class CollectionAnalytics:
    """Tracks evidence collection pipeline performance and volume."""

    async def get_collection_summary(self, user_id: str | None = None,
                                      tenant_id: str | None = None,
                                      days: int = 30) -> CollectionSummary:
        start_ts = int(time.time() * 1000) - days * 86400000
        items = await self._query_evidence(start_ts, user_id, tenant_id)

        total = len(items)
        by_source: dict[str, int] = {}
        by_state: dict[str, int] = {}
        new_count = updated_count = failed_count = 0

        for item in items:
            by_source[item.source_type.value] = by_source.get(item.source_type.value, 0) + 1
            by_state[item.state.value if item.state else "unknown"] = by_state.get(item.state.value if item.state else "unknown", 0) + 1
            if item.created_at >= start_ts:
                new_count += 1

        auto_discovered = sum(1 for i in items if i.metadata.get("auto_discovered", False))
        user_submitted = total - auto_discovered

        return CollectionSummary(
            period_days=days, total_evidence=total, new_items=new_count,
            by_source=by_source, by_state=by_state,
            auto_discovered=auto_discovered, user_submitted=user_submitted,
            avg_per_day=round(total / max(days, 1), 1),
        )

    async def get_collection_rate(self, source_type: EvidenceSourceType | None = None) -> CollectionRate:
        """Get collection success/failure rates."""
        return CollectionRate(
            source_type=source_type.value if source_type else "all",
            success_rate=0.95, failure_rate=0.05, avg_duration_ms=1200,
            rate_limited_count=12, error_distribution={},
        )

    async def _query_evidence(self, start_ts: int, user_id: str | None, tenant_id: str | None) -> list[EvidenceItem]:
        return []


@dataclass
class CollectionSummary:
    period_days: int
    total_evidence: int
    new_items: int
    by_source: dict[str, int]
    by_state: dict[str, int]
    auto_discovered: int
    user_submitted: int
    avg_per_day: float


@dataclass
class CollectionRate:
    source_type: str
    success_rate: float
    failure_rate: float
    avg_duration_ms: int
    rate_limited_count: int
    error_distribution: dict
```

### 9.3 Verification Analytics

```python
class VerificationAnalytics:
    """Tracks verification pipeline performance and tier distribution."""

    async def get_verification_summary(self, days: int = 30) -> VerificationSummary:
        total = 500  # In production: query DB
        by_tier = {"auto": 350, "ai": 100, "human": 50}
        by_status = {"verified": 400, "rejected": 60, "pending": 40}
        avg_duration = {"auto_ms": 340, "ai_ms": 3200, "human_ms": 86400000}
        escalation_rate = 0.08
        auto_pass_rate = 0.70

        return VerificationSummary(
            total_verified=total, by_tier=by_tier, by_status=by_status,
            avg_duration_ms=avg_duration, escalation_rate=escalation_rate,
            auto_pass_rate=auto_pass_rate, human_review_avg_queue_hours=36.5,
        )

    async def get_tier_breakdown(self, source_type: EvidenceSourceType | None = None) -> dict:
        return {"auto": {"count": 350, "avg_confidence": 0.88, "pass_rate": 0.70},
                "ai": {"count": 100, "avg_confidence": 0.92, "pass_rate": 0.85},
                "human": {"count": 50, "avg_confidence": 0.96, "pass_rate": 0.90}}


@dataclass
class VerificationSummary:
    total_verified: int
    by_tier: dict[str, int]
    by_status: dict[str, int]
    avg_duration_ms: dict[str, int]
    escalation_rate: float
    auto_pass_rate: float
    human_review_avg_queue_hours: float
```

### 9.4 Trust & Weight Analytics

```python
class TrustAnalytics:
    """Tracks trust score distribution and weight trends."""

    async def get_trust_distribution(self) -> dict:
        return {"very_low_0_0.25": 50, "low_0.25_0.5": 120, "medium_0.5_0.75": 280, "high_0.75_1.0": 550}

    async def get_avg_trust_by_source(self) -> dict[str, float]:
        return {"github": 0.92, "certification": 0.88, "project": 0.75,
                "hackathon": 0.65, "freelance": 0.70, "opensource": 0.82,
                "assessment": 0.95, "work_experience": 0.55}

    async def get_weight_distribution(self) -> dict:
        return {"zero_weight": 45, "low_0_0.3": 150, "medium_0.3_0.6": 320, "high_0.6_1.0": 485}
```

### 9.5 Fraud Analytics

```python
class FraudAnalytics:
    """Tracks fraud detection signals and risk distribution."""

    async def get_fraud_summary(self, days: int = 30) -> FraudSummary:
        return FraudSummary(
            total_scanned=5000, total_signals=120, total_blocked=15,
            signal_breakdown={
                "forged_credential": 20, "repo_inflation": 35,
                "cert_template_fraud": 15, "identity_fraud": 5,
                "temporal_anomaly": 25, "cross_platform_mismatch": 8,
                "duplicate_evidence": 7, "pattern_anomaly": 5,
            },
            risk_distribution={"safe": 4700, "suspicious": 250, "blocked": 50},
            false_positive_rate=0.03,
            avg_risk_score=0.12,
        )

    async def get_user_risk_trend(self, user_id: str, days: int = 90) -> list[dict]:
        """Get daily risk scores for a user over time."""
        return [{"date": "2026-06-01", "risk_score": 0.05},
                {"date": "2026-06-02", "risk_score": 0.08}]

    async def get_top_flagged_users(self, limit: int = 10) -> list[dict]:
        return [{"user_id": "user_1", "risk_score": 0.85, "evidence_flagged": 12}]


@dataclass
class FraudSummary:
    total_scanned: int
    total_signals: int
    total_blocked: int
    signal_breakdown: dict[str, int]
    risk_distribution: dict[str, int]
    false_positive_rate: float
    avg_risk_score: float
```

### 9.6 Confidence Analytics

```python
class ConfidenceAnalytics:
    """Tracks skill confidence scores across the user base."""

    async def get_confidence_distribution(self) -> dict:
        return {"beginner_0_0.35": 120, "intermediate_0.35_0.6": 250,
                "advanced_0.6_0.8": 180, "expert_0.8_0.95": 60, "master_0.95_1.0": 20}

    async def get_avg_confidence_by_skill_category(self) -> dict:
        return {"programming": 0.72, "design": 0.65, "data_science": 0.58,
                "devops": 0.62, "management": 0.55, "communication": 0.60}

    async def get_confidence_trend(self, skill_id: str, days: int = 180) -> list[dict]:
        return [{"date": "2026-01-01", "confidence": 0.45, "level": "intermediate"},
                {"date": "2026-06-01", "confidence": 0.72, "level": "advanced"}]
```

### 9.7 Alerting

```python
class EvidenceAlertManager:
    """Manages system-wide alerts based on analytics thresholds."""

    ALERT_THRESHOLDS = {
        "verification_escalation_rate": 0.15,    # Alert if > 15% escalate to human
        "fraud_block_rate": 0.05,                # Alert if > 5% evidence blocked
        "auto_verification_pass_rate": 0.50,     # Alert if < 50% auto pass
        "collection_failure_rate": 0.10,         # Alert if > 10% collection fails
        "ai_validator_confidence": 0.60,         # Alert if avg AI confidence < 0.6
    }

    async def check_alerts(self) -> list[Alert]:
        alerts = []
        for metric, threshold in self.ALERT_THRESHOLDS.items():
            value = await self._get_current_value(metric)
            if value is not None and self._is_breached(metric, value, threshold):
                alerts.append(Alert(
                    alert_id=f"ev_alert_{uuid.uuid4().hex[:8]}",
                    metric=metric, current_value=value, threshold=threshold,
                    severity="warning" if value < threshold * 1.5 else "critical",
                    message=f"Alert: {metric} = {value:.2f} (threshold: {threshold})",
                    created_at=int(time.time() * 1000),
                ))
        return alerts

    async def _get_current_value(self, metric: str) -> float | None:
        return None

    def _is_breached(self, metric: str, value: float, threshold: float) -> bool:
        upper_metrics = {"verification_escalation_rate", "fraud_block_rate", "collection_failure_rate"}
        lower_metrics = {"auto_verification_pass_rate", "ai_validator_confidence"}
        if metric in upper_metrics:
            return value > threshold
        if metric in lower_metrics:
            return value < threshold
        return False


@dataclass
class Alert:
    alert_id: str
    metric: str
    current_value: float
    threshold: float
    severity: str
    message: str
    created_at: int
```

### 9.8 Real-Time Monitoring Publisher

```python
class EvidenceMetricsPublisher:
    """
    Publishes real-time evidence metrics to monitoring systems.
    Supports WebSocket for live dashboards and Prometheus for metrics collection.
    """

    def __init__(self, ws_broadcaster=None, prometheus_registry=None):
        self.ws = ws_broadcaster
        self.metrics = {
            "collection_rate": Counter("evidence_collection_total", "Total evidence collected", ["source_type"]),
            "verification_tier": Counter("evidence_verification_tier", "Verification by tier", ["tier"]),
            "fraud_signals": Counter("evidence_fraud_signals", "Fraud signals by type", ["signal_type"]),
            "trust_score": Gauge("evidence_trust_score", "Current trust score distribution"),
            "confidence_score": Gauge("evidence_confidence_score", "Current confidence score per skill", ["skill_id"]),
            "collection_duration": Histogram("evidence_collection_duration_ms", "Collection duration", ["source_type"]),
            "ai_validation_duration": Histogram("evidence_ai_validation_duration_ms", "AI validation duration"),
            "human_review_queue_depth": Gauge("evidence_human_review_queue_depth", "Pending human reviews"),
        }
        self.logger = StructuredLogger("evidence.metrics_publisher")

    async def publish_collection(self, result: EvidenceCollectionResult) -> None:
        self.metrics["collection_rate"].labels(source_type=result.source.value).inc(result.items_collected)
        duration = int(time.time() * 1000) - result.collected_at
        self.metrics["collection_duration"].labels(source_type=result.source.value).observe(duration)

    async def publish_verification(self, state: VerificationState) -> None:
        self.metrics["verification_tier"].labels(tier=f"tier_{state.current_tier}").inc()
        if self.ws:
            await self.ws.broadcast("verification_update", {
                "evidence_id": state.evidence_id,
                "status": state.final_status.value,
                "tier": state.current_tier,
            })

    async def publish_fraud(self, result: FraudScanResult) -> None:
        for signal in result.signals:
            self.metrics["fraud_signals"].labels(signal_type=signal.signal_type.value).inc()
        if result.is_blocked and self.ws:
            await self.ws.broadcast("security_alert", {
                "evidence_id": result.evidence_id,
                "risk_score": result.risk_score,
                "signals": [s.signal_type.value for s in result.signals],
            })

    async def publish_confidence(self, confidence: SkillConfidence) -> None:
        self.metrics["confidence_score"].labels(skill_id=confidence.skill_id).set(confidence.confidence_score)

    async def publish_human_review_queue(self, depth: int) -> None:
        self.metrics["human_review_queue_depth"].set(depth)
```

### 9.9 Dashboard Report Generator

```python
class EvidenceDashboardReport:
    """Generates comprehensive evidence system reports for dashboards."""

    def __init__(self):
        self.collection = CollectionAnalytics()
        self.verification = VerificationAnalytics()
        self.trust = TrustAnalytics()
        self.fraud = FraudAnalytics()
        self.confidence = ConfidenceAnalytics()

    async def generate_full_report(self, days: int = 30) -> dict:
        report = {
            "generated_at": datetime.now().isoformat(),
            "period_days": days,
            "collection": await self._get_collection_section(days),
            "verification": await self._get_verification_section(days),
            "trust": await self._get_trust_section(),
            "fraud": await self._get_fraud_section(days),
            "confidence": await self._get_confidence_section(),
            "health": await self._get_health_summary(),
        }
        return report

    async def generate_user_report(self, user_id: str, days: int = 90) -> dict:
        collection = await self.collection.get_collection_summary(user_id=user_id, days=days)
        fraud_profile = await self.fraud.get_user_risk_trend(user_id, days)
        return {
            "user_id": user_id,
            "period_days": days,
            "total_evidence": collection.total_evidence,
            "evidence_by_source": collection.by_source,
            "auto_discovered": collection.auto_discovered,
            "fraud_risk_trend": fraud_profile,
            "skill_confidence_summary": await self._get_user_confidence_summary(user_id),
        }

    async def _get_collection_section(self, days: int) -> dict:
        summary = await self.collection.get_collection_summary(days=days)
        return {"total": summary.total_evidence, "new": summary.new_items,
                "by_source": summary.by_source, "by_state": summary.by_state,
                "auto_discovered": summary.auto_discovered, "avg_per_day": summary.avg_per_day}

    async def _get_verification_section(self, days: int) -> dict:
        summary = await self.verification.get_verification_summary(days)
        return {"total_verified": summary.total_verified, "by_tier": summary.by_tier,
                "by_status": summary.by_status, "escalation_rate": summary.escalation_rate,
                "auto_pass_rate": summary.auto_pass_rate, "avg_duration_ms": summary.avg_duration_ms}

    async def _get_trust_section(self) -> dict:
        return {"distribution": await self.trust.get_trust_distribution(),
                "by_source": await self.trust.get_avg_trust_by_source(),
                "weight_distribution": await self.trust.get_weight_distribution()}

    async def _get_fraud_section(self, days: int) -> dict:
        summary = await self.fraud.get_fraud_summary(days)
        return {"total_scanned": summary.total_scanned, "total_signals": summary.total_signals,
                "total_blocked": summary.total_blocked, "signal_breakdown": summary.signal_breakdown,
                "risk_distribution": summary.risk_distribution,
                "false_positive_rate": summary.false_positive_rate}

    async def _get_confidence_section(self) -> dict:
        return {"distribution": await self.confidence.get_confidence_distribution(),
                "by_category": await self.confidence.get_avg_confidence_by_skill_category()}

    async def _get_health_summary(self) -> dict:
        return {"status": "healthy", "pipeline_operational": True,
                "last_collection_success": True, "ai_validator_available": True,
                "human_review_queue_depth": 12, "avg_latency_ms": 450}

    async def _get_user_confidence_summary(self, user_id: str) -> list[dict]:
        return [{"skill_id": "python", "confidence": 0.82, "level": "advanced", "trend": "stable"}]
```


---
## 10. Database Design

### 10.1 PostgreSQL Schema

The relational store holds evidence items, verification states, fraud signals, and analytics snapshots.

```sql
-- ============================================================
-- Core evidence table
-- ============================================================
CREATE TABLE evidence_items (
    evidence_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_ids           UUID[] NOT NULL DEFAULT '{}',
    source_type         TEXT NOT NULL CHECK (source_type IN (
        'project', 'github', 'certification', 'hackathon',
        'freelance', 'opensource', 'assessment', 'work_experience'
    )),
    state               TEXT NOT NULL DEFAULT 'raw' CHECK (state IN (
        'raw', 'pending_verification', 'verified', 'verified_auto',
        'verified_ai', 'verified_human', 'rejected', 'flagged',
        'active', 'expired'
    )),
    title               TEXT NOT NULL,
    description         TEXT NOT NULL DEFAULT '',
    url                 TEXT,
    metadata            JSONB NOT NULL DEFAULT '{}',
    quality_score       REAL NOT NULL DEFAULT 0.0 CHECK (quality_score >= 0.0 AND quality_score <= 1.0),
    trust_score         REAL NOT NULL DEFAULT 0.0 CHECK (trust_score >= 0.0 AND trust_score <= 1.0),
    weight              REAL NOT NULL DEFAULT 0.0 CHECK (weight >= 0.0 AND weight <= 1.0),
    collected_at        BIGINT NOT NULL,
    verified_at         BIGINT,
    verification_method TEXT,
    credentials_used    TEXT,
    signed_hash         TEXT NOT NULL,
    previous_hash       TEXT,
    fraud_signals       TEXT[] NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),

    -- Constraints
    CONSTRAINT valid_quality_range CHECK (quality_score >= 0.0 AND quality_score <= 1.0),
    CONSTRAINT valid_trust_range CHECK (trust_score >= 0.0 AND trust_score <= 1.0)
);

-- Indexes
CREATE INDEX idx_evidence_user_id ON evidence_items(user_id);
CREATE INDEX idx_evidence_source_type ON evidence_items(source_type);
CREATE INDEX idx_evidence_state ON evidence_items(state);
CREATE INDEX idx_evidence_skill_ids ON evidence_items USING GIN(skill_ids);
CREATE INDEX idx_evidence_collected_at ON evidence_items(collected_at DESC);
CREATE INDEX idx_evidence_metadata ON evidence_items USING GIN(metadata jsonb_path_ops);
CREATE INDEX idx_evidence_user_source ON evidence_items(user_id, source_type);
CREATE INDEX idx_evidence_trust_score ON evidence_items(trust_score DESC);
CREATE INDEX idx_evidence_weight ON evidence_items(weight DESC);

-- Partition by creation month (requires pg_partman or manual partitioning)
-- CREATE TABLE evidence_items_y2026m06 PARTITION OF evidence_items
--     FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');


-- ============================================================
-- Verification state table
-- ============================================================
CREATE TABLE verification_states (
    verification_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evidence_id         UUID NOT NULL REFERENCES evidence_items(evidence_id) ON DELETE CASCADE,
    current_tier        INT NOT NULL DEFAULT 1,
    final_status        TEXT NOT NULL DEFAULT 'pending' CHECK (final_status IN (
        'pending', 'verified_auto', 'verified_ai', 'verified_human',
        'rejected_auto', 'rejected_ai', 'rejected_human', 'expired', 'inconclusive'
    )),
    auto_confidence     REAL,
    ai_confidence       REAL,
    human_confidence    REAL,
    escalation_count    INT NOT NULL DEFAULT 0,
    last_verified_at    BIGINT,
    expires_at          BIGINT,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),

    CONSTRAINT unique_evidence_verification UNIQUE (evidence_id)
);

CREATE INDEX idx_verification_status ON verification_states(final_status);
CREATE INDEX idx_verification_expires ON verification_states(expires_at) WHERE expires_at IS NOT NULL;


-- ============================================================
-- Fraud signals table
-- ============================================================
CREATE TABLE fraud_signals (
    signal_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evidence_id         UUID NOT NULL REFERENCES evidence_items(evidence_id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    signal_type         TEXT NOT NULL CHECK (signal_type IN (
        'forged_credential', 'repo_inflation', 'cert_template_fraud',
        'identity_fraud', 'temporal_anomaly', 'cross_platform_mismatch',
        'duplicate_evidence', 'pattern_anomaly'
    )),
    confidence          REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    severity_weight     REAL NOT NULL CHECK (severity_weight >= 0.0 AND severity_weight <= 1.0),
    description         TEXT NOT NULL,
    details             JSONB NOT NULL DEFAULT '{}',
    detected_at         BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    resolved_at         BIGINT,
    resolution          TEXT
);

CREATE INDEX idx_fraud_evidence ON fraud_signals(evidence_id);
CREATE INDEX idx_fraud_user ON fraud_signals(user_id);
CREATE INDEX idx_fraud_type ON fraud_signals(signal_type);
CREATE INDEX idx_fraud_severity ON fraud_signals(severity_weight DESC);


-- ============================================================
-- Evidence source reputation cache
-- ============================================================
CREATE TABLE source_reputation_cache (
    source_type         TEXT PRIMARY KEY,
    platform            TEXT NOT NULL,
    base_score          REAL NOT NULL,
    trust_level         TEXT NOT NULL,
    last_verified_at    BIGINT NOT NULL,
    next_verification_at BIGINT NOT NULL,
    cache_ttl_seconds   INT NOT NULL DEFAULT 86400
);


-- ============================================================
-- Trust score audit log (immutable)
-- ============================================================
CREATE TABLE trust_score_audit_log (
    audit_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evidence_id         UUID NOT NULL,
    trust_score         REAL NOT NULL,
    provenance_score    REAL,
    reputation_score    REAL,
    custody_score       REAL,
    identity_score      REAL,
    broken_factor       TEXT,
    computed_at         BIGINT NOT NULL,
    duration_ms         INT NOT NULL
);

CREATE INDEX idx_trust_audit_evidence ON trust_score_audit_log(evidence_id);
CREATE INDEX idx_trust_audit_computed ON trust_score_audit_log(computed_at DESC);


-- ============================================================
-- Human review queue
-- ============================================================
CREATE TABLE human_review_queue (
    review_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evidence_id         UUID NOT NULL REFERENCES evidence_items(evidence_id) ON DELETE CASCADE,
    reason              TEXT NOT NULL,
    priority            INT NOT NULL DEFAULT 3 CHECK (priority >= 1 AND priority <= 5),
    status              TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'resolved', 'escalated_max')),
    assigned_to         UUID REFERENCES users(id),
    assigned_at         BIGINT,
    sla_deadline        BIGINT NOT NULL,
    escalation_level    INT NOT NULL DEFAULT 0,
    decision_approved   BOOLEAN,
    decision_confidence REAL,
    decision_notes      TEXT,
    resolved_at         BIGINT,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
);

CREATE INDEX idx_review_status ON human_review_queue(status);
CREATE INDEX idx_review_priority ON human_review_queue(priority DESC, created_at ASC);
CREATE INDEX idx_review_sla ON human_review_queue(sla_deadline ASC) WHERE status IN ('pending', 'in_progress');


-- ============================================================
-- Auto-discovery pending items
-- ============================================================
CREATE TABLE auto_discovery_items (
    discovery_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source              TEXT NOT NULL,
    title               TEXT NOT NULL,
    description         TEXT NOT NULL DEFAULT '',
    suggested_skills    TEXT[] NOT NULL DEFAULT '{}',
    confidence          REAL NOT NULL DEFAULT 0.7,
    raw_data            JSONB NOT NULL DEFAULT '{}',
    status              TEXT NOT NULL DEFAULT 'pending_approval' CHECK (status IN ('discovered', 'pending_approval', 'approved', 'rejected', 'expired')),
    notification_id     TEXT,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    expires_at          BIGINT NOT NULL  -- Auto-reject after 7 days for AUTO_IMPORT mode
);

CREATE INDEX idx_discovery_user ON auto_discovery_items(user_id);
CREATE INDEX idx_discovery_status ON auto_discovery_items(status);


-- ============================================================
-- Analytics snapshots (materialized for dashboards)
-- ============================================================
CREATE TABLE evidence_analytics_snapshots (
    snapshot_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_type       TEXT NOT NULL,  -- 'collection', 'verification', 'trust', 'fraud', 'confidence'
    snapshot_date       DATE NOT NULL,
    tenant_id           UUID,
    data                JSONB NOT NULL,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),

    CONSTRAINT unique_snapshot UNIQUE (snapshot_type, snapshot_date, tenant_id)
);

CREATE INDEX idx_analytics_date ON evidence_analytics_snapshots(snapshot_date DESC);
CREATE INDEX idx_analytics_type ON evidence_analytics_snapshots(snapshot_type);
```

### 10.2 Neo4j Evidence Graph

The graph database stores evidence provenance chains and relationships for the SkillGraphArchitecture.md system.

```cypher
// ============================================================
// Evidence node with full provenance
// ============================================================
CREATE CONSTRAINT evidence_id_unique IF NOT EXISTS
FOR (e:Evidence) REQUIRE e.evidence_id IS UNIQUE;

CREATE CONSTRAINT user_id_unique IF NOT EXISTS
FOR (u:User) REQUIRE u.user_id IS UNIQUE;

// Evidence node structure:
// (:Evidence {
//     evidence_id: "uuid",
//     source_type: "github",
//     title: "...",
//     state: "verified",
//     quality_score: 0.85,
//     trust_score: 0.92,
//     weight: 0.78,
//     collected_at: 1234567890000,
//     verified_at: 1234567890000
// })

// Provenance chain (linked list through time)
// (:Evidence) -[:PREVIOUS_STATE]-> (:Evidence)
// Each link represents a state transition

// Evidence → User relationship
// (:User) -[:HAS_EVIDENCE {collected_at: ..., source_type: "..."}]-> (:Evidence)

// Evidence → Skill relationship
// (:Evidence) -[:EVIDENCE_FOR {weight: 0.78}]-> (:Skill)

// Cross-reference relationships
// (:Evidence) -[:CROSS_REFERENCED_WITH {synergy: 1.25}]-> (:Evidence)

// Fraud signal relationships
// (:Evidence) -[:HAS_FRAUD_SIGNAL {type: "forged_credential", confidence: 0.9}]-> (:FraudSignal)


// ============================================================
// Query: Get evidence provenance chain for an item
// ============================================================
// MATCH path = (e:Evidence {evidence_id: $evidence_id})
//             -[:PREVIOUS_STATE*]-> (prev:Evidence)
// RETURN path
// ORDER BY prev.collected_at ASC


// ============================================================
// Query: Find cross-referenced skills
// ============================================================
// MATCH (u:User {user_id: $user_id})-[:HAS_EVIDENCE]->(e:Evidence)
// MATCH (e)-[:EVIDENCE_FOR]->(s:Skill {skill_id: $skill_id})
// MATCH (e)-[:CROSS_REFERENCED_WITH]->(other:Evidence)
// RETURN e, other, s
```

### 10.3 Redis Cache Schema

```python
# ============================================================
# Redis key patterns for evidence caching
# ============================================================

# Source reputation cache (24h TTL)
# Key:   evidence:rep:{source_type}
# Value: JSON(SourceReputationResult)
# TTL:   86400

# User evidence list (1h TTL)
# Key:   evidence:user:{user_id}:list
# Value: JSON(list[EvidenceItem])
# TTL:   3600

# User evidence count (1h TTL)
# Key:   evidence:user:{user_id}:count
# Value: integer
# TTL:   3600

# Verification rate limiter (per source per user)
# Key:   evidence:ratelimit:{user_id}:{source_type}
# Value: integer (count)
# TTL:   3600

# Fraud scan cache (prevent duplicate scans)
# Key:   evidence:fraud_scan:{evidence_id}
# Value: JSON(FraudScanResult)
# TTL:   86400

# Analytics snapshot lock
# Key:   evidence:analytics_lock:{snapshot_type}:{date}
# Value: "computing" | "done"
# TTL:   300

# Cross-reference cache (24h TTL)
# Key:   evidence:xref:{user_id}:{skill_id}
# Value: JSON(CrossReferenceResult)
# TTL:   86400

# Collection scheduler lock
# Key:   evidence:scheduler_lock:{user_id}:{source_type}
# Value: timestamp
# TTL:   (schedule_interval_seconds)
```

### 10.4 Partitioning Strategy

```sql
-- ============================================================
-- Evidence items partition by creation month
-- ============================================================
-- For 1M+ evidence items per month, partition by month:

CREATE TABLE evidence_items_template (
    LIKE evidence_items INCLUDING DEFAULTS INCLUDING CONSTRAINTS INCLUDING INDEXES
);

-- Create partitions (run monthly)
-- CREATE TABLE evidence_items_2026_06 PARTITION OF evidence_items
--     FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');

-- Partition pruning: queries filter by collected_at range
-- SELECT * FROM evidence_items
-- WHERE collected_at >= 1717200000000  -- June 1, 2026
--   AND collected_at < 1719792000000   -- July 1, 2026
--   AND user_id = $1;


-- ============================================================
-- Archival policy
-- ============================================================
-- Evidence older than 3 years with weight = 0:
--   → Move to evidence_archive table (same schema, different tablespace)
-- Evidence older than 5 years:
--   → Anonymize user_id, then move to cold storage

-- Archival job pseudocode:
-- INSERT INTO evidence_archive SELECT * FROM evidence_items
-- WHERE collected_at < EXTRACT(EPOCH FROM NOW() - INTERVAL '3 years') * 1000
--   AND weight = 0.0;
-- DELETE FROM evidence_items WHERE collected_at < ... AND weight = 0.0;
```

### 10.5 RLS Policies

```sql
-- ============================================================
-- Row-Level Security for multi-tenant isolation
-- ============================================================

ALTER TABLE evidence_items ENABLE ROW LEVEL SECURITY;

-- Users can only see their own evidence
CREATE POLICY user_evidence_isolation ON evidence_items
    FOR ALL
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- Admins can see all evidence
CREATE POLICY admin_view_all_evidence ON evidence_items
    FOR SELECT
    USING (auth.role() = 'admin');

-- Fraud signals visible to security team only
ALTER TABLE fraud_signals ENABLE ROW LEVEL SECURITY;

CREATE POLICY security_view_fraud ON fraud_signals
    FOR SELECT
    USING (auth.role() IN ('admin', 'security'));

-- Human review queue visible to reviewers
ALTER TABLE human_review_queue ENABLE ROW LEVEL SECURITY;

CREATE POLICY reviewer_access ON human_review_queue
    FOR ALL
    USING (auth.role() IN ('admin', 'reviewer', 'security'));
```

### 10.6 Materialized Views for Reporting

```sql
-- ============================================================
-- Daily evidence summary (refreshed by cron)
-- ============================================================
CREATE MATERIALIZED VIEW daily_evidence_summary AS
SELECT
    DATE(to_timestamp(collected_at / 1000)) AS collection_date,
    source_type,
    state,
    COUNT(*) AS count,
    AVG(quality_score) AS avg_quality,
    AVG(trust_score) AS avg_trust,
    AVG(weight) AS avg_weight
FROM evidence_items
WHERE collected_at > EXTRACT(EPOCH FROM NOW() - INTERVAL '90 days') * 1000
GROUP BY 1, 2, 3
WITH DATA;

CREATE UNIQUE INDEX idx_daily_summary ON daily_evidence_summary(collection_date, source_type, state);

-- ============================================================
-- User skill confidence snapshot (refreshed after batch compute)
-- ============================================================
CREATE MATERIALIZED VIEW user_skill_confidence AS
SELECT
    e.user_id,
    UNNEST(e.skill_ids) AS skill_id,
    COUNT(*) AS evidence_count,
    AVG(e.weight) AS avg_weight,
    SUM(e.weight) AS total_weight,
    MAX(e.trust_score) AS max_trust,
    MIN(e.trust_score) AS min_trust
FROM evidence_items e
WHERE e.state IN ('active', 'verified', 'verified_auto', 'verified_ai', 'verified_human')
GROUP BY 1, 2
WITH DATA;

CREATE INDEX idx_user_skill_confidence ON user_skill_confidence(user_id, skill_id);

-- ============================================================
-- Fraud hotspot analysis (refreshed daily)
-- ============================================================
CREATE MATERIALIZED VIEW fraud_hotspots AS
SELECT
    fs.signal_type,
    COUNT(*) AS signal_count,
    AVG(fs.severity_weight) AS avg_severity,
    COUNT(DISTINCT fs.user_id) AS affected_users,
    COUNT(DISTINCT fs.evidence_id) AS affected_evidence
FROM fraud_signals fs
WHERE fs.detected_at > EXTRACT(EPOCH FROM NOW() - INTERVAL '30 days') * 1000
GROUP BY 1
ORDER BY signal_count DESC
WITH DATA;
```

### 10.7 Cron Maintenance Jobs

```sql
-- ============================================================
-- Daily maintenance jobs (run via pg_cron or application scheduler)
-- ============================================================

-- Job 1: Refresh daily evidence summary (every hour)
-- SELECT cron.schedule('refresh-daily-summary', '0 * * * *',
--     'REFRESH MATERIALIZED VIEW CONCURRENTLY daily_evidence_summary');

-- Job 2: Refresh fraud hotspots (every 6 hours)
-- SELECT cron.schedule('refresh-fraud-hotspots', '0 */6 * * *',
--     'REFRESH MATERIALIZED VIEW CONCURRENTLY fraud_hotspots');

-- Job 3: Refresh user skill confidence (every 12 hours)
-- SELECT cron.schedule('refresh-user-confidence', '0 */12 * * *',
--     'REFRESH MATERIALIZED VIEW CONCURRENTLY user_skill_confidence');

-- Job 4: Archive old evidence (weekly)
-- SELECT cron.schedule('archive-old-evidence', '0 3 * * 0',
--     'CALL archive_expired_evidence()');

-- Job 5: Clean up expired auto-discovery items (daily)
-- SELECT cron.schedule('cleanup-expired-discoveries', '0 0 * * *',
--     'DELETE FROM auto_discovery_items WHERE expires_at < EXTRACT(EPOCH FROM NOW()) * 1000 AND status = ''pending_approval''');

-- Job 6: Verify expired re-verification deadlines (hourly)
-- SELECT cron.schedule('check-expired-verifications', '0 * * * *',
--     "UPDATE evidence_items SET state = 'expired' WHERE evidence_id IN (
--         SELECT vs.evidence_id FROM verification_states vs
--         WHERE vs.expires_at < EXTRACT(EPOCH FROM NOW()) * 1000
--         AND vs.final_status NOT IN ('rejected_auto', 'rejected_ai', 'rejected_human', 'expired')
--     )");


-- ============================================================
-- Stored procedure: Archive expired evidence
-- ============================================================
CREATE OR REPLACE PROCEDURE archive_expired_evidence()
LANGUAGE plpgsql
AS $$
BEGIN
    -- Move expired zero-weight evidence to archive
    INSERT INTO evidence_archive
    SELECT * FROM evidence_items
    WHERE collected_at < EXTRACT(EPOCH FROM NOW() - INTERVAL '3 years') * 1000
      AND weight = 0.0;

    -- Delete from main table
    DELETE FROM evidence_items
    WHERE collected_at < EXTRACT(EPOCH FROM NOW() - INTERVAL '3 years') * 1000
      AND weight = 0.0;

    -- Anonymize evidence older than 5 years
    UPDATE evidence_items
    SET user_id = 'anonymized',
        metadata = jsonb_build_object('anonymized', true, 'original_source_type', source_type)
    WHERE collected_at < EXTRACT(EPOCH FROM NOW() - INTERVAL '5 years') * 1000;
END;
$$;
```


---
## Appendix A: Source Verifier Matrix

| Source Type | Auto Checks | AI Validation | Human Review | Trust Baseline | Primary Fraud Risk |
|---|---|---|---|---|---|
| **Project** | URL reachable, repo metadata, commit count, README | Code quality, project complexity, authorship consistency | Manual code review, demo verification | 0.70 | Repo inflation, stolen repos |
| **GitHub** | Profile exists, account age, repos, contribution streak, PR merge rate | Contribution pattern authenticity, organic vs bot activity | N/A (sufficient auto/AI) | 0.95 | Fake contributions, bot activity, account farming |
| **Certification** | Credential ID format, provider API lookup, expiry, issuer domain | Certificate authenticity, provider recognition | Credential ID manual lookup, issuer contact | 0.85 | Forged credentials, template certs, misspelled issuers |
| **Hackathon** | Event lookup, submission URL, date verification, team size | Submission quality, prize plausibility | Event organizer confirmation | 0.60 | Fake event submissions, inflated prizes |
| **Freelance** | Contract API lookup, payment data, client reviews, platform profile | Contract description authenticity, rate plausibility | Client reference check | 0.65 | Fake contracts, inflated earnings, platform fraud |
| **Open Source** | Package registry API, download stats, version history, maintainer check | Package quality, dependency analysis, contribution pattern | N/A (sufficient auto/AI) | 0.80 | Fake packages, inflated downloads, attribution theft |
| **Assessment** | Session signature verification, duration check, score range, proctoring logs | N/A (assessment engine handles anti-cheat) | N/A (fully automated) | 0.90 | Session hijacking, credential sharing (handled by §7) |
| **Work Experience** | LinkedIn API, employment dates, company domain, job title | Description authenticity, title plausibility | Manager reference, pay stub verification | 0.50 | Falsified employment, title inflation, fake companies |

### Verification Level Recommendations by Evidence Tier

| Evidence Tier | Auto Threshold | AI Threshold | Human Required? | Cross-Ref Bypass |
|---|---|---|---|---|
| **Gold** | 0.85 | 0.90 | Only for high-risk sources (Work Exp) | 3+ sources → AI skip |
| **Silver** | 0.75 | 0.85 | For Work Exp + Cert only | 3+ sources → AI only |
| **Bronze** | 0.65 | 0.80 | Never | 3+ sources → Auto only |
| **Unverified** | N/A | N/A | N/A | N/A |


## Appendix B: Trust Score Formulas

### B.1 Multiplicative Trust

```
Trust_Score = Provenance_Score × Source_Reputation × Custody_Score × Identity_Score

Where each factor ∈ [0.0, 1.0], and any 0.0 → Trust_Score = 0.0

Example:
  Provenance_Score  = 0.95  (source validated, ext ID exists, URL works)
  Source_Reputation = 0.85  (AWS certification via Credly)
  Custody_Score     = 1.0   (chain intact, hashes match)
  Identity_Score    = 0.80  (OAuth linked + email match)
  ─────────────────────────────────────────────────
  Trust_Score       = 0.95 × 0.85 × 1.0 × 0.80 = 0.646
```

### B.2 Provenance Score

```
Provenance_Score = (Source_Valid + Ext_ID_Valid + URL_Valid + TS_Valid + Metadata_Complete) / 5

Critical failure: Source_Valid = false OR Ext_ID_Valid = false → Score = 0.0
```

### B.3 Source Reputation

```
Source_Reputation = Base_Score + Provider_Adjustment

Adjustments:
  Certification: Credly +0.05, Udemy -0.10, unknown -0.05
  Freelance:     Upwork +0.05, Toptal +0.10, Fiverr -0.05
  Project:       github.com +0.10, gitlab.com +0.08, bitbucket.org +0.05

Clamped to [0.0, 1.0]
```

### B.4 Identity Binding Score

```
Identity_Score = Σ(Weight_i × Method_Active_i) × Multiplicity_Bonus

Method weights:
  OAuth:               0.35  (strongest — platform verified identity)
  Crypto_Signature:    0.25  (user signed the submission)
  Account_Ownership:   0.20  (still holds the linked account)
  Email_Domain:        0.10  (email matches evidence context)
  Profile_Cross_Ref:   0.10  (name/location matches)

Multiplicity_Bonus:
  1 method:  1.0×
  2 methods: 1.1×
  3+ methods: 1.2×

If no methods: Score = 0.0
```

### B.5 Chain of Custody

```
Custody_Score = (Hash_Valid + Chain_Intact + TS_Ordered + State_Valid + Not_Modified) / 5

Critical failure: Hash_Valid = false → Score = 0.0
```


## Appendix C: Glossary

| Term | Definition |
|---|---|
| **Evidence** | Any verifiable data point that supports a skill claim (project, cert, assessment, etc.) |
| **Evidence Item** | Canonical representation of evidence in the system (persisted to PostgreSQL + Neo4j) |
| **Raw Evidence** | Unprocessed evidence as collected from a source, pre-normalization |
| **Source Type** | Category of evidence origin: Project, GitHub, Certification, Hackathon, Freelance, Open Source, Assessment, Work Experience |
| **Collector** | Adapter class that gathers evidence from a specific source type |
| **Auto-Discovery** | ARIA proactively finding evidence without user submission |
| **AUTO_IMPORT Mode** | Tenant config: discover → import → notify user (7-day rejection window) |
| **CONFIRM_FIRST Mode** | Tenant config: discover → notify → import only on user approval |
| **Verification** | Process of determining evidence authenticity through 3-tier escalation |
| **Tier 1 (Auto)** | Deterministic algorithmic verification (no AI, no humans) |
| **Tier 2 (AI)** | LLM-based authenticity and inconsistency detection |
| **Tier 3 (Human)** | Expert manual review for inconclusive evidence |
| **Cross-Referencing** | Triangulating skill claims across 3+ independent sources for trust synergy |
| **Synergy Bonus** | Trust multiplier applied when the same skill has evidence from 3+ independent sources |
| **Trust Score** | Multiplicative score (0.0-1.0) combining provenance, reputation, custody, and identity |
| **Provenance** | Cryptographic trace of where evidence originated and its chain of custody |
| **Source Reputation** | Baseline trustworthiness of a platform/provider (GitHub = high, LinkedIn = low) |
| **Chain of Custody** | Immutable hash chain proving evidence hasn't been tampered with |
| **Identity Binding** | Cryptographic proof that evidence belongs to the claiming user |
| **Evidence Weight** | Final contribution of an evidence item to skill confidence (quality × trust × recency × context) |
| **Recency Decay** | Exponential half-life decay of evidence value over time |
| **Level Gate Cap** | Maximum weight evidence can contribute at each skill level (beginner = 0.5 cap) |
| **Diversity Bonus** | Weight bonus from having multiple independent source types for the same skill |
| **Fraud Signal** | Detection of a specific type of evidence fraud |
| **Forged Credential** | Credential that doesn't exist at the claimed source |
| **Repo Inflation** | Artificially inflated GitHub statistics (stars, forks, commits) |
| **Cert Template Fraud** | Certification created from a template rather than issued by a legitimate provider |
| **Identity Fraud** | Evidence claimed under a stolen or false identity |
| **Temporal Anomaly** | Suspicious timing patterns (batch creation, improbable hours) |
| **Pattern Anomaly** | Statistical outlier compared to peer group |
| **Confidence Score** | Bayesian-calibrated measure of skill proficiency (0.0-1.0) |
| **Prior Probability** | Base rate estimate for skill level before evidence is considered |
| **Confidence Interval** | Range estimate around the confidence score, wider with less evidence |
| **AI Validation Engine** | LLM-powered authenticity checking using PromptLoader prompts |
| **PromptLoader** | Central prompt registry loaded from `prompts/` directory with inline fallbacks |
| **ECE** | Expected Calibration Error — measures how well LLM confidence matches actual accuracy |
| **RLS** | Row-Level Security — PostgreSQL policy for multi-tenant data isolation |
| **SLA** | Service Level Agreement — 48h for human review, 24h for escalated items |
| **Half-Life (Recency)** | Time after which evidence weight is halved (varies by source: 90d-730d) |
| **Skill Level** | Classification: beginner → intermediate → advanced → expert → master |
| **Evidence Tier** | Quality classification: Gold / Silver / Bronze / Unverified |
| **Collection Pipeline** | DAG of stages: gather → normalize → enrich → verify → persist |
| **Normalizer** | Converts source-specific raw data to canonical EvidenceItem format |
| **Enricher** | Infers skills and metadata from raw evidence during processing |
| **Collection Scheduler** | Manages cron-based collection intervals per source type |
| **Rate Limiter** | Prevents API abuse by enforcing minimum intervals between collections |
| **Auto-Verification** | Tier 1 deterministic checks: URL reachable, metadata present, hashes match |
| **AI Validation** | Tier 2 LLM-based check: authenticity, inconsistency, exaggeration detection |
| **Human Review** | Tier 3 manual check: expert reviews evidence that AI couldn't classify |
| **Verification Escalation** | Process of moving evidence from Tier 1 → Tier 2 → Tier 3 |
| **Chain-of-Custody** | Immutable hash-linked record of every evidence state transition |
| **Multiplicative Trust** | Trust model where zero in any factor zeros the total trust score |
| **Provenance** | Verifiable origin trail: where evidence came from and how it was collected |
| **Source Reputation** | Baseline trustworthiness score for a platform (0.50-0.95) |
| **Identity Binding** | Proof linking evidence to user via OAuth, signatures, email, or profile |
| **Recency Half-Life** | Days after which evidence weight decays by 50% (90d-730d per source) |
| **Level Gate Cap** | Maximum weight an evidence item can contribute at a given skill level |
| **Diversity Bonus** | Weight multiplier (1.0-1.5) from having 2+ independent source types |
| **Synergy Multiplier** | Trust bonus from cross-referencing (1.0× single, 1.25× dual, 1.5× 3+) |
| **Forged Credential** | Fraud type: credential ID that doesn't exist at the claimed provider |
| **Repo Inflation** | Fraud type: artificially inflated GitHub stars, forks, or commits |
| **Cert Template** | Fraud type: certification generated from template, not real issuer |
| **Identity Fraud** | Fraud type: evidence claimed under stolen or fabricated identity |
| **Temporal Anomaly** | Fraud type: suspicious timing (batch creation, improbable hours, round timestamps) |
| **Pattern Anomaly** | Fraud type: statistical outlier compared to peer group |
| **Confidence Score** | 0.0-1.0 calibrated measure combining evidence + assessment + prior |
| **Confidence Interval** | Range estimate around the confidence score (wider = less data) |
| **Prior Probability** | Bayesian base rate for skill level before any evidence is considered |
| **Batch Processing** | Computing confidence for multiple skills/users in parallel batches |
| **Trend Analysis** | Detecting improving/declining/stable confidence over time |
| **Regression Alert** | Notification when a skill's confidence drops significantly |
| **Confidence Decay** | Automatic reduction of confidence for skills without recent evidence |
| **ECE** | Expected Calibration Error — measures LLM confidence calibration quality |
| **PromptLoader** | Central registry loading prompts from `prompts/` with inline fallback |
| **Multi-LLM Router** | Failover across Claude → GPT-4o → Ollama for AI validation |
| **RLS** | Row-Level Security — PostgreSQL per-row access control for multi-tenancy |
| **SLA** | Service Level Agreement — 48h human review, 24h escalated review |
| **Materialized View** | Pre-computed query result for dashboard reporting performance |
| **Evidence Archive** | Cold storage for evidence older than 3 years with zero weight |
| **Partition Pruning** | Query optimization that scans only relevant month partitions |
| **TTL Cache** | Time-to-live cache in Redis for source reputation and cross-references |
| **Cron Job** | Scheduled maintenance task for archival, refresh, and cleanup |
| **Gauge** | Prometheus metric type for current values (queue depth, trust scores) |
| **Histogram** | Prometheus metric type for duration distributions (collection, validation) |
| **Counter** | Prometheus metric type for cumulative counts (items collected, fraud signals) |


---
*End of SkillEvidence.md — Enterprise Evidence Intelligence Architecture*



