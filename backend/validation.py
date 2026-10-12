def require_non_empty_string(value: object, field_name: str) -> str:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def require_non_negative_int(value: object, field_name: str) -> int:
    return require_int_in_range(value, field_name, min_val=0)


def require_int_in_range(
    value: object,
    field_name: str,
    min_val: int | None = None,
    max_val: int | None = None,
) -> int:
    if type(value) is not int:
        raise ValueError(f"{field_name} must be an integer")
    if (
        min_val is not None
        and max_val is not None
        and (value < min_val or value > max_val)
    ):
        raise ValueError(
            f"{field_name} must be an integer between {min_val} and {max_val}"
        )
    elif min_val is not None and value < min_val:
        raise ValueError(f"{field_name} must be an integer no less than {min_val}")
    elif max_val is not None and value > max_val:
        raise ValueError(f"{field_name} must be an integer no greater than {max_val}")
    return value
