from dataclasses import replace
from datetime import date, timedelta

import pytest

from scoring import budget_fit, recency, score

TODAY = date(2026, 10, 12)


@pytest.mark.parametrize(
    "price, budget, expected",
    [
        # The $300k example table from the README.
        (200_000, 300_000, 1 / 3),
        (270_000, 300_000, 0.8),
        (300_000, 300_000, 1.0),
        (330_000, 300_000, 0.6),
        (450_000, 300_000, 0.0),
        # Tolerance boundaries: exactly 50% under and 25% over reach 0, and stay there.
        (150_000, 300_000, 0.0),
        (375_000, 300_000, 0.0),
        (100_000, 300_000, 0.0),
        # Relative distance: the same percentages give the same fit on a larger budget.
        (1_800_000, 2_000_000, 0.8),
        (2_000_000, 2_000_000, 1.0),
        (2_200_000, 2_000_000, 0.6),
    ],
)
def test_budget_fit(price, budget, expected):
    assert budget_fit(price, budget) == pytest.approx(expected)


@pytest.mark.parametrize(
    "listed_date, today, expected",
    [
        pytest.param(TODAY, TODAY, 1.0, id="listed_today"),
        pytest.param(
            TODAY - timedelta(days=30), TODAY, 0.5**0.5, id="half_a_half_life"
        ),
        pytest.param(TODAY - timedelta(days=60), TODAY, 0.5, id="one_half_life"),
        pytest.param(TODAY - timedelta(days=120), TODAY, 0.25, id="two_half_lives"),
        pytest.param(TODAY + timedelta(days=10), TODAY, 1.0, id="future_date_clamped"),
    ],
)
def test_recency(listed_date, today, expected):
    assert recency(listed_date, today) == pytest.approx(expected)


@pytest.mark.parametrize(
    "price, listed_date, budget, expected",
    [
        # 100 × (0.7 × budget_fit + 0.3 × recency)
        pytest.param(300_000, TODAY, 300_000, 100.0, id="perfect_fit_listed_today"),
        pytest.param(
            300_000, TODAY - timedelta(days=60), 300_000, 85.0, id="perfect_fit_60_days"
        ),
        pytest.param(270_000, TODAY, 300_000, 86.0, id="10pct_under_listed_today"),
        pytest.param(330_000, TODAY, 300_000, 72.0, id="10pct_over_listed_today"),
        pytest.param(
            330_000, TODAY - timedelta(days=60), 300_000, 57.0, id="10pct_over_60_days"
        ),
        pytest.param(450_000, TODAY, 300_000, 30.0, id="out_of_budget_listed_today"),
        pytest.param(
            450_000,
            TODAY - timedelta(days=120),
            300_000,
            7.5,
            id="out_of_budget_120_days",
        ),
    ],
)
def test_score(valid_listing, price, listed_date, budget, expected):
    listing = replace(valid_listing, price=price, listed_date=listed_date)
    assert score(listing, TODAY, budget) == pytest.approx(expected)


@pytest.mark.parametrize(
    "price, listed_date, expected",
    [
        # No budget: 100 × recency, and price has no effect.
        pytest.param(300_000, TODAY, 100.0, id="listed_today"),
        pytest.param(5_000_000, TODAY, 100.0, id="price_ignored"),
        pytest.param(300_000, TODAY - timedelta(days=60), 50.0, id="60_days"),
        pytest.param(300_000, TODAY - timedelta(days=120), 25.0, id="120_days"),
        pytest.param(
            300_000, TODAY + timedelta(days=10), 100.0, id="future_date_clamped"
        ),
    ],
)
def test_score_without_budget(valid_listing, price, listed_date, expected):
    listing = replace(valid_listing, price=price, listed_date=listed_date)
    assert score(listing, TODAY, None) == pytest.approx(expected)
