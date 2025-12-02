"""
Authorize Google Sheets API for KM Master Discrepancy Detection System
"""

import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
    )
logger = logging.getLogger(__name__)

def sheets_loader(sheet_url: str, credentials_path: str=os.path.join(os.path.dirname(__file__), "..", "credentials.json")):
    """
    Authorize Google Sheets API and return worksheet.
    
    Parameters:
    credentials_path (str): Path to credentials.json file
    sheet_url (str): URL of the Google Sheet
    
    Returns:
    gspread.Spreadsheet: Google Sheet
    """
    logger.info(f"Loading Google Sheets from URL: {sheet_url[:30]}...")
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    logger.info("Credentials loaded successfully")

    client = gspread.authorize(creds)
    logger.info("Google Sheets API authorized")

    sheet = client.open_by_url(sheet_url)
    logger.info("Sheet opened successfully")
    
    return sheet

# !notes: add sheets_updater function later

if __name__ == "__main__":
    # back to project root
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    # get environment variables
    load_dotenv(env_path)
    sheets_url = os.getenv("SHEETS_URL")
    # run
    print(sheets_loader(sheets_url))
