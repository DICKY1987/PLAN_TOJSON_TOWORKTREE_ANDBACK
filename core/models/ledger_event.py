"""
ledger_event.py
===============

Data model for a ledger event in the autonomous Document
Versioning module. The ledger is an append‑only journal of
lifecycle operations on ID Cards. Each event contains a type,
timestamp, ULID reference, and arbitrary additional data.

While this model does not enforce validation on its own,
``id.ledger.append`` is responsible for ensuring events conform
to the schema in ``schemas/ledger_event.schema.json``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class LedgerEvent:
    """Representation of a ledger event."""

    event_type: str
    timestamp: str
    ulid: str
    doc_key: str
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the event to a dictionary suitable for JSONL."""
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "ulid": self.ulid,
            "doc_key": self.doc_key,
            "data": self.data,
        }
