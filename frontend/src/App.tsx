import { useEffect, useState } from "react";
import { searchListings, type SearchParams, type SearchResponse } from "./api";
import { SearchForm } from "./SearchForm";

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
        if (!ignore) setData(response)
      } catch (err) {
        if (!ignore) setError(err instanceof Error ? err.message : String(err))
      } finally {
        if (!ignore) setLoading(false)
      }
    }
    load();
    return () => { ignore = true; };
  }, [query, page]);

  function handleSearch(params: SearchParams) {
    setQuery(params);
    setPage(1);
  }

  return (
    <>
      <SearchForm onSearch={handleSearch} />
      <p>Query: {JSON.stringify(query)}</p>
      <p>Page: {page}</p>
      <p>Data: {JSON.stringify(data)}</p>
      <p>Loading: {JSON.stringify(loading)}</p>
      <p>Error: {JSON.stringify(error)}</p>
    </>
  );
}

export default App;
