"""
Authorize Google Sheets API for KM Master Discrepancy Detection System
"""

from utils import mask_numeric_value
import config
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import logging

# set up logging
logging.basicConfig(
    level=config.LOG_LEVEL, format=config.LOG_FORMAT
) # get override from utils.py later (force=True)
logger = logging.getLogger(__name__)

def sheets_loader(
    sheets_url:str, credentials_path:str = config.CREDENTIALS_PATH,
    hide_values:bool = config.HIDE_VALUES
) -> gspread.Spreadsheet:
    """
    Authorize Google Sheets API and return worksheet.
    
    Parameters:
    -----------
    sheets_url: str
        URL of the Google Sheet.
    credentials_path: str
        Path to credentials.json file.
    hide_values : bool
        Whether to hide numeric values in logs.
    
    Returns:
    --------
    gspread.Spreadsheet
        Authorized Google Sheets Spreadsheet object.
    """
    # hide values if configured
    if hide_values:
        logger.info(f"Loading Google Sheets from URL: {sheets_url[:30]} [Redacted]...") # for privacy, only show part of the URL
    else:
        logger.info(f"Loading Google Sheets from URL: {sheets_url} ...") 
    
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    logger.info("Credentials loaded successfully")

    client = gspread.authorize(creds)
    logger.info("Google Sheets API authorized")

    sheets = client.open_by_url(sheets_url)
    logger.info("Sheet opened successfully")
    
    return sheets

def sheets_updater(
    sheets_url:str, df:pd.DataFrame, 
    worksheet:str = config.UPDATED_WORKSHEET, 
    credentials_path:str = config.CREDENTIALS_PATH,
    hide_values:bool = config.HIDE_VALUES
) -> None:
    """
    Authorize Google Sheets API with edit access and return worksheet.
    
    Parameters:
    -----------
    sheets_url: str
        URL of the Google Sheet.
    worksheet: str
        Name of the worksheet to access.
    credentials_path: str
        Path to credentials.json file.
    hide_values : bool
        Whether to hide numeric values in logs.
    """
    # hide values if configured
    if hide_values:
        logger.info(f"Loading Google Sheets for update from URL: {sheets_url[:30]} [Redacted]...") # for privacy, only show part of the URL
    else:
        logger.info(f"Loading Google Sheets for update from URL: {sheets_url} ...") 
    
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    logger.info("Credentials loaded successfully")

    client = gspread.authorize(creds)
    logger.info("Google Sheets API authorized with edit access")

    sheets = client.open_by_url(sheets_url)
    logger.info("Sheet opened successfully")

    sheets = sheets.worksheet(worksheet)
    logger.info(f"Worksheet '{worksheet}' accessed successfully")

    sheets.update([df.columns.values.tolist()] + df.values.tolist())

    logger.info(f"Update {mask_numeric_value(f'{len(df):,}')} rows to worksheet '{worksheet}'.")

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    # get environment variables
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(env_path)
    sheets_url = os.getenv("SHEETS_URL")

    # run
    print(sheets_loader(sheets_url))
