import pytest
from fastapi.testclient import TestClient

from main import app, get_listings


@pytest.fixture
def client(listings):
    app.dependency_overrides[get_listings] = lambda: listings
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cors(client):
    response = client.get("/api/health", headers={"Origin": "http://localhost:5173"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_not_allow(client):
    response = client.get("/api/health", headers={"Origin": "http://evil.host"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "access-control-allow-origin" not in response.headers


def test_search_default(client):
    response = client.get("/api/listings")
    assert response.status_code == 200
    response_obj = response.json()
    listings = response_obj["results"]
    assert [listing["id"] for listing in listings] == ["a", "b", "d", "f"]
    assert response_obj["page"] == 1
    assert response_obj["pageSize"] == 10
    assert response_obj["totalResults"] == 4
    assert response_obj["totalPages"] == 1


@pytest.mark.parametrize(
    "params, expected_ids, expected_total_results, expected_total_pages",
    [
        pytest.param(
            {"targetBudget": 300000}, ["b", "a", "d", "f"], 4, 1, id="budget_only"
        ),
        pytest.param(
            {"targetBudget": 300000, "city": "testville"},
            ["b", "a"],
            2,
            1,
            id="city_filter_with_budget",
        ),
        pytest.param(
            {"targetBudget": 300000, "page": 2, "pageSize": 2},
            ["d", "f"],
            4,
            2,
            id="pagination",
        ),
        pytest.param({"city": "Nowhere"}, [], 0, 1, id="city_with_no_matches"),
    ],
)
def test_search(
    client, params, expected_ids, expected_total_results, expected_total_pages
):
    response = client.get("/api/listings", params=params)
    assert response.status_code == 200
    response_obj = response.json()
    listings = response_obj["results"]
    assert [listing["id"] for listing in listings] == expected_ids
    assert response_obj["totalResults"] == expected_total_results
    assert response_obj["totalPages"] == expected_total_pages


@pytest.mark.parametrize(
    "params, message",
    [
        # Domain rule errors (InvalidSearchError): our own wording.
        pytest.param(
            {"minPrice": 500000, "maxPrice": 100000},
            "min_price cannot be greater than max_price",
            id="min_price_above_max_price",
        ),
        pytest.param(
            {"pageSize": 0},
            "page_size must be an integer between 1 and 100",
            id="page_size_zero",
        ),
        pytest.param({"city": " "}, "city must be a non-empty string", id="blank_city"),
        # Request errors (RequestValidationError): "<param>: " is our handler's format;
        # the rest is Pydantic's wording, so only its stable start is checked.
        pytest.param(
            {"minPrice": "abc"},
            "minPrice: Input should be a valid integer",
            id="min_price_not_a_number",
        ),
        pytest.param(
            {"minprice": 1},
            "minprice: Extra inputs are not permitted",
            id="misspelled_parameter",
        ),
    ],
)
def test_search_400(client, params, message):
    response = client.get("/api/listings", params=params)
    assert response.status_code == 400
    response_obj = response.json()
    assert response_obj.keys() == {"detail"}
    assert message in response_obj["detail"]


def test_search_result_shape(client):
    response = client.get("/api/listings")
    assert response.status_code == 200
    response_obj = response.json()
    first = response_obj["results"][0]
    assert first.keys() == {
        "id",
        "source",
        "address",
        "city",
        "state",
        "zip",
        "price",
        "bedrooms",
        "bathrooms",
        "sqft",
        "latitude",
        "longitude",
        "listedDate",
        "status",
        "description",
        "score",
    }
