"""
json.py
=======

Plugin to export the registry as a JSON file. The resulting
structure maps ULIDs to their doc_key and aliases. This format is
useful for machine consumption.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..registry import Registry
from ...id.base import IDPlugin


class JSONExportPlugin(IDPlugin):
    """Export registry to a JSON file."""

    def run(self, registry: Registry, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        json_obj = {
            ulid: {
                "doc_key": doc_key,
                "aliases": registry.aliases.get(ulid, [])
            }
            for ulid, doc_key in registry.by_ulid.items()
        }
        output_path.write_text(json.dumps(json_obj, indent=2), encoding="utf-8")
