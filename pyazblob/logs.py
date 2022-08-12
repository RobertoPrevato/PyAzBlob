import logging
import logging.handlers
import os
import sys
from datetime import datetime

from essentials.folders import ensure_folder

logger = None


def _configure_file_handler(logger):
    file_logger_enabled = os.environ.get("PYAZBLOB_FILE_LOG") in {"true", "TRUE"}

    if not file_logger_enabled:
        return

    now = datetime.now()
    ts = now.strftime("%Y%m%d")
    ensure_folder(f"logs/{ts}")
    file_handler = logging.handlers.RotatingFileHandler(
        f"logs/{ts}/app.log", maxBytes=24 * 1024 * 1024, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)


def get_app_logger():
    global logger

    if logger is not None:
        return logger

    logger = logging.getLogger("pyazblob")
    logger.setLevel(logging.INFO)
    _configure_file_handler(logger)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    return logger
