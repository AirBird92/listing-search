# tests/conftest.py
import datetime

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
