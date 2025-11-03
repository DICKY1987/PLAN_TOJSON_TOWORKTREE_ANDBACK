
# Simultaneous Execution with Git Worktrees — Technical Specification

## 1. Overview
This document defines the architecture and operational flow that enables **simultaneous, conflict-free execution** of multiple workstreams using **Git worktrees** in the CLI Multi-Rapid orchestration system.

Git worktrees allow several working directories from a single Git repository to exist at once—each on its own branch but sharing the same `.git` history.  
In this architecture, each **parallel workstream** executes inside its own isolated worktree, providing filesystem-level isolation for concurrent AI agents, pipelines, or human developers.

---

## 2. Workstream Architecture

### 2.1 Workstream Creation
Workstreams are instantiated by the orchestration layer through multiple mechanisms:

| Creation Path | Location | Function |
|----------------|-----------|-----------|
| **Database-Level** | `src/cli_multi_rapid/coordination/registry.py` | Creates persistent `Workstream` records with `status="pending"`, metadata, correlation IDs, and timestamps. |
| **Configuration-Level** | `workflows/phase_definitions/multi_stream.yaml` | Defines logical streams (A–E) with ownership, scope, phases, dependencies, and AI tool assignment. |

Example configuration:

```yaml
streams:
  A:
    owner: Claude
    scope: .github/**
    phases: [foundation, infra]
  B:
    owner: Codex
    scope: contracts/schemas/**
    phases: [schema, validation]
```

---

## 3. Workstream Execution

### 3.1 Orchestrator
**File:** `workflows/orchestrator.py`

The orchestrator controls lifecycle operations:

```python
execute_stream(stream_id: str, dry_run: bool) -> Dict
execute_phase(phase_id: str, dry_run: bool) -> PhaseResult
list_streams() -> List[Dict]
```

Execution flow:
1. Load configuration (`multi_stream.yaml`)
2. Retrieve phases and dependencies
3. Execute phases sequentially **within** each stream
4. Execute multiple streams **in parallel** across worktrees

### 3.2 Priority Queue & Dispatcher
**Files:**  
- `src/cli_multi_rapid/coordination/queue.py`  
- `src/cli_multi_rapid/coordination/dispatcher.py`

Mechanism:
- `PriorityQueue.put(workstream_id, task_name, payload, priority)`
- `dispatch(queue, func, workers=4) → List[Any]`

Parallelism is achieved using `ThreadPoolExecutor`:
- High-priority tasks (hotfixes, patches)
- Medium-priority (features)
- Low-priority (docs/tests)

### 3.3 Merge Queue
**File:** `src/cli_multi_rapid/coordination/merge_queue.py`

Handles branch integration:
- Queued status: `QUEUED → CHECKING → MERGING → MERGED`
- Pre-merge checks: lint, tests, security scan
- Conflict detection & wait-time estimation

---

## 4. Git Worktree Integration

### 4.1 Concept
A **Git worktree** creates an additional working directory attached to the same Git repository:

```bash
git worktree add <path> <branch>
```

Each worktree maintains its own checked-out branch while sharing `.git` history with the root repo.

| Benefit | Description |
|----------|--------------|
| **Isolation** | Each stream modifies files in its own directory tree. |
| **Parallelism** | Multiple branches checked out simultaneously. |
| **Safety** | No race conditions or accidental overwrites. |
| **Rollback** | Failed workstreams can be discarded cleanly. |

### 4.2 Implementation Example

**Without worktrees:**
```bash
git checkout main
git checkout feature-branch
# switching branches replaces file contents
```

**With worktrees:**
```bash
git worktree add ../feature-work feature-branch
# two independent directories sharing the same history
```

---

## 5. Worktree Lifecycle in CLI Multi-Rapid

| Stage | Operation | Command / Function |
|--------|------------|--------------------|
| **Create** | When stream starts, orchestrator provisions isolated workspace | `git worktree add /tmp/stream-a lane/stream-a-foundation` |
| **Execute** | Tool (Aider, Codex, etc.) runs in isolated directory | `cd /tmp/stream-a` |
| **Commit & Push** | Code committed and pushed to origin | `git commit`, `git push origin lane/...` |
| **Merge** | Merge queue integrates branches after validation | `git merge lane/...` |
| **Cleanup** | Worktree removed post-merge | `git worktree remove /tmp/stream-a` |

Each worktree maps 1-to-1 with a **branch** and a **workstream**.

---

## 6. Parallel Execution Strategy

### 6.1 Execution Order
Defined in `multi_stream.yaml`:

```yaml
execution_order:
  - parallel: [stream-a, stream-b]
  - parallel: [stream-c, stream-d]
  - sequential: [stream-e]
  - sequential: [stream-complete]
```

### 6.2 Safety Mechanisms

| Mechanism | Description |
|------------|-------------|
| **Path Claims** | Each stream declares exclusive file scopes. |
| **Conflict Detection** | Scheduler blocks overlapping path claims. |
| **Git Worktree Isolation** | Each stream operates in a separate filesystem. |
| **Dependency Management** | Later phases await prerequisite completions. |

Example:
```python
# Stream A: .github/**, README.md
# Stream B: contracts/schemas/**
# → No conflict: run in parallel
```

---

## 7. Monitoring and Status Tracking

### 7.1 Real-Time Status
Commands:
```bash
python -m workflows.orchestrator status
python -m workflows.orchestrator list-streams
```
Output:
- Current/failed/completed phase counts  
- Owner AI and assigned tool per stream

### 7.2 Health Verification
```bash
python -m workflows.orchestrator health-check
```
Validates repository structure and integrity of all worktrees.

---

## 8. Example End-to-End Flow

1. **User Request** — submitted via Interface & Planning Tool (IPT).  
2. **IPT Analysis** — identifies non-conflicting workstreams.  
3. **Worktree Provisioning** — `git worktree add /tmp/ws-A lane/feature/stream-A`  
4. **Parallel Execution** — Dispatcher launches AI tools in isolated directories.  
5. **Result Persistence** — statuses, artifacts, and logs stored to DB.  
6. **Merge Coordination** — branches validated and merged through queue.  
7. **IPT Verification** — final quality and security checks.  
8. **Cleanup** — worktrees removed post-merge.

---

## 9. Advantages of Worktree-Based Execution

| Capability | Description |
|-------------|-------------|
| **True Concurrency** | Independent filesystem state per branch allows multi-threaded execution. |
| **Conflict-Free Development** | Each AI tool modifies distinct file scopes. |
| **Resilience** | Failures in one workstream don’t affect others. |
| **Rollback Simplicity** | Deleting the worktree discards failed changes. |
| **Performance** | Parallel execution yields 3–5× speed improvement. |
| **Traceability** | Database links every worktree and branch to correlation IDs. |

---

## 10. Practical Worktree Commands

| Operation | Command | Notes |
|------------|----------|------|
| **List Worktrees** | `git worktree list` | Shows all paths and associated branches |
| **Remove Worktree** | `git worktree remove <path>` | Deletes workspace |
| **Force Remove** | `git worktree remove --force <path>` | Bypasses lock issues |
| **Prune Stale Entries** | `git worktree prune` | Cleans orphaned records |

---

## 11. Integration with Multi-AI Orchestration

Each worktree maps to a **parallel AI agent** or CLI tool instance:

| Stream | AI Owner | Typical Scope |
|---------|-----------|---------------|
| A | Claude | Infrastructure & Docs |
| B | Codex | Schema & Validation |
| C | Claude | Orchestration & Policies |
| D | Codex | Services & Docker |
| E | Claude | Final Documentation |

---

## 12. Summary
Git worktrees are foundational to the CLI Multi-Rapid parallel workflow system.  
They provide **safe, deterministic concurrency** by giving each stream an isolated yet version-controlled workspace linked to the same `.git` history.

**Key Outcomes:**
- Full parallel execution across independent streams  
- Zero file conflicts through scoped path claims  
- Centralized orchestration and status tracking  
- Rapid iteration with atomic rollback and safe merges  
