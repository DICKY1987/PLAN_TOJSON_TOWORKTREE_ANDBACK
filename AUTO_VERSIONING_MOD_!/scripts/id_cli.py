"""
id_cli.py
=========

Command‑line interface for the ID module. Provides a unified entry
point to invoke various ID plugins from the shell. For example:

    python id_cli.py mint --doc-key OC_CORE --semver 1.0.0 --owner Platform.Engineering --contract-type policy

Currently this CLI implements only the ``mint`` subcommand. Other
subcommands can be added following the same pattern. See
core/plugins/id for more details on each plugin's behaviour.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from ..core.plugins.id.mint import MintPlugin
from ..core.plugins.id.validate import ValidatePlugin


def main() -> None:
    parser = argparse.ArgumentParser(description="ID module command‑line interface")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # mint command
    mint_parser = subparsers.add_parser("mint", help="Create a new ID card")
    mint_parser.add_argument("--doc-key", required=True, help="Human identifier for the document")
    mint_parser.add_argument("--semver", required=True, help="Initial semantic version")
    mint_parser.add_argument("--owner", required=True, help="Owner of the document")
    mint_parser.add_argument("--contract-type", required=True, help="Contract type")

    args = parser.parse_args()

    if args.command == "mint":
        plugin = MintPlugin()
        card = plugin.run(doc_key=args.doc_key, semver=args.semver, owner=args.owner, contract_type=args.contract_type)
        validator = ValidatePlugin()
        validator.run(card)
        print(f"Minted ID card: {card.ulid} (doc_key: {card.doc_key})")


if __name__ == "__main__":
    main()
