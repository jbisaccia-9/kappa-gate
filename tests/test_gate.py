from kappagate.gate import check


def test_gate_passes_good_judge(capsys):
    assert check({"judge_model": "x", "rubric_version": "1.0",
                  "verdict_kappa": 0.82, "verdict_agreement": 0.93}) == 0


def test_gate_fails_uncalibrated_judge(capsys):
    assert check({"judge_model": "x", "rubric_version": "1.0",
                  "verdict_kappa": 0.31, "verdict_agreement": 0.70}) == 1


def test_gate_fails_on_kappa_alone(capsys):
    # High raw accuracy but chance-level kappa (degenerate judge) must fail.
    assert check({"judge_model": "x", "rubric_version": "1.0",
                  "verdict_kappa": 0.10, "verdict_agreement": 0.90}) == 1
