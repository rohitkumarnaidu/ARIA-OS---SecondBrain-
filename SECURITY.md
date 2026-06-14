# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 0.x (alpha) | ✅ |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in Second Brain OS, please follow these steps:

1. **Do NOT** open a public GitHub issue
2. Send details to the project maintainer via GitHub Issues with the label `security` (visible only to maintainers initially)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

| Timeframe | Action |
|---|---|
| Within 24 hours | Acknowledgment of receipt |
| Within 72 hours | Initial assessment and severity classification |
| Within 7 days | Patch released for critical/high severity |
| Within 30 days | Patch released for medium/low severity |

### What to Expect

- You will receive acknowledgment within 24 hours
- We will provide regular updates on the fix progress
- You will be credited in the release notes (unless you prefer anonymity)
- We will notify you when the fix is deployed

## Security Commitments

- All data encrypted in transit (HTTPS/TLS 1.3)
- Row-Level Security enforced on all database tables
- Authentication via Supabase (Google OAuth)
- Rate limiting on API endpoints (100 req/min)
- Input validation via Pydantic models
- Secrets stored in environment variables (never in code)
- Regular dependency audits (npm audit, pip-audit)
- API keys rotated quarterly
- No telemetry or data collection without consent

## Responsible Disclosure

We follow coordinated disclosure. Please allow us reasonable time to fix the issue before public disclosure.

## Security Relevant Files

- `docs/security/24_Security.md` — Full security documentation
- `docs/security/25_Compliance.md` — Compliance documentation
- `docs/security/46_DataPrivacy.md` — Data privacy & GDPR compliance
- `.github/workflows/ci.yml` — CI pipeline with security checks
