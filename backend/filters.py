from dataclasses import dataclass

from errors import InvalidSearchError
from models import Listing, Status
from validation import require_non_empty_string, require_non_negative_int

SEARCHABLE_STATUSES = frozenset({Status.ACTIVE})


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
                require_non_negative_int(self.min_price, "min_price")
            if self.max_price is not None:
                require_non_negative_int(self.max_price, "max_price")
            if self.min_bedrooms is not None:
                require_non_negative_int(self.min_bedrooms, "min_bedrooms")
            if self.city is not None:
                require_non_empty_string(self.city, "city")
            if self.keyword is not None:
                require_non_empty_string(self.keyword, "keyword")
        except ValueError as e:
            raise InvalidSearchError(str(e)) from e

        if (
            self.min_price is not None
            and self.max_price is not None
            and self.min_price > self.max_price
        ):
            raise InvalidSearchError("min_price cannot be greater than max_price")


def filter_listings(
    listings: list[Listing], search_filter: SearchFilter
) -> list[Listing]:
    city = (
        search_filter.city.strip().casefold()
        if search_filter.city is not None
        else None
    )
    keyword = (
        search_filter.keyword.strip().casefold()
        if search_filter.keyword is not None
        else None
    )

    def matches(listing: Listing) -> bool:
        if listing.status not in SEARCHABLE_STATUSES:
            return False
        if (
            search_filter.min_price is not None
            and listing.price < search_filter.min_price
        ):
            return False
        if (
            search_filter.max_price is not None
            and listing.price > search_filter.max_price
        ):
            return False
        if (
            search_filter.min_bedrooms is not None
            and listing.bedrooms < search_filter.min_bedrooms
        ):
            return False
        if city is not None and listing.city.strip().casefold() != city:
            return False
        if keyword is not None and keyword not in listing.description.casefold():
            return False
        return True

    return [listing for listing in listings if matches(listing)]
