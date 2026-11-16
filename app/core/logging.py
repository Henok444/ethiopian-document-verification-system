import logging
import sys


def setup_logging():
    """Sets up unified, formatted logging for the application."""
    log_format = "%(asctime)s | %(levelname)-7s | %(name)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Silence overly verbose external loggers if needed
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("PIL").setLevel(logging.WARNING)


logger = logging.getLogger("ethiopian_doc_verification")
