import datetime
from dataclasses import replace
from pathlib import Path

import pytest

from search import DATA_FILE, Listing, Status, load, parse_listing

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
    "pair",
    [
        {"address": ""},
        {"city": ""},
        {"state": ""},
        {"zip": ""},
        {"price": "not_a_number"},
        {"bedrooms": "not_a_number"},
        {"bathrooms": "not_a_number"},
        {"sqft": "not_a_number"},
        {"latitude": "not_a_number"},
        {"longitude": "not_a_number"},
        {"listedDate": "invalid_date"},
        {"status": "invalid_status"},
        {"description": ""},
        {"address": None},
        {"city": None},
        {"state": None},
        {"zip": None},
        {"price": None},
        {"bedrooms": None},
        {"bathrooms": None},
        {"sqft": None},
        {"latitude": None},
        {"longitude": None},
        {"listedDate": None},
        {"status": None},
        {"description": None},
    ],
)
def test_parse_listing_invalid_field(pair):
    item = {**VALID_ITEM, **pair}
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
