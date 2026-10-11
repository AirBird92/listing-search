# Listing Search Service

A small full-stack search over property listings ingested from multiple MLS feeds.

- **Backend:** Python, FastAPI
- **Frontend:** React, TypeScript (Vite)

> _How to run, API reference and scoring approach: to be added as the project is built._

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

### Listing identity

**Observation:** `id` is unique per source but not across sources.

**Decision:** a listing's unique key is `(source, id)`. This is also used as the React list key and as the final tie-breaker when sorting.

### Status

**Observation:** listings can be `active`, `pending` or `sold` (A7 is `pending`). The requirements don't say which should be searchable.

**Decision:** status is a filter on the API with a backend default of `active` only. `pending` and `sold` are excluded unless requested. The UI exposes it so the user can widen it.

**Why:** buyers mostly want homes they can still buy, and a pending sale usually can't be. The default lives in the backend so every API client gets the same behaviour, not just this UI.

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

## Future work

- **Cross-feed deduplication.** Group records into one Property containing its source listings, and show one card per home with each feed's price.
  - Match key: location (lat/long) alone isn't enough, because units in the same building share coordinates. Combine it with unit-level fields (sqft, bedrooms, bathrooms). Feeds may geocode slightly differently, so use a distance threshold rather than exact or rounded equality.
  - Open questions: which price and date drive filtering and scoring, how to resolve conflicting fields (e.g. zip), and how to build a stable property ID.
- **Structured attributes from free text.** Extract fields such as `petsAllowed: yes | no | unknown` once, at ingestion time (rules or an LLM), and filter on them. Doing this per search would be slow, costly and non-deterministic. Better still, check whether the MLS feeds already provide a structured pet-policy field.
- **Dependency lock file.** `requirements.txt` pins only the direct dependencies. Add a full lock file (e.g. uv or pip-tools) for fully reproducible installs.

## Clarifying questions

1. Should `pending` and `sold` listings be searchable, and what should the default be? (Assumed: `active` only by default.)
2. Are duplicate listings across feeds expected to be merged? If so, which feed's price and date should win?
3. Should keyword search match whole words or substrings, and match one keyword or several? (Assumed: one case-insensitive substring.)
4. Do the feeds provide structured attributes (e.g. pet policy) that we could filter on instead of the description?
5. Are price filters inclusive (`minPrice <= price <= maxPrice`)?
