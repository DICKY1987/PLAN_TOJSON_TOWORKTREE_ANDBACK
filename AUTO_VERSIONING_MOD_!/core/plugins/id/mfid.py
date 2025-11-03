"""
mfid.py
=======

Optional plugin to compute a content hash (MFID) using blake3. The
resulting hash can be used to prove the exact content version
represented by a document. When run, this plugin calculates the
blake3 hash of a file's normalized contents and updates the ID
Card and ledger accordingly. This skeleton just computes the hash.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
import blake3
from ..id.base import IDPlugin
from ..models.ledger_event import LedgerEvent
from .ledger import LedgerPlugin
from ..models.id_card import IDCard
import yaml
from datetime import datetime


class MFIDPlugin(IDPlugin):
    """Calculate and record a blake3 hash for a document."""

    def __init__(self, cards_dir: Path | None = None, ledger_path: Path | None = None) -> None:
        base = Path("AUTO_VERSIONING_MOD")
        self.cards_dir = cards_dir or base / "ids/cards"
        self.ledger = LedgerPlugin(ledger_path)

    def run(self, ulid: str, file_path: Path) -> str:
        """Compute the blake3 hash of a file and update its ID Card."""
        h = blake3.blake3()
        # Normalize: read bytes directly; call caller to normalise line endings if desired
        with open(file_path, "rb") as fh:
            h.update(fh.read())
        digest = h.hexdigest()
        card_path = self.cards_dir / f"{ulid}.yaml"
        if card_path.exists():
            data = yaml.safe_load(card_path.read_text())
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
                merged_into=card.merged_into,
                absorbs=card.absorbs,
                mfid=digest,
            )
            yaml.safe_dump(updated_card.to_dict(), card_path.open("w", encoding="utf-8"))
            event = LedgerEvent(
                event_type="MFID_UPDATE",
                timestamp=datetime.utcnow().isoformat() + "Z",
                ulid=ulid,
                doc_key=card.doc_key,
                data={"mfid": digest},
            )
            self.ledger.run(event)
        return digest
