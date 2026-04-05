```
.\backend-framework\scripts\up-all-local.ps1
```

```
.\backend-framework\scripts\down-all-local.ps1
```

## Shared Logging (backend_framework)

All services created through `backend_framework.create_app(...)` now get:

- centralized logger setup (single root logger)
- optional JSON log output (default: enabled)
- per-request logs (`method`, `path`, `status_code`, `duration_ms`, `client_host`)
- unhandled exception logs with stack traces

This is framework-level, so both `auth-service` and `stuff` benefit automatically.

### Environment Variables

- `LOG_LEVEL` (default: `INFO`)
- `LOG_JSON` (default: `true`)
- `ENVIRONMENT` (default: `local`)
- `SERVICE_NAME` (optional, defaults to FastAPI app title)

Example:

```env
LOG_LEVEL=INFO
LOG_JSON=true
ENVIRONMENT=local
SERVICE_NAME=auth-service
```

### Loki / Promtail / Grafana

When `LOG_JSON=true`, logs are emitted as structured JSON to stdout. This works well with Docker logging drivers or Promtail scraping container stdout and shipping to Loki.

Suggested Loki labels to extract in your pipeline:

- `service`
- `environment`
- `level`
- `logger`

