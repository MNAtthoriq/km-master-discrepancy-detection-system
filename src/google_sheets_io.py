"""
Authorize Google Sheets API for KM Master Discrepancy Detection System
"""

import gspread
from google.oauth2.service_account import Credentials
import config
import logging

# set up logging
logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT) # get override from utils.py later (force=True)
logger = logging.getLogger(__name__)

def sheets_loader(sheets_url:str, credentials_path:str = config.CREDENTIALS_PATH) -> gspread.Spreadsheet:
    """
    Authorize Google Sheets API and return worksheet.
    
    Parameters:
    -----------
    sheets_url: str
        URL of the Google Sheet.
    credentials_path: str
        Path to credentials.json file.
    
    Returns:
    --------
    gspread.Spreadsheet
        Authorized Google Sheets Spreadsheet object.
    """
    logger.info(f"Loading Google Sheets from URL: {sheets_url[:30]} [Redacted]...") # for privacy, only show part of the URL
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    logger.info("Credentials loaded successfully")

    client = gspread.authorize(creds)
    logger.info("Google Sheets API authorized")

    sheets = client.open_by_url(sheets_url)
    logger.info("Sheet opened successfully")
    
    return sheets

# !notes: add sheets_updater function later

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    # get environment variables
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(env_path)
    sheets_url = os.getenv("SHEETS_URL")

    # run
    print(sheets_loader(sheets_url))
