import os
import json
from datetime import datetime
from typing import Dict

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ----------------------------------------
# CONFIG
# ----------------------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")  # JSON content as env var (for Render)
SPREADSHEET_ID = os.getenv("GOOGLE_SHEET_ID")

SHEET_NAME = "Leads"  # change if needed

# ----------------------------------------
# AUTH
# ----------------------------------------
def get_sheets_service():
    if not SPREADSHEET_ID:
        raise RuntimeError("GOOGLE_SHEET_ID env variable is missing")

    # Option 1: Read from JSON file (local dev)
    if SERVICE_ACCOUNT_FILE and os.path.exists(SERVICE_ACCOUNT_FILE):
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
    # Option 2: Read from JSON env var (Render deployment)
    elif SERVICE_ACCOUNT_JSON:
        service_info = json.loads(SERVICE_ACCOUNT_JSON)
        creds = Credentials.from_service_account_info(
            service_info, scopes=SCOPES
        )
    else:
        raise RuntimeError(
            "Google Sheets credentials missing. Set either "
            "GOOGLE_SERVICE_ACCOUNT_FILE (path) or "
            "GOOGLE_SERVICE_ACCOUNT_JSON (JSON content)"
        )

    service = build("sheets", "v4", credentials=creds)
    return service

# ----------------------------------------
# APPEND LEAD
# ----------------------------------------
def append_lead_to_sheet(lead: Dict):
    """
    lead dict must contain:
    - session_id
    - name
    - email
    - phone
    - intent_summary
    """

    service = get_sheets_service()
    sheet = service.spreadsheets()

    values = [[
        datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        lead.get("session_id"),
        lead.get("name"),
        lead.get("email"),
        lead.get("phone"),
        lead.get("intent_summary"),
    ]]

    body = {"values": values}

    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()
