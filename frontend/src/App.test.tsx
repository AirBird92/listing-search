import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { searchListings, type SearchResponse } from "./api";
import App from "./App";
import userEvent from "@testing-library/user-event";

vi.mock("./api", () => ({
  searchListings: vi.fn(),
}));

describe("App", () => {
  function buildSearchResponse(
    overrides: Partial<SearchResponse> = {},
  ): SearchResponse {
    return {
      results: [
        {
          id: "1",
          source: "s1",
          address: "123 Main St",
          city: "testville",
          state: "TT",
          zip: "12345",
          price: 12345,
          bedrooms: 1,
          bathrooms: 1,
          sqft: 123,
          latitude: 12,
          longitude: 34,
          listedDate: "2026-01-01",
          status: "active",
          description: "test",
          score: 12.34,
        },
      ],
      page: 1,
      pageSize: 10,
      totalResults: 1,
      totalPages: 1,
      ...overrides,
    };
  }

  it("shows results", async () => {
    vi.mocked(searchListings).mockResolvedValue(buildSearchResponse());
    render(<App />);
    expect(await screen.findByText("123 Main St")).toBeInTheDocument();
  });

  it("shows the error", async () => {
    vi.mocked(searchListings).mockRejectedValue(
      new Error("min_price cannot be greater than max_price"),
    );
    render(<App />);
    expect(
      await screen.findByText("min_price cannot be greater than max_price"),
    ).toBeInTheDocument();
  });

  it("shows no results", async () => {
    vi.mocked(searchListings).mockResolvedValue(
      buildSearchResponse({ results: [], totalResults: 0 }),
    );
    render(<App />);
    expect(
      await screen.findByText("No listings match your filters"),
    ).toBeInTheDocument();
  });

  it("searches on load with no filters", async () => {
    vi.mocked(searchListings).mockResolvedValue(buildSearchResponse());
    render(<App />);
    await screen.findByText("123 Main St");
    expect(searchListings).toHaveBeenCalledWith({ page: 1, pageSize: 10 });
    expect(searchListings).toHaveBeenCalledTimes(1);
  });

  it("next requests page 2", async () => {
    vi.mocked(searchListings).mockResolvedValue(
      buildSearchResponse({ totalPages: 2 }),
    );
    render(<App />);
    await userEvent.click(await screen.findByRole("button", { name: "Next" }));
    expect(searchListings).toHaveBeenLastCalledWith({ page: 2, pageSize: 10 });
    expect(searchListings).toHaveBeenCalledTimes(2);
  });

  it("a new search resets to page 1", async () => {
    vi.mocked(searchListings).mockResolvedValue(
      buildSearchResponse({ totalPages: 2 }),
    );
    render(<App />);
    await userEvent.click(await screen.findByRole("button", { name: "Next" }));
    await userEvent.type(screen.getByLabelText("City"), "Fairfax");
    await userEvent.click(
      await screen.findByRole("button", { name: "Search" }),
    );
    expect(searchListings).toHaveBeenLastCalledWith({
      city: "Fairfax",
      page: 1,
      pageSize: 10,
    });
    expect(searchListings).toHaveBeenCalledTimes(3);
  });
});
