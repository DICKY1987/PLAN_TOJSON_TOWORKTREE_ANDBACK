import json
import pathlib
from jsonschema import Draft202012Validator
from plugins.sample_recommender.plugin import SamplePlugin


def load_schema(name):
    return json.loads(pathlib.Path("schemas", name).read_text())


def test_recommendation_conforms_schema(tmp_path):
    rec = SamplePlugin().analyze(str(tmp_path), {"seed": 1})
    schema = load_schema("recommendation.schema.json")
    Draft202012Validator(schema).validate(rec.model_dump())