import sys

from loguru import logger

from app.core.config import settings


def setup_logger() -> None:
    if settings.logging.stream.enabled:
        _ = logger.add(
            sink=sys.stdout,
            level=settings.logging.stream.level,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            ),
            colorize=True,
        )

    if settings.logging.common_file.enabled:
        _ = logger.add(
            sink=settings.logging.common_file.path,
            level=settings.logging.common_file.level,
            format=(
                "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
            ),
            rotation=settings.logging.common_file.rotation,
            retention=settings.logging.common_file.retention,
            compression="zip",
            encoding="utf-8",
        )

    if settings.logging.error_file.enabled:
        _ = logger.add(
            sink=settings.logging.error_file.path,
            level=settings.logging.error_file.level,
            format=(
                "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
            ),
            rotation=settings.logging.error_file.rotation,
            retention=settings.logging.error_file.retention,
            compression="zip",
            encoding="utf-8",
            backtrace=True,
            diagnose=True,
        )

    if settings.logging.json_file.enabled:
        _ = logger.add(
            sink=settings.logging.json_file.path,
            level=settings.logging.json_file.level,
            format="{message}",
            rotation=settings.logging.json_file.rotation,
            retention=settings.logging.json_file.retention,
            compression="zip",
            encoding="utf-8",
            serialize=True,
        )

    logger.info("Logging setup completed successfully.")
