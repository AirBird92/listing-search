import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { SearchForm } from "./SearchForm";

describe("SearchForm", () => {
  it("sends no parameters when every field is empty", async () => {
    const onSearch = vi.fn();
    render(<SearchForm onSearch={onSearch} />);
    await userEvent.click(screen.getByRole("button", { name: "Search" }));

    expect(onSearch).toHaveBeenCalledWith({});
  });

  it("sends only the fields that are filled in", async () => {
    const onSearch = vi.fn();
    render(<SearchForm onSearch={onSearch} />);
    await userEvent.type(screen.getByLabelText("City"), "Fairfax");
    await userEvent.click(screen.getByRole("button", { name: "Search" }));

    expect(onSearch).toHaveBeenCalledWith({ city: "Fairfax" });
  });

  it("converts number fields to numbers", async () => {
    const onSearch = vi.fn();
    render(<SearchForm onSearch={onSearch} />);
    await userEvent.type(screen.getByLabelText("Minimum Price"), "300000");
    await userEvent.type(screen.getByLabelText("City"), "Fairfax");
    await userEvent.click(screen.getByRole("button", { name: "Search" }));

    expect(onSearch).toHaveBeenCalledWith({
      minPrice: 300000,
      city: "Fairfax",
    });
  });

  it("sends every field with its own value", async () => {
    // Distinct values per field, so a field wired to the wrong input would fail.
    const onSearch = vi.fn();
    render(<SearchForm onSearch={onSearch} />);
    await userEvent.type(screen.getByLabelText("Minimum Price"), "200000");
    await userEvent.type(screen.getByLabelText("Maximum Price"), "500000");
    await userEvent.type(screen.getByLabelText("Minimum Bedrooms"), "3");
    await userEvent.type(screen.getByLabelText("City"), "Fairfax");
    await userEvent.type(screen.getByLabelText("Keyword"), "pets");
    await userEvent.type(screen.getByLabelText("Target Budget"), "400000");
    await userEvent.click(screen.getByRole("button", { name: "Search" }));

    expect(onSearch).toHaveBeenCalledWith({
      minPrice: 200000,
      maxPrice: 500000,
      minBedrooms: 3,
      city: "Fairfax",
      keyword: "pets",
      targetBudget: 400000,
    });
  });

  it("trims text fields", async () => {
    const onSearch = vi.fn();
    render(<SearchForm onSearch={onSearch} />);
    await userEvent.type(screen.getByLabelText("City"), "  Fairfax  ");
    await userEvent.click(screen.getByRole("button", { name: "Search" }));

    expect(onSearch).toHaveBeenCalledWith({ city: "Fairfax" });
  });

  it("leaves out whitespace-only text fields", async () => {
    const onSearch = vi.fn();
    render(<SearchForm onSearch={onSearch} />);
    await userEvent.type(screen.getByLabelText("City"), "   ");
    await userEvent.type(screen.getByLabelText("Keyword"), "   ");
    await userEvent.click(screen.getByRole("button", { name: "Search" }));

    expect(onSearch).toHaveBeenCalledWith({});
  });

  it("clears every field on Reset", async () => {
    render(<SearchForm onSearch={vi.fn()} />);
    await userEvent.type(screen.getByLabelText("Minimum Price"), "300000");
    await userEvent.type(screen.getByLabelText("City"), "Fairfax");
    await userEvent.click(screen.getByRole("button", { name: "Reset" }));

    expect(screen.getByLabelText("Minimum Price")).toHaveValue(null); //toHaveValue reports an empty number input as null
    expect(screen.getByLabelText("City")).toHaveValue("");
  });
});
