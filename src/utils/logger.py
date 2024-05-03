import sys
import logging


def setup_logger(logger_name: str, output_log_file: str) -> logging.Logger:
    """
    Setup a logger with both file and stream handlers.

    Args:
        logger_name (str): The name of the logger.
        output_log_file (str): The filename for the log file.

    Returns:
        logging.Logger: The configured logger object.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Create a file handler for errors, warnings, and critical messages
    file_handler = logging.FileHandler(output_log_file)
    file_handler.setLevel(logging.WARNING)  # Only logs WARNING, ERROR, and CRITICAL messages to the file

    # Create a stream handler (to write to terminal)
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(logging.DEBUG)  # Logs all levels to the terminal

    # Create a logging format
    fmt = logging.Formatter(
        "%(asctime)s [%(name)s/%(filename)s:%(lineno)s]: (%(levelname)s)>>> %(message)s"
    )
    file_handler.setFormatter(fmt)
    stream_handler.setFormatter(fmt)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
