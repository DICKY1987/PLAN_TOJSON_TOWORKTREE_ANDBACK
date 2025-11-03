# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the **AUTO_VERSIONING_MOD** project containing documentation and infrastructure for two integrated systems:

1. **ACMS (Autonomous Code Modification System)**: A headless AI-driven pipeline for autonomous code modifications
2. **R_PIPELINE**: A plugin-based repository maintenance system

The repository is primarily documentation with some automation scripts, governed by strict versioning and compliance requirements.

## Core Architecture

### ACMS 5-Layer Design
```
Layer 5: Output Management (PR creation, git worktree sync)
Layer 4: Deterministic Validation (code gates, auto-fix, security scanning)
Layer 3: Agent Execution (Claude Code CLI, Aider, Context Broker)
Layer 2: Orchestration (state machine, task scheduler, ULID generation)
Layer 1: Input Ingestion (structured YAML/JSON requests)
```

### Key Technologies
- **Python 3.11+**: Primary language for orchestration
- **PowerShell 7+**: Windows-specific tooling
- **OpenTelemetry + Jaeger**: Distributed tracing
- **MkDocs**: Documentation generation
- **Pulumi**: Infrastructure as Code
- **Git Worktrees**: Isolation for concurrent execution

## Critical Governance Rules

### Document Versioning (VERSIONING_OPERATING_CONTRACT.md)

**Every document in `/docs` and `/plans` MUST include YAML front matter:**

```yaml
---
doc_key: UNIQUE_IDENTIFIER    # Never changes, stable
semver: 1.0.0                 # MAJOR.MINOR.PATCH
status: active                # active | deprecated | frozen
effective_date: 2025-11-02    # YYYY-MM-DD
owner: Platform.Engineering   # CODEOWNERS team
contract_type: policy         # policy | intent | execution_contract
---
```

**Semantic Versioning Rules:**
- **MAJOR**: Breaking changes (e.g., removing requirements, incompatible changes)
- **MINOR**: New features, backward-compatible additions
- **PATCH**: Editorial fixes, clarifications, typos

**Special: execution_contract documents:**
- ONLY allow MAJOR (scope rebaseline) or PATCH (editorial)
- MINOR bumps are explicitly blocked (no silent scope creep)
- Require `contract-rebaseline` PR label for MAJOR changes

### When Modifying Documents

1. Update the `semver` field according to change type
2. Update `effective_date` if meaning changed
3. Set `supersedes_version` to previous semver
4. Update the "Change Log (recent)" section (keep last 3 entries)
5. Use Conventional Commit format in commit messages:
   - `fix:` → PATCH bump
   - `feat:` → MINOR bump
   - `feat!:` or `BREAKING CHANGE:` → MAJOR bump

**Automated Enforcement:**
- `.github/workflows/docs-guard.yml` validates all changes on PR
- `.github/workflows/doc-tags.yml` creates git tags after merge: `docs-{doc_key}-{semver}`

## Development Commands

### Documentation Generation
```bash
# Build documentation site
python generate_docs.py --config-file mkdocs.yml --site-dir site

# Build with strict mode (fails on warnings)
python generate_docs.py --strict

# Preview locally
mkdocs serve
# View at http://127.0.0.1:8000
```

### Plugin Development (R_PIPELINE)
```powershell
# Generate plugin scaffold from spec
.\core\Generate-PluginScaffold.ps1 -SpecFile "plugins\{name}\plugin.spec.json"

# Validate plugin compliance
.\core\Validate-Plugin.ps1 -PluginPath "plugins\{name}"
```

### Testing
```bash
# Run all tests with coverage (must be >= 80%)
pytest tests/ -v --cov=. --cov-report=term

# Run infrastructure tests (Test-Driven Infrastructure)
pytest infrastructure/tests/ --hosts=localhost

# Run BDD tests
behave features/
```

### Linting & Formatting
```bash
# Python
black .                          # Format code
ruff check . --fix              # Lint and auto-fix
mypy core/ plugins/             # Type checking
pylint core/ plugins/           # Code analysis

# PowerShell
Invoke-ScriptAnalyzer -Path . -Recurse
```

### Observability
```bash
# Start Jaeger for trace visualization
docker run -d --name jaeger \
  -p 16686:16686 -p 4318:4318 \
  jaegertracing/all-in-one:latest

# View traces at http://localhost:16686
# All operations MUST include a trace_id (ULID format)
```

## Core Principles (Apply to All Work)

### 1. Determinism
**Same input + same environment → always same output**
- No hidden state, no ambient configuration
- All dependencies explicitly declared
- Reproducible operations

### 2. Observability
**Every operation tagged with Trace ID**
- Use ULID format for all identifiers (chronologically sortable)
- OpenTelemetry tracing with span attributes
- JSONL append-only ledger for audit trail
- All logs must include trace_id

### 3. Isolation
**Concurrent execution without interference**
- Git worktrees for isolated workspaces
- Nox sessions for virtual environments
- Independent validation per worktree

### 4. Safety
**Multiple layers of protection**
- SafePatch fences (restrict AI to designated sections)
- Quality gates (lint, test, security)
- Max 3 retry attempts
- Rollback capability via git checkpoints

### 5. Test-Driven Development
**Red → Green → Refactor cycle**
- Write failing test first
- Implement minimum code to pass
- Refactor while keeping tests green
- Target: 80% minimum code coverage
- Test-Driven Infrastructure (TDI) for IaC

## File Structure

```
AUTO_VERSIONING_MOD/
├── ACMS_EXECUTIVE_SUMMARY.md           # Architecture overview
├── ACMS_BUILD_EXECUTION_CONTRACT.yaml  # Build manifest with templates
├── VERSIONING_OPERATING_CONTRACT.md    # Versioning governance (CRITICAL)
├── OPERATING_CONTRACT.md               # Documentation governance
├── R_PIPELINE_IMPLEMENTATION_GUIDE.md  # Development methodology
├── generate_docs.py                    # MkDocs build automation
├── mkdocs.yml                          # MkDocs configuration
├── docs/                               # Documentation source
│   ├── index.md                        # Portal landing page
│   └── OPERATING_CONTRACT.md           # Docs governance
└── .github/workflows/
    ├── docs-guard.yml                  # Pre-merge validation
    └── doc-tags.yml                    # Post-merge tagging
```

## Common Tasks

### Creating a New Document

1. **Start with proper front matter:**
```yaml
---
doc_key: NEW_DOC_KEY
semver: 1.0.0
status: active
effective_date: 2025-11-02
owner: Platform.Engineering
contract_type: policy  # or intent or execution_contract
---
```

2. **Write content using Markdown**

3. **Add to mkdocs.yml nav** if it should appear in docs site

4. **Create PR with conventional commit:**
```bash
git checkout -b docs/new-document
git add new-document.md
git commit -m "feat: Add new architecture document"
git push origin docs/new-document
```

### Updating an Existing Document

1. **Read the document to get current semver**

2. **Determine bump type:**
   - Typo fix → PATCH (1.2.3 → 1.2.4)
   - New section/requirement → MINOR (1.2.4 → 1.3.0)
   - Breaking change → MAJOR (1.3.0 → 2.0.0)

3. **Update front matter:**
```yaml
semver: 1.3.0                    # Bumped from 1.2.4
effective_date: 2025-11-02       # Updated
supersedes_version: 1.2.4        # Previous version
```

4. **Update change log at bottom** (keep last 3 entries)

5. **Commit with matching convention:**
```bash
# MINOR change example
git commit -m "feat: Add validation requirements to contract"
```

### Generating Documentation

```bash
# Local build and preview
python generate_docs.py
# Creates site/ directory

# Build with strict validation (recommended for PR)
python generate_docs.py --strict

# Manual MkDocs commands
mkdocs build          # Build to site/
mkdocs serve          # Preview at localhost:8000
```

### Working with Trace IDs

All operations must propagate a trace_id. Use ULID format:

```python
# Python example
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def process_file(input_data: dict) -> dict:
    trace_id = input_data.get("trace_id", "unknown")

    with tracer.start_as_current_span(
        "process_file",
        attributes={"trace.id": trace_id}
    ) as span:
        # Your logic here
        result = {"status": "success", "trace_id": trace_id}
        return result
```

## Important Notes

### What NOT to Do

- ❌ Skip writing tests before implementation
- ❌ Modify documents without bumping semver
- ❌ Create MINOR bumps on execution_contract documents
- ❌ Forget to include trace_id in plugin input/output schemas
- ❌ Deploy without running validation scripts
- ❌ Commit without updating Change Log
- ❌ Use ambient configuration (everything must be explicit)

### What to ALWAYS Do

- ✅ Write tests first (TDD)
- ✅ Include trace_id in all operations
- ✅ Validate documents before committing: `python generate_docs.py --strict`
- ✅ Run quality gates: linting, tests, coverage (≥80%)
- ✅ Update effective_date for semantic changes
- ✅ Follow Conventional Commits format
- ✅ Check CI passes before requesting review
- ✅ Document with YAML front matter

## Build Execution Contract Templates

The `ACMS_BUILD_EXECUTION_CONTRACT.yaml` defines standard templates for headers:

**Python Header:**
```python
"""
${title}
Version: ${semver}
Date: ${date}
Owner: ${owner}
"""
```

**PowerShell Header:**
```powershell
<#
.SYNOPSIS
    ${synopsis}
.VERSION
    ${semver}
.DATE
    ${date}
#>
```

**Markdown Front Matter:**
```yaml
---
doc_key: ${doc_key}
semver: ${semver}
status: active
effective_date: ${date}
owner: ${owner}
---
```

## CI/CD Integration

### Automated Checks on PR

1. **docs-guard.yml** validates:
   - All required front matter fields present
   - semver increases monotonically
   - PR title matches version bump type
   - execution_contract only has MAJOR or PATCH
   - supersedes_version matches previous version

2. **Tests must pass:**
   - Unit tests (pytest)
   - Infrastructure tests (pytest-testinfra)
   - Coverage ≥ 80%

3. **Linting must be clean:**
   - black, ruff, mypy, pylint (Python)
   - PSScriptAnalyzer (PowerShell)

### Post-Merge Actions

1. **doc-tags.yml** automatically creates git tags:
   - Format: `docs-{doc_key}-{semver}`
   - Example: `docs-VERSIONING_OC-1.0.0`

2. **Documentation deployed** (if configured)

## Quick Reference

| Task | Command |
|------|---------|
| Build docs | `python generate_docs.py` |
| Serve docs locally | `mkdocs serve` |
| Run tests | `pytest tests/ -v --cov` |
| Format Python | `black .` |
| Lint Python | `ruff check . --fix` |
| Type check | `mypy core/ plugins/` |
| Start Jaeger | `docker run -d -p 16686:16686 -p 4318:4318 jaegertracing/all-in-one` |
| Validate plugin | `.\core\Validate-Plugin.ps1 -PluginPath plugins\{name}` |

## Getting Help

- **Versioning questions**: Read `VERSIONING_OPERATING_CONTRACT.md`
- **Architecture questions**: Read `ACMS_EXECUTIVE_SUMMARY.md`
- **Development workflow**: Read `R_PIPELINE_IMPLEMENTATION_GUIDE.md`
- **Document governance**: Read `OPERATING_CONTRACT.md`

## Performance Targets

- **Planning Phase**: 30-60 seconds (Claude Code CLI)
- **Execution Phase**: 2-5 minutes per worktree (Aider)
- **Validation Phase**: 1-3 minutes (linting + testing)
- **Total Pipeline**: 5-15 minutes per run

## Security Controls

- ✅ Input validation on all external data
- ✅ Secret scanning (gitleaks)
- ✅ Dependency auditing (pip-audit, bandit)
- ✅ Least privilege (scoped API tokens)
- ✅ Audit logging (immutable JSONL)
- ✅ Code review (optional human gate)
