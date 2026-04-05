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

## Shared Auth Proxy

Services that rely on `auth-service` for credentials can expose framework-owned proxy routes with:

```python
from backend_framework.auth import create_auth_proxy_router
```

The shared router exposes these endpoints on the service itself:

- `POST /auth/login`
- `POST /auth/register`
- `POST /auth/refresh`
- `POST /auth/logout`

`/auth/login` accepts the OAuth2 password form used by Swagger UI and forwards it to `auth-service` as the auth-service JSON payload.

Projects can attach service-specific post-auth logic through `create_auth_proxy_router(on_auth_success=...)`. The hook receives the auth event (`login`, `register`, or `refresh`) plus the decoded token payload, which lets services create local profile rows or run other project-specific synchronization after successful authentication.

### Auth Environment Variables

- `AUTH_SERVICE_URL` (default: `http://localhost:8001`)

In local Docker Desktop development, set `AUTH_SERVICE_URL=http://host.docker.internal:8001` for containers that need to reach the host-published auth-service.

