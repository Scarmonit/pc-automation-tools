#!/usr/bin/env python
"""
Unified Health Check Utility for pc-automation-tools

Checks availability and basic functionality of:
- LocalAI / OpenAI-compatible endpoint
- Ollama
- vLLM (if exposed)
- Flowise
- Prometheus
- Grafana
- Any custom agent orchestrator endpoints you configure

Usage:
    python scripts/health_check.py
Environment (override with env vars):
    OPENAI_BASE_URL, LOCALAI_BASE_URL
    OLLAMA_BASE_URL
    VLLM_BASE_URL
    FLOWISE_BASE_URL
    PROMETHEUS_BASE_URL
    GRAFANA_BASE_URL
    TIMEOUT_SECONDS
"""

from __future__ import annotations
import os
import asyncio
import json
import time
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List

import httpx

DEFAULT_TIMEOUT = float(os.getenv("TIMEOUT_SECONDS", "8"))


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
        # Resolve endpoints with sensible fallbacks
        self.endpoints = {
            "localai": os.getenv("LOCALAI_BASE_URL") or os.getenv("OPENAI_BASE_URL") or "http://localhost:8080/v1",
            "ollama": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "vllm": os.getenv("VLLM_BASE_URL", "http://localhost:8000"),
            "flowise": os.getenv("FLOWISE_BASE_URL", "http://localhost:3000"),
            "prometheus": os.getenv("PROMETHEUS_BASE_URL", "http://localhost:9090"),
            "grafana": os.getenv("GRAFANA_BASE_URL", "http://localhost:3001"),
        }

    async def _check_openai_compatible(self, client: httpx.AsyncClient, name: str, base_url: str) -> EndpointResult:
        # Try models list
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
            return EndpointResult(name=name, url=url, ok=ok,
                                  status_code=resp.status_code,
                                  latency_ms=latency, detail=detail, extra=extra)
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
            return EndpointResult(name=name, url=full_url, ok=ok,
                                  status_code=resp.status_code,
                                  latency_ms=latency, detail=detail)
        except Exception as e:
            return EndpointResult(name=name, url=full_url, ok=False, detail=str(e))

    async def run(self) -> HealthReport:
        results: List[EndpointResult] = []
        async with httpx.AsyncClient() as client:
            tasks = []

            # LocalAI / OpenAI compatible endpoint
            tasks.append(self._check_openai_compatible(client, "localai_or_openai", self.endpoints["localai"]))

            # Ollama (check /api/tags)
            tasks.append(self._check_simple(client, "ollama", self.endpoints["ollama"], "/api/tags"))

            # vLLM (check /v1/models)
            tasks.append(self._check_openai_compatible(client, "vllm", self.endpoints["vllm"]))

            # Flowise (root or /api/v1/ping if available)
            tasks.append(self._check_simple(client, "flowise", self.endpoints["flowise"]))

            # Prometheus (/api/v1/status/runtimeinfo)
            tasks.append(self._check_simple(client, "prometheus", self.endpoints["prometheus"], "/api/v1/status/runtimeinfo"))

            # Grafana (/api/health)
            tasks.append(self._check_simple(client, "grafana", self.endpoints["grafana"], "/api/health"))

            gathered = await asyncio.gather(*tasks)
            results.extend(gathered)

        return HealthReport(timestamp=time.time(), results=results)


async def main() -> None:
    checker = HealthChecker()
    report = await checker.run()
    print(json.dumps(report.to_dict(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())