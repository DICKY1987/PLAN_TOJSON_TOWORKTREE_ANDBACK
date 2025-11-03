"""
markdown.py
===========

Plugin to export the registry as a Markdown table. Useful for
embedding in documentation. The table lists ULIDs, doc_keys and
aliases.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ..registry import Registry
from ...id.base import IDPlugin


class MarkdownExportPlugin(IDPlugin):
    """Export registry to a Markdown file."""

    def run(self, registry: Registry, output_path: Path) -> None:
        lines = ["| ULID | doc_key | aliases |", "| --- | --- | --- |"]
        for ulid, doc_key in registry.by_ulid.items():
            aliases = ", ".join(registry.aliases.get(ulid, []))
            lines.append(f"| {ulid} | {doc_key} | {aliases} |")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(lines), encoding="utf-8")
