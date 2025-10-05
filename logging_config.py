import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(log_folder_path=None, log_level=logging.DEBUG):
    """
    Set up logging with rotation for the entire application.
    
    Args:
        log_folder_path: Path to log folder (defaults to LOG_FOLDER_PATH env var)
        log_level: Logging level (default: DEBUG)
    """
    # Get log directory from parameter or environment variable
    log_dir = log_folder_path or os.getenv("LOG_FOLDER_PATH")
    
    if not log_dir:
        raise ValueError("LOG_FOLDER_PATH must be set or provided as parameter")
    
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "tennis.log")
    
    # Create the rotating file handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=3,
        encoding='utf-8'
    )
    
    # Create console handler (optional but recommended)
    console_handler = logging.StreamHandler()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set formatter for both handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove any existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger