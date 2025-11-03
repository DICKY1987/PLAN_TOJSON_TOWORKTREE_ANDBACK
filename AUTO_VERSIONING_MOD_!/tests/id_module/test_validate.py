"""
Tests for the ValidatePlugin.
"""
import pytest
from AUTO_VERSIONING_MOD.core.plugins.id.validate import ValidatePlugin
from AUTO_VERSIONING_MOD.core.plugins.id.mint import MintPlugin


def test_validate_card_passes() -> None:
    card = MintPlugin().run(doc_key="VAL", semver="1.0.0", owner="QA", contract_type="policy")
    validator = ValidatePlugin()
    # Should not raise
    validator.run(card)

def test_validate_card_missing_field_raises() -> None:
    validator = ValidatePlugin()
    # Create a malformed card dict manually
    from AUTO_VERSIONING_MOD.core.models.id_card import IDCard
    bad_card = IDCard(
        doc_key="BAD",
        ulid="01HXXXXXXULIDXXXXXXBADXXX",
        semver="1.0.0",
        status="active",
        effective_date="2025-01-01",
        owner="QA",
        contract_type="policy",
        card_version=1,
    )
    # Remove required field by converting to dict and deleting
    data = bad_card.to_dict()
    del data["semver"]
    with pytest.raises(Exception):
        validator.card_validator.validate(data)
