import datetime
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

DATA_FILE = Path(__file__).parent / "sample_listings.json"


class Status(Enum):
    ACTIVE = "active"
    PENDING = "pending"
    SOLD = "sold"


@dataclass(frozen=True, kw_only=True)
class Listing:
    id: str
    source: str
    address: str
    city: str
    state: str
    zip: str
    price: int
    bedrooms: int
    bathrooms: float
    sqft: int
    latitude: float
    longitude: float
    listed_date: datetime.date
    status: Status
    description: str


class InvalidFilterError(ValueError):
    pass


@dataclass(frozen=True, kw_only=True)
class SearchFilter:
    min_price: int | None = None
    max_price: int | None = None
    min_bedrooms: int | None = None
    city: str | None = None
    keyword: str | None = None

    def __post_init__(self):
        try:
            if self.min_price is not None:
                _require_non_negative_int(self.min_price, "min_price")
            if self.max_price is not None:
                _require_non_negative_int(self.max_price, "max_price")
            if self.min_bedrooms is not None:
                _require_non_negative_int(self.min_bedrooms, "min_bedrooms")
            if self.city is not None:
                _require_non_empty_string(self.city, "city")
            if self.keyword is not None:
                _require_non_empty_string(self.keyword, "keyword")
        except ValueError as e:
            raise InvalidFilterError(str(e)) from e

        if (
            self.min_price is not None
            and self.max_price is not None
            and self.min_price > self.max_price
        ):
            raise InvalidFilterError("min_price cannot be greater than max_price")


def parse_listing(item: dict) -> Listing:
    try:
        return Listing(
            id=_require_non_empty_string(item["id"], "id"),
            source=_require_non_empty_string(item["source"], "source"),
            address=_require_non_empty_string(item["address"], "address"),
            city=_require_non_empty_string(item["city"], "city"),
            state=_require_non_empty_string(item["state"], "state"),
            zip=_require_non_empty_string(item["zip"], "zip"),
            price=_require_non_negative_int(int(item["price"]), "price"),
            bedrooms=_require_non_negative_int(item["bedrooms"], "bedrooms"),
            bathrooms=float(item["bathrooms"]),
            sqft=_require_non_negative_int(item["sqft"], "sqft"),
            latitude=float(item["latitude"]),
            longitude=float(item["longitude"]),
            listed_date=datetime.date.fromisoformat(item["listedDate"]),
            status=Status(item["status"]),
            description=_require_non_empty_string(item["description"], "description"),
        )
    except KeyError as e:
        raise ValueError(
            f"Invalid listing {item.get('source')}/{item.get('id')}: missing field {e}"
        ) from e
    except (ValueError, TypeError) as e:
        raise ValueError(
            f"Invalid listing {item.get('source')}/{item.get('id')}: {e}"
        ) from e


def load(path: Path) -> list[Listing]:
    with open(path, encoding="utf-8") as json_data:
        data = json.load(json_data)
    return [parse_listing(item) for item in data]


def _require_non_empty_string(value: object, field_name: str) -> str:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _require_non_negative_int(value: object, field_name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer")
    return value
