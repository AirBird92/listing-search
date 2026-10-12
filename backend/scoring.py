from datetime import date

from models import Listing

UNDER_TOLERANCE = 0.50
OVER_TOLERANCE = 0.25
HALF_LIFE_DAYS = 60
W_BUDGET = 0.7
W_RECENCY = 0.3


def budget_fit(price: int, target_budget: int) -> float:
    d = (price - target_budget) / target_budget
    if d <= 0:
        return max(0, 1 + d / UNDER_TOLERANCE)
    return max(0, 1 - d / OVER_TOLERANCE)


def recency(listed_date: date, today: date) -> float:
    if listed_date >= today:
        return 1
    return 0.5 ** ((today - listed_date).days / HALF_LIFE_DAYS)


def score(listing: Listing, today: date, target_budget: int | None) -> float:
    recency_score = recency(listing.listed_date, today)
    if target_budget is None:
        return 100 * recency_score
    budget_score = budget_fit(listing.price, target_budget)
    return 100 * (W_BUDGET * budget_score + W_RECENCY * recency_score)
