import logging
import sys


def is_dev_env(env: str) -> bool:
    return env.lower() in {"dev", "development"}


def setup_logging(env: str, configured_level: str) -> str:
    is_dev = is_dev_env(env)
    fallback_level = "DEBUG" if is_dev else "INFO"
    selected_level = (configured_level or fallback_level).upper()
    log_level = getattr(logging, selected_level, logging.INFO)

    log_format = (
        "%(asctime)s | %(levelname)s | course-service | %(name)s | %(message)s"
        if is_dev
        else "%(asctime)s | %(levelname)s | %(message)s"
    )

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    noisy_level = logging.INFO if is_dev else logging.WARNING
    logging.getLogger("uvicorn.access").setLevel(noisy_level)
    logging.getLogger("sqlalchemy.engine").setLevel(noisy_level)

    return selected_level
