import datetime
import json
from pathlib import Path

from models import Listing, Status
from validation import require_non_empty_string, require_non_negative_int

DATA_FILE = Path(__file__).parent / "sample_listings.json"


def parse_listing(item: dict) -> Listing:
    try:
        return Listing(
            id=require_non_empty_string(item["id"], "id"),
            source=require_non_empty_string(item["source"], "source"),
            address=require_non_empty_string(item["address"], "address"),
            city=require_non_empty_string(item["city"], "city"),
            state=require_non_empty_string(item["state"], "state"),
            zip=require_non_empty_string(item["zip"], "zip"),
            price=require_non_negative_int(int(item["price"]), "price"),
            bedrooms=require_non_negative_int(item["bedrooms"], "bedrooms"),
            bathrooms=float(item["bathrooms"]),
            sqft=require_non_negative_int(item["sqft"], "sqft"),
            latitude=float(item["latitude"]),
            longitude=float(item["longitude"]),
            listed_date=datetime.date.fromisoformat(item["listedDate"]),
            status=Status(item["status"]),
            description=require_non_empty_string(item["description"], "description"),
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
