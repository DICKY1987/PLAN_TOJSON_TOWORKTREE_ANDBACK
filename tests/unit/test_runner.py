from core.runner import run, ExecutionError
from plugins.sample_recommender.plugin import SamplePlugin


def test_run_with_sample_plugin_creates_readme(tmp_path):
    repo = tmp_path
    result = run([SamplePlugin()], str(repo), {"seed": 42})
    assert "plan" in result and result["plan"]["items"] != []
    assert result["artifacts"]["created"] >= 1


def test_update_missing_target_raises(tmp_path):
    from core.contracts import Plan, PlanItem
    from core.runner import _apply_plan

    plan = Plan(items=[PlanItem(path="x.txt", action="update", content="x")])
    try:
        _apply_plan(str(tmp_path), plan)
    except ExecutionError:
        assert True
    else:
        assert False