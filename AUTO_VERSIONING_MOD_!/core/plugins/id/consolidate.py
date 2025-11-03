"""
consolidate.py
=============

Plugin implementing the CONSOLIDATE operation. It merges multiple
source IDs into a target ID. The source cards are updated with a
``merged_into`` field and the target card records which IDs it
absorbs. A CONSOLIDATE event is appended to the ledger. This
skeleton performs only basic in-place updates.
"""
from __future__ import annotations

from typing import Iterable
from datetime import datetime
import yaml
from pathlib import Path

from ..id.base import IDPlugin
from ..models.id_card import IDCard
from ..models.ledger_event import LedgerEvent
from .ledger import LedgerPlugin


class ConsolidatePlugin(IDPlugin):
    """Merge multiple documents into a single target."""

    def __init__(self, cards_dir: Path | None = None, ledger_path: Path | None = None) -> None:
        base = Path("AUTO_VERSIONING_MOD")
        self.cards_dir = cards_dir or base / "ids/cards"
        self.ledger = LedgerPlugin(ledger_path)

    def run(self, target_ulid: str, source_ulids: Iterable[str]) -> None:
        target_path = self.cards_dir / f"{target_ulid}.yaml"
        if not target_path.exists():
            raise FileNotFoundError(f"Target ID Card {target_ulid} does not exist")
        # Load target card
        target_data = yaml.safe_load(target_path.read_text())
        target_card = IDCard.from_dict(target_data)
        # Update target absorbs
        absorbs = list(target_card.absorbs)
        for src_ulid in source_ulids:
            if src_ulid == target_ulid:
                continue
            absorbs.append(src_ulid)
        target_card = IDCard(
            doc_key=target_card.doc_key,
            ulid=target_card.ulid,
            semver=target_card.semver,
            status=target_card.status,
            effective_date=target_card.effective_date,
            owner=target_card.owner,
            contract_type=target_card.contract_type,
            card_version=target_card.card_version + 1,
            aliases=target_card.aliases,
            supersedes_version=target_card.supersedes_version,
            merged_into=target_card.merged_into,
            absorbs=absorbs,
            mfid=target_card.mfid,
        )
        yaml.safe_dump(target_card.to_dict(), target_path.open("w", encoding="utf-8"))
        # Update source cards
        for src_ulid in source_ulids:
            if src_ulid == target_ulid:
                continue
            src_path = self.cards_dir / f"{src_ulid}.yaml"
            if not src_path.exists():
                continue
            data = yaml.safe_load(src_path.read_text())
            card = IDCard.from_dict(data)
            updated_card = IDCard(
                doc_key=card.doc_key,
                ulid=card.ulid,
                semver=card.semver,
                status=card.status,
                effective_date=card.effective_date,
                owner=card.owner,
                contract_type=card.contract_type,
                card_version=card.card_version + 1,
                aliases=card.aliases,
                supersedes_version=card.supersedes_version,
                merged_into=target_ulid,
                absorbs=card.absorbs,
                mfid=card.mfid,
            )
            yaml.safe_dump(updated_card.to_dict(), src_path.open("w", encoding="utf-8"))
        # Append ledger event
        event = LedgerEvent(
            event_type="CONSOLIDATE",
            timestamp=datetime.utcnow().isoformat() + "Z",
            ulid=target_ulid,
            doc_key=target_card.doc_key,
            data={"sources": list(source_ulids)},
        )
        self.ledger.run(event)
