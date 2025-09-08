#!/usr/bin/env python
"""
Unified Health Check Utility for pc-automation-tools

Features:
- Probes LocalAI/OpenAI-compatible endpoint (/models), Ollama (/api/tags), vLLM (/v1/models),
  Flowise (/), Prometheus (/api/v1/status/runtimeinfo), Grafana (/api/health)
- JSON structured output (stdout)
- Optional Prometheus metrics export (--prometheus-export <file>)
- Optional CI gating (--fail-on-down)
- Optional persistent report storage (--save-dir, --retain)
- Optional automatic issue reporting for down services (--auto-report --issue-repo <owner/repo>)
- Deduplicated issue creation via signature caching
"""
from __future__ import annotations
import os
import asyncio
import json
import time
import argparse
import hashlib
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List

import httpx

DEFAULT_TIMEOUT = float(os.getenv("TIMEOUT_SECONDS", "8"))
ISSUE_STATE_DIR = os.getenv("HEALTH_ISSUE_STATE_DIR", ".health_issue_state")

@dataclass
class EndpointResult:
    name: str
    url: str
    ok: bool
    status_code: Optional[int] = None
    latency_ms: Optional[float] = None
    detail: Optional[str] = None
    extra: Dict[str, Any] = None

@dataclass
class HealthReport:
    timestamp: float
    results: List[EndpointResult]

    def summary(self) -> Dict[str, Any]:
        total = len(self.results)
        up = sum(1 for r in self.results if r.ok)
        return {
            "total": total,
            "up": up,
            "down": total - up,
            "uptime_percent": (up / total * 100) if total else 0.0
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "summary": self.summary(),
            "results": [asdict(r) for r in self.results]
        }

class HealthChecker:
    def __init__(self) -> None:
        self.endpoints = {
            "localai": os.getenv("LOCALAI_BASE_URL") or os.getenv("OPENAI_BASE_URL") or "http://localhost:8080/v1",
            "ollama": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "vllm": os.getenv("VLLM_BASE_URL", "http://localhost:8000"),
            "flowise": os.getenv("FLOWISE_BASE_URL", "http://localhost:3000"),
            "prometheus": os.getenv("PROMETHEUS_BASE_URL", "http://localhost:9090"),
            "grafana": os.getenv("GRAFANA_BASE_URL", "http://localhost:3001"),
        }

    async def _check_openai_compatible(self, client: httpx.AsyncClient, name: str, base_url: str) -> EndpointResult:
        url = base_url.rstrip("/") + "/models"
        start = time.perf_counter()
        try:
            resp = await client.get(url, timeout=DEFAULT_TIMEOUT)
            latency = (time.perf_counter() - start) * 1000
            ok = resp.status_code == 200 and "data" in resp.json()
            detail = None
            extra = {}
            if ok:
                models = resp.json().get("data", [])
                extra["model_count"] = len(models)
                if models:
                    extra["first_model"] = models[0].get("id")
            else:
                detail = f"Unexpected response: {resp.text[:160]}"
            return EndpointResult(name=name, url=url, ok=ok, status_code=resp.status_code, latency_ms=latency, detail=detail, extra=extra)
        except Exception as e:
            return EndpointResult(name=name, url=url, ok=False, detail=str(e))

    async def _check_simple(self, client: httpx.AsyncClient, name: str, url: str, path: str = "/") -> EndpointResult:
        full_url = url.rstrip("/") + path
        start = time.perf_counter()
        try:
            resp = await client.get(full_url, timeout=DEFAULT_TIMEOUT)
            latency = (time.perf_counter() - start) * 1000
            ok = resp.status_code < 500
            detail = None
            if not ok:
                detail = f"Bad status {resp.status_code}"
            return EndpointResult(name=name, url=full_url, ok=ok, status_code=resp.status_code, latency_ms=latency, detail=detail)
        except Exception as e:
            return EndpointResult(name=name, url=full_url, ok=False, detail=str(e))

    async def run(self) -> HealthReport:
        results: List[EndpointResult] = []
        async with httpx.AsyncClient() as client:
            tasks = [
                self._check_openai_compatible(client, "localai_or_openai", self.endpoints["localai"]),
                self._check_simple(client, "ollama", self.endpoints["ollama"], "/api/tags"),
                self._check_openai_compatible(client, "vllm", self.endpoints["vllm"]),
                self._check_simple(client, "flowise", self.endpoints["flowise"]),
                self._check_simple(client, "prometheus", self.endpoints["prometheus"], "/api/v1/status/runtimeinfo"),
                self._check_simple(client, "grafana", self.endpoints["grafana"], "/api/health"),
            ]
            gathered = await asyncio.gather(*tasks)
            results.extend(gathered)
        return HealthReport(timestamp=time.time(), results=results)

def generate_prometheus_metrics(report: HealthReport) -> str:
    lines = [
        "# HELP service_up Was the service marked healthy (1) or not (0)",
        "# TYPE service_up gauge",
        "# HELP service_latency_ms Observed latency in milliseconds (if available)",
        "# TYPE service_latency_ms gauge",
    ]
    for r in report.results:
        up = 1 if r.ok else 0
        lines.append(f'service_up{{service="{r.name}"}} {up}')
        if r.latency_ms is not None:
            lines.append(f'service_latency_ms{{service="{r.name}"}} {r.latency_ms:.3f}')
    return "\n".join(lines) + "\n"

async def create_issue(owner_repo: str, token: str, title: str, body: str, labels: List[str]) -> Optional[str]:
    api_url = f"https://api.github.com/repos/{owner_repo}/issues"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "pc-automation-tools-health-agent"
    }
    payload = {"title": title, "body": body}
    if labels:
        payload["labels"] = labels
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(api_url, headers=headers, json=payload)
        if resp.status_code in (200, 201):
            return resp.json().get("html_url")
        return None

def signature_for(service_name: str, reason: str) -> str:
    h = hashlib.sha256()
    h.update(service_name.encode())
    h.update(reason.encode())
    return h.hexdigest()[:20]

def issue_already_reported(sig: str) -> bool:
    os.makedirs(ISSUE_STATE_DIR, exist_ok=True)
    marker = os.path.join(ISSUE_STATE_DIR, f"{sig}.mark")
    return os.path.exists(marker)

def mark_issue_reported(sig: str) -> None:
    os.makedirs(ISSUE_STATE_DIR, exist_ok=True)
    marker = os.path.join(ISSUE_STATE_DIR, f"{sig}.mark")
    try:
        with open(marker, "w", encoding="utf-8") as f:
            f.write(str(int(time.time())))
    except OSError:
        pass

async def auto_report(report: HealthReport, issue_repo: str, label_prefix: str = "health") -> Dict[str, Any]:
    token = os.getenv("GITHUB_TOKEN")
    results: Dict[str, Any] = {"created": [], "skipped": []}
    if not token:
        return {"error": "GITHUB_TOKEN missing", "created": [], "skipped": []}
    tasks = []
    for r in report.results:
        if r.ok:
            continue
        reason = r.detail or f"Service {r.name} failed"
        sig = signature_for(r.name, reason)
        if issue_already_reported(sig):
            results["skipped"].append(r.name)
            continue
        title = f"[Health] {r.name} DOWN"
        body_lines = [
            f"Automated health monitor detected a failure for `{r.name}`.",
            "",
            f"- URL: `{r.url}`",
            f"- Status Code: {r.status_code}",
            f"- Detail: {r.detail or 'n/a'}",
            f"- Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(report.timestamp))} UTC",
            "",
            f"Signature: `{sig}`",
            "",
            "This issue was auto-generated. Close when resolved; delete the state marker to allow re-reporting if needed."
        ]
        labels = [label_prefix, "automated", "incident"]
        async def create_and_mark():
            url = await create_issue(issue_repo, token, title, "\n".join(body_lines), labels)
            if url:
                mark_issue_reported(sig)
                results["created"].append({"service": r.name, "issue_url": url})
            else:
                results["skipped"].append(r.name)
        tasks.append(create_and_mark())
    if tasks:
        await asyncio.gather(*tasks)
    return results

async def async_main(args) -> int:
    checker = HealthChecker()
    report = await checker.run()
    data = report.to_dict()

    if args.save_dir:
        os.makedirs(args.save_dir, exist_ok=True)
        fname = f"health_{int(report.timestamp)}.json"
        fpath = os.path.join(args.save_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        if args.retain and args.retain > 0:
            files = sorted([p for p in os.listdir(args.save_dir) if p.startswith("health_") and p.endswith(".json")])
            excess = len(files) - args.retain
            for old in files[:excess]:
                try:
                    os.remove(os.path.join(args.save_dir, old))
                except OSError:
                    pass

    if args.prometheus_export:
        metrics = generate_prometheus_metrics(report)
        os.makedirs(os.path.dirname(args.prometheus_export) or ".", exist_ok=True)
        with open(args.prometheus_export, "w", encoding="utf-8") as f:
            f.write(metrics)

    if args.auto_report:
        issue_repo = args.issue_repo or os.getenv("GITHUB_REPOSITORY")
        if issue_repo:
            data["auto_issue"] = await auto_report(report, issue_repo)
        else:
            data["auto_issue"] = {"error": "No repository specified (use --issue-repo or set GITHUB_REPOSITORY)"}

    print(json.dumps(data, indent=2))

    if args.fail_on_down and data["summary"]["down"] > 0:
        return 1
    return 0

def main() -> None:
    parser = argparse.ArgumentParser(description="Unified health check")
    parser.add_argument("--prometheus-export", help="Write Prometheus metrics to file")
    parser.add_argument("--fail-on-down", action="store_true", help="Exit 1 if any service is down")
    parser.add_argument("--save-dir", help="Directory to persist JSON reports")
    parser.add_argument("--retain", type=int, default=0, help="Maximum number of JSON reports to retain (0 = unlimited)")
    parser.add_argument("--auto-report", action="store_true", help="Automatically open GitHub issues for down services")
    parser.add_argument("--issue-repo", help="Override target repo (owner/name) for issue reporting")
    args = parser.parse_args()
    try:
        exit_code = asyncio.run(async_main(args))
    except KeyboardInterrupt:
        exit_code = 130
    raise SystemExit(exit_code)

if __name__ == "__main__":
    main()