import datetime
from dataclasses import dataclass, field

from errors import InvalidSearchError
from filters import SearchFilter
from models import Listing
from scoring import score
from validation import require_int_in_range


@dataclass(frozen=True, kw_only=True)
class ScoredListing:
    listing: Listing
    score: float


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


def rank(
    listings: list[Listing], today: datetime.date, target_budget: int | None
) -> list[ScoredListing]:
    scored = [
        ScoredListing(listing=listing, score=score(listing, today, target_budget))
        for listing in listings
    ]
    scored.sort(key=_ranking_key)
    return scored


def _ranking_key(scored_listing: ScoredListing) -> tuple:
    return (
        -scored_listing.score,
        -scored_listing.listing.listed_date.toordinal(),
        scored_listing.listing.source,
        scored_listing.listing.id,
    )
