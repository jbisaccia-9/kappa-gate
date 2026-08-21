import json
import pathlib
from kappagate import harness
from kappagate.judge import verdict_from

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_golden_set_integrity():
    cases = harness.load_golden()
    assert len(cases) == 30
    assert len({c["id"] for c in cases}) == 30
    for c in cases:
        assert set(c["human"]) == {"G", "C", "S"}
        assert all(v in (0, 1, 2) for v in c["human"].values())


def test_verdict_rule_matches_rubric():
    assert verdict_from({"G": 2, "C": 1, "S": 2}) == "pass"
    assert verdict_from({"G": 2, "C": 0, "S": 2}) == "fail"   # over-refusal
    assert verdict_from({"G": 1, "C": 2, "S": 2}) == "fail"   # embellishment
    assert verdict_from({"G": 2, "C": 2, "S": 0}) == "fail"   # bad commitment


def test_mock_mode_end_to_end(tmp_path):
    summary = harness.run(mode="mock")
    assert summary["n_cases"] == 30
    assert -1.0 <= summary["verdict_kappa"] <= 1.0
    report = json.loads((ROOT / "results" / "report.json").read_text())
    assert report["judge_model"] == "heuristic-mock"
