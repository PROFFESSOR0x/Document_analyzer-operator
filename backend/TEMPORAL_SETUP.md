# Temporal.io Dependencies

Add these dependencies to your existing `pyproject.toml`:

```toml
[tool.poetry.dependencies]
# Add to existing dependencies
temporalio = "^1.4.0"
croniter = "^2.0.0"
```

## Installation

```bash
cd backend
poetry add temporalio croniter
```

## Temporal Server Setup

### Development (Docker)

```bash
# Start Temporal server
docker run --rm --name temporal \
  -p 7233:7233 \
  temporalio/auto-setup:latest

# Start Temporal Web UI (optional)
docker run --rm --name temporal-ui \
  -p 8080:8080 \
  --env TEMPORAL_ADDRESS=temporal:7233 \
  --link temporal \
  temporalio/ui:latest
```

Visit http://localhost:8080 for the Web UI.

### Production

Use Temporal Cloud or self-hosted cluster. See WORKFLOW_ENGINE.md for details.
