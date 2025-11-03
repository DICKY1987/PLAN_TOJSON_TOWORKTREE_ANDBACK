"""
registry.py
===========

Simple in‑memory representation of a bidirectional ID registry.

The registry maps ULIDs to human‑readable doc_keys and vice versa.
It is generated from the authoritative ID cards by the
``id.registry.build`` plugin and persisted to YAML for fast lookup.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Registry:
    """Bidirectional registry for document identifiers."""

    by_ulid: Dict[str, str] = field(default_factory=dict)
    by_key: Dict[str, str] = field(default_factory=dict)
    aliases: Dict[str, List[str]] = field(default_factory=dict)

    def add_entry(self, ulid: str, doc_key: str, aliases: Optional[List[str]] = None) -> None:
        """Add an entry to the registry.

        Args:
            ulid: The machine identifier.
            doc_key: The human identifier.
            aliases: Optional list of alternative keys pointing to the same ULID.
        """
        self.by_ulid[ulid] = doc_key
        self.by_key[doc_key] = ulid
        if aliases:
            for alias in aliases:
                self.by_key[alias] = ulid
                self.aliases.setdefault(ulid, []).append(alias)

    def lookup_ulid(self, doc_key: str) -> Optional[str]:
        """Return the ULID for a given document key or alias."""
        return self.by_key.get(doc_key)

    def lookup_key(self, ulid: str) -> Optional[str]:
        """Return the primary document key for a given ULID."""
        return self.by_ulid.get(ulid)
