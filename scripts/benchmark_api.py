#!/usr/bin/env python
"""
Second Brain OS — API Performance Benchmark Script

Measures p50/p75/p90/p95/p99 latencies for key API endpoints.
Runs 50 iterations per endpoint by default.
Exits non-zero in CI mode if any SLO is exceeded.

Usage:
    python scripts/benchmark_api.py                          # Default run
    python scripts/benchmark_api.py --ci                     # CI mode (exit 1 on SLO breach)
    python scripts/benchmark_api.py --url http://localhost:8000
    python scripts/benchmark_api.py --iterations 100
    python scripts/benchmark_api.py --skip-ai                # Skip AI-powered endpoints
    python scripts/benchmark_api.py --output custom/path.json

Dependencies: httpx (in requirements.txt), Python 3.10+
"""

import argparse
import json
import math
import os
import sys
import time
from datetime import datetime, timezone

try:
    import httpx
except ImportError:
    print("ERROR: httpx is required. Install with: pip install httpx")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_URL = "http://localhost:8000"
DEFAULT_ITERATIONS = 50
DEFAULT_OUTPUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs",
    "engineering",
    "benchmark-results.json",
)

# SLOs in milliseconds — (category, p95_slo_ms)
# These must be kept in sync with docs/engineering/performance-benchmarks.md Section 2
ENDPOINT_SLOS = {
    "health": {"p95_ms": 200, "category": "health"},
    "health_ready": {"p95_ms": 200, "category": "health"},
    "tasks_list": {"p95_ms": 500, "category": "crud"},
    "tasks_create": {"p95_ms": 500, "category": "crud"},
    "habits_list": {"p95_ms": 500, "category": "crud"},
    "chat": {"p95_ms": 30000, "category": "ai"},
}

# Endpoints to benchmark — (name, method, path, json_body)
ENDPOINTS = [
    ("health", "GET", "/health", None),
    ("health_ready", "GET", "/health/ready", None),
    ("tasks_list", "GET", "/api/v1/tasks/?limit=5", None),
    ("tasks_create", "POST", "/api/v1/tasks/", {"title": "benchmark-task", "priority": "medium", "status": "pending"}),
    ("habits_list", "GET", "/api/v1/habits/?limit=5", None),
    ("chat", "POST", "/api/v1/chat/", {"message": "What is my top priority today?"}),
]

AI_ENDPOINT_NAMES = {"chat"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def compute_percentiles(values, percentiles):
    """Compute arbitrary percentiles from a sorted list of values."""
    values = sorted(values)
    n = len(values)
    results = {}
    for p in percentiles:
        if n == 0:
            results[p] = 0.0
        else:
            k = (p / 100.0) * (n - 1)
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                results[p] = values[int(k)]
            else:
                results[p] = values[f] * (c - k) + values[c] * (k - f)
    return results


def format_duration(ms):
    """Format milliseconds into a human-readable string."""
    if ms < 1:
        return f"{ms * 1000:.1f}us"
    if ms < 1000:
        return f"{ms:.2f}ms"
    return f"{ms / 1000:.2f}s"


def print_table(results):
    """Print a formatted results table."""
    print()
    print("=" * 100)
    print(f"{'Endpoint':<30} {'p50':>10} {'p75':>10} {'p90':>10} {'p95':>10} {'p99':>10} {'Errors':>8} {'SLO':>12}")
    print("=" * 100)

    for entry in results:
        p = entry["percentiles"]
        slo = entry["slo_ms"]
        slo_str = format_duration(slo) if slo else "N/A"
        status = "PASS" if entry["passed"] else "FAIL"
        print(
            f"{entry['name']:<30} "
            f"{format_duration(p[50]):>10} "
            f"{format_duration(p[75]):>10} "
            f"{format_duration(p[90]):>10} "
            f"{format_duration(p[95]):>10} "
            f"{format_duration(p[99]):>10} "
            f"{entry['errors']:>8} "
            f"{status:>8} ({slo_str})"
        )

    print("=" * 100)
    print(f"  All SLOs passed: {all(r['passed'] for r in results)}")
    print()


# ---------------------------------------------------------------------------
# Core Benchmark Logic
# ---------------------------------------------------------------------------

def benchmark_endpoint(client, name, method, path, json_body, iterations):
    """Benchmark a single endpoint and return stats."""
    latencies = []
    errors = 0

    for i in range(iterations):
        try:
            start = time.perf_counter()
            if method == "GET":
                response = client.get(path, timeout=httpx.Timeout(connect=2.0, read=120.0))
            elif method == "POST":
                response = client.post(path, json=json_body, timeout=httpx.Timeout(connect=2.0, read=120.0))
            elif method == "PUT":
                response = client.put(path, json=json_body, timeout=httpx.Timeout(connect=2.0, read=120.0))
            elif method == "DELETE":
                response = client.delete(path, timeout=httpx.Timeout(connect=2.0, read=120.0))
            else:
                raise ValueError(f"Unsupported method: {method}")

            elapsed = (time.perf_counter() - start) * 1000  # ms
            latencies.append(elapsed)

            if response.status_code >= 500:
                errors += 1

        except (httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError, httpx.ReadTimeout, httpx.WriteTimeout):
            errors += 1
            # Record a placeholder latency for error cases
            latencies.append(float("inf"))

    # Filter out infinities for percentile computation
    valid = [v for v in latencies if v != float("inf") and not math.isnan(v)]
    if not valid:
        return {
            "name": name,
            "method": method,
            "path": path,
            "iterations": iterations,
            "completed": iterations - errors,
            "errors": errors,
            "p50_ms": None,
            "p75_ms": None,
            "p90_ms": None,
            "p95_ms": None,
            "p99_ms": None,
            "percentiles": {},
            "slo_ms": None,
            "passed": False,
        }

    percentiles = compute_percentiles(valid, [50, 75, 90, 95, 99])

    slo = ENDPOINT_SLOS.get(name, {}).get("p95_ms")
    passed = True
    if slo is not None and percentiles[95] > slo:
        passed = False

    return {
        "name": name,
        "method": method,
        "path": path,
        "iterations": iterations,
        "completed": iterations - errors,
        "errors": errors,
        "p50_ms": round(percentiles[50], 2),
        "p75_ms": round(percentiles[75], 2),
        "p90_ms": round(percentiles[90], 2),
        "p95_ms": round(percentiles[95], 2),
        "p99_ms": round(percentiles[99], 2),
        "percentiles": percentiles,
        "slo_ms": slo,
        "passed": passed,
    }


def load_existing_results(path):
    """Load existing benchmark results from JSON file."""
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except (json.JSONDecodeError, IOError):
            pass
    return []


def save_results(path, results, target_url):
    """Append a new benchmark result entry to the JSON file."""
    existing = load_existing_results(path)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "script": "scripts/benchmark_api.py",
        "target": target_url,
        "endpoints": {},
    }

    for r in results:
        entry["endpoints"][r["name"]] = {
            "p50_ms": r["p50_ms"],
            "p75_ms": r["p75_ms"],
            "p90_ms": r["p90_ms"],
            "p95_ms": r["p95_ms"],
            "p99_ms": r["p99_ms"],
            "iterations": r["iterations"],
            "errors": r["errors"],
            "slo_ms": r["slo_ms"],
            "passed": r["passed"],
        }

    existing.append(entry)

    # Keep only the last 100 entries
    existing = existing[-100:]

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(existing, f, indent=2)

    print(f"  Results saved to: {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Second Brain OS — API Performance Benchmark Tool"
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help=f"Target API URL (default: {DEFAULT_URL})",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=DEFAULT_ITERATIONS,
        help=f"Number of iterations per endpoint (default: {DEFAULT_ITERATIONS})",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: exit with code 1 if any SLO is exceeded",
    )
    parser.add_argument(
        "--skip-ai",
        action="store_true",
        help="Skip AI-powered endpoints (faster, avoids LLM latency)",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output JSON file path (default: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("  Second Brain OS — API Benchmark")
    print(f"  Target: {args.url}")
    print(f"  Iterations per endpoint: {args.iterations}")
    print(f"  CI mode: {args.ci}")
    print(f"  Skip AI endpoints: {args.skip_ai}")
    print()

    # Filter endpoints
    endpoints = ENDPOINTS
    if args.skip_ai:
        endpoints = [ep for ep in ENDPOINTS if ep[0] not in AI_ENDPOINT_NAMES]

    results = []
    all_passed = True

    # Quick connectivity check before running benchmarks
    timeout = httpx.Timeout(connect=3.0, read=5.0, write=5.0, pool=3.0)
    try:
        probe = httpx.get(f"{args.url}/health", timeout=timeout)
    except httpx.ConnectError:
        print(f"  ERROR: Cannot connect to {args.url}")
        print("  Is the API server running?")
        print("  Start it with: make dev-api  (or uvicorn apps.api.main:app --reload)")
        print()
        if args.ci:
            sys.exit(1)
        sys.exit(0)
    except Exception as e:
        print(f"  ERROR connecting to {args.url}: {e}")
        if args.ci:
            sys.exit(1)
        sys.exit(0)

    timeout = httpx.Timeout(connect=5.0, read=120.0, write=30.0, pool=5.0)
    try:
        with httpx.Client(base_url=args.url, timeout=timeout) as client:
            for name, method, path, json_body in endpoints:
                print(f"  Benchmarking: {method} {path} ...", end=" ")
                try:
                    result = benchmark_endpoint(
                        client, name, method, path, json_body, args.iterations
                    )
                    results.append(result)
                    print(f"done ({result['completed']}/{result['iterations']} ok, {result['errors']} errors)")
                    if not result["passed"]:
                        all_passed = False
                        p95 = result["p95_ms"]
                        slo = result["slo_ms"]
                        print(f"    ⚠ SLO violation: p95={p95}ms > SLO={slo}ms")
                except Exception as e:
                    print(f"FAILED: {e}")
                    results.append({
                        "name": name,
                        "method": method,
                        "path": path,
                        "iterations": args.iterations,
                        "completed": 0,
                        "errors": args.iterations,
                        "p50_ms": None,
                        "p75_ms": None,
                        "p90_ms": None,
                        "p95_ms": None,
                        "p99_ms": None,
                        "percentiles": {},
                        "slo_ms": ENDPOINT_SLOS.get(name, {}).get("p95_ms"),
                        "passed": False,
                    })
                    all_passed = False

    except httpx.ConnectError:
        print(f"\n  ERROR: Cannot connect to {args.url}")
        print("  Is the API server running?")
        print("  Start it with: make dev-api  (or uvicorn apps.api.main:app --reload)")
        print()
        if args.ci:
            sys.exit(1)
        sys.exit(0)

    # Print results table
    print_table(results)

    # Save results
    save_results(args.output, results, args.url)

    # CI mode: exit non-zero if any SLO is violated
    if args.ci and not all_passed:
        print("  CI CHECK FAILED: One or more SLOs were exceeded.")
        sys.exit(1)

    if all_passed:
        print("  All SLOs met.")
    else:
        print("  Some SLOs were exceeded (see above).")


if __name__ == "__main__":
    main()
