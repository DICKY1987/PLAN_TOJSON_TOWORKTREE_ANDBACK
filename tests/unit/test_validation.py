from core.validation import deterministic_hash


def test_deterministic_hash_stable():
    a = {"b": 2, "a": 1}
    b = {"a": 1, "b": 2}
    assert deterministic_hash(a) == deterministic_hash(b)