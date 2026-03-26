import logging
import sys


def setup_logger() -> logging.Logger:
    """
    Create a simple console logger.

    We keep it beginner-friendly and avoid external logging dependencies.
    """

    logger = logging.getLogger("weather_orders")
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if the module is imported more than once.
    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

