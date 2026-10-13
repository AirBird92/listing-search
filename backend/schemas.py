import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from filters import SearchFilter
from models import Status
from pagination import Page
from ranking import ScoredListing
from search import SearchRequest


class SearchQuery(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, extra="forbid", frozen=True)

    min_price: int | None = None
    max_price: int | None = None
    min_bedrooms: int | None = None
    city: str | None = None
    keyword: str | None = None
    target_budget: int | None = None
    page: int | None = None
    page_size: int | None = None

    def to_search_request(self) -> SearchRequest:
        pagination = {}
        if self.page is not None:
            pagination["page"] = self.page
        if self.page_size is not None:
            pagination["page_size"] = self.page_size
        search_request = SearchRequest(
            filters=SearchFilter(
                min_price=self.min_price,
                max_price=self.max_price,
                min_bedrooms=self.min_bedrooms,
                city=self.city,
                keyword=self.keyword,
            ),
            target_budget=self.target_budget,
            **pagination,
        )
        return search_request


class ListingResult(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, extra="forbid", frozen=True, validate_by_name=True
    )

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
    score: float

    @classmethod
    def from_scored_listing(cls, scored_listing: ScoredListing) -> "ListingResult":
        return cls(
            id=scored_listing.listing.id,
            source=scored_listing.listing.source,
            address=scored_listing.listing.address,
            city=scored_listing.listing.city,
            state=scored_listing.listing.state,
            zip=scored_listing.listing.zip,
            price=scored_listing.listing.price,
            bedrooms=scored_listing.listing.bedrooms,
            bathrooms=scored_listing.listing.bathrooms,
            sqft=scored_listing.listing.sqft,
            latitude=scored_listing.listing.latitude,
            longitude=scored_listing.listing.longitude,
            listed_date=scored_listing.listing.listed_date,
            status=scored_listing.listing.status,
            description=scored_listing.listing.description,
            score=scored_listing.score,
        )


class SearchResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, extra="forbid", frozen=True, validate_by_name=True
    )

    results: list[ListingResult]
    page: int
    page_size: int
    total_results: int
    total_pages: int

    @classmethod
    def from_page(cls, page: Page) -> "SearchResponse":
        return cls(
            results=[
                ListingResult.from_scored_listing(scored_listing)
                for scored_listing in page.items
            ],
            page=page.page,
            page_size=page.page_size,
            total_results=page.total_results,
            total_pages=page.total_pages,
        )
