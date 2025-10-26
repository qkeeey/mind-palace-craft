"""
Persistent Logging Configuration for MindPalace
Logs are saved to the 'logs' directory with timestamps for later review
"""

import os
import logging
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

def setup_logger(name: str, log_file: str = None, level=logging.INFO):
    """
    Set up a logger with both file and console handlers.
    
    Args:
        name: Logger name (typically __name__ of the calling module)
        log_file: Optional specific log file name. If None, uses name + timestamp
        level: Logging level (default: INFO)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Generate log filename with timestamp
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{name.replace('.', '_')}_{timestamp}.log"
    
    log_path = LOGS_DIR / log_file
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler (detailed logs)
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    
    # Console handler (simpler output)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log the log file location
    logger.info(f"Logging to file: {log_path}")
    
    return logger


def get_session_log_file(prefix: str = "session"):
    """
    Get a session-specific log file name with timestamp.
    
    Args:
        prefix: Prefix for the log file name
        
    Returns:
        str: Log file name
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.log"


class ProgressLogger:
    """
    Helper class for logging progress of long-running operations.
    """
    
    def __init__(self, logger, total: int, operation: str = "Processing"):
        """
        Initialize progress logger.
        
        Args:
            logger: Logger instance
            total: Total number of items to process
            operation: Description of the operation
        """
        self.logger = logger
        self.total = total
        self.operation = operation
        self.current = 0
        self.start_time = datetime.now()
    
    def update(self, step: int = 1, message: str = None):
        """
        Update progress.
        
        Args:
            step: Number of items completed in this step
            message: Optional custom message
        """
        self.current += step
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        rate = self.current / elapsed if elapsed > 0 else 0
        eta = (self.total - self.current) / rate if rate > 0 else 0
        
        if message:
            log_msg = f"{self.operation}: {self.current}/{self.total} ({percentage:.1f}%) - {message}"
        else:
            log_msg = f"{self.operation}: {self.current}/{self.total} ({percentage:.1f}%)"
        
        if eta > 0:
            log_msg += f" - ETA: {eta:.0f}s"
        
        self.logger.info(log_msg)
    
    def complete(self, message: str = None):
        """
        Mark operation as complete.
        
        Args:
            message: Optional completion message
        """
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        if message:
            log_msg = f"{self.operation} complete: {message} (took {elapsed:.1f}s)"
        else:
            log_msg = f"{self.operation} complete: {self.total} items processed in {elapsed:.1f}s"
        
        self.logger.info(log_msg)


# Example usage and testing
if __name__ == "__main__":
    # Test the logging setup
    logger = setup_logger("test_logger")
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test progress logger
    progress = ProgressLogger(logger, 10, "Testing progress")
    for i in range(10):
        progress.update(message=f"Item {i+1}")
    progress.complete()
    
    print(f"\nLogs saved to: {LOGS_DIR}")
    print("Check the logs directory for the log file.")
