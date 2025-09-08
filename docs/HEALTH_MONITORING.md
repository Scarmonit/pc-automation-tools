# 🩺 Health Monitoring

A unified asynchronous health check utility is available at `scripts/health_check.py`. It probes key AI and observability services to quickly surface outages or misconfigurations.

## ✅ Covered Components

| Component | Purpose | Probe Path |
|-----------|---------|------------|
| LocalAI / OpenAI-compatible endpoint | Model listing + latency | `/models` |
| Ollama | Installed models (tags) | `/api/tags` |
| vLLM | Model listing (OpenAI schema) | `/v1/models` |
| Flowise | Basic reachability | `/` |
| Prometheus | Runtime info | `/api/v1/status/runtimeinfo` |
| Grafana | Core health | `/api/health` |

## 🔧 Environment Configuration

Set any of these to override defaults:

```
LOCALAI_BASE_URL
OPENAI_BASE_URL   (fallback if LOCALAI_BASE_URL unset)
OLLAMA_BASE_URL               (default: http://localhost:11434)
VLLM_BASE_URL                  (default: http://localhost:8000)
FLOWISE_BASE_URL               (default: http://localhost:3000)
PROMETHEUS_BASE_URL            (default: http://localhost:9090)
GRAFANA_BASE_URL               (default: http://localhost:3001)
TIMEOUT_SECONDS                (default: 8)
```

## 🧪 Output Format (JSON)

Example (truncated):
```json
{
  "timestamp": 1725770000.123,
  "summary": {
    "total": 6,
    "up": 5,
    "down": 1,
    "uptime_percent": 83.33
  },
  "results": [
    {
      "name": "localai_or_openai",
      "url": "http://localhost:8080/v1/models",
      "ok": true,
      "status_code": 200,
      "latency_ms": 123.5,
      "extra": {
        "model_count": 4,
        "first_model": "llama3.2"
      }
    }
  ]
}
```

## 🧩 Extending

Add a new endpoint:
1. Provide an env var for its base URL.
2. Append a check task in `HealthChecker.run()` (use `_check_simple` or write a specialized checker).
3. Include any structured metadata in the `extra` field.

## 🚨 Suggested Next Enhancements

- Optional: emit Prometheus exposition text for integration into monitoring.
- Optional: add `--fail-on-down` flag for CI gating.
- Optional: write results to `health_reports/` with timestamped JSON files for trend analysis.

## 🛡️ Exit Behavior

Currently always exits 0. Modify `main()` to enforce non-zero exit codes if you want CI to block deployments on failed dependencies.

---

Maintainer note: Keep this lightweight—avoid adding heavyweight dependencies so it stays usable in minimal environments.
