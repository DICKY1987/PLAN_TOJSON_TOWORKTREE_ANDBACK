"""
rekey.py
========

Plugin implementing the REKEY operation. It updates the human
identifier (doc_key) for a document by modifying its ID Card and
adding the previous doc_key to the aliases list. A REKEY event is
also appended to the ledger. This skeleton updates the in-memory
representation; persistence should be handled in future work.
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


class RekeyPlugin(IDPlugin):
    """Update the doc_key for an existing ID Card and log the change."""

    def __init__(self, cards_dir: Path | None = None, ledger_path: Path | None = None) -> None:
        base = Path("AUTO_VERSIONING_MOD")
        self.cards_dir = cards_dir or base / "ids/cards"
        self.ledger = LedgerPlugin(ledger_path)

    def run(self, ulid: str, new_key: str) -> None:
        """Perform a REKEY operation on the ID specified by ULID."""
        card_path = self.cards_dir / f"{ulid}.yaml"
        if not card_path.exists():
            raise FileNotFoundError(f"ID Card {ulid} does not exist")
        data = yaml.safe_load(card_path.read_text())
        card = IDCard.from_dict(data)
        # update card
        aliases = card.aliases + [card.doc_key]
        updated_card = IDCard(
            doc_key=new_key,
            ulid=card.ulid,
            semver=card.semver,
            status=card.status,
            effective_date=card.effective_date,
            owner=card.owner,
            contract_type=card.contract_type,
            card_version=card.card_version + 1,
            aliases=aliases,
            supersedes_version=card.supersedes_version,
            merged_into=card.merged_into,
            absorbs=card.absorbs,
            mfid=card.mfid,
        )
        yaml.safe_dump(updated_card.to_dict(), card_path.open("w", encoding="utf-8"))
        # append ledger event
        event = LedgerEvent(
            event_type="REKEY",
            timestamp=datetime.utcnow().isoformat() + "Z",
            ulid=card.ulid,
            doc_key=new_key,
            data={"old_key": card.doc_key, "new_key": new_key},
        )
        self.ledger.run(event)
