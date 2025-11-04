# PLAN_TOJSON_TOWORKTREE_ANDBACK

Deterministic planner that serializes plans to JSON, validates with schemas, and applies them to a git worktree with core-controlled execution. Plugins provide read-only recommendations; core validates and executes.

## Quickstart
```bash
python -m venv .venv && . .venv/bin/activate
pip install -e .[dev]
pre-commit install
pytest -q
```

## Architecture
- Core layers: ingestion → planning → validation → execution → reporting
- Trust model: plugins read-only; core decides/executes

## Observability
Set `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317` to export traces to Jaeger/OTLP.

## CI/CD
See `.github/workflows/ci.yml` for staged gates.