import pytest

from filters import InvalidFilterError, SearchFilter


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
