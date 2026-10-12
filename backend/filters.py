from dataclasses import dataclass

from validation import require_non_empty_string, require_non_negative_int


class InvalidFilterError(ValueError):
    pass


@dataclass(frozen=True, kw_only=True)
class SearchFilter:
    min_price: int | None = None
    max_price: int | None = None
    min_bedrooms: int | None = None
    city: str | None = None
    keyword: str | None = None

    def __post_init__(self):
        try:
            if self.min_price is not None:
                require_non_negative_int(self.min_price, "min_price")
            if self.max_price is not None:
                require_non_negative_int(self.max_price, "max_price")
            if self.min_bedrooms is not None:
                require_non_negative_int(self.min_bedrooms, "min_bedrooms")
            if self.city is not None:
                require_non_empty_string(self.city, "city")
            if self.keyword is not None:
                require_non_empty_string(self.keyword, "keyword")
        except ValueError as e:
            raise InvalidFilterError(str(e)) from e

        if (
            self.min_price is not None
            and self.max_price is not None
            and self.min_price > self.max_price
        ):
            raise InvalidFilterError("min_price cannot be greater than max_price")
