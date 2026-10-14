import type { ListingResult } from "./api";

type ResultsListProps = {
  results: ListingResult[];
};

const priceFormat = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

export function ResultsList({ results }: ResultsListProps) {
  return (
    <ul>
      {results.map((result) => (
        <li key={`${result.source}/${result.id}`}>
          <p>
            {result.address}, {result.city}, {result.state}
          </p>
          <p>Price: {priceFormat.format(result.price)}</p>
          <p>Bedrooms: {result.bedrooms}</p>
          <p>Listed Date: {result.listedDate}</p>
          <p>Relevance Score: {result.score.toFixed(1)}</p>
          <p>Source: {result.source}</p>
        </li>
      ))}
    </ul>
  );
}
