"""
Tests for the LedgerPlugin.
"""
from pathlib import Path
import json

from AUTO_VERSIONING_MOD.core.plugins.id.ledger import LedgerPlugin
from AUTO_VERSIONING_MOD.core.models.ledger_event import LedgerEvent


def test_append_event_creates_file(tmp_path: Path) -> None:
    ledger_path = tmp_path / "ids.jsonl"
    plugin = LedgerPlugin(ledger_path)
    event = LedgerEvent(
        event_type="CREATE",
        timestamp="2025-11-03T00:00:00Z",
        ulid="01HXXXXXXULIDXXXXXXLEDGERX",
        doc_key="LEDGER_TEST",
        data={},
    )
    plugin.run(event)
    assert ledger_path.exists()
    contents = ledger_path.read_text().strip().splitlines()
    assert json.loads(contents[0])["event_type"] == "CREATE"
