# Document Analyzer Operator - Backend API

Production-ready FastAPI backend for the Document Analyzer Operator Platform.

## Features

- **FastAPI** - Modern, fast web framework for building APIs
- **PostgreSQL** - Primary database with async SQLAlchemy
- **Redis** - Caching, session management, and token blacklist
- **JWT Authentication** - Secure token-based authentication with refresh tokens
- **WebSocket** - Real-time event streaming
- **Alembic** - Database migrations
- **Docker** - Containerized deployment
- **Type Safety** - Full type hints with Pydantic validation
- **Testing** - Comprehensive test suite with pytest

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- Poetry (for local development)

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**

```bash
cd backend
```

2. **Copy environment file**

```bash
cp .env.example .env
```

3. **Update environment variables**

Edit `.env` and set:
- `SECRET_KEY` - Generate a secure random key
- Database credentials (if not using defaults)
- LLM API keys (optional)

4. **Start services**

```bash
docker-compose up -d
```

5. **Access the API**

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- MinIO Console: http://localhost:9001

### Option 2: Local Development

1. **Install Poetry**

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. **Install dependencies**

```bash
poetry install
```

3. **Set up environment**

```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Start PostgreSQL and Redis**

Using Docker:
```bash
docker-compose up -d postgres redis
```

Or install locally.

5. **Run database migrations**

```bash
poetry run alembic upgrade head
```

6. **Start the server**

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. **Access the API**

- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py       # Authentication endpoints
│   │   │   │   ├── agents.py     # Agent CRUD endpoints
│   │   │   │   ├── health.py     # Health check endpoints
│   │   │   │   └── websocket.py  # WebSocket endpoint
│   │   │   └── router.py         # API router configuration
│   │   └── deps.py               # API dependencies
│   ├── core/
│   │   ├── settings.py           # Application settings
│   │   ├── security.py           # Security utilities
│   │   └── logging_config.py     # Logging configuration
│   ├── db/
│   │   └── session.py            # Database session management
│   ├── models/
│   │   ├── base.py               # Base model with common fields
│   │   ├── user.py               # User model
│   │   ├── agent.py              # Agent model
│   │   ├── agent_type.py         # Agent type model
│   │   ├── workflow.py           # Workflow model
│   │   ├── task.py               # Task model
│   │   ├── workspace.py          # Workspace model
│   │   ├── knowledge_entity.py   # Knowledge entity model
│   │   └── validation_result.py  # Validation result model
│   ├── schemas/
│   │   ├── token.py              # Token schemas
│   │   ├── user.py               # User schemas
│   │   ├── agent.py              # Agent schemas
│   │   └── auth.py               # Authentication schemas
│   ├── services/                 # Business logic services
│   ├── utils/                    # Utility functions
│   ├── websocket/
│   │   ├── manager.py            # WebSocket connection manager
│   │   └── events.py             # Event system
│   └── main.py                   # FastAPI application entry point
├── alembic/
│   └── versions/                 # Database migrations
├── tests/
│   ├── conftest.py               # Pytest fixtures
│   ├── test_auth.py              # Authentication tests
│   ├── test_agents.py            # Agent tests
│   └── test_security.py          # Security tests
├── .env.example                  # Environment variables template
├── docker-compose.yml            # Docker Compose configuration
├── Dockerfile                    # Docker build configuration
├── pyproject.toml                # Poetry dependencies
└── README.md                     # This file
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | Login and get tokens |
| POST | `/api/v1/auth/logout` | Logout and blacklist token |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Get current user info |
| POST | `/api/v1/auth/register` | Register new user |

### Agents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/agents` | List user's agents |
| GET | `/api/v1/agents/{id}` | Get agent by ID |
| POST | `/api/v1/agents` | Create new agent |
| PATCH | `/api/v1/agents/{id}` | Update agent |
| DELETE | `/api/v1/agents/{id}` | Delete agent |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Basic health check |
| GET | `/api/v1/ready` | Readiness check |
| GET | `/api/v1/live` | Liveness check |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `/api/v1/ws` | Real-time event streaming |

## Environment Variables

### Application

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | Document Analyzer Operator | Application name |
| `APP_DEBUG` | false | Debug mode |
| `APP_ENVIRONMENT` | development | Environment (development/production) |
| `SECRET_KEY` | - | JWT secret key (required) |

### Database

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | postgres | Database user |
| `POSTGRES_PASSWORD` | postgres | Database password |
| `POSTGRES_HOST` | localhost | Database host |
| `POSTGRES_PORT` | 5432 | Database port |
| `POSTGRES_DB` | document_analyzer | Database name |

### Redis

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_HOST` | localhost | Redis host |
| `REDIS_PORT` | 6379 | Redis port |

## Testing

### Run all tests

```bash
poetry run pytest
```

### Run with coverage

```bash
poetry run pytest --cov=app
```

### Run specific test file

```bash
poetry run pytest tests/test_auth.py -v
```

## Database Migrations

### Create a new migration

```bash
poetry run alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations

```bash
poetry run alembic upgrade head
```

### Rollback migrations

```bash
poetry run alembic downgrade -1
```

### View migration history

```bash
poetry run alembic history
```

## Development

### Code formatting

```bash
poetry run ruff format .
```

### Linting

```bash
poetry run ruff check .
```

### Type checking

```bash
poetry run mypy app
```

## Security Considerations

1. **Change the `SECRET_KEY`** in production - Generate a secure random key
2. **Use HTTPS** in production - Configure SSL/TLS
3. **Set `APP_DEBUG=false`** in production
4. **Use strong passwords** for database and Redis
5. **Rotate API keys** regularly
6. **Enable rate limiting** for production use
7. **Review CORS settings** for your domain

## Troubleshooting

### Database connection errors

- Verify PostgreSQL is running: `docker-compose ps`
- Check credentials in `.env`
- Ensure network connectivity

### Redis connection errors

- Verify Redis is running: `docker-compose ps`
- Check Redis URL in `.env`

### Import errors

- Ensure dependencies are installed: `poetry install`
- Activate virtual environment: `poetry shell`

## License

MIT
