from dataclasses import dataclass, field
from datetime import date

from errors import InvalidSearchError
from filters import SearchFilter, filter_listings
from models import Listing
from pagination import Page, paginate
from ranking import rank
from validation import require_int_in_range


@dataclass(frozen=True, kw_only=True)
class SearchRequest:
    filters: SearchFilter = field(default_factory=SearchFilter)
    target_budget: int | None = None
    page: int = 1
    page_size: int = 10

    def __post_init__(self):
        try:
            if self.target_budget is not None:
                require_int_in_range(self.target_budget, "target_budget", min_val=1)
            require_int_in_range(self.page, "page", min_val=1)
            require_int_in_range(self.page_size, "page_size", 1, 100)
        except ValueError as e:
            raise InvalidSearchError(str(e)) from e


def search(listings: list[Listing], request: SearchRequest, today: date) -> Page:
    filtered_listings = filter_listings(listings, request.filters)
    ranked_listings = rank(filtered_listings, today, request.target_budget)
    return paginate(ranked_listings, request.page, request.page_size)
