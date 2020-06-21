import logging
import logging.handlers
from datetime import datetime
from essentials.folders import ensure_folder


logger = None


def get_app_logger():
    global logger

    if logger is not None:
        return logger

    logger = logging.getLogger("app")

    logger.setLevel(logging.INFO)

    max_bytes = 24 * 1024 * 1024

    file_handler = logging.handlers.RotatingFileHandler

    now = datetime.now()
    ts = now.strftime("%Y%m%d")

    ensure_folder(f"logs/{ts}")

    file_handler = file_handler(f"logs/{ts}/app.log", maxBytes=max_bytes, backupCount=5)

    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(file_handler)
    logger.addHandler(logging.StreamHandler())

    return logger
