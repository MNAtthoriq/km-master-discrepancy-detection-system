"""
Authorize Google Sheets API for KM Master Discrepancy Detection System
"""

import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

def sheets_loader(sheet_url: str, credentials_path: str=os.path.join(os.path.dirname(__file__), "..", "credentials.json")):
    """
    Authorize Google Sheets API and return worksheet.
    
    Parameters:
    credentials_path (str): Path to credentials.json file
    sheet_url (str): URL of the Google Sheet
    
    Returns:
    gspread.Worksheet: Authorized worksheet object
    """
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(sheet_url)
    
    return sheet

if __name__ == "__main__":
    # back to project root
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    # get environment variables
    load_dotenv(env_path)
    sheets_url = os.getenv("SHEETS_URL")
    # run
    print(sheets_loader(sheets_url))
