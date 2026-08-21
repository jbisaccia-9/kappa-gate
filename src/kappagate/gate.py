"""Calibration gate: is this judge trustworthy enough to gate anything else?

Exit code 0 = judge cleared the bar; 1 = judge is not to be trusted and any
pipeline downstream of it should not ship on its scores. The thresholds live in
eval_config.json so a threshold change is a reviewed, versioned event - never a
silent edit.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]


def check(report=None):
    cfg = json.loads((ROOT / "eval_config.json").read_text())
    if report is None:
        report = json.loads((ROOT / "results" / "report.json").read_text())
    gate = cfg["calibration_gate"]
    checks = [
        ("verdict_kappa", report["verdict_kappa"], gate["verdict_kappa_min"]),
        ("verdict_agreement", report["verdict_agreement"], gate["verdict_agreement_min"]),
    ]
    failures = [(n, v, m) for n, v, m in checks if v < m]
    for name, value, minimum in checks:
        status = "PASS" if value >= minimum else "FAIL"
        print(f"  {status}  {name}: {value} (min {minimum})")
    if failures:
        print(f"GATE: FAILED - judge '{report['judge_model']}' is not calibrated; "
              f"do not gate releases on its scores.")
        return 1
    print(f"GATE: PASSED - judge '{report['judge_model']}' cleared calibration "
          f"on rubric {report['rubric_version']}.")
    return 0


if __name__ == "__main__":
    sys.exit(check())
