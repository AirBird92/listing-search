import datetime
from dataclasses import dataclass

from models import Listing
from scoring import score


@dataclass(frozen=True, kw_only=True)
class ScoredListing:
    listing: Listing
    score: float


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
