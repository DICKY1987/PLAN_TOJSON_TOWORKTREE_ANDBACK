from __future__ import annotations
import os
import pathlib
import shutil
import tempfile
from typing import Dict, Any, Sequence

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .contracts import Plugin, Plan
from .validation import deterministic_hash


_tracer_provider = TracerProvider(resource=Resource.create({"service.name": "plan-runner"}))
_otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
if _otel_endpoint:
    _sp = BatchSpanProcessor(OTLPSpanExporter(endpoint=_otel_endpoint, insecure=True))
    _tracer_provider.add_span_processor(_sp)
trace.set_tracer_provider(_tracer_provider)
tracer = trace.get_tracer(__name__)


class PlanError(Exception):
    ...


class ValidationError(Exception):
    ...


class ExecutionError(Exception):
    ...


def run(plugins: Sequence[Plugin], repo_root: str, context: Dict[str, Any]) -> dict:
    with tracer.start_as_current_span("pipeline") as span:
        span.set_attribute("repo.root", repo_root)
        recommendations = []
        with tracer.start_as_current_span("analyze"):
            for p in plugins:
                rec = p.analyze(repo_root, dict(context))  # copy context for read-only safety
                recommendations.append({"plugin": p.name, "rec": rec.model_dump()})
        combined = _combine_plans([r["rec"]["proposed"] for r in recommendations])
        with tracer.start_as_current_span("validate"):
            _validate_plan(combined)
        with tracer.start_as_current_span("execute"):
            artifacts = _apply_plan(repo_root, Plan.model_validate(combined))
        result = {"recommendations": recommendations, "plan": combined, "artifacts": artifacts}
        span.set_attribute("plan.hash", deterministic_hash(combined))
        return result


def _combine_plans(plans: Sequence[dict]) -> dict:
    items = []
    for p in plans:
        items.extend(p.get("items", []))
    return {"version": "1.0", "items": items, "metadata": {"sources": len(plans)}}


def _validate_plan(plan: dict) -> None:
    if "items" not in plan:
        raise ValidationError("Plan missing items")
    # TODO: Optionally load and enforce schemas/plan.schema.json here


def _apply_plan(repo_root: str, plan: Plan) -> dict:
    tmpdir = tempfile.mkdtemp(prefix="worktree-")
    worktree = pathlib.Path(tmpdir) / "worktree"
    shutil.copytree(repo_root, worktree, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git"))
    created, updated, deleted = 0, 0, 0
    for it in plan.items:
        target = worktree / it.path
        if it.action == "create":
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(it.content or "", encoding="utf-8")
            created += 1
        elif it.action == "update":
            if not target.exists():
                raise ExecutionError(f"update target missing: {it.path}")
            target.write_text(it.content or "", encoding="utf-8")
            updated += 1
        elif it.action == "delete":
            if target.exists():
                target.unlink()
                deleted += 1
        else:
            raise ExecutionError(f"unknown action: {it.action}")
    return {"worktree": str(worktree), "created": created, "updated": updated, "deleted": deleted}