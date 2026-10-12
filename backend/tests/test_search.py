from datetime import date

import pytest

from errors import InvalidSearchError
from filters import SearchFilter
from search import SearchRequest, search

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
    "search_request, expected_ids, expected_total_results",
    [
        # The `listings` fixture shares one listed date, so recency ties and the order
        # comes from budget fit, then id. Pending (c) and sold (e) are always excluded.
        pytest.param(
            SearchRequest(),
            ["a", "b", "d", "f"],
            4,
            id="defaults_active_only_ties_by_id",
        ),
        pytest.param(
            SearchRequest(target_budget=300_000),
            ["b", "a", "d", "f"],
            4,
            id="budget_ranks_by_fit",
        ),
        pytest.param(
            SearchRequest(
                filters=SearchFilter(city="testville"), target_budget=300_000
            ),
            ["b", "a"],
            2,
            id="filter_then_rank",
        ),
        pytest.param(
            SearchRequest(
                filters=SearchFilter(keyword="lovely"), target_budget=450_000
            ),
            ["d", "b"],
            2,
            id="keyword_and_budget",
        ),
        pytest.param(
            SearchRequest(filters=SearchFilter(city="Nowhere")),
            [],
            0,
            id="city_with_no_matches_is_empty_not_error",
        ),
        pytest.param(
            SearchRequest(target_budget=300_000, page=2, page_size=2),
            ["d", "f"],
            4,
            id="second_page_continues_ranking",
        ),
        pytest.param(
            SearchRequest(target_budget=300_000, page=3, page_size=2),
            [],
            4,
            id="page_past_the_end_is_empty",
        ),
    ],
)
def test_search(listings, search_request, expected_ids, expected_total_results):
    results = search(listings, search_request, TODAY)
    assert [
        scored_listing.listing.id for scored_listing in results.items
    ] == expected_ids
    assert results.total_results == expected_total_results
