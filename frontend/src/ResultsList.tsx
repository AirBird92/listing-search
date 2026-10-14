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
    <>
      <div className="listing header">
        <p>Address</p>
        <p>Price</p>
        <p>Bedrooms</p>
        <p>Listed Date</p>
        <p>Relevance Score</p>
        <p>Source</p>
      </div>
      <ul className="results">
        {results.map((result) => (
          <li className="listing" key={`${result.source}/${result.id}`}>
            <div>
              <p>{result.address}</p>
              <p>
                {result.city}, {result.state} {result.zip}
              </p>
            </div>
            <p>{priceFormat.format(result.price)}</p>
            <p>{result.bedrooms}</p>
            <p>{result.listedDate}</p>
            <p>{result.score.toFixed(1)}</p>
            <p>{result.source}</p>
          </li>
        ))}
      </ul>
    </>
  );
}
