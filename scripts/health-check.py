import argparse
import json
import sys
import time
from datetime import datetime, timezone
import httpx
from httpx import ConnectError, TimeoutException, HTTPStatusError


MONITORS = [
    {
        "friendly_name": "ARIA OS - API Health",
        "url": "https://api.secondbrain-os.com/health",
    },
    {
        "friendly_name": "ARIA OS - API Ready",
        "url": "https://api.secondbrain-os.com/health/ready",
    },
    {
        "friendly_name": "ARIA OS - Frontend",
        "url": "https://secondbrain-os.vercel.app",
    },
    {
        "friendly_name": "ARIA OS - Scheduler",
        "url": "https://scheduler.secondbrain-os.com/health",
    },
]


class HealthCheckLogger:
    def _log(self, level: str, message: str, **kwargs):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "service": "health-check",
            "message": message,
            **kwargs,
        }
        stream = sys.stderr if level in ("ERROR", "WARN") else sys.stdout
        stream.write(json.dumps(entry) + "\n")
        stream.flush()

    def info(self, message: str, **kwargs):
        self._log("INFO", message, **kwargs)

    def warn(self, message: str, **kwargs):
        self._log("WARN", message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log("ERROR", message, **kwargs)


logger = HealthCheckLogger()


def check_endpoint(client: httpx.Client, name: str, url: str, timeout: int = 10) -> dict:
    start = time.monotonic()
    status = "up"
    status_code = None
    error_message = None

    try:
        resp = client.get(url, timeout=timeout, follow_redirects=True)
        status_code = resp.status_code
        duration_ms = (time.monotonic() - start) * 1000

        if 200 <= status_code < 400:
            status = "up"
        else:
            status = "degraded"
            error_message = f"HTTP {status_code}"

        logger.info(
            "Health check completed",
            endpoint=name,
            url=url,
            status_code=status_code,
            duration_ms=round(duration_ms, 2),
            status=status,
        )

    except ConnectError as e:
        duration_ms = (time.monotonic() - start) * 1000
        status = "down"
        error_message = f"Connection refused: {e}"
        logger.error(
            "Health check failed",
            endpoint=name,
            url=url,
            duration_ms=round(duration_ms, 2),
            status="down",
            error_type="ConnectError",
            error_message=error_message,
        )

    except TimeoutException as e:
        duration_ms = (time.monotonic() - start) * 1000
        status = "down"
        error_message = f"Timeout after {timeout}s: {e}"
        logger.error(
            "Health check timeout",
            endpoint=name,
            url=url,
            duration_ms=round(duration_ms, 2),
            status="down",
            error_type="TimeoutException",
            error_message=error_message,
        )

    except HTTPStatusError as e:
        duration_ms = (time.monotonic() - start) * 1000
        status = "degraded"
        error_message = f"HTTP error: {e.response.status_code}"
        logger.error(
            "Health check HTTP error",
            endpoint=name,
            url=url,
            status_code=e.response.status_code,
            duration_ms=round(duration_ms, 2),
            status="degraded",
            error_message=error_message,
        )

    except Exception as e:
        duration_ms = (time.monotonic() - start) * 1000
        status = "down"
        error_message = f"Unexpected error: {type(e).__name__}: {e}"
        logger.error(
            "Health check exception",
            endpoint=name,
            url=url,
            duration_ms=round(duration_ms, 2),
            status="down",
            error_type=type(e).__name__,
            error_message=str(e),
        )

    return {
        "friendly_name": name,
        "url": url,
        "status": status,
        "status_code": status_code,
        "error_message": error_message,
        "duration_ms": round((time.monotonic() - start) * 1000, 2),
    }


def send_slack_alert(webhook_url: str, results: list[dict]):
    down = [r for r in results if r["status"] == "down"]
    degraded = [r for r in results if r["status"] == "degraded"]
    failed = down + degraded

    if not failed:
        return

    lines = [f"*ARIA OS Health Check — {len(failed)} issue(s) detected*\n"]
    for r in failed:
        icon = "🔴" if r["status"] == "down" else "🟡"
        lines.append(f"{icon} *{r['friendly_name']}* — {r['status'].upper()}")
        lines.append(f"  URL: {r['url']}")
        if r["error_message"]:
            lines.append(f"  Error: {r['error_message']}")
        lines.append("")

    payload = {
        "text": "\n".join(lines),
        "username": "ARIA OS Health Bot",
        "icon_emoji": ":robot_face:",
    }

    try:
        resp = httpx.post(webhook_url, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Slack alert sent", webhook=webhook_url[:50], results_count=len(failed))
    except Exception as e:
        logger.error("Failed to send Slack alert", error_message=str(e))


def output_prometheus(results: list[dict]):
    ts = int(time.time())
    for r in results:
        status_val = {"up": 1, "degraded": 0, "down": 0}.get(r["status"], 0)
        name = r["friendly_name"].lower().replace(" ", "_").replace("-", "_")
        print('# HELP health_check_status ARIA OS endpoint health status (1=up, 0=down/degraded)')
        print('# TYPE health_check_status gauge')
        print(f'health_check_status{{endpoint="{name}",url="{r["url"]}"}} {status_val} {ts}')
        print(f'health_check_duration_ms{{endpoint="{name}",url="{r["url"]}"}} {r["duration_ms"]} {ts}')
    print()


def run_checks(timeout: int = 10) -> list[dict]:
    results = []
    with httpx.Client() as client:
        for monitor in MONITORS:
            result = check_endpoint(client, monitor["friendly_name"], monitor["url"], timeout)
            results.append(result)
    return results


def exit_code(results: list[dict]) -> int:
    if any(r["status"] == "down" for r in results):
        return 1
    if any(r["status"] == "degraded" for r in results):
        return 2
    return 0


def main():
    parser = argparse.ArgumentParser(description="ARIA OS External Health Checker")
    parser.add_argument(
        "--slack-webhook",
        type=str,
        default=None,
        help="Slack webhook URL to send failure notifications",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=0,
        help="Run in a loop every N minutes (0 = run once)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="HTTP request timeout in seconds",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--prometheus",
        action="store_true",
        help="Output metrics in Prometheus format",
    )
    args = parser.parse_args()

    interval_seconds = args.repeat * 60

    while True:
        results = run_checks(timeout=args.timeout)

        if args.format == "json":
            print(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "results": results}, indent=2))
        elif args.prometheus:
            output_prometheus(results)
        else:
            for r in results:
                icon = {"up": "✅", "down": "❌", "degraded": "⚠️"}.get(r["status"], "❓")
                print(f"{icon} {r['friendly_name']:40s} {r['status'].upper():10s} {r['url']}")
                if r["error_message"]:
                    print(f"   └─ {r['error_message']}")

            up_count = sum(1 for r in results if r["status"] == "up")
            total = len(results)
            print(f"\nResults: {up_count}/{total} endpoints UP")

        if args.slack_webhook and any(r["status"] != "up" for r in results):
            send_slack_alert(args.slack_webhook, results)

        code = exit_code(results)

        if interval_seconds <= 0:
            sys.exit(code)

        logger.info(f"Sleeping {args.repeat} minute(s) before next check...")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()