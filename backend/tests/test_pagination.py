from dataclasses import replace

import pytest

from pagination import paginate
from ranking import ScoredListing


def _build_listings(valid_listing, size):
    # Ids "0", "1", ... so each page's contents are easy to read; score is irrelevant here.
    return [
        ScoredListing(listing=replace(valid_listing, id=str(i)), score=0.0)
        for i in range(size)
    ]


@pytest.mark.parametrize(
    "size, page, page_size, expected_ids",
    [
        # expected_ids is a range of the ids on the page; range(0) means an empty page.
        pytest.param(25, 1, 10, range(10), id="first_page"),
        pytest.param(25, 2, 10, range(10, 20), id="middle_page"),
        pytest.param(25, 3, 10, range(20, 25), id="last_partial_page"),
        pytest.param(25, 4, 10, range(0), id="past_the_end_is_empty"),
        pytest.param(20, 2, 10, range(10, 20), id="exactly_full_last_page"),
        pytest.param(20, 3, 10, range(0), id="after_exactly_full_last_page_is_empty"),
        pytest.param(5, 1, 10, range(5), id="page_size_larger_than_total"),
        pytest.param(3, 2, 1, range(1, 2), id="page_size_one"),
        pytest.param(0, 1, 10, range(0), id="no_results"),
        pytest.param(0, 2, 10, range(0), id="no_results_past_the_end"),
    ],
)
def test_paginate_items(valid_listing, size, page, page_size, expected_ids):
    result = paginate(_build_listings(valid_listing, size), page, page_size)
    assert [s.listing.id for s in result.items] == [str(i) for i in expected_ids]


@pytest.mark.parametrize(
    "size, expected_total_pages",
    [
        pytest.param(0, 1, id="no_results_is_one_page"),
        pytest.param(1, 1, id="one_result"),
        pytest.param(10, 1, id="exactly_one_page"),
        pytest.param(11, 2, id="one_over"),
        pytest.param(20, 2, id="exactly_two_pages"),
        pytest.param(21, 3, id="one_over_two_pages"),
    ],
)
def test_paginate_total_pages(valid_listing, size, expected_total_pages):
    result = paginate(_build_listings(valid_listing, size), 1, 10)
    assert result.total_pages == expected_total_pages


def test_paginate_metadata(valid_listing):
    # A page past the end still reports accurate totals and echoes the request.
    result = paginate(_build_listings(valid_listing, 25), 4, 10)
    assert result.page == 4
    assert result.page_size == 10
    assert result.total_results == 25
    assert result.total_pages == 3


def test_paginate_items_is_a_tuple(valid_listing):
    result = paginate(_build_listings(valid_listing, 3), 1, 10)
    assert isinstance(result.items, tuple)
