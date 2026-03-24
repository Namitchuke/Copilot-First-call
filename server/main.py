import os
import gspread
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

import json
import asyncio
import httpx

load_dotenv()

# Setup API App
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://copilot-first-call.vercel.app",
        "https://copilot-first-call-namitchukes-projects.vercel.app",
        "*"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Google Sheets Connect
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
GOOGLE_CREDENTIALS_JSON = os.getenv('GOOGLE_CREDENTIALS')

def get_sheet():
    if not SPREADSHEET_ID:
        raise ValueError("SPREADSHEET_ID is missing from environment")
        
    if GOOGLE_CREDENTIALS_JSON:
        # Load from env var (for cloud deployment)
        creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
        credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    else:
        # Load from local file (for local development)
        credentials_file = os.path.join(os.path.dirname(__file__), 'credentials.json')
        if not os.path.exists(credentials_file):
            raise FileNotFoundError("Neither GOOGLE_CREDENTIALS env var nor credentials.json file found")
        credentials = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
        
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(SPREADSHEET_ID)
    return spreadsheet.sheet1

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Counsellor Co-Pilot Backend is running"}

# Keep-Alive Background Task for Render Free Tier
async def keep_alive():
    """Pings itself every 10 minutes to stay awake on Render free tier."""
    await asyncio.sleep(5)  # Initial delay
    url = os.getenv("RENDER_EXTERNAL_URL") or "http://localhost:8000"
    if not url.endswith("/"): url += "/"
    
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # We skip pinging localhost to save resources in dev
                if "localhost" not in url:
                    await client.get(url)
                    print(f"Self-ping successful: {url}")
            except Exception as e:
                print(f"Self-ping failed: {e}")
            await asyncio.sleep(600)  # 10 minutes

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(keep_alive())

@app.post("/admin/add-field")
async def add_field(request: Request):
    data = await request.json()
    field_name = data.get("field_name")
    if not field_name:
        return {"status": "error", "message": "field_name is required"}
    
    sheet = get_sheet()
    all_values = sheet.get_all_values()
    headers = all_values[0] if len(all_values) > 0 else []
    
    if field_name in headers:
        return {"status": "warning", "message": f"Field '{field_name}' already exists"}
    
    headers.append(field_name)
    if len(all_values) == 0:
        sheet.append_row(headers)
    else:
        # Update row 1 with expanded headers
        cell_range = f"A1:{gspread.utils.rowcol_to_a1(1, len(headers))}"
        sheet.update(range_name=cell_range, values=[headers])
    
    return {"status": "success", "message": f"Field '{field_name}' added successfully!"}

@app.post("/submit")
async def submit_profile(request: Request):
    try:
        data = await request.json()
        print(f"DEBUG: Received payload")
        sheet = get_sheet()
        all_values = sheet.get_all_values()
        headers = all_values[0] if len(all_values) > 0 else []
        missing_headers = [key for key in data.keys() if key not in headers]
        if missing_headers:
            headers.extend(missing_headers)
            cell_range = f"A1:{gspread.utils.rowcol_to_a1(1, len(headers))}"
            sheet.update(range_name=cell_range, values=[headers])
        row_data = [str(data.get(header, "")) for header in headers]
        sheet.append_row(row_data)
        return {"status": "ok", "message": "Profile synced successfully!"}
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
