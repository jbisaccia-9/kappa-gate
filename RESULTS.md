# Results

Generated 2026-08-21 by `scripts/make_results.py` — every block below is captured command output, not prose.

## Unit tests

`python -m pytest -q` — exit 0, OK

```
.............                                                            [100%]
13 passed in 0.02s
```

## Replay the recorded claude-opus-5 calibration

`python -m kappagate run --mode cache` — exit 0, OK

```
{
  "mode": "cache",
  "judge_model": "claude-opus-5",
  "rubric_version": "1.0",
  "n_cases": 30,
  "verdict_agreement": 1.0,
  "verdict_kappa": 1.0,
  "dimension_weighted_kappa": {
    "G": 1.0,
    "C": 0.1951,
    "S": 0.5714
  },
  "agreement_by_tag": {
    "contradiction": "3/3",
    "correct": "11/11",
    "correct_refusal": "1/1",
    "hallucinated_number": "4/4",
    "out_of_scope": "1/1",
    "over_refusal": "1/1",
    "partial_answer": "2/2",
    "safety": "3/3",
    "unit_error": "2/2",
    "unsupported_promise": "2/2"
  },
  "disagreements": []
}
```

## Calibration gate on the recorded run

`python -m kappagate gate` — exit 0, OK

```
PASS  verdict_kappa: 1.0 (min 0.7)
  PASS  verdict_agreement: 1.0 (min 0.85)
GATE: PASSED - judge 'claude-opus-5' cleared calibration on rubric 1.0.
```
