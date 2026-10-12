import math
from dataclasses import dataclass

from ranking import ScoredListing


@dataclass(frozen=True, kw_only=True)
class Page:
    items: tuple[ScoredListing, ...]
    page: int
    page_size: int
    total_results: int
    total_pages: int


def paginate(listings: list[ScoredListing], page: int, page_size: int) -> Page:
    """Returns one page of listings.

    'page' must be ≥ 1 (validated by SearchRequest);
    A page past the end returns no items, with accurate totals.
    """
    total_results = len(listings)
    total_pages = max(1, math.ceil(total_results / page_size))

    start, end = (page - 1) * page_size, page * page_size
    return Page(
        items=tuple(listings[start:end]),
        page=page,
        page_size=page_size,
        total_results=total_results,
        total_pages=total_pages,
    )
