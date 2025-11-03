"""
Tests for the RegistryBuildPlugin.
"""
from pathlib import Path
import yaml

from AUTO_VERSIONING_MOD.core.plugins.id.registry import RegistryBuildPlugin
from AUTO_VERSIONING_MOD.core.models.registry import Registry


def test_registry_build(tmp_path: Path) -> None:
    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    # Create two ID card YAML files
    card1 = {
        "doc_key": "DOC1",
        "ulid": "01HXXXX1XXXXXXXXXXXXXXXXXXXX",
        "semver": "1.0.0",
        "status": "active",
        "effective_date": "2025-01-01",
        "owner": "QA",
        "contract_type": "policy",
        "card_version": 1,
    }
    card2 = {
        "doc_key": "DOC2",
        "ulid": "01HXXXX2XXXXXXXXXXXXXXXXXXXX",
        "semver": "1.0.0",
        "status": "active",
        "effective_date": "2025-01-01",
        "owner": "QA",
        "contract_type": "policy",
        "card_version": 1,
    }
    yaml.safe_dump(card1, (cards_dir / f"{card1['ulid']}.yaml").open("w"))
    yaml.safe_dump(card2, (cards_dir / f"{card2['ulid']}.yaml").open("w"))
    plugin = RegistryBuildPlugin(cards_dir=cards_dir, registry_path=tmp_path / "registry.yaml")
    registry = plugin.run()
    assert registry.lookup_ulid("DOC1") == card1["ulid"]
    assert registry.lookup_key(card2["ulid"]) == "DOC2"
