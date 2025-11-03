"""
conftest.py
===========

Pytest configuration and fixtures for the ID module tests. This file
defines shared fixtures used across unit tests. For example, it
provides helper functions to create sample card data for tests.

Currently this skeleton does not implement any complex fixtures.
Workstream A can add fixtures here as needed.
"""

import pytest


@pytest.fixture
def sample_card_data() -> dict:
    """Return a minimal dictionary representing an ID card for tests."""
    return {
        "doc_key": "TEST_DOC",
        "ulid": "01HXXXXXXULIDXXXXXXTESTXX",
        "semver": "1.0.0",
        "status": "active",
        "effective_date": "2025-01-01",
        "owner": "QA",
        "contract_type": "policy",
        "card_version": 1,
        "aliases": [],
        "supersedes_version": None,
        "merged_into": None,
        "absorbs": [],
        "mfid": None,
    }
