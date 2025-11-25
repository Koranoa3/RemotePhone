import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FILE = "launcher.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_BYTES = 5 * 1024 * 1024  # 5MB
BACKUP_COUNT = 3

_logger_initialized = False

def setup_logger():
    """Initialize the logger for the launcher application."""
    global _logger_initialized
    if _logger_initialized:
        return
    
    # Create logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Remove any existing handlers
    root_logger.handlers.clear()
    
    # Create rotating file handler
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    _logger_initialized = True
    logging.info("Logger initialized successfully")

def get_logger(name):
    """Get a logger instance with the specified name."""
    if not _logger_initialized:
        setup_logger()
    return logging.getLogger(name)
