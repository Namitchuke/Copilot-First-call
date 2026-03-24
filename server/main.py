import os
import gspread
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import json
import asyncio
import httpx

load_dotenv()

app = FastAPI()

# Explicit Vercel Origins for Credentials support
origins = [
    "https://copilot-first-call.vercel.app",
    "https://copilot-first-call-namitchukes-projects.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
GOOGLE_CREDENTIALS_JSON = os.getenv('GOOGLE_CREDENTIALS')

def get_sheet():
    if not SPREADSHEET_ID:
        raise ValueError("SPREADSHEET_ID is missing")
    if not GOOGLE_CREDENTIALS_JSON:
        raise ValueError("GOOGLE_CREDENTIALS is missing")
    
    creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
    credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(SPREADSHEET_ID)
    return spreadsheet.sheet1

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Backend is live"}

@app.post("/submit")
async def submit_profile(request: Request, response: Response):
    try:
        data = await request.json()
        print(f"DEBUG: Processing submission for {data.get('userId', 'Unknown')}")
        
        sheet = get_sheet()
        all_values = sheet.get_all_values()
        headers = all_values[0] if len(all_values) > 0 else []
        
        # Identify missing columns
        missing = [k for k in data.keys() if k not in headers]
        if missing:
            headers.extend(missing)
            # Update Header Row
            sheet.update(range_name=f"A1:{gspread.utils.rowcol_to_a1(1, len(headers))}", values=[headers])
        
        # Build Row
        row = [str(data.get(h, "")) for h in headers]
        sheet.append_row(row)
        
        return {"status": "ok", "message": "Synced"}
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        response.status_code = 500
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
