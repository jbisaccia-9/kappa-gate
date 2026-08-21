"""kappa-gate: an LLM-as-judge harness where the judge itself must pass a gate.

Reference labels are authored by hand against a versioned rubric; a candidate
judge is admitted only when its agreement with those labels clears Cohen's
kappa and accuracy thresholds. Until then, nothing downstream ships on its say-so.
"""
__version__ = "0.1.0"
