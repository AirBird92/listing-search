from dataclasses import replace

import pytest

from filters import InvalidFilterError, SearchFilter, filter_listings
from models import Status


@pytest.mark.parametrize(
    "kwargs",
    [
        pytest.param(
            {"min_price": 100000, "max_price": 500000}, id="valid_price_range"
        ),
        pytest.param(
            {"min_price": 100000, "max_price": 100000}, id="equal_price_range"
        ),
        pytest.param({"min_price": 0}, id="zero_min_price"),
        pytest.param({"min_bedrooms": 0}, id="zero_min_bedrooms"),
        pytest.param({"city": " Testville "}, id="city_with_whitespace"),
        pytest.param({"keyword": "lovely"}, id="valid_keyword"),
        pytest.param({}, id="no_filters"),
    ],
)
def test_valid_search_filter(kwargs):
    search_filter = SearchFilter(**kwargs)
    for field, value in kwargs.items():
        assert getattr(search_filter, field) == value


@pytest.mark.parametrize(
    "kwargs, message",
    [
        pytest.param(
            {"min_price": 500000, "max_price": 100000},
            "min_price cannot be greater than max_price",
            id="min_price_greater_than_max_price",
        ),
        pytest.param(
            {"min_price": -100000},
            "min_price must be a non-negative integer",
            id="min_price_negative",
        ),
        pytest.param(
            {"max_price": -500000},
            "max_price must be a non-negative integer",
            id="max_price_negative",
        ),
        pytest.param(
            {"min_price": "100"},
            "min_price must be a non-negative integer",
            id="min_price_not_integer",
        ),
        pytest.param(
            {"min_price": 1.5},
            "min_price must be a non-negative integer",
            id="min_price_float",
        ),
        pytest.param(
            {"min_bedrooms": -2},
            "min_bedrooms must be a non-negative integer",
            id="min_bedrooms_negative",
        ),
        pytest.param(
            {"min_bedrooms": True},
            "min_bedrooms must be a non-negative integer",
            id="min_bedrooms_not_integer",
        ),
        pytest.param({"city": ""}, "city must be a non-empty string", id="city_empty"),
        pytest.param(
            {"city": 123}, "city must be a non-empty string", id="city_not_string"
        ),
        pytest.param(
            {"keyword": ""}, "keyword must be a non-empty string", id="keyword_empty"
        ),
        pytest.param(
            {"keyword": " "},
            "keyword must be a non-empty string",
            id="keyword_whitespace",
        ),
        pytest.param(
            {"keyword": 123},
            "keyword must be a non-empty string",
            id="keyword_not_string",
        ),
    ],
)
def test_invalid_search_filter(kwargs, message):
    with pytest.raises(InvalidFilterError, match=message):
        SearchFilter(**kwargs)


@pytest.fixture
def listings(valid_listing):
    # id | status  | price   | beds | city            | description
    # a  | active  | 200,000 | 2    | "Testville"     | no "lovely"
    # b  | active  | 300,000 | 3    | "  testville "  | "Lovely" (capitalised)
    # c  | pending | 300,000 | 3    | "Testville"     | "lovely": same as b, but not active
    # d  | active  | 450,000 | 4    | "Springfield"   | "LOVELY" (upper case)
    # e  | sold    | 200,000 | 2    | "Testville"     | "lovely": same as a, but not active
    # f  | active  | 600,000 | 5    | "Springfield"   | no "lovely"
    # Prices and bedrooms are distinct round values so min/max boundaries are easy to hit.
    # Inactive listings are interleaved so order-preservation is actually tested.
    return [
        replace(
            valid_listing,
            id="a",
            price=200_000,
            bedrooms=2,
            city="Testville",
            description="Cozy condo near the park.",
        ),
        replace(
            valid_listing,
            id="b",
            price=300_000,
            bedrooms=3,
            city="  testville ",
            description="Lovely family home with a big yard.",
        ),
        replace(
            valid_listing,
            id="c",
            status=Status.PENDING,
            price=300_000,
            bedrooms=3,
            city="Testville",
            description="Lovely home, sale pending.",
        ),
        replace(
            valid_listing,
            id="d",
            price=450_000,
            bedrooms=4,
            city="Springfield",
            description="Spacious house with LOVELY views.",
        ),
        replace(
            valid_listing,
            id="e",
            status=Status.SOLD,
            price=200_000,
            bedrooms=2,
            city="Testville",
            description="Lovely starter home, already sold.",
        ),
        replace(
            valid_listing,
            id="f",
            price=600_000,
            bedrooms=5,
            city="Springfield",
            description="Luxury estate with a pool.",
        ),
    ]


@pytest.mark.parametrize(
    "search_filter, expected",
    [
        # No filters: every active listing, in input order (c and e are not active).
        pytest.param(SearchFilter(), ["a", "b", "d", "f"], id="no_filters"),
        # Price: bounds are inclusive.
        pytest.param(
            SearchFilter(min_price=200_000, max_price=300_000),
            ["a", "b"],
            id="price_range_inclusive_both_ends",
        ),
        pytest.param(
            SearchFilter(min_price=450_000), ["d", "f"], id="min_price_boundary"
        ),
        pytest.param(SearchFilter(max_price=200_000), ["a"], id="max_price_boundary"),
        pytest.param(
            SearchFilter(min_price=300_000, max_price=300_000),
            ["b"],
            id="exact_price",
        ),
        pytest.param(
            SearchFilter(min_price=700_000), [], id="price_above_all_listings"
        ),
        # Bedrooms: inclusive minimum.
        pytest.param(SearchFilter(min_bedrooms=4), ["d", "f"], id="min_bedrooms"),
        pytest.param(SearchFilter(min_bedrooms=5), ["f"], id="min_bedrooms_boundary"),
        pytest.param(
            SearchFilter(min_bedrooms=0), ["a", "b", "d", "f"], id="min_bedrooms_zero"
        ),
        # City: trimmed and case-insensitive on both sides, but an exact match.
        pytest.param(
            SearchFilter(city=" TESTVILLE "), ["a", "b"], id="city_case_and_whitespace"
        ),
        pytest.param(SearchFilter(city="springfield"), ["d", "f"], id="city_other"),
        pytest.param(SearchFilter(city="Test"), [], id="city_partial_does_not_match"),
        pytest.param(SearchFilter(city="Nowhere"), [], id="city_no_match"),
        # Keyword: case-insensitive substring of the description.
        pytest.param(SearchFilter(keyword="lovely"), ["b", "d"], id="keyword"),
        pytest.param(
            SearchFilter(keyword="  LOVELY "),
            ["b", "d"],
            id="keyword_case_and_whitespace",
        ),
        pytest.param(SearchFilter(keyword="lov"), ["b", "d"], id="keyword_substring"),
        pytest.param(SearchFilter(keyword="garage"), [], id="keyword_no_match"),
        # Combined: a listing must pass every filter.
        pytest.param(
            SearchFilter(city="springfield", keyword="lovely"),
            ["d"],
            id="city_and_keyword",
        ),
        pytest.param(
            SearchFilter(city="testville", min_bedrooms=3),
            ["b"],
            id="city_and_min_bedrooms",
        ),
        pytest.param(
            SearchFilter(min_price=300_000, max_price=300_000, keyword="lovely"),
            ["b"],
            id="inactive_excluded_even_when_all_filters_match",
        ),
    ],
)
def test_filter_listings(listings, search_filter: SearchFilter, expected: list[str]):
    assert [
        listing.id for listing in filter_listings(listings, search_filter)
    ] == expected


def test_filter_listings_empty_input():
    assert filter_listings([], SearchFilter()) == []
