import logging

# Configure the logger once
logger2 = logging.getLogger(__name__)
logger2.setLevel(logging.INFO)

if not logger2.handlers:  # Prevent duplicate handlers
    # Create and configure handler and formatter
    handler2 = logging.FileHandler(f"{__name__}", mode="a")
    formatter2 = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler2.setFormatter(formatter2)
    logger2.addHandler(handler2)


def log_format(level, message):
    if level == "info":
        logger2.info(message)
    elif level == "warning":
        logger2.warning(message)
    elif level == "error":
        logger2.error(message)
    elif level == "critical":
        logger2.critical(message)
        