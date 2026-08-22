"""Braintrust-shaped eval suite: data -> task -> scorers.

Mirrors braintrust.Eval(name, data, task, scores) so the identical suite runs
keyless in CI (regression gate) or pushes to hosted Braintrust with the obs
extra (pip install ".[obs]" + BRAINTRUST_API_KEY). The task replays the
RECORDED judge run from cache/ - the suite scores the judge that actually ran,
not a fresh sample.
"""
import json
import pathlib

from .harness import load_golden
from .judge import load_cache, verdict_from

ROOT = pathlib.Path(__file__).resolve().parents[2]


def data():
    cache = load_cache(ROOT / "cache" / "judgments.jsonl")
    return [{"case": c, "judge": cache[c["id"]]["scores"]} for c in load_golden()]


def task(row):
    return {"verdict": verdict_from(row["judge"]),
            "scores": {k: row["judge"][k] for k in ("G", "C", "S")}}


def verdict_match(row, out):
    return 1.0 if out["verdict"] == verdict_from(row["case"]["human"]) else 0.0


def dimensions_exact(row, out):
    return 1.0 if out["scores"] == row["case"]["human"] else 0.0


SCORERS = [("verdict_match", verdict_match), ("dimensions_exact", dimensions_exact)]


def run_local():
    rows = data()
    means = {}
    for name, fn in SCORERS:
        means[name] = round(sum(fn(r, task(r)) for r in rows) / len(rows), 4)
        print(f"  {name}: {means[name]}")
    ok = means["verdict_match"] >= 0.85   # aligned with the calibration gate
    print("SUITE: PASS - judge verdicts hold." if ok else "SUITE: FAIL - verdict regression.")
    return 0 if ok else 1


def push_braintrust():
    import braintrust  # optional extra
    braintrust.Eval("kappa-gate",
                    data=lambda: [{"input": r, "expected": r["case"]["human"]} for r in data()],
                    task=task,
                    scores=[lambda input, expected, output, n=n, f=f:
                            braintrust.Score(name=n, score=f(input, output))
                            for n, f in SCORERS])
