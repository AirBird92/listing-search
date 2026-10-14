type PaginationProps = {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
};

export function Pagination({
  page,
  totalPages,
  onPageChange,
}: PaginationProps) {
  function handleClickPrevious() {
    onPageChange(page - 1);
  }

  function handleClickNext() {
    onPageChange(page + 1);
  }

  return (
    <nav className="pagination" aria-label="Pagination">
      <button disabled={page <= 1} onClick={handleClickPrevious}>
        Previous
      </button>
      Page {page} of {totalPages}
      <button disabled={page >= totalPages} onClick={handleClickNext}>
        Next
      </button>
    </nav>
  );
}
