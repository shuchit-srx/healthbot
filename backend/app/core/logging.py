import logging
import sys


def setup_logging(debug: bool = False) -> None:
    """Configure application-wide logging."""

    level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    """Return a logger for the requested module."""

    return logging.getLogger(name)