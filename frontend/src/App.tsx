import { useEffect, useState } from "react";
import { searchListings, type SearchParams, type SearchResponse } from "./api";
import { SearchForm } from "./SearchForm";
import { ResultsList } from "./ResultsList";
import { Pagination } from "./Pagination";

function App() {
  const [query, setQuery] = useState<SearchParams>({});
  const [page, setPage] = useState(1);
  const [data, setData] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const response = await searchListings({ ...query, page });
        if (!ignore) setData(response);
      } catch (err) {
        if (!ignore) setError(err instanceof Error ? err.message : String(err));
      } finally {
        if (!ignore) setLoading(false);
      }
    }
    load();
    return () => {
      ignore = true;
    };
  }, [query, page]);

  function handleSearch(params: SearchParams) {
    setQuery(params);
    setPage(1);
  }

  function renderResults() {
    if (error) return <p>{error}</p>;
    if (!data) return <p>Loading...</p>;
    if (data.results.length === 0) return <p>No listings match your filters</p>;
    return (
      <>
        <p>{data.totalResults} listings found</p>
        <ResultsList results={data.results} />
        <Pagination
          page={data.page}
          totalPages={data.totalPages}
          onPageChange={setPage}
        />
      </>
    );
  }

  return (
    <>
      <SearchForm onSearch={handleSearch} />
      {loading && data && <p>Loading...</p>}
      {renderResults()}
    </>
  );
}

export default App;
