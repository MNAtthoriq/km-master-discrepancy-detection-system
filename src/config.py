"""
Configuration module for KM Master Discrepancy Detection System.
Contains constants and configuration settings
"""
import os

# ==============================================================
# LOGGING CONFIGURATION (used in utils.py)
# ==============================================================
LOG_FILE_PATH = "logs/km_master_discrepancy_detection.log"
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# =============================================================
# GOOGLE SHEETS CONFIGURATION (used in google_sheets_io.py)
# ==============================================================
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "..", "credentials.json")