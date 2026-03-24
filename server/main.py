import os
import gspread
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

# Setup API App
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Google Sheets Connect
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

def get_sheet():
    if not SPREADSHEET_ID:
        raise ValueError("SPREADSHEET_ID is missing from .env")
        
    credentials = Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    gc = gspread.authorize(credentials)
    # Open the Google Spreadsheet
    spreadsheet = gc.open_by_key(SPREADSHEET_ID)
    return spreadsheet.sheet1

@app.post("/submit")
async def submit_profile(request: Request):
    data = await request.json()
    sheet = get_sheet()

    # 1. Fetch Existing Headers
    all_values = sheet.get_all_values()
    headers = all_values[0] if len(all_values) > 0 else []

    # 2. Check for novel columns in the incoming payload
    missing_headers = []
    for key in data.keys():
        if key not in headers:
            missing_headers.append(key)

    # 3. Append missing columns to the header row (Row 1)
    if missing_headers:
        headers.extend(missing_headers)
        if len(all_values) == 0:
            sheet.append_row(headers)
        else:
            # Update row 1 with expanded headers
            cell_range = f"A1:{gspread.utils.rowcol_to_a1(1, len(headers))}"
            sheet.update(range_name=cell_range, values=[headers])

    # 4. Construct Row Array logically based on the final header mapping
    row_data = []
    for header in headers:
        val = data.get(header, "")
        row_data.append(str(val))

    # 5. Append Row Data
    sheet.append_row(row_data)

    return {"status": "success", "message": "Profile synced successfully!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
