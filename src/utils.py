"""
Utility functions for KM Master Discrepancy Detection System
Contains setup logging and repetitive helper functions for analysis and visualization
"""

import logging
import config

# setup logging
logger = logging.getLogger(__name__)

def setup_logging(log_file_path: str=None, log_level: int=config.LOG_LEVEL,
                  log_format: str=config.LOG_FORMAT, log_date_format: str=config.LOG_DATE_FORMAT) -> None:
    """
    Setup logging configuration.

    Parameters:
    -----------
    log_file_path : str, optional
        Path to the log file. If None, logs will only be printed to console.
    log_level : int
        Logging level.
    log_format : str
        Format of the log messages.
    log_date_format : str
        Format of the date in log messages.
    """
    # configure logging
    handlers = [logging.StreamHandler()] # console handler

    if log_file_path: # if log file path is provided
        import os
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True) # create directory if not exists
        handlers.append(logging.FileHandler(log_file_path)) # add file handler
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=log_date_format,
        handlers=handlers,
        force=True) # force=True to override any existing logging configuration
