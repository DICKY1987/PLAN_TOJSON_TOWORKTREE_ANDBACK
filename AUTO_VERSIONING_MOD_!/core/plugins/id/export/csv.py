"""
csv.py
======

Plugin to export the registry as a CSV file. It accepts a
Registry instance and path to write the CSV. Each row contains a
ULID, its primary doc_key and any aliases.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from ..registry import Registry
from ...id.base import IDPlugin


class CSVExportPlugin(IDPlugin):
    """Export registry to a CSV file."""

    def run(self, registry: Registry, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ulid", "doc_key", "aliases"])
            for ulid, doc_key in registry.by_ulid.items():
                aliases = ",".join(registry.aliases.get(ulid, []))
                writer.writerow([ulid, doc_key, aliases])
