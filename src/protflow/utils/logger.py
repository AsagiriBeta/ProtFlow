"""
Logging configuration for ProtFlow pipeline.
Provides structured logging with color support and file output.
"""
import logging
import sys
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for terminal output."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        """Format the log record with colors."""
        if sys.stderr.isatty():  # Only use colors if outputting to terminal
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    level: str = 'INFO',
    log_file: Optional[Path] = None,
    console: bool = True,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up logging for the ProtFlow pipeline.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        console: Whether to output to console
        format_string: Custom format string for logs

    Returns:
        Configured logger instance
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Get root logger
    logger = logging.getLogger('protflow')
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_formatter = ColoredFormatter(format_string)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file is not None:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_formatter = logging.Formatter(format_string)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = 'protflow') -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (will be prefixed with 'protflow.')

    Returns:
        Logger instance
    """
    if not name.startswith('protflow'):
        name = f'protflow.{name}'
    return logging.getLogger(name)

