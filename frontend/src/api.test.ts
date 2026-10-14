import { describe, expect, it, vi } from "vitest";
import { searchListings } from "./api";

const EMPTY_RESPONSE = {
  results: [],
  page: 1,
  pageSize: 10,
  totalResults: 0,
  totalPages: 1,
};

describe("api", () => {
  function mockFetch(body: unknown = EMPTY_RESPONSE, status = 200) {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(new Response(JSON.stringify(body), { status }));
    vi.stubGlobal("fetch", fetchMock);
    return fetchMock;
  }

  it("sends only the parameters that are set", async () => {
    const fetchMock = mockFetch();
    await searchListings({
      city: "Fairfax",
      minPrice: 300000,
      keyword: undefined,
    });
    const url = fetchMock.mock.calls[0][0];
    expect(String(url)).toBe(
      "http://localhost:8000/api/listings?city=Fairfax&minPrice=300000",
    );
  });

  it("requests the bare URL when there are no parameters", async () => {
    const fetchMock = mockFetch();
    await searchListings({});
    const url = fetchMock.mock.calls[0][0];
    expect(String(url)).toBe("http://localhost:8000/api/listings");
  });

  it("URL-encodes parameter values", async () => {
    const fetchMock = mockFetch();
    await searchListings({ keyword: "pets allowed" });
    const url = fetchMock.mock.calls[0][0];
    expect(String(url)).toBe(
      "http://localhost:8000/api/listings?keyword=pets+allowed",
    );
  });

  it("returns the parsed response body on success", async () => {
    mockFetch();
    expect(await searchListings({})).toEqual(EMPTY_RESPONSE);
  });

  it("throws the API's detail message on an error response", async () => {
    mockFetch({ detail: "min_price cannot be greater than max_price" }, 400);
    await expect(searchListings({})).rejects.toThrow(
      "min_price cannot be greater than max_price",
    );
  });

  it("falls back to the status code when the error body isn't JSON", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          new Response("Internal Server Error", { status: 500 }),
        ),
    );
    await expect(searchListings({})).rejects.toThrow(
      "Request failed with status 500",
    );
  });

  it("propagates network failures", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new TypeError("Failed to fetch")),
    );
    await expect(searchListings({})).rejects.toThrow("Failed to fetch");
  });
});
