"""
Steps for the deprecate_document.feature.
"""
from behave import given, when, then
from pathlib import Path
import yaml

from AUTO_VERSIONING_MOD.core.plugins.id.mint import MintPlugin
from AUTO_VERSIONING_MOD.core.plugins.id.deprecate import DeprecatePlugin


@given("an existing document with id card")
def given_existing_doc(context):
    cards_dir = context.tmp_dir / "cards"
    cards_dir.mkdir(parents=True, exist_ok=True)
    card = MintPlugin().run(doc_key="DOC", semver="1.0.0", owner="QA", contract_type="policy")
    yaml.safe_dump(card.to_dict(), (cards_dir / f"{card.ulid}.yaml").open("w"))
    context.ulid = card.ulid
    context.cards_dir = cards_dir


@when('I deprecate the document with reason "{reason}"')
def when_deprecate(context, reason):
    plugin = DeprecatePlugin(cards_dir=context.cards_dir, ledger_path=context.tmp_dir / "ledger.jsonl")
    plugin.run(context.ulid, reason)


@then("the id card status should be \"deprecated\"")
def then_status(context):
    card_path = context.cards_dir / f"{context.ulid}.yaml"
    data = yaml.safe_load(card_path.read_text())
    assert data["status"] == "deprecated"
