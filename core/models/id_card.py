"""
id_card.py
==========

Data model for an ID Card. ID Cards represent the authoritative
metadata for a document within the autonomous Document Versioning
module. Fields and defaults are informed by the JSON schema in
``schemas/id_card.schema.json``.

This module uses Python dataclasses to provide a simple,
immutable representation. Validation should be performed by
``id.validate`` plugin rather than inline within the model.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass(frozen=True)
class IDCard:
    """Immutable representation of an ID card."""

    doc_key: str
    ulid: str
    semver: str
    status: str
    effective_date: str
    owner: str
    contract_type: str
    card_version: int
    aliases: List[str] = field(default_factory=list)
    supersedes_version: Optional[str] = None
    merged_into: Optional[str] = None
    absorbs: List[str] = field(default_factory=list)
    mfid: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "IDCard":
        """Create an IDCard from a dictionary. Ignores unknown keys."""
        return cls(
            doc_key=data.get("doc_key"),
            ulid=data.get("ulid"),
            semver=data.get("semver"),
            status=data.get("status"),
            effective_date=data.get("effective_date"),
            owner=data.get("owner"),
            contract_type=data.get("contract_type"),
            card_version=int(data.get("card_version")),
            aliases=list(data.get("aliases", [])),
            supersedes_version=data.get("supersedes_version"),
            merged_into=data.get("merged_into"),
            absorbs=list(data.get("absorbs", [])),
            mfid=data.get("mfid"),
        )

    def to_dict(self) -> Dict[str, object]:
        """Serialise the ID card back to a dictionary suitable for YAML/JSON."""
        return {
            "doc_key": self.doc_key,
            "ulid": self.ulid,
            "semver": self.semver,
            "status": self.status,
            "effective_date": self.effective_date,
            "owner": self.owner,
            "contract_type": self.contract_type,
            "card_version": self.card_version,
            "aliases": list(self.aliases),
            "supersedes_version": self.supersedes_version,
            "merged_into": self.merged_into,
            "absorbs": list(self.absorbs),
            "mfid": self.mfid,
        }
