from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import datetime
import json

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


def parse_listing(item: dict) -> Listing:
    try:
        return Listing(
            id=item["id"],
            source=item["source"],
            address=item["address"],
            city=item["city"],
            state=item["state"],
            zip=item["zip"],
            price=int(item["price"]),
            bedrooms=int(item["bedrooms"]),
            bathrooms=float(item["bathrooms"]),
            sqft=int(item["sqft"]),
            latitude=float(item["latitude"]),
            longitude=float(item["longitude"]),
            listed_date=datetime.date.fromisoformat(item["listedDate"]),
            status=Status(item["status"]),
            description=item["description"]
        )
    except KeyError as e:
        raise ValueError(f"Invalid listing {item.get('source')}/{item.get('id')}: missing field {e}") from e
    except ValueError as e:
        raise ValueError(f"Invalid listing {item.get('source')}/{item.get('id')}: {e}") from e


def load(path: Path) -> list[Listing]:
    with open(path, encoding="utf-8") as json_data:
        data = json.load(json_data)
    return [parse_listing(item) for item in data]
