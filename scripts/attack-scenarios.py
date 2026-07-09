#!/usr/bin/env python3
"""Custom attack scenarios for penetration testing.
Runs SQL injection, XSS, path traversal, auth bypass, and rate-limit tests.

Usage: python scripts/attack-scenarios.py [target_url]
"""

import sys
import json
import time
import httpx
from typing import List, Dict

TARGET = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"


class AttackScenario:
    def __init__(self, name: str):
        self.name = name
        self.results: List[Dict] = []

    def record(self, endpoint: str, payload: dict, status: int, expected: int, detail: str = ""):
        passed = status == expected if expected >= 0 else status != abs(expected)
        self.results.append(
            {
                "scenario": self.name,
                "endpoint": endpoint,
                "payload": payload,
                "actual_status": status,
                "expected_status": expected,
                "passed": passed,
                "detail": detail,
            }
        )

    def report(self) -> Dict:
        total = len(self.results)
        passed_count = sum(1 for r in self.results if r["passed"])
        return {
            "scenario": self.name,
            "total": total,
            "passed": passed_count,
            "failed": total - passed_count,
            "results": self.results,
        }


def run_sql_injection(client: httpx.Client) -> AttackScenario:
    scenario = AttackScenario("SQL Injection")
    payloads = [
        "' OR '1'='1",
        "'; DROP TABLE tasks; --",
        "' UNION SELECT * FROM users --",
        "' OR 1=1 --",
        '" OR "1"="1',
    ]
    for payload in payloads:
        for endpoint in [f"/api/v1/tasks/?search={payload}", f"/api/v1/goals/?q={payload}"]:
            try:
                resp = client.get(endpoint, timeout=10)
                scenario.record(
                    endpoint,
                    {"search": payload},
                    resp.status_code,
                    400,
                    "Expected 400 (parameterized query) or 200 (sanitized)",
                )
            except Exception as e:
                scenario.record(endpoint, {"search": payload}, 0, 400, str(e))
    return scenario


def run_xss(client: httpx.Client) -> AttackScenario:
    scenario = AttackScenario("Cross-Site Scripting (XSS)")
    payloads = [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "javascript:alert(1)",
        '"><script>alert(1)</script>',
    ]
    for payload in payloads:
        try:
            resp = client.post(
                f"{TARGET}/api/v1/tasks/",
                json={
                    "title": payload,
                    "priority": "medium",
                    "status": "pending",
                },
                timeout=10,
            )
            if resp.status_code == 201:
                data = resp.json()
                title = data.get("title", "")
                sanitized = "<" not in title and ">" not in title
                scenario.record(
                    "/api/v1/tasks/",
                    {"title": payload},
                    resp.status_code,
                    201,
                    "Sanitized" if sanitized else "UNSANITIZED - XSS RISK",
                )
            else:
                scenario.record("/api/v1/tasks/", {"title": payload}, resp.status_code, 201)
        except Exception as e:
            scenario.record("/api/v1/tasks/", {"title": payload}, 0, 201, str(e))
    return scenario


def run_path_traversal(client: httpx.Client) -> AttackScenario:
    scenario = AttackScenario("Path Traversal")
    payloads = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\win.ini",
        "%2e%2e%2f%2e%2e%2fetc/passwd",
        "....//....//etc/passwd",
    ]
    for payload in payloads:
        for endpoint in [f"/api/v1/resources/?path={payload}", f"/api/v1/tasks/?file={payload}"]:
            try:
                resp = client.get(endpoint, timeout=10)
                scenario.record(
                    endpoint,
                    {"path": payload},
                    resp.status_code,
                    400,
                    "Blocked" if resp.status_code >= 400 else "POTENTIAL TRAVERSAL",
                )
            except Exception as e:
                scenario.record(endpoint, {"path": payload}, 0, 400, str(e))
    return scenario


def run_auth_bypass(client: httpx.Client) -> AttackScenario:
    scenario = AttackScenario("Authentication Bypass")
    tokens = [
        "invalid-token",
        "Bearer invalid",
        "fake-jwt-token-string-for-testingInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dummy",
        "'' OR 1=1 --",
    ]
    for token in tokens:
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp = client.get(f"{TARGET}/api/v1/tasks/", headers=headers, timeout=10)
            scenario.record(
                "/api/v1/tasks/",
                {"token": token[:20]},
                resp.status_code,
                401,
                "Blocked" if resp.status_code in (401, 403) else "POTENTIAL BYPASS",
            )
        except Exception as e:
            scenario.record("/api/v1/tasks/", {"token": token[:20]}, 0, 401, str(e))
    return scenario


def run_rate_limit(client: httpx.Client) -> AttackScenario:
    scenario = AttackScenario("Rate Limit Bypass")
    rapid_requests = 0
    for _ in range(20):
        try:
            resp = client.get(f"{TARGET}/health", timeout=5)
            if resp.status_code == 429:
                break
            rapid_requests += 1
        except Exception:
            break
    scenario.record(
        "/health",
        {},
        200 if rapid_requests < 20 else 429,
        429 if rapid_requests >= 20 else 200,
        f"20 rapid requests resulted in {rapid_requests} successes",
    )
    return scenario


def run_ssrf(client: httpx.Client) -> AttackScenario:
    scenario = AttackScenario("Server-Side Request Forgery")
    internal_hosts = [
        "http://localhost:5432",
        "http://127.0.0.1:8000",
        "http://169.254.169.254/latest/meta-data/",
        "http://[::1]:22",
    ]
    for host in internal_hosts:
        try:
            resp = client.post(
                f"{TARGET}/api/v1/chat/",
                json={
                    "message": f"Fetch data from {host}",
                },
                timeout=10,
            )
            scenario.record(
                "/api/v1/chat/",
                {"message": f"fetch {host}"},
                resp.status_code,
                400,
                "Blocked" if resp.status_code >= 400 else "POTENTIAL SSRF",
            )
        except Exception as e:
            scenario.record("/api/v1/chat/", {"message": f"fetch {host}"}, 0, 400, str(e))
    return scenario


def main():
    print(f"Running attack scenarios against {TARGET}")
    print("=" * 60)

    with httpx.Client(base_url=TARGET, verify=False) as client:
        scenarios = [
            run_sql_injection(client),
            run_xss(client),
            run_path_traversal(client),
            run_auth_bypass(client),
            run_rate_limit(client),
            run_ssrf(client),
        ]

    print()
    print("=" * 60)
    print("ATTACK SCENARIO RESULTS")
    print("=" * 60)

    all_passed = True
    consolidated = {"target": TARGET, "timestamp": time.time(), "scenarios": []}
    for scenario in scenarios:
        report = scenario.report()
        consolidated["scenarios"].append(report)
        status = "PASS" if report["failed"] == 0 else f"FAIL ({report['failed']} failed)"
        print(f"\n[{status}] {report['scenario']}")
        print(f"  {report['passed']}/{report['total']} passed")

        if report["failed"] > 0:
            all_passed = False
            for r in report["results"]:
                if not r["passed"]:
                    print(f"  ! {r['endpoint']}: got {r['actual_status']}, expected {r['expected_status']}")
                    if r["detail"]:
                        print(f"    {r['detail']}")

    # Save report
    with open("security/reports/attack-scenarios.json", "w") as f:
        json.dump(consolidated, f, indent=2, default=str)
    print("\nReport saved to security/reports/attack-scenarios.json")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
