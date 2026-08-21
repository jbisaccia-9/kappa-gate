"""Run the judge over the golden set and compute calibration statistics."""
import json
import pathlib

from . import judge as J
from .kappa import cohens_kappa, weighted_kappa, percent_agreement

ROOT = pathlib.Path(__file__).resolve().parents[2]


def load_config():
    return json.loads((ROOT / "eval_config.json").read_text())


def load_golden():
    return [json.loads(l) for l in
            (ROOT / "data" / "golden_set.jsonl").read_text().splitlines() if l.strip()]


def run(mode="mock", record=False):
    cfg = load_config()
    cases = load_golden()
    cache = J.load_cache(ROOT / "cache" / "judgments.jsonl") if mode == "cache" else {}
    results, recorded = [], []
    for case in cases:
        if mode == "live":
            scores = J.judge_live(case, model=cfg["judge_model"])
        elif mode == "cache":
            if case["id"] not in cache:
                raise KeyError(f"case {case['id']} missing from cache - rerun live with record")
            scores = cache[case["id"]]["scores"]
        else:
            scores = J.judge_mock(case)
        rec = {"id": case["id"], "tag": case["tag"], "human": case["human"],
               "judge": {k: scores[k] for k in ("G", "C", "S")},
               "human_verdict": J.verdict_from(case["human"]),
               "judge_verdict": J.verdict_from(scores)}
        results.append(rec)
        if record:
            recorded.append({"id": case["id"], "scores": scores,
                             "model": cfg["judge_model"],
                             "rubric_version": cfg["rubric_version"]})
    if record and recorded:
        (ROOT / "cache").mkdir(exist_ok=True)
        with open(ROOT / "cache" / "judgments.jsonl", "w") as f:
            for r in recorded:
                f.write(json.dumps(r) + "\n")
    return summarize(results, cfg, mode)


def summarize(results, cfg, mode):
    hv = [r["human_verdict"] for r in results]
    jv = [r["judge_verdict"] for r in results]
    per_dim = {d: weighted_kappa([r["human"][d] for r in results],
                                 [r["judge"][d] for r in results])
               for d in ("G", "C", "S")}
    by_tag = {}
    for r in results:
        by_tag.setdefault(r["tag"], []).append(r["human_verdict"] == r["judge_verdict"])
    summary = {
        "mode": mode,
        "judge_model": cfg["judge_model"] if mode != "mock" else "heuristic-mock",
        "rubric_version": cfg["rubric_version"],
        "n_cases": len(results),
        "verdict_agreement": round(percent_agreement(hv, jv), 4),
        "verdict_kappa": round(cohens_kappa(hv, jv), 4),
        "dimension_weighted_kappa": {k: round(v, 4) for k, v in per_dim.items()},
        "agreement_by_tag": {t: f"{sum(v)}/{len(v)}" for t, v in sorted(by_tag.items())},
        "disagreements": [r["id"] for r in results if r["human_verdict"] != r["judge_verdict"]],
    }
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    (out / "report.json").write_text(json.dumps(summary, indent=2))
    (out / "cases.jsonl").write_text("\n".join(json.dumps(r) for r in results))
    return summary
