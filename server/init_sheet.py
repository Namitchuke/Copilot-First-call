import os
import gspread
import json
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# We use the correct ID I recently verified
SPREADSHEET_ID = "1hyRaNJXnAn-7qvHnmNQinWp0UfYgIpeaUqOQDz88rpA"
CRED_FILE = "server/credentials.json"

# Fallback headers based on the Counselor Co-Pilot payload
HEADERS = [
    "userId", "duration", "highest_edu", "edu_12_grade", "edu_12_maths", 
    "edu_bach_course", "edu_bach_cgpa", "edu_bach_backlogs", "edu_bach_year", 
    "edu_mast_course", "edu_mast_cgpa", "edu_mast_backlogs", "edu_mast_year",
    "edu_12_year", "edu_12_english", "has_work_ex", "work_role", "work_years", 
    "gap_years", "preferred_degree", "target_course", "target_country", 
    "target_intake", "budget", "mode_financing", "preferences", "five_year_goal", 
    "elt_status", "elt_exam", "elt_score", "elt_date", "elt_willing", "elt_plan", 
    "elt_prep_stage", "elt_waiver", "elt_reason", "pref_course_notes", 
    "pref_location_notes", "pref_ranking_notes", "pref_low_fee_notes", 
    "pref_scholarship_notes", "follow_up_date", "follow_up_time", 
    "counselor_notes", "student_questions"
]

def init_sheet():
    if not os.path.exists(CRED_FILE):
        print(f"ERROR: {CRED_FILE} not found.")
        return

    credentials = Credentials.from_service_account_file(CRED_FILE, scopes=SCOPES)
    gc = gspread.authorize(credentials)
    
    try:
        print(f"Opening sheet {SPREADSHEET_ID}...")
        sheet = gc.open_by_key(SPREADSHEET_ID).sheet1
        
        print("Clearing sheet...")
        sheet.clear()
        
        print("Inserting headers...")
        sheet.insert_row(HEADERS, 1)
        
        # Format headers
        sheet.format("A1:AZ1", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}})
        
        print("SUCCESS! Headers created and formatted.")
    except Exception as e:
        print(f"FAILED: {str(e)}")

if __name__ == "__main__":
    init_sheet()
