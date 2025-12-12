"""
Configuration module for KM Master Discrepancy Detection System.
Contains constants and configuration settings
"""
import os
import logging

# ==============================================================
# LOGGING CONFIGURATION (used in utils.py)
# ==============================================================
LOG_FILE_PATH = "logs/km_master_discrepancy_detection.log"
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ==============================================================
# PATH CONFIGURATION
# ==============================================================
MAIN_PATH = os.path.join(os.path.dirname(__file__), "..")
DATA_PATH = os.path.join(MAIN_PATH, "data")
LOGS_PATH = os.path.join(MAIN_PATH, "logs", "km_master_discrepancy_detection.log")
CREDENTIALS_PATH = os.path.join(MAIN_PATH, "credentials.json")
ENV_PATH = os.path.join(MAIN_PATH, ".env")

# ==============================================================
# GOOGLE SHEETS CONFIGURATION
# ==============================================================
UPDATED_WORKSHEET = "Rekomendasi Manual KM Master"

# ==============================================================
# DATA PREPROCESSING CONFIGURATION
# ==============================================================
CTOC_SHEETS_NAME = "Master Kode OP"
CTOC_METHOD_DEFAULT = "complete"
CTOC_DF_OP_NAME = "OP"
CTOC_MASTER_OP_NAME = "Operating Point"
CTOC_MASTER_OP_CODE = "Kode OP"

CSN_SHEETS_NAME = "Master Saintifik Toko"
CSN_DF_OP_CODE = "OP"
CSN_DF_KM_MASTER = "KM Master"
CSN_DF_TOKO_SAINTIFIK = "Toko"
CSN_DF_TOKO_BENAR = CSN_DF_TOKO_SAINTIFIK
CSN_MASTER_OP_CODE = "Kode OP"
CSN_MASTER_KM_MASTER = "KM Master"
CSN_MASTER_TOKO_SAINTIFIK = "Toko Saintifik"
CSN_MASTER_TOKO_BENAR = "Toko Benar"

# ==============================================================
# UTILS CONFIGURATION
# ==============================================================
SYMBOLS_TO_PRESERVE = (',', '.', '%', ' ', '+', '-')
IQR_COLUMN = "KM Deviation (%)"
LOWER_IQR_CONSTANT = 1.5
UPPER_IQR_CONSTANT = 1.5
LOWER_ZOOM_CONSTANT = 10.0
UPPER_ZOOM_CONSTANT = 10.0
HIDE_VALUES = True

