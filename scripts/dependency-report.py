#!/usr/bin/env python3
"""
Dependency Vulnerability Report Generator

Reads all dependency files, runs vulnerability scanners (safety, pip-audit),
and generates a comprehensive report in both text and JSON formats.
Outputs to dependency-report.txt and dependency-report.json.

Usage:
    python scripts/dependency-report.py
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REQUIREMENT_FILES: list[tuple[str, str]] = [
    ("API", "apps/api/requirements.txt"),
    ("Scheduler", "services/scheduler/requirements.txt"),
]

PACKAGE_JSON = "apps/web/package.json"
OUTPUT_REPORT = "dependency-report.txt"
OUTPUT_JSON = "dependency-report.json"

STORYBOOK_PEER_DEPS: set[str] = {
    "@storybook/addon-essentials",
    "@storybook/addon-docs",
    "@storybook/addon-a11y",
    "@storybook/addon-vitest",
    "@storybook/nextjs",
    "@storybook/nextjs-vite",
    "@storybook/react",
    "@storybook/theming",
    "storybook",
}


def parse_requirements(path: str) -> list[dict[str, Any]]:
    """Parse a pip requirements.txt into structured entries."""
    entries: list[dict[str, Any]] = []
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("-"):
                    continue
                match = re.match(
                    r"^([a-zA-Z0-9_.-]+)\s*([><=!~]+)\s*([a-zA-Z0-9_.*-]+)", line
                )
                if match:
                    entries.append(
                        {
                            "name": match.group(1),
                            "operator": match.group(2),
                            "version": match.group(3),
                        }
                    )
                else:
                    entries.append({"name": line, "operator": None, "version": None})
    except FileNotFoundError:
        print(f"  [WARN] Requirements file not found: {path}")
    return entries


def parse_package_json(path: str) -> dict[str, Any]:
    """Parse package.json and extract all dependencies."""
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return {
            "dependencies": data.get("dependencies", {}),
            "devDependencies": data.get("devDependencies", {}),
        }
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"  [WARN] Could not parse {path}: {e}")
        return {"dependencies": {}, "devDependencies": {}}


def run_safety_check(req_file: str) -> list[dict[str, Any]]:
    """Run safety check on a requirements file and return vulnerabilities."""
    try:
        result = subprocess.run(
            ["safety", "check", "-r", req_file, "--output", "json"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                vulns: list[dict[str, Any]] = []
                if isinstance(data, list):
                    for v in data:
                        vulns.append(
                            {
                                "package": v.get("package_name", v.get("name", "unknown")),
                                "installed": v.get("installed_version", v.get("version", "unknown")),
                                "vulnerable_spec": v.get("vulnerable_spec", v.get("spec", "unknown")),
                                "severity": v.get("severity", v.get("severity_level", "UNKNOWN")).upper(),
                                "description": v.get("advisory", v.get("description", "")),
                                "scanner": "safety",
                            }
                        )
                    return vulns
            except json.JSONDecodeError:
                pass
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"  [WARN] safety check failed: {e}")
    return []


def run_pip_audit(req_file: str) -> list[dict[str, Any]]:
    """Run pip-audit on a requirements file and return vulnerabilities."""
    try:
        result = subprocess.run(
            ["pip-audit", "-r", req_file, "--format", "json"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                vulns: list[dict[str, Any]] = []
                for dep in data.get("dependencies", []):
                    for v in dep.get("vulnerabilities", []):
                        vulns.append(
                            {
                                "package": dep.get("name", "unknown"),
                                "installed": dep.get("version", "unknown"),
                                "vulnerable_spec": v.get("spec", "unknown"),
                                "severity": v.get("severity", "UNKNOWN").upper(),
                                "description": v.get("advisory", v.get("description", "")),
                                "scanner": "pip-audit",
                            }
                        )
                return vulns
            except json.JSONDecodeError:
                pass
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"  [WARN] pip-audit failed: {e}")
    return []


def check_outdated_storybook_deps(
    packages: dict[str, str],
) -> list[dict[str, Any]]:
    """Flag Storybook packages pinned for peer-dependency compatibility."""
    findings: list[dict[str, Any]] = []
    for name, version in packages.items():
        if name in STORYBOOK_PEER_DEPS:
            pin_type = "exact"
            if version.startswith("^"):
                pin_type = "caret"
            elif version.startswith("~"):
                pin_type = "tilde"
            elif version.startswith(">="):
                pin_type = "gte"

            if pin_type == "exact":
                findings.append(
                    {
                        "package": name,
                        "current": version,
                        "severity": "INFO",
                        "description": (
                            "Pinned to exact version for Storybook compatibility. "
                            "Update cautiously and verify peer deps."
                        ),
                        "scanner": "peer-check",
                    }
                )
    return findings


def generate_report(
    python_vulns: list[dict[str, Any]],
    npm_findings: list[dict[str, Any]],
    python_deps: dict[str, list[dict[str, Any]]],
    npm_deps: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    """Generate human-readable text report and structured JSON report."""
    now = datetime.utcnow().isoformat() + "Z"

    severity_counts: dict[str, int] = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
        "UNKNOWN": 0,
        "INFO": 0,
    }
    all_vulns = python_vulns + npm_findings
    for v in all_vulns:
        sev = v.get("severity", "UNKNOWN").upper()
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    total_python_deps = sum(len(deps) for deps in python_deps.values())

    critical = [v for v in all_vulns if v.get("severity") == "CRITICAL"]

    report_data: dict[str, Any] = {
        "generated_at": now,
        "summary": {
            "total_python_packages": total_python_deps,
            "total_npm_packages": sum(len(d) for d in npm_deps.values()),
            "total_vulnerabilities": len(all_vulns),
            "critical_count": len(critical),
            "severity_breakdown": severity_counts,
        },
        "vulnerabilities": all_vulns,
        "python_dependencies": python_deps,
    }

    lines: list[str] = []
    lines.append("=" * 72)
    lines.append("  DEPENDENCY VULNERABILITY REPORT")
    lines.append(f"  Generated: {now}")
    lines.append("=" * 72)
    lines.append("")

    lines.append(f"  Python packages:  {report_data['summary']['total_python_packages']}")
    lines.append(f"  npm packages:     {report_data['summary']['total_npm_packages']}")
    lines.append(f"  Total vulns:      {report_data['summary']['total_vulnerabilities']}")
    lines.append(f"  Critical vulns:   {report_data['summary']['critical_count']}")
    lines.append("")

    active_severities = [s for s in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN", "INFO"] if severity_counts.get(s, 0) > 0]  # fmt: skip
    if active_severities:
        lines.append("  Severity breakdown:")
        for sev in active_severities:
            lines.append(f"    {sev:8s}: {severity_counts[sev]}")
        lines.append("")

    if python_vulns:
        lines.append("-" * 72)
        lines.append("  PYTHON VULNERABILITIES")
        lines.append("-" * 72)
        for v in python_vulns:
            sev = v.get("severity", "?").upper()
            pkg = v.get("package", "?")
            ver = v.get("installed", "?")
            desc = v.get("description", "N/A")[:120]
            scanner = v.get("scanner", "?")
            lines.append(f"    [{sev:8s}] {pkg}=={ver}")
            lines.append(f"              Scanner: {scanner}")
            lines.append(f"              {desc}")
            lines.append("")

    if npm_findings:
        lines.append("-" * 72)
        lines.append("  NPM / STORYBOOK NOTES")
        lines.append("-" * 72)
        for v in npm_findings:
            sev = v.get("severity", "?").upper()
            pkg = v.get("package", "?")
            ver = v.get("current", "?")
            desc = v.get("description", "N/A")[:120]
            lines.append(f"    [{sev:8s}] {pkg}@{ver}")
            lines.append(f"              {desc}")
            lines.append("")

    lines.append("=" * 72)
    lines.append("  END OF REPORT")
    lines.append("=" * 72)

    return "\n".join(lines), report_data


def main() -> None:
    """Main entry point for the dependency report generator."""
    repo_root = Path(__file__).resolve().parent.parent

    print("=" * 60)
    print("  Dependency Vulnerability Report Generator")
    print("=" * 60)
    print()

    # 1. Parse dependency files
    print("[1/5] Parsing dependency files...")
    python_deps: dict[str, list[dict[str, Any]]] = {}
    for label, rel_path in REQUIREMENT_FILES:
        full_path = repo_root / rel_path
        deps = parse_requirements(str(full_path))
        python_deps[label] = deps
        print(f"  {label}: {len(deps)} packages ({rel_path})")

    npm_deps = parse_package_json(str(repo_root / PACKAGE_JSON))
    total_npm = sum(len(d) for d in npm_deps.values())
    print(f"  npm: {total_npm} packages ({PACKAGE_JSON})")
    print()

    # 2. Run safety checks
    print("[2/5] Running safety checks...")
    python_vulns: list[dict[str, Any]] = []
    for label, rel_path in REQUIREMENT_FILES:
        full_path = repo_root / rel_path
        if full_path.exists():
            vulns = run_safety_check(str(full_path))
            python_vulns.extend(vulns)
            print(f"  {label}: {len(vulns)} vulnerabilities found")

    # 3. Run pip-audit
    print("[3/5] Running pip-audit checks...")
    for label, rel_path in REQUIREMENT_FILES:
        full_path = repo_root / rel_path
        if full_path.exists():
            vulns = run_pip_audit(str(full_path))
            python_vulns.extend(vulns)
            print(f"  {label}: {len(vulns)} vulnerabilities found")
    print()

    # 4. Check npm Storybook peer constraints
    print("[4/5] Checking npm Storybook peer constraints...")
    npm_findings: list[dict[str, Any]] = []
    for dep_type in ("dependencies", "devDependencies"):
        findings = check_outdated_storybook_deps(npm_deps.get(dep_type, {}))
        npm_findings.extend(findings)
        if findings:
            print(f"  {dep_type}: {len(findings)} pinned Storybook packages found")
    print()

    # 5. Generate report
    print("[5/5] Generating report...")
    report_text, report_data = generate_report(
        python_vulns, npm_findings, python_deps, npm_deps
    )

    report_path = repo_root / OUTPUT_REPORT
    json_path = repo_root / OUTPUT_JSON

    with open(report_path, "w") as f:
        f.write(report_text)
    with open(json_path, "w") as f:
        json.dump(report_data, f, indent=2)

    print(f"  Text report: {report_path}")
    print(f"  JSON report: {json_path}")
    print()
    print(report_text)

    critical_count = report_data["summary"]["critical_count"]
    if critical_count > 0:
        print(f"\n  FAILURE: {critical_count} critical vulnerabilities found.")
        sys.exit(1)
    else:
        print("\n  SUCCESS: No critical vulnerabilities found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
