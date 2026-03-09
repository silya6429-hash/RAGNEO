from loguru import logger
from pathlib import Path
from .config import config
import sys


def setup_logger():
    """
    Настройка логирования
    """

    config.LOG_DIR.mkdir(parents=True, exist_ok=True)

    log_file = Path(config.LOG_DIR) / "rag_system.log"

    logger.remove()

    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time}</green> | <level>{level}</level> | <cyan>{name}</cyan> | {message}"
    )

    logger.add(
        log_file,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        level="DEBUG"
    )


setup_logger()