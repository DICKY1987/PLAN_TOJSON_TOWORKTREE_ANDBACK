"""
Steps for the merge_documents.feature.
"""
from behave import given, when, then
import yaml

from AUTO_VERSIONING_MOD.core.plugins.id.mint import MintPlugin
from AUTO_VERSIONING_MOD.core.plugins.id.consolidate import ConsolidatePlugin


@given("three existing documents with id cards")
def given_three_docs(context):
    cards_dir = context.tmp_dir / "cards"
    cards_dir.mkdir(parents=True, exist_ok=True)
    card1 = MintPlugin().run(doc_key="TARGET", semver="1.0.0", owner="QA", contract_type="policy")
    card2 = MintPlugin().run(doc_key="SRC1", semver="1.0.0", owner="QA", contract_type="policy")
    card3 = MintPlugin().run(doc_key="SRC2", semver="1.0.0", owner="QA", contract_type="policy")
    for card in [card1, card2, card3]:
        yaml.safe_dump(card.to_dict(), (cards_dir / f"{card.ulid}.yaml").open("w"))
    context.target_ulid = card1.ulid
    context.source_ulids = [card2.ulid, card3.ulid]
    context.cards_dir = cards_dir


@when("I consolidate the two source documents into the target")
def when_consolidate(context):
    plugin = ConsolidatePlugin(cards_dir=context.cards_dir, ledger_path=context.tmp_dir / "ledger.jsonl")
    plugin.run(target_ulid=context.target_ulid, source_ulids=context.source_ulids)


@then("the source documents should be marked as merged into the target")
def then_consolidated(context):
    for ulid in context.source_ulids:
        data = yaml.safe_load((context.cards_dir / f"{ulid}.yaml").read_text())
        assert data.get("merged_into") == context.target_ulid
