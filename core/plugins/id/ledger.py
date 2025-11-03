"""
ledger.py
=========

Plugin responsible for appending events to the ledger. The ledger
is stored as a JSON Lines file at ``.ledger/ids.jsonl`` and should
never be rewritten. Each invocation appends exactly one event.
This skeleton writes to an in-memory string when run locally; it
should be extended to write to disk in production.
"""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict

from ..id.base import IDPlugin
from ..models.ledger_event import LedgerEvent


class LedgerPlugin(IDPlugin):
    """Append events to the ledger file."""

    def __init__(self, ledger_path: Path | None = None) -> None:
        self.ledger_path = ledger_path or Path("AUTO_VERSIONING_MOD/.ledger/ids.jsonl")

    def run(self, event: LedgerEvent) -> None:
        """Append a ledger event to the JSONL file."""
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event.to_dict()) + "\n")
