# Listing Search Service

A small full-stack search over property listings ingested from multiple MLS feeds.

- **Backend:** Python, FastAPI
- **Frontend:** React, TypeScript (Vite)

> _API reference and frontend setup: to be added as the project is built._

## Running the backend tests

Run all backend commands from `backend/`: pytest and Ruff read their configuration (`pytest.ini`, `ruff.toml`) from there.

```
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows; on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest                          # tests
ruff check .                    # lint
ruff format .                   # format
```

## Data observations & decisions

Notes from reviewing `backend/sample_listings.json` (12 listings, 2 feeds) before writing any logic.

### Duplicate listings across feeds

**Observation:** the same property often appears in both feeds. 12 records describe only 8 distinct homes:

| Property         | MLS_A           | MLS_B            |
| ---------------- | --------------- | ---------------- |
| 123 Main St, 4B  | A1 · $450,000   | B7 · $452,000    |
| 456 Oak Ave      | A2 · $525,000   | B8 · $527,500    |
| 789 Pine Rd      | A3 · $399,000   | B9 · $399,500    |
| 55 Elm Ct        | A5 · $470,000   | B11 · $465,000   |

Within each pair, the address formatting ("St" / "Street", "Apt" / "Unit"), price and `listedDate` differ. For 456 Oak the zip code differs too (22150 / 22151).

**Decision:** don't deduplicate. Every record is shown as its own result, and each result displays its `source` so users can see when two results come from different feeds.

**Why:** dedup isn't in the requirements, and it raises several open questions (see [Future work](#future-work)) that would delay the core features. The search pipeline is built as separate steps (filter → score → sort → paginate) so a dedupe step can be added later without a rewrite.

### Required fields and invalid records

**Observation:** the spec doesn't say which fields may be missing. The sample data is complete.

**Decision:** every field is required. A record with a missing field, an unparseable value or an unknown status fails loading with a clear error that names the listing (`source/id`). Empty strings are treated as missing (e.g. an empty `city` would never match a city search). Prices are truncated to whole dollars.

**Why:** the data is loaded once at startup, so failing loudly surfaces bad data immediately instead of serving wrong results. With real feeds, fields not used by any feature (e.g. `sqft`, `latitude`) could become optional (`None` = unknown, never a fake default like `0`), and bad records could be skipped and logged instead of failing the whole load.

### Listing identity

**Observation:** `id` is unique per source but not across sources.

**Decision:** a listing's unique key is `(source, id)`. This is also used as the React list key and as the final tie-breaker when sorting (see [Ranking and ties](#ranking-and-ties)).

### Status

**Observation:** listings can be `active`, `pending` or `sold` (A7 is `pending`). The requirements don't say which should be searchable.

**Decision:** search returns `active` listings only. `pending` and `sold` listings are always excluded, and there is no status filter.

**Why:** buyers mostly want homes they can still buy, and a pending sale usually can't be. A user-facing status filter isn't in the requirements; it would be a small addition (an optional filter defaulting to `active`), and the rule lives in the backend so every API client gets the same behaviour.

### Keyword search vs. meaning

**Observation:** a plain keyword match on the description often gives the wrong answer. For the keyword `pets` (case-insensitive):

| Listing | Description fragment     | Matches "pets"? | Pet-friendly? |
| ------- | ------------------------ | --------------- | ------------- |
| A1      | "Pet friendly"           | no              | yes (missed)  |
| B7      | "Pets allowed"           | yes             | yes           |
| A3      | "no pets"                | yes             | no (wrong)    |
| B9      | "pets not permitted"     | yes             | no (wrong)    |
| A4      | "Pets welcome"           | yes             | yes           |
| A5      | "No pets"                | yes             | no (wrong)    |
| B11     | "Pet restrictions apply" | no              | unclear       |
| A6      | "pets allowed"           | yes             | yes           |
| A7      | "no pets due to HOA"     | yes             | no (wrong)    |

4 of the 7 matches mean the opposite of what the user wants, and the clearest pet-friendly listing (A1) is missed.

**Decision:** implement the keyword search as specified: a case-insensitive **substring** match against `description`. Document the limitation; don't try to interpret negation.

**Why:** the spec asks for free-text keyword matching. A substring match is simple and catches word variants (`pet` matches "pets"), at the cost of occasional false positives (`pet` also matches "car**pet**"). Interpreting meaning properly calls for structured data (see [Future work](#future-work)), not a cleverer string match.

### City matching

**Observation:** city names are consistent in this sample, but the spec warns that city/state/zip "may contain minor inconsistencies between sources" (e.g. case, surrounding whitespace).

**Decision:** compare cities case-insensitively after trimming whitespace, on both the stored value and the user's input.

**Why:** users shouldn't have to guess the exact spelling a feed used.

### Recency and "today"

**Observation:** recency scoring depends on the current date. If the scoring function read the system clock itself, the expected scores in tests would change every day.

**Decision:** the scoring function takes `today` as a parameter. Tests pass a fixed date. The API passes the real date.

**Why:** a pure function is predictable and needs no mocking. This is the same idea as injecting a `Clock` in Java.

## Scoring

Results are ranked by a relevance score from 0 to 100, combining how well the price fits the user's `targetBudget` with how recently the listing went live.

```
score = 100 × (W_BUDGET × budget_fit + W_RECENCY × recency)      if targetBudget is given
score = 100 × recency                                             otherwise
```

| Constant          | Value   | Meaning                                       |
| ----------------- | ------- | --------------------------------------------- |
| `W_BUDGET`        | 0.7     | Weight of budget fit                          |
| `W_RECENCY`       | 0.3     | Weight of recency                             |
| `UNDER_TOLERANCE` | 0.50    | Budget fit reaches 0 at 50% **under** budget  |
| `OVER_TOLERANCE`  | 0.25    | Budget fit reaches 0 at 25% **over** budget   |
| `HALF_LIFE_DAYS`  | 60      | Recency halves every 60 days                  |

### Budget fit (0–1)

Uses the signed relative distance from the budget, so a $50k gap matters more on a $200k budget than on a $2M one:

```
d = (price − targetBudget) / targetBudget          negative = under, positive = over

budget_fit = max(0, 1 − |d| / UNDER_TOLERANCE)    if d <= 0
budget_fit = max(0, 1 −  d  / OVER_TOLERANCE)     if d > 0
```

Going over budget is penalised twice as fast as coming in under it: most buyers can't stretch upward, but are happy to pay less. Example for a $300k budget:

| Price      | $200k | $270k | $300k | $330k | $450k |
| ---------- | ----- | ----- | ----- | ----- | ----- |
| budget_fit | 0.33  | 0.80  | 1.00  | 0.60  | 0.00  |

### Recency (0–1)

Exponential decay with a half-life:

```
age_days = max(0, today − listedDate)
recency  = 0.5 ^ (age_days / HALF_LIFE_DAYS)
```

A new listing scores 1.0, a 60-day-old one 0.5 and a 120-day-old one 0.25. It never reaches 0, so older listings still rank among themselves. A listing dated in the future (bad data) is treated as listed today rather than scoring above 1.

### Why these choices

- **Price outweighs recency (0.7 / 0.3).** Price is what decides whether a buyer can act on a listing at all. Recency is a tie-breaker between similar fits: newer listings are less likely to be under offer.
- **A 60-day half-life.** Assumption: a listing being on the market for one to two months is normal, so a 76-day-old listing that fits the budget well should still rank high. A 30-day half-life would push everything older than two months below 0.25.
- **No budget means recency only,** rather than treating budget fit as 0 or 1. Either constant would shift every score equally without adding information.
- **Scores are relative within one search.** A 60 with a budget and a 60 without one are not comparable, and they don't need to be.
- **`targetBudget` must be a positive integer if provided.** It is omitted (`None`) to mean "no budget"; `0` would divide by zero and negative values are meaningless, so both are rejected as invalid input.
- **Scores are not rounded during ranking,** only for display, to avoid creating artificial ties.
- **`targetBudget` ranks but never filters.** Listings far outside the budget still appear, with a low score, unless the user also sets `maxPrice`; excluding them is what the price filters are for. For example, every sample listing is at least 33% over a $300k budget, beyond `OVER_TOLERANCE`, so all of them get a budget fit of 0. Their scores then come from recency alone (`30 × recency`, roughly 15–20) and they are ordered newest first. With a $450k budget, the same data ranks as expected: A1 ($450k) scores 88 and B7 ($452k) 86.

## Search pipeline

A search runs four steps, each a small, separately tested function:

```
SearchRequest (validated) → filter_listings → rank → paginate → Page
```

| Module          | Responsibility                                                          |
| --------------- | ----------------------------------------------------------------------- |
| `models.py`     | `Listing` and `Status`: immutable (frozen) data                         |
| `loader.py`     | Reads and validates the JSON feed file once, at startup                 |
| `validation.py` | Shared field checks (non-empty string, integer in range)                |
| `filters.py`    | `SearchFilter` and `filter_listings`                                    |
| `scoring.py`    | The relevance score for one listing                                    |
| `ranking.py`    | Scores many listings and sorts them, including tie-breaking             |
| `pagination.py` | `Page` and `paginate`                                                   |
| `search.py`     | `SearchRequest` and `search()`, which runs the steps above              |
| `errors.py`     | `InvalidSearchError`: every kind of invalid user input raises this type |

**Validate at the boundary, trust inside.** All user input is checked once, when a `SearchFilter` or `SearchRequest` is created; an invalid object cannot exist. The functions after that assume valid input. Every validation failure raises `InvalidSearchError`, so the API can turn exactly that type into a 400 response without catching unrelated errors (which are bugs, and should be 500s).

**Pure and deterministic.** `listings` and `today` are passed in, never read from a file or the system clock inside the pipeline, so the same request always gives the same result and tests need no mocking.

### Filters

| Filter        | Rule                                                                 |
| ------------- | -------------------------------------------------------------------- |
| `minPrice`    | `price >= minPrice` (inclusive). Non-negative integer.               |
| `maxPrice`    | `price <= maxPrice` (inclusive). Non-negative integer, `>= minPrice`. `minPrice == maxPrice` means an exact price. |
| `minBedrooms` | `bedrooms >= minBedrooms` (inclusive). Non-negative integer.          |
| `city`        | Equal after trimming and casefolding both sides; not a partial match (`"Test"` doesn't match `"Testville"`). |
| `keyword`     | Case-insensitive substring of `description` (see [Keyword search](#keyword-search-vs-meaning)). |

An omitted filter means "no filter". A filter that is present but blank (`""` or whitespace) is rejected rather than ignored, so the frontend must leave empty fields out of the request. Only `active` listings are ever returned. Filtering runs before scoring, so excluded listings are never scored.

### Ranking and ties

Results are sorted by:

1. score, highest first
2. listed date, newest first
3. `source`, then `id`, ascending

The last step makes the order unique and fully deterministic, which is what makes stateless pagination consistent (see below). It means exact ties prefer `MLS_A` over `MLS_B`. That preference is explicit rather than hidden in input order, and exact ties on both score and date are rare; a stable hash of `source/id` would remove it if it mattered.

### Pagination

- Pages are 1-based. `page >= 1`; `pageSize` is between 1 and 100 (default 10).
- A page beyond the last one returns no items with accurate totals, not an error, because results can change between requests. The UI uses `totalPages` to disable "Next", so users don't normally reach it.
- Zero results is reported as page 1 of 1 with no items. A city (or any filter) with no matches is an empty result, not an error.
- **No server-side state or cache is needed for "next page".** Every request reruns the same deterministic pipeline, so page 2 is exactly the next slice of the ranking page 1 came from. The exceptions are data changing between requests and the date changing at midnight (recency shifts slightly); cursor pagination would address both (see [Future work](#future-work)).

## Future work

- **Cross-feed deduplication.** Group records into one Property containing its source listings, and show one card per home with each feed's price.
  - Match key: location (lat/long) alone isn't enough, because units in the same building share coordinates. Combine it with unit-level fields (sqft, bedrooms, bathrooms). Feeds may geocode slightly differently, so use a distance threshold rather than exact or rounded equality.
  - Open questions: which price and date drive filtering and scoring, how to resolve conflicting fields (e.g. zip), and how to build a stable property ID.
- **Structured attributes from free text.** Extract fields such as `petsAllowed: yes | no | unknown` once, at ingestion time (rules or an LLM), and filter on them. Doing this per search would be slow, costly and non-deterministic. Better still, check whether the MLS feeds already provide a structured pet-policy field.
- **Scaling.** The current design keeps all listings in memory and, per request, scans every listing, scores the matches, fully sorts them and slices out one page. That is the right trade-off for a small fixed dataset; at millions of listings:
  - **Filtering:** move listings into a database with indexes on price, bedrooms and city, and use a full-text index (e.g. PostgreSQL full-text search or Elasticsearch/OpenSearch) for keywords instead of a substring scan of every description.
  - **Precompute what doesn't depend on the request.** Normalised city and description (trimmed, casefolded) are the same for every search, so they can be computed once at ingestion and stored alongside the originals, which are kept for display. The score cannot be precomputed: it depends on the user's `targetBudget` and on today's date.
  - **Top-k instead of a full sort.** A page needs only the best `page × pageSize` results; `heapq.nlargest` finds them in O(m log k) instead of sorting all m matches in O(m log m). The benefit shrinks for deep pages.
  - **Cursor (keyset) pagination.** Because the sort key (score, listed date, source, id) is unique and deterministic, the API can return a cursor ("continue after this key") instead of a page number. Results stay stable when listings change between requests, and deep pages cost the same as early ones.
  - **Caching.** If ranking became expensive, the ranked list could be cached per (filters, budget, day) and pages sliced from it. `SearchFilter` is frozen and therefore hashable, so it can be part of the cache key. Not worth the memory and invalidation complexity at this size.
- **Dependency lock file.** `requirements.txt` pins only the direct dependencies. Add a full lock file (e.g. uv or pip-tools) for fully reproducible installs.

## Clarifying questions

1. Should `pending` and `sold` listings be searchable, and what should the default be? (Assumed: `active` only, not user-configurable.)
2. Are duplicate listings across feeds expected to be merged? If so, which feed's price and date should win?
3. Should keyword search match whole words or substrings, and match one keyword or several? (Assumed: one case-insensitive substring.)
4. Do the feeds provide structured attributes (e.g. pet policy) that we could filter on instead of the description?
5. Are price filters inclusive (`minPrice <= price <= maxPrice`)?
6. Which fields can feeds omit, and should one bad record fail the whole load or be skipped? (Assumed: all fields required; fail loudly.)
7. Is there a known weighting between price fit and recency, or a typical days-on-market figure for these markets? (Assumed: 70/30, and one to two months on market is normal.)
8. Should listings far outside `targetBudget` be hidden, or only ranked lower? (Assumed: ranked lower; `maxPrice` is the way to exclude them.)
