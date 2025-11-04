from __future__ import annotations
import hashlib
import json
from jsonschema import Draft202012Validator


def validate_json(instance: dict, schema: dict) -> None:
    Draft202012Validator(schema).validate(instance)


def deterministic_hash(obj: dict) -> str:
    data = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()