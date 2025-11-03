"""
validate.py
==========

Plugin responsible for validating ID Cards and document front
matter against defined JSON schemas. Validation ensures the ID
module remains consistent and prevents invalid data from entering
the system. This skeleton demonstrates how to load and apply
schemas using the ``jsonschema`` library.
"""
from __future__ import annotations

from typing import Any, Dict
import json
from pathlib import Path

from jsonschema import Draft7Validator

from ..id.base import IDPlugin
from ..models.id_card import IDCard


class ValidatePlugin(IDPlugin):
    """Validate ID Cards using JSON Schema."""

    def __init__(self) -> None:
        # Load schemas at initialisation time
        base_path = Path(__file__).resolve().parents[3] / "schemas"
        card_schema = json.loads((base_path / "id_card.schema.json").read_text())
        self.card_validator = Draft7Validator(card_schema)

    def run(self, card: IDCard) -> None:
        """Validate an IDCard instance.

        Raises:
            jsonschema.exceptions.ValidationError if invalid.
        """
        self.card_validator.validate(card.to_dict())
