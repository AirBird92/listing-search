from dataclasses import replace
from datetime import date

import pytest

from errors import InvalidSearchError
from filters import SearchFilter
from search import ScoredListing, SearchRequest, _ranking_key, rank

TODAY = date(2026, 10, 12)


@pytest.mark.parametrize(
    "kwargs",
    [
        pytest.param({"target_budget": 1}, id="min_budget"),
        pytest.param({"target_budget": 300_000}, id="typical_budget"),
        pytest.param({"target_budget": None}, id="no_budget"),
        pytest.param({"page": 1}, id="first_page"),
        pytest.param({"page": 50}, id="page_past_results_is_still_valid_input"),
        pytest.param({"page_size": 1}, id="min_page_size"),
        pytest.param({"page_size": 100}, id="max_page_size"),
        pytest.param({"filters": SearchFilter(city="Testville")}, id="with_filters"),
        pytest.param(
            {
                "filters": SearchFilter(min_price=200_000),
                "target_budget": 300_000,
                "page": 2,
                "page_size": 20,
            },
            id="all_fields",
        ),
    ],
)
def test_valid_search_request(kwargs):
    search_request = SearchRequest(**kwargs)
    for field, value in kwargs.items():
        assert getattr(search_request, field) == value


@pytest.mark.parametrize(
    "kwargs, message",
    [
        # target_budget: positive if given (0 would divide by zero in budget_fit).
        pytest.param(
            {"target_budget": 0},
            "target_budget must be an integer no less than 1",
            id="budget_zero",
        ),
        pytest.param(
            {"target_budget": -1},
            "target_budget must be an integer no less than 1",
            id="budget_negative",
        ),
        pytest.param(
            {"target_budget": "300000"},
            "target_budget must be an integer",
            id="budget_string",
        ),
        pytest.param(
            {"target_budget": 1.5},
            "target_budget must be an integer",
            id="budget_float",
        ),
        pytest.param(
            {"target_budget": True},
            "target_budget must be an integer",
            id="budget_bool",
        ),
        # page: 1-based.
        pytest.param(
            {"page": 0}, "page must be an integer no less than 1", id="page_zero"
        ),
        pytest.param(
            {"page": -1}, "page must be an integer no less than 1", id="page_negative"
        ),
        pytest.param({"page": "2"}, "page must be an integer", id="page_string"),
        # page_size: 1 to 100 (the handout's "pageSize of zero or less" case).
        pytest.param(
            {"page_size": 0},
            "page_size must be an integer between 1 and 100",
            id="page_size_zero",
        ),
        pytest.param(
            {"page_size": -1},
            "page_size must be an integer between 1 and 100",
            id="page_size_negative",
        ),
        pytest.param(
            {"page_size": 101},
            "page_size must be an integer between 1 and 100",
            id="page_size_over_max",
        ),
        pytest.param(
            {"page_size": "10"}, "page_size must be an integer", id="page_size_string"
        ),
    ],
)
def test_invalid_search_request(kwargs, message):
    with pytest.raises(InvalidSearchError, match=message):
        SearchRequest(**kwargs)


def test_search_request_defaults():
    search_request = SearchRequest()
    assert search_request.filters == SearchFilter()
    assert search_request.target_budget is None
    assert search_request.page == 1
    assert search_request.page_size == 10


@pytest.mark.parametrize(
    "target_budget, expected",
    [
        # Every `listings` fixture entry shares a source and listed date, so recency is
        # equal and only budget fit (or the id tie-breaker) decides the order.
        # rank() doesn't filter: pending (c) and sold (e) are ranked like the rest.
        pytest.param(
            300_000,
            # b, c on budget (1.0) > a, e 33% under (0.33) > d, f too far over (0)
            ["b", "c", "a", "e", "d", "f"],
            id="budget_300k",
        ),
        pytest.param(
            450_000,
            # d on budget > b, c 33% under > a, e beyond 50% under and f 33% over (all 0)
            ["d", "b", "c", "a", "e", "f"],
            id="budget_450k",
        ),
        pytest.param(
            600_000,
            # f on budget > d 25% under (0.5) > a, b, c, e at or beyond 50% under (all 0)
            ["f", "d", "a", "b", "c", "e"],
            id="budget_600k",
        ),
        pytest.param(
            None,
            # No budget: score is recency only, so every listing ties and id decides.
            ["a", "b", "c", "d", "e", "f"],
            id="no_budget",
        ),
    ],
)
def test_rank(listings, target_budget, expected):
    assert [s.listing.id for s in rank(listings, TODAY, target_budget)] == expected


def test_rank_newer_listing_first_when_budget_fit_is_equal(valid_listing):
    older = replace(valid_listing, id="old", listed_date=date(2026, 8, 1))
    newer = replace(valid_listing, id="new", listed_date=date(2026, 10, 1))
    result = rank([older, newer], TODAY, valid_listing.price)
    assert [s.listing.id for s in result] == ["new", "old"]


def test_rank_returns_scores(valid_listing):
    listing = replace(valid_listing, listed_date=TODAY)
    [scored] = rank([listing], TODAY, listing.price)
    assert scored.listing == listing
    assert scored.score == pytest.approx(100.0)


def test_rank_empty():
    assert rank([], TODAY, 300_000) == []


def test_rank_does_not_modify_input(listings):
    before = list(listings)
    rank(listings, TODAY, 300_000)
    assert listings == before


# Tie-breaker rules, tested on hand-built scores so ties are exact and don't depend on
# the scoring formula: score (high first) → listed date (new first) → source → id.
@pytest.mark.parametrize(
    "entries, expected",
    [
        pytest.param(
            [(50.0, "2026-10-01", "MLS_A", "1"), (90.0, "2026-01-01", "MLS_A", "2")],
            ["MLS_A/2", "MLS_A/1"],
            id="higher_score_first_even_if_older",
        ),
        pytest.param(
            [(80.0, "2026-08-01", "MLS_A", "1"), (80.0, "2026-10-01", "MLS_A", "2")],
            ["MLS_A/2", "MLS_A/1"],
            id="equal_score_newer_first",
        ),
        pytest.param(
            [(80.0, "2026-10-01", "MLS_B", "A1"), (80.0, "2026-10-01", "MLS_A", "A1")],
            ["MLS_A/A1", "MLS_B/A1"],
            id="equal_score_and_date_same_id_source_decides",
        ),
        pytest.param(
            [(80.0, "2026-10-01", "MLS_A", "B"), (80.0, "2026-10-01", "MLS_A", "A")],
            ["MLS_A/A", "MLS_A/B"],
            id="equal_score_date_and_source_id_decides",
        ),
    ],
)
def test_ranking_key(valid_listing, entries, expected):
    scored = [
        ScoredListing(
            listing=replace(
                valid_listing,
                source=source,
                id=listing_id,
                listed_date=date.fromisoformat(listed),
            ),
            score=score,
        )
        for score, listed, source, listing_id in entries
    ]
    result = sorted(scored, key=_ranking_key)
    assert [f"{s.listing.source}/{s.listing.id}" for s in result] == expected
