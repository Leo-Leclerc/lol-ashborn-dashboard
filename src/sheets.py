import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")
CREDS_PATH = os.getenv("GOOGLE_CREDS_PATH")

_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def get_client():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, _SCOPES)
    return gspread.authorize(creds)

def open_sheet(tab: str):
    client = get_client()
    return client.open(SPREADSHEET_NAME).worksheet(tab)
