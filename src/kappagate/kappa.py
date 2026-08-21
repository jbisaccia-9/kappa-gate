"""Agreement statistics for judge calibration.

Cohen's kappa corrects raw percent-agreement for the agreement two raters would
reach by chance alone (kappa = (p_o - p_e) / (1 - p_e)). A judge that labels
everything "pass" against a 50/50 dataset scores 50% raw agreement but kappa 0 —
which is why the calibration gate uses kappa, not accuracy alone.
"""
from collections import Counter


def cohens_kappa(a, b):
    """Unweighted Cohen's kappa between two equal-length label sequences."""
    if len(a) != len(b) or not a:
        raise ValueError("label sequences must be equal-length and non-empty")
    n = len(a)
    p_o = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    p_e = sum((ca[k] / n) * (cb[k] / n) for k in set(ca) | set(cb))
    if p_e == 1.0:  # both raters constant and identical: perfect by definition
        return 1.0
    return (p_o - p_e) / (1 - p_e)


def weighted_kappa(a, b, levels=(0, 1, 2)):
    """Linear-weighted kappa for ordinal scores (0-2 rubric dimensions).

    Disagreeing 0-vs-2 is penalized twice as hard as 0-vs-1 — appropriate for
    ordered rubric anchors where distance carries meaning.
    """
    if len(a) != len(b) or not a:
        raise ValueError("label sequences must be equal-length and non-empty")
    n, k = len(a), len(levels)
    idx = {v: i for i, v in enumerate(levels)}
    w = [[abs(i - j) / (k - 1) for j in range(k)] for i in range(k)]
    obs = [[0.0] * k for _ in range(k)]
    for x, y in zip(a, b):
        obs[idx[x]][idx[y]] += 1 / n
    ra = [sum(row) for row in obs]
    rb = [sum(obs[i][j] for i in range(k)) for j in range(k)]
    exp = [[ra[i] * rb[j] for j in range(k)] for i in range(k)]
    d_o = sum(w[i][j] * obs[i][j] for i in range(k) for j in range(k))
    d_e = sum(w[i][j] * exp[i][j] for i in range(k) for j in range(k))
    if d_e == 0:
        return 1.0
    return 1 - d_o / d_e


def percent_agreement(a, b):
    if len(a) != len(b) or not a:
        raise ValueError("label sequences must be equal-length and non-empty")
    return sum(x == y for x, y in zip(a, b)) / len(a)
