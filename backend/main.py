from datetime import date
from typing import Annotated

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from errors import InvalidSearchError
from loader import DATA_FILE, load
from models import Listing
from schemas import SearchQuery, SearchResponse
from search import search

app = FastAPI()

LISTINGS = load(DATA_FILE)


def get_listings() -> list[Listing]:
    return LISTINGS


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/listings")
def search_listings(
    listings: Annotated[list[Listing], Depends(get_listings)],
    query: Annotated[SearchQuery, Query()],
) -> SearchResponse:
    return SearchResponse.from_page(
        search(listings, query.to_search_request(), date.today())
    )


@app.exception_handler(InvalidSearchError)
def handle_invalid_search_error(
    request: Request, exc: InvalidSearchError
) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(RequestValidationError)
def handle_request_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    first = exc.errors()[0]
    return JSONResponse(
        status_code=400,
        content={"detail": f"{first['loc'][-1]}: {first['msg']}"},
    )
