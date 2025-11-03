"""
mint.py
=======

Plugin responsible for minting new IDs. It generates a ULID using
the python-ulid library, constructs a deterministic document key
(doc_key) where needed, and creates a new ID Card on disk. It
also writes an entry to the ledger via the ledger plugin.

This implementation provides only a skeleton of the desired
behaviour. Real logic will need to ensure uniqueness of keys and
persist files to the correct directories.
"""
from __future__ import annotations

import datetime
from typing import Any, Dict

import ulid

from ..id.base import IDPlugin
from ..models.id_card import IDCard


class MintPlugin(IDPlugin):
    """Create new ID cards with unique ULIDs and doc_keys."""

    def run(self, doc_key: str, semver: str, owner: str, contract_type: str, **kwargs: Any) -> IDCard:
        """Generate a new ID card.

        Args:
            doc_key: Proposed human-readable identifier. Collisions should be handled
                by caller prior to invocation.
            semver: Initial semantic version for the document.
            owner: Owner of the document.
            contract_type: Contract type.

        Returns:
            A new :class:`IDCard` instance.
        """
        new_ulid = ulid.new().str
        effective_date = datetime.date.today().isoformat()
        card = IDCard(
            doc_key=doc_key,
            ulid=new_ulid,
            semver=semver,
            status="active",
            effective_date=effective_date,
            owner=owner,
            contract_type=contract_type,
            card_version=1,
        )
        # TODO: persist ID card to ids/cards and append CREATE event to ledger.
        return card
