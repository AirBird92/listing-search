export type ListingResult = {
  id: string;
  source: string;
  address: string;
  city: string;
  state: string;
  zip: string;
  price: number;
  bedrooms: number;
  bathrooms: number;
  sqft: number;
  latitude: number;
  longitude: number;
  listedDate: string;
  status: string;
  description: string;
  score: number;
};

export type SearchResponse = {
  results: ListingResult[];
  page: number;
  pageSize: number;
  totalResults: number;
  totalPages: number;
};

export type SearchParams = {
  minPrice?: number;
  maxPrice?: number;
  minBedrooms?: number;
  city?: string;
  keyword?: string;
  targetBudget?: number;
  page?: number;
  pageSize?: number;
};

const BASE_URL = "http://localhost:8000";
const LISTING_API = "/api/listings";

export async function searchListings(
  params: SearchParams,
): Promise<SearchResponse> {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) {
      query.append(key, String(value));
    }
  }

  const url = new URL(`${BASE_URL}${LISTING_API}`);
  url.search = query.toString();
  const response = await fetch(url);

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") {
        message = body.detail;
      }
    } catch {
      // body wasn't JSON: keep the fallback message
    }
    throw new Error(message);
  }
  return response.json();
}
