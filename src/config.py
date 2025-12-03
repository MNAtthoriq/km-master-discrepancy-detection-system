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
# GOOGLE SHEETS IO CONFIGURATION
# ==============================================================
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "..", "credentials.json")

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