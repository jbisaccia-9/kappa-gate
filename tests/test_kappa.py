import math
import pytest
from kappagate.kappa import cohens_kappa, weighted_kappa, percent_agreement


def test_perfect_agreement():
    assert cohens_kappa(["p", "f", "p"], ["p", "f", "p"]) == 1.0


def test_chance_only_agreement_is_zero():
    # Rater B says "pass" half the time independent of A: kappa ~ 0.
    a = ["p", "p", "f", "f"]
    b = ["p", "f", "p", "f"]
    assert abs(cohens_kappa(a, b)) < 1e-9


def test_known_value():
    # Worked by hand: 8/10 agree (p_o=0.8), both raters 50/50 (p_e=0.5)
    # -> kappa = (0.8 - 0.5) / (1 - 0.5) = 0.6
    a = ["y"] * 5 + ["n"] * 5
    b = ["y", "y", "y", "y", "n", "n", "n", "n", "n", "y"]
    assert math.isclose(cohens_kappa(a, b), 0.6, abs_tol=1e-9)


def test_constant_identical_raters():
    assert cohens_kappa(["p", "p"], ["p", "p"]) == 1.0


def test_weighted_kappa_orders_penalties():
    # A 0-vs-2 disagreement must hurt more than 0-vs-1.
    base = [0, 1, 2, 0, 1, 2]
    near = [0, 1, 2, 1, 1, 2]   # one off-by-one
    far = [0, 1, 2, 2, 1, 2]    # one off-by-two
    assert weighted_kappa(base, near) > weighted_kappa(base, far)


def test_percent_agreement():
    assert percent_agreement([1, 2, 3], [1, 2, 4]) == pytest.approx(2 / 3)


def test_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        cohens_kappa([1], [1, 2])
