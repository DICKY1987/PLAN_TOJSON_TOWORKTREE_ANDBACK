from core.runner import run
from plugins.sample_recommender.plugin import SamplePlugin


def test_e2e_pipeline(tmp_path):
    result = run([SamplePlugin()], str(tmp_path), {"seed": 123})
    assert result["artifacts"]["worktree"]
    assert result["plan"]["version"] == "1.0"