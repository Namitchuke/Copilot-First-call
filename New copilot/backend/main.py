import os
import gspread
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import json
import time

load_dotenv()

app = FastAPI()

# Enable CORS for Vercel and Localhost
origins = [
    "*", # Allow all for convenience in this specific tool setting, or restrict to user's vercel domains
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

# Definitive header list for mapping 50+ data points
HEADERS = [
    "timestamp", "userId", "duration", "follow_up_date", "follow_up_time", "notes",
    "intent", "work_ex", "work_role", "years_ex", "academics", "ug_course", "ug_cgpa", 
    "ug_backlogs", "ug_year", "pg_course", "pg_cgpa", "pg_backlogs", "pg_year", 
    "edu_12_grade", "edu_12_year", "edu_12_maths", "edu_12_english", "gap_years", 
    "preferred_degree", "target_course", "target_country", "target_intake", "budget", 
    "mode_financing", "five_year_goal", "elt_status", "elt_exam", "elt_score", "elt_date", 
    "elt_willing", "elt_plan", "elt_prep_stage", "elt_waiver", "elt_reason", 
    "pref_course_notes", "pref_location_notes", "pref_ranking_notes", "pref_low_fee_notes", 
    "pref_scholarship_notes", "student_questions"
]

def get_sheet():
    try:
        if not SPREADSHEET_ID:
            print("CRITICAL: Missing SPREADSHEET_ID")
            return None
            
        # Try full JSON first
        if GOOGLE_CREDENTIALS_JSON:
            creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
        else:
            # Fallback to individual keys (as seen in user screenshot)
            creds_dict = {
                "type": os.getenv("type"),
                "project_id": os.getenv("project_id"),
                "private_key_id": os.getenv("private_key_id"),
                "private_key": os.getenv("private_key").replace('\\n', '\n') if os.getenv("private_key") else None,
                "client_email": os.getenv("client_email"),
                "client_id": os.getenv("client_id"),
                "auth_uri": os.getenv("auth_uri"),
                "token_uri": os.getenv("token_uri"),
                "auth_provider_x509_cert_url": os.getenv("auth_provider_x509_cert_url"),
                "client_x509_cert_url": os.getenv("client_x509_cert_url"),
                "universe_domain": os.getenv("universe_domain")
            }
            
        if not creds_dict.get("project_id"):
            print("CRITICAL: No valid credentials found (JSON or individual keys)")
            return None

        credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        gc = gspread.authorize(credentials)
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        return spreadsheet.sheet1
    except Exception as e:
        print(f"CRITICAL: Failed to authorize or open sheet: {str(e)}")
        return None

def process_submission(data):
    """Sync data to Google Sheets, auto-creating headers if missing"""
    try:
        sheet = get_sheet()
        if not sheet: return
        
        # Check current headers
        try:
            current_headers = sheet.row_values(1)
        except:
            current_headers = []

        # If sheet is empty or headers mismatch, reset headers
        if not current_headers or current_headers[0] != HEADERS[0]:
            print("Initializing sheet with standardized headers...")
            sheet.clear()
            header_range = f"A1:{gspread.utils.rowcol_to_a1(1, len(HEADERS))}"
            sheet.update(range_name=header_range, values=[HEADERS])
            # Format header row
            try:
                sheet.format("A1:AZ1", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.94, "green": 0.94, "blue": 0.94}})
            except: pass
            current_headers = HEADERS

        # Map data to the header order
        row = [str(data.get(h, "")) for h in current_headers]
        
        # Handle tags/keys not in our standard HEADERS list (dynamic growth)
        extra_keys = [k for k in data.keys() if k not in current_headers]
        if extra_keys:
            new_headers = current_headers + extra_keys
            header_range = f"A1:{gspread.utils.rowcol_to_a1(1, len(new_headers))}"
            sheet.update(range_name=header_range, values=[new_headers])
            # Add extra values to the current row
            for k in extra_keys:
                row.append(str(data.get(k, "")))

        sheet.append_row(row)
        print(f"SUCCESS: Synced session data for {data.get('userId')} to Sheets.")
    except Exception as e:
        print(f"ASYNC ERROR: {str(e)}")

@app.get("/")
async def health():
    return {"status": "ok", "time": time.time()}

@app.post("/submit")
async def submit_data(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        # Add timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
            
        background_tasks.add_task(process_submission, data)
        return {"status": "ok", "message": "Submission received!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
