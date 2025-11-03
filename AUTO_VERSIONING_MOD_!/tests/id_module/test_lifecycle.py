"""
Tests for lifecycle operation plugins (Rekey, Deprecate, Consolidate).
"""
from pathlib import Path
import yaml

from AUTO_VERSIONING_MOD.core.plugins.id.rekey import RekeyPlugin
from AUTO_VERSIONING_MOD.core.plugins.id.deprecate import DeprecatePlugin
from AUTO_VERSIONING_MOD.core.plugins.id.consolidate import ConsolidatePlugin
from AUTO_VERSIONING_MOD.core.models.id_card import IDCard


def create_card(path: Path, ulid: str, doc_key: str) -> None:
    card = IDCard(
        doc_key=doc_key,
        ulid=ulid,
        semver="1.0.0",
        status="active",
        effective_date="2025-01-01",
        owner="QA",
        contract_type="policy",
        card_version=1,
    )
    yaml.safe_dump(card.to_dict(), path.open("w"))


def test_rekey(tmp_path: Path) -> None:
    cards_dir = tmp_path / "cards"
    ledger_path = tmp_path / "ledger.jsonl"
    cards_dir.mkdir()
    ulid = "01HXXXXXXULIDXXREKEYXXXXX"
    create_card(cards_dir / f"{ulid}.yaml", ulid, "OLD")
    plugin = RekeyPlugin(cards_dir=cards_dir, ledger_path=ledger_path)
    plugin.run(ulid=ulid, new_key="NEW")
    data = yaml.safe_load((cards_dir / f"{ulid}.yaml").read_text())
    assert data["doc_key"] == "NEW"
    assert "OLD" in data["aliases"]


def test_deprecate(tmp_path: Path) -> None:
    cards_dir = tmp_path / "cards"
    ledger_path = tmp_path / "ledger.jsonl"
    cards_dir.mkdir()
    ulid = "01HXXXXXXULIDXXDEPXXXXXX"
    create_card(cards_dir / f"{ulid}.yaml", ulid, "DOC")
    plugin = DeprecatePlugin(cards_dir=cards_dir, ledger_path=ledger_path)
    plugin.run(ulid=ulid, reason="obsolete")
    data = yaml.safe_load((cards_dir / f"{ulid}.yaml").read_text())
    assert data["status"] == "deprecated"


def test_consolidate(tmp_path: Path) -> None:
    cards_dir = tmp_path / "cards"
    ledger_path = tmp_path / "ledger.jsonl"
    cards_dir.mkdir()
    target = "01HXXXXXXULIDXXTARGETXXX"
    src1 = "01HXXXXXXULIDXXSRC1XXXXX"
    src2 = "01HXXXXXXULIDXXSRC2XXXXX"
    create_card(cards_dir / f"{target}.yaml", target, "TARGET")
    create_card(cards_dir / f"{src1}.yaml", src1, "SRC1")
    create_card(cards_dir / f"{src2}.yaml", src2, "SRC2")
    plugin = ConsolidatePlugin(cards_dir=cards_dir, ledger_path=ledger_path)
    plugin.run(target_ulid=target, source_ulids=[src1, src2])
    # Ensure source cards now reference target
    data1 = yaml.safe_load((cards_dir / f"{src1}.yaml").read_text())
    data2 = yaml.safe_load((cards_dir / f"{src2}.yaml").read_text())
    assert data1["merged_into"] == target
    assert data2["merged_into"] == target
    # Target absorbs sources
    target_data = yaml.safe_load((cards_dir / f"{target}.yaml").read_text())
    assert src1 in target_data["absorbs"]
    assert src2 in target_data["absorbs"]
