"""
Audit Google Sheet columns vs frontend payload, then hide stale columns.
"""
import os, sys, json
sys.path.insert(0, r"d:\Antigraity\Copilot for counsellor\server")

import gspread
from google.oauth2.service_account import Credentials

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SPREADSHEET_ID = "1hyRaNJXnAn-7qvHnmNQinWp0UfYgIpeaUqOQDz88rpA"
CRED_FILE = r"d:\Antigraity\Copilot for counsellor\server\credentials.json"

# Current frontend payload keys (from submitToSheets in index.html)
FRONTEND_PAYLOAD_KEYS = [
    "userId", "duration", "highest_edu",
    "edu_12_grade", "edu_12_maths",
    "edu_bach_course", "edu_bach_cgpa", "edu_bach_backlogs", "edu_bach_year",
    "edu_mast_course", "edu_mast_cgpa", "edu_mast_backlogs", "edu_mast_year",
    "edu_12_board", "edu_12_year", "edu_12_english",
    "has_work_ex", "work_role", "work_years", "gap_years",
    "preferred_degree", "target_course", "target_country", "target_intake",
    "budget", "mode_financing", "preferences", "five_year_goal",
    "elt_status", "elt_exam", "elt_score", "elt_date",
    "elt_willing", "elt_plan", "elt_prep_stage", "elt_waiver", "elt_reason",
    "pref_course_notes", "pref_location_notes", "pref_ranking_notes",
    "pref_low_fee_notes", "pref_scholarship_notes",
    "follow_up_date", "follow_up_time",
    "counselor_notes", "student_questions"
]

# These are the stale columns to HIDE (UI removed, will always be empty)
COLUMNS_TO_HIDE = [
    "pref_course_notes", "pref_location_notes", "pref_ranking_notes",
    "pref_low_fee_notes", "pref_scholarship_notes"
]

def main():
    credentials = Credentials.from_service_account_file(CRED_FILE, scopes=SCOPES)
    gc = gspread.authorize(credentials)
    sheet = gc.open_by_key(SPREADSHEET_ID).sheet1
    
    headers = sheet.row_values(1)
    
    print("=" * 60)
    print("CURRENT GOOGLE SHEET HEADERS:")
    print("=" * 60)
    for i, h in enumerate(headers, 1):
        print(f"  Col {i}: {h}")
    
    print(f"\n  Total columns in sheet: {len(headers)}")
    
    print("\n" + "=" * 60)
    print("FRONTEND PAYLOAD KEYS:")
    print("=" * 60)
    for k in FRONTEND_PAYLOAD_KEYS:
        status = "IN SHEET" if k in headers else "NOT IN SHEET (will be auto-created)"
        print(f"  {k}: {status}")
    
    print("\n" + "=" * 60)
    print("SHEET COLUMNS NOT IN FRONTEND PAYLOAD (orphaned):")
    print("=" * 60)
    orphans = [h for h in headers if h not in FRONTEND_PAYLOAD_KEYS]
    if orphans:
        for h in orphans:
            print(f"  ORPHAN: {h}")
    else:
        print("  None - all sheet columns match frontend payload!")
    
    print("\n" + "=" * 60)
    print("HIDING STALE COLUMNS...")
    print("=" * 60)
    
    cols_to_hide_indices = []
    for col_name in COLUMNS_TO_HIDE:
        if col_name in headers:
            idx = headers.index(col_name)
            cols_to_hide_indices.append((col_name, idx))
            print(f"  Will hide: {col_name} (Column {idx + 1})")
        else:
            print(f"  Skip: {col_name} (not in sheet)")
    
    if cols_to_hide_indices:
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        sheet_id = spreadsheet.sheet1.id
        
        requests = []
        for col_name, col_idx in cols_to_hide_indices:
            requests.append({
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": col_idx,
                        "endIndex": col_idx + 1
                    },
                    "properties": {
                        "hiddenByUser": True
                    },
                    "fields": "hiddenByUser"
                }
            })
        
        spreadsheet.batch_update({"requests": requests})
        print(f"\n  Successfully hid {len(cols_to_hide_indices)} columns!")
    else:
        print("\n  No columns to hide.")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
