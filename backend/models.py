import datetime
from dataclasses import dataclass
from enum import Enum


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
