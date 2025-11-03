"""
deprecate.py
===========

Plugin implementing the DEPRECATE operation. It marks an ID Card
as deprecated, records a deprecation date and reason, and logs an
event to the ledger. This skeleton updates the YAML file for the
card and appends the event.
"""
from __future__ import annotations

from typing import Any
from datetime import datetime
import yaml
from pathlib import Path

from ..id.base import IDPlugin
from ..models.id_card import IDCard
from ..models.ledger_event import LedgerEvent
from .ledger import LedgerPlugin


class DeprecatePlugin(IDPlugin):
    """Deprecate an existing document ID."""

    def __init__(self, cards_dir: Path | None = None, ledger_path: Path | None = None) -> None:
        base = Path("AUTO_VERSIONING_MOD")
        self.cards_dir = cards_dir or base / "ids/cards"
        self.ledger = LedgerPlugin(ledger_path)

    def run(self, ulid: str, reason: str) -> None:
        card_path = self.cards_dir / f"{ulid}.yaml"
        if not card_path.exists():
            raise FileNotFoundError(f"ID Card {ulid} does not exist")
        data = yaml.safe_load(card_path.read_text())
        card = IDCard.from_dict(data)
        updated_card = IDCard(
            doc_key=card.doc_key,
            ulid=card.ulid,
            semver=card.semver,
            status="deprecated",
            effective_date=card.effective_date,
            owner=card.owner,
            contract_type=card.contract_type,
            card_version=card.card_version + 1,
            aliases=card.aliases,
            supersedes_version=card.supersedes_version,
            merged_into=card.merged_into,
            absorbs=card.absorbs,
            mfid=card.mfid,
        )
        yaml.safe_dump(updated_card.to_dict(), card_path.open("w", encoding="utf-8"))
        event = LedgerEvent(
            event_type="DEPRECATE",
            timestamp=datetime.utcnow().isoformat() + "Z",
            ulid=card.ulid,
            doc_key=card.doc_key,
            data={"reason": reason},
        )
        self.ledger.run(event)
