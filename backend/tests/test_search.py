import datetime
from dataclasses import replace
from pathlib import Path

import pytest

from search import (
    DATA_FILE,
    InvalidFilterError,
    Listing,
    SearchFilter,
    Status,
    load,
    parse_listing,
)

TEST_FILE = Path(__file__).parent / "test_listings.json"

VALID_ITEM = {
    "id": "123",
    "source": "test_source",
    "address": "123 Main St",
    "city": "Testville",
    "state": "TS",
    "zip": "12345",
    "price": 250000,
    "bedrooms": 3,
    "bathrooms": 2.5,
    "sqft": 1500,
    "latitude": 38.8951,
    "longitude": -77.0364,
    "listedDate": "2023-01-01",
    "status": "active",
    "description": "A lovely home.",
}

VALID_LISTING = Listing(
    id="123",
    source="test_source",
    address="123 Main St",
    city="Testville",
    state="TS",
    zip="12345",
    price=250000,
    bedrooms=3,
    bathrooms=2.5,
    sqft=1500,
    latitude=38.8951,
    longitude=-77.0364,
    listed_date=datetime.date(2023, 1, 1),
    status=Status.ACTIVE,
    description="A lovely home.",
)


@pytest.mark.parametrize("item", [VALID_ITEM, {**VALID_ITEM, "price": 250000.99}])
def test_parse_listing(item):
    assert parse_listing(item) == VALID_LISTING


@pytest.mark.parametrize("id", [None, ""])
def test_parse_listing_invalid_id(id):
    item = {**VALID_ITEM, "id": id}
    with pytest.raises(ValueError, match=f"Invalid listing test_source/{id}:"):
        parse_listing(item)


@pytest.mark.parametrize("source", [None, ""])
def test_parse_listing_invalid_source(source):
    item = {**VALID_ITEM, "source": source}
    with pytest.raises(ValueError, match=f"Invalid listing {source}/123:"):
        parse_listing(item)


@pytest.mark.parametrize(
    "field, value",
    [
        ("address", ""),
        ("city", ""),
        ("state", ""),
        ("zip", ""),
        ("price", "not_a_number"),
        ("bedrooms", "not_a_number"),
        ("bathrooms", "not_a_number"),
        ("sqft", "not_a_number"),
        ("latitude", "not_a_number"),
        ("longitude", "not_a_number"),
        ("listedDate", "invalid_date"),
        ("status", "invalid_status"),
        ("description", ""),
        ("address", None),
        ("city", None),
        ("state", None),
        ("zip", None),
        ("price", None),
        ("bedrooms", None),
        ("bathrooms", None),
        ("sqft", None),
        ("latitude", None),
        ("longitude", None),
        ("listedDate", None),
        ("status", None),
        ("description", None),
        ("bedrooms", -1),
        ("sqft", -1),
        ("price", -1),
        ("bedrooms", 1.5),
        ("sqft", 1500.5),
    ],
)
def test_parse_listing_invalid_field(field, value):
    item = {**VALID_ITEM, field: value}
    with pytest.raises(ValueError, match="Invalid listing test_source/123:"):
        parse_listing(item)


def test_parse_listing_missing_id():
    item = {k: v for k, v in VALID_ITEM.items() if k != "id"}
    with pytest.raises(
        ValueError, match="Invalid listing test_source/None: missing field 'id'"
    ):
        parse_listing(item)


def test_parse_listing_missing_source():
    item = {k: v for k, v in VALID_ITEM.items() if k != "source"}
    with pytest.raises(
        ValueError, match="Invalid listing None/123: missing field 'source'"
    ):
        parse_listing(item)


@pytest.mark.parametrize(
    "key",
    [
        "address",
        "city",
        "state",
        "zip",
        "price",
        "bedrooms",
        "bathrooms",
        "sqft",
        "latitude",
        "longitude",
        "listedDate",
        "status",
        "description",
    ],
)
def test_parse_listing_missing_field(key):
    item = {k: v for k, v in VALID_ITEM.items() if k != key}
    with pytest.raises(
        ValueError, match=f"Invalid listing test_source/123: missing field '{key}'"
    ):
        parse_listing(item)


def test_load_listings():
    listings = load(TEST_FILE)
    assert listings[0] == VALID_LISTING
    assert listings[1] == replace(VALID_LISTING, id="124", address="124 Main St")
    assert len(listings) == 2


def test_smoke():
    listings = load(DATA_FILE)
    assert len(listings) > 0


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
