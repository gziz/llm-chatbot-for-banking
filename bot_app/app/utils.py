import logging

import colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s: %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )
)

logger = colorlog.getLogger("my_logger")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
