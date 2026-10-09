"""Small parsing helpers shared by the view and API layers."""


def parse_int(value, default=None):
    """Best-effort conversion of ``value`` to ``int``."""

    try:
        if value in (None, "", "None"):
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def parse_float(value, default=None):
    """Best-effort conversion of ``value`` to ``float``."""

    try:
        if value in (None, "", "None"):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_str(value, default=""):
    """Trim a value into a string, returning ``default`` when empty."""

    if value is None:
        return default
    value = str(value).strip()
    return value or default
