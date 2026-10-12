from dataclasses import replace
from pathlib import Path

import pytest

from loader import DATA_FILE, load, parse_listing

TEST_FILE = Path(__file__).parent / "test_listings.json"


@pytest.mark.parametrize("kwargs", [{}, {"price": 250000.99}])
def test_parse_listing(valid_item, valid_listing, kwargs):
    item = {**valid_item, **kwargs}
    assert parse_listing(item) == valid_listing


@pytest.mark.parametrize("id", [None, ""])
def test_parse_listing_invalid_id(valid_item, id):
    item = {**valid_item, "id": id}
    with pytest.raises(ValueError, match=f"Invalid listing test_source/{id}:"):
        parse_listing(item)


@pytest.mark.parametrize("source", [None, ""])
def test_parse_listing_invalid_source(valid_item, source):
    item = {**valid_item, "source": source}
    with pytest.raises(ValueError, match=f"Invalid listing {source}/123:"):
        parse_listing(item)


@pytest.mark.parametrize(
    "field, value",
    [
        pytest.param("address", "", id="address_empty"),
        pytest.param("city", "", id="city_empty"),
        pytest.param("state", "", id="state_empty"),
        pytest.param("zip", "", id="zip_empty"),
        ("price", "not_a_number"),
        ("bedrooms", "not_a_number"),
        ("bathrooms", "not_a_number"),
        ("sqft", "not_a_number"),
        ("latitude", "not_a_number"),
        ("longitude", "not_a_number"),
        ("listedDate", "invalid_date"),
        ("status", "invalid_status"),
        pytest.param("description", "", id="description_empty"),
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
def test_parse_listing_invalid_field(valid_item, field, value):
    item = {**valid_item, field: value}
    with pytest.raises(ValueError, match="Invalid listing test_source/123:"):
        parse_listing(item)


def test_parse_listing_missing_id(valid_item):
    item = {k: v for k, v in valid_item.items() if k != "id"}
    with pytest.raises(
        ValueError, match="Invalid listing test_source/None: missing field 'id'"
    ):
        parse_listing(item)


def test_parse_listing_missing_source(valid_item):
    item = {k: v for k, v in valid_item.items() if k != "source"}
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
def test_parse_listing_missing_field(valid_item, key):
    item = {k: v for k, v in valid_item.items() if k != key}
    with pytest.raises(
        ValueError, match=f"Invalid listing test_source/123: missing field '{key}'"
    ):
        parse_listing(item)


def test_load_listings(valid_listing):
    listings = load(TEST_FILE)
    assert listings[0] == valid_listing
    assert listings[1] == replace(valid_listing, id="124", address="124 Main St")
    assert len(listings) == 2


def test_smoke():
    listings = load(DATA_FILE)
    assert len(listings) > 0
