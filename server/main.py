import os
import gspread
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import json

load_dotenv()

app = FastAPI()

# Explicit Vercel Origins
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

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
GOOGLE_CREDENTIALS_JSON = os.getenv('GOOGLE_CREDENTIALS')

def get_sheet():
    if not SPREADSHEET_ID: raise ValueError("Backend Error: SPREADSHEET_ID is not set in Render Environment Variables.")
    if not GOOGLE_CREDENTIALS_JSON: raise ValueError("Backend Error: GOOGLE_CREDENTIALS is not set in Render Environment Variables.")
    
    try:
        creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
        credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        gc = gspread.authorize(credentials)
        
        print(f"DEBUG: Attempting to open sheet with ID: {SPREADSHEET_ID}")
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        return spreadsheet.sheet1
    except gspread.exceptions.SpreadsheetNotFound:
        raise ValueError(f"Spreadsheet Not Found. Ensure the ID '{SPREADSHEET_ID}' is correct and the sheet is NOT deleted.")
    except gspread.exceptions.APIError as e:
        if "403" in str(e):
            raise ValueError(f"Permission Denied. You MUST share your Google Sheet with the service account as an Editor: {creds_dict.get('client_email')}")
        raise ValueError(f"Google API Error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Connection Error: {str(e)}")

@app.get("/")
async def health():
    return {"status": "ok", "id_used": SPREADSHEET_ID[:5] + "..." if SPREADSHEET_ID else "None"}

@app.post("/submit")
async def submit_profile(request: Request, response: Response):
    try:
        data = await request.json()
        sheet = get_sheet()
        
        all_values = sheet.get_all_values()
        headers = all_values[0] if len(all_values) > 0 else []
        
        missing = [k for k in data.keys() if k not in headers]
        if missing:
            headers.extend(missing)
            sheet.update(range_name=f"A1:{gspread.utils.rowcol_to_a1(1, len(headers))}", values=[headers])
        
        row = [str(data.get(h, "")) for h in headers]
        sheet.append_row(row)
        
        return {"status": "ok", "message": "Successfully Synced to Google Sheets!"}
    except Exception as e:
        print(f"SERVER ERROR: {str(e)}")
        # We return a 200 with status:error so the frontend can alert the specific message
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
