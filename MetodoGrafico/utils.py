from typing import Union


def format_num(value: Union[float, int], decimals: int = 1) -> str:
    """Return a string with ``decimals`` digits for non-integers.

    Integers are returned without decimal part.
    """
    try:
        num = round(float(value), decimals)
    except (TypeError, ValueError):
        return str(value)

    return str(int(num)) if num.is_integer() else f"{num:.{decimals}f}"