from typing import Any


def is_valid_text(value: Any) -> bool:
    """Return True if value is a non-empty string."""
    return isinstance(value, str) and bool(value.strip())


def format_prompt(template: str, **kwargs) -> str:
    """Safely format a prompt using the supplied variables."""
    if not is_valid_text(template):
        raise ValueError("Prompt template cannot be empty.")

    try:
        return template.format(**kwargs)

    except KeyError as e:
        raise ValueError(
            f"Missing prompt variable: {e.args[0]}"
        ) from e

    except Exception as e:
        raise ValueError(
            f"Prompt formatting failed: {e}"
        ) from e