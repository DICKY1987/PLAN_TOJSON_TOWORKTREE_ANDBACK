"""
migrate_to_id_module.py
=======================

Script to migrate existing documents into the autonomous ID module. It scans
all files under the ``docs`` and ``plans`` directories, extracts
front matter, mints ULIDs for documents lacking them, creates ID Cards,
updates the front matter with the newly minted ULIDs and appends CREATE
events to the ledger.

This skeleton outlines the high‑level steps without implementing
file discovery or YAML front matter parsing. It can be extended
by workstream D during migration week.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import yaml

from ..core.plugins.id.mint import MintPlugin
from ..core.plugins.id.ledger import LedgerPlugin
from ..core.plugins.id.validate import ValidatePlugin


def migrate_directory(directory: Path) -> None:
    """Placeholder for migrating all documents in a directory."""
    if not directory.exists():
        return
    for file in directory.glob("*.md"):
        # TODO: parse front matter; skip if ULID already present.
        doc_key = file.stem.upper()
        card = MintPlugin().run(doc_key=doc_key, semver="1.0.0", owner="Unknown", contract_type="policy")
        ValidatePlugin().run(card)
        # Persist ID Card YAML
        cards_dir = Path("AUTO_VERSIONING_MOD/ids/cards")
        cards_dir.mkdir(parents=True, exist_ok=True)
        yaml.safe_dump(card.to_dict(), (cards_dir / f"{card.ulid}.yaml").open("w", encoding="utf-8"))
        # Append event handled by MintPlugin in future
        print(f"Migrated {file.name} -> {card.ulid}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate existing docs into ID module")
    parser.add_argument("--docs-dir", type=Path, default=Path("docs"), help="Directory containing markdown docs")
    parser.add_argument("--plans-dir", type=Path, default=Path("plans"), help="Directory containing plans")
    args = parser.parse_args()
    migrate_directory(args.docs_dir)
    migrate_directory(args.plans_dir)


if __name__ == "__main__":
    main()
