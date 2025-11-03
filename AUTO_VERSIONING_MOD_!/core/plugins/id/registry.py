"""
registry.py
===========

Plugin responsible for building the ID registry from the stored
ID Cards. It parses all YAML files under ``ids/cards`` and
constructs a bidirectional lookup mapping. The resulting
registry is written to ``ids/registry.yaml``. This skeleton only
assembles the registry in memory and writes a placeholder YAML
file.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml

from ..id.base import IDPlugin
from ..models.id_card import IDCard
from ..models.registry import Registry


class RegistryBuildPlugin(IDPlugin):
    """Build the registry from ID Card YAML files."""

    def __init__(self, cards_dir: Path | None = None, registry_path: Path | None = None) -> None:
        base = Path("AUTO_VERSIONING_MOD")
        self.cards_dir = cards_dir or base / "ids/cards"
        self.registry_path = registry_path or base / "ids/registry.yaml"

    def run(self) -> Registry:
        """Generate a registry from existing ID cards and persist it."""
        reg = Registry()
        if not self.cards_dir.exists():
            return reg
        for path in self.cards_dir.glob("*.yaml"):
            data = yaml.safe_load(path.read_text())
            card = IDCard.from_dict(data)
            reg.add_entry(card.ulid, card.doc_key, aliases=card.aliases)
        # Write registry to YAML
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        yaml.safe_dump({k: {"ulid": k, "doc_key": v, "aliases": reg.aliases.get(k, [])}
                        for k, v in reg.by_ulid.items()},
                       self.registry_path.open("w", encoding="utf-8"))
        return reg
