function doPost(e) {
  try {
    // Check if there is data sent
    if (!e || !e.postData || !e.postData.contents) {
      return ContentService.createTextOutput(JSON.stringify({
        status: 'error',
        message: 'No data received'
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    // Parse the JSON payload from the HTML file
    var data = JSON.parse(e.postData.contents);
    
    // Specify the sheet (assumes the linked active sheet)
    var doc = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = doc.getActiveSheet();
    
    // Auto-generate Headers if sheet is completely empty
    if (sheet.getLastRow() === 0) {
      var headers = [
        "Timestamp", "Counsellor ID", "Duration", "Pre User ID", "Course", "College / Uni", 
        "CGPA / %", "Backlogs", "Years of Graduation", "Has Work Ex?", "Role", "Total Years", 
        "Gap Years", "Target Course", "Target Intake", "Budget (INR)", "Preferred Countries", "Career Outcome", 
        "Other Preferences", "ELT Given?", "ELT Exam", "ELT Score", "ELT Date", "Willing to take?", 
        "Planning Exam Name", "Status", "When to book?", "Prep Stage", "Booked Date", "Why Not ELT?", 
        "Require Waiver?", "12th Year", "12th Board", "12th English Score", "Slot Date", "Slot Time",
        "✓ Course", "✓ College", "✓ Stream Motivation", "✓ CGPA", "✓ Backlogs", "✓ Extra-curricular",
        "✓ Exact Role", "✓ Field Switch?", "✓ Switch Reason", "✓ Duration", "✓ Gap Years", "✓ Target Course", "✓ Why Course?",
        "✓ Why Abroad?", "✓ Country Pref", "✓ ELT Status", "✓ College Prefs", "✓ Target Intake", "✓ Parents Support", "✓ Budget",
        "✓ Career Goals", "✓ Stay Back", "✓ Alternate Plans"
      ];
      sheet.appendRow(headers);
    }
    
    // Define the exact order of columns to be logged
    var row = [
      data.callDate || new Date().toISOString(),
      data.counsellor || '',
      data.callDuration || '',
      data.userId || '',
      data.ugCourse || '',
      data.college || '',
      data.cgpa || '',
      data.backlogs || '',
      data.gradYr || '',
      data.hasWorkEx || '',
      data.role || '',
      data.expYears || '',
      data.gapYears || '',
      
      data.targetCourse || '',
      data.intake || '',
      data.budget || '',
      data.countries || '',
      data.career || '',
      data.prefs || '',
      
      data.eltGiven || '',
      data.eltExam || '',
      data.eltScore || '',
      data.eltDate || '',
      data.eltWilling || '',
      data.eltExPlanning || '',
      data.eltStatus || '',
      data.eltPlanWhen || '',
      data.eltPrep || '',
      data.eltBookDate || '',
      data.eltWhy || '',
      data.eltWaiver || '',
      data.twelveYear || '',
      data.twelveBoard || '',
      data.twelveEng || '',
      
      data.slotDate || '',
      data.slotTime || '',
      
      // Checklist booleans
      data.c_course ? 'Yes' : 'No',
      data.c_college ? 'Yes' : 'No',
      data.c_motiv ? 'Yes' : 'No',
      data.c_cgpa ? 'Yes' : 'No',
      data.c_backlogs ? 'Yes' : 'No',
      data.c_extra ? 'Yes' : 'No',
      
      data.c_exactrole ? 'Yes' : 'No',
      data.c_fieldsw ? 'Yes' : 'No',
      data.c_swreason ? 'Yes' : 'No',
      data.c_duration ? 'Yes' : 'No',
      data.c_gap ? 'Yes' : 'No',
      data.c_tcourse ? 'Yes' : 'No',
      data.c_whycourse ? 'Yes' : 'No',
      
      data.c_why ? 'Yes' : 'No',
      data.c_country ? 'Yes' : 'No',
      data.c_elt ? 'Yes' : 'No',
      data.c_prefs ? 'Yes' : 'No',
      data.c_intake ? 'Yes' : 'No',
      data.c_parents ? 'Yes' : 'No',
      data.c_budget ? 'Yes' : 'No',
      
      data.c_career ? 'Yes' : 'No',
      data.c_stay ? 'Yes' : 'No',
      data.c_alt ? 'Yes' : 'No'
    ];
    
    // Append the row to the Google Sheet
    sheet.appendRow(row);
    
    // Return a success JSON response so the website knows it worked
    return ContentService.createTextOutput(JSON.stringify({
      status: 'success',
      rowLength: row.length
    })).setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    // Return the specific error if something crashes
    return ContentService.createTextOutput(JSON.stringify({
      status: 'error',
      message: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

// Ensure CORS preflight OPTIONS requests work
function doOptions(e) {
  return ContentService.createTextOutput("")
    .setMimeType(ContentService.MimeType.TEXT)
    .setHeader("Access-Control-Allow-Origin", "*")
    .setHeader("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
    .setHeader("Access-Control-Allow-Headers", "Content-Type");
}
