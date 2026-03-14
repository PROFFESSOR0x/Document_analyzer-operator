# API Reference

API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/auth/logout` | User logout |
| POST | `/api/v1/auth/refresh` | Refresh token |
| GET | `/api/v1/auth/me` | Get current user |

## Agent Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/agents` | List agents |
| GET | `/api/v1/agents/{id}` | Get agent details |
| POST | `/api/v1/agents` | Create agent |
| PUT | `/api/v1/agents/{id}` | Update agent |
| DELETE | `/api/v1/agents/{id}` | Delete agent |
| POST | `/api/v1/agents/{id}/execute` | Execute task |

## Workflow Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/workflows` | List workflows |
| GET | `/api/v1/workflows/{id}` | Get workflow |
| POST | `/api/v1/workflows` | Create workflow |
| POST | `/api/v1/workflows/{id}/execute` | Execute workflow |
| POST | `/api/v1/workflows/{id}/pause` | Pause workflow |
| POST | `/api/v1/workflows/{id}/resume` | Resume workflow |
| POST | `/api/v1/workflows/{id}/cancel` | Cancel workflow |

## LLM Provider Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/llm-providers` | List providers |
| GET | `/api/v1/llm-providers/{id}` | Get provider details |
| POST | `/api/v1/llm-providers` | Create provider |
| PUT | `/api/v1/llm-providers/{id}` | Update provider |
| DELETE | `/api/v1/llm-providers/{id}` | Delete provider |
| POST | `/api/v1/llm-providers/{id}/test` | Test connection |
| GET | `/api/v1/llm-providers/usage` | Usage statistics |

## WebSocket

| Endpoint | Description |
|----------|-------------|
| `WS /api/v1/ws` | Real-time events |

For complete API documentation, visit http://localhost:8000/docs when the backend is running.
