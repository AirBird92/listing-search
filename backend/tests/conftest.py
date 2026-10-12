import datetime
from dataclasses import replace

import pytest

from models import Listing, Status


@pytest.fixture
def valid_listing():
    return Listing(
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


@pytest.fixture
def valid_item():
    return {
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
    # All share valid_listing's source and listed_date, so ranking ties fall back to id.
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
