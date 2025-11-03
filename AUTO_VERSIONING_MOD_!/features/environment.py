"""
Behave environment configuration for ID module BDD tests.

This file defines hooks to set up and tear down test state for each
scenario. It initialises a temporary directory for ID cards and
ledger files so that scenarios do not interfere with each other.
"""
from __future__ import annotations

from pathlib import Path


def before_scenario(context, scenario):
    # Create temporary working directory for each scenario
    tmp_dir = Path("/tmp/behave_id_module")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    context.tmp_dir = tmp_dir


def after_scenario(context, scenario):
    # Clean up if necessary
    pass
