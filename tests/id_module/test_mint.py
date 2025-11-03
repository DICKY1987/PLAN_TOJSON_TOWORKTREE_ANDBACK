"""
Unit tests for the MintPlugin.

These tests exercise the ability of MintPlugin to generate new
ULIDs and construct IDCard instances. The ULID pattern is not
strictly enforced here but should produce a 26-character string.
"""
from AUTO_VERSIONING_MOD.core.plugins.id.mint import MintPlugin


def test_mint_returns_idcard() -> None:
    plugin = MintPlugin()
    card = plugin.run(doc_key="TEST_DOC", semver="1.0.0", owner="QA", contract_type="policy")
    assert card.doc_key == "TEST_DOC"
    assert len(card.ulid) == 26
    assert card.status == "active"
