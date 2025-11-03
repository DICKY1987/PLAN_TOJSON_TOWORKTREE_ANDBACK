"""
Steps for the rename_document.feature.
"""
from behave import given, when, then
from pathlib import Path
import yaml

from AUTO_VERSIONING_MOD.core.plugins.id.mint import MintPlugin
from AUTO_VERSIONING_MOD.core.plugins.id.rekey import RekeyPlugin


@given("an existing document with id card")
def step_given_existing_doc(context):
    # Create sample card in temporary directory
    cards_dir = context.tmp_dir / "cards"
    cards_dir.mkdir(parents=True, exist_ok=True)
    card = MintPlugin().run(doc_key="OLD_KEY", semver="1.0.0", owner="QA", contract_type="policy")
    # Persist card
    context.ulid = card.ulid
    yaml.safe_dump(card.to_dict(), (cards_dir / f"{card.ulid}.yaml").open("w"))
    context.cards_dir = cards_dir


@when('I rekey the document to "{new_key}"')
def step_when_rekey(context, new_key):
    plugin = RekeyPlugin(cards_dir=context.cards_dir, ledger_path=context.tmp_dir / "ledger.jsonl")
    plugin.run(context.ulid, new_key)


@then("the id card should include the old key in aliases")
def step_then_aliases(context):
    card_path = context.cards_dir / f"{context.ulid}.yaml"
    data = yaml.safe_load(card_path.read_text())
    assert "OLD_KEY" in data["aliases"]
