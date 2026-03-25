/**
 * Counsellor Co-Pilot — Google Apps Script Backend
 * Receives form submissions and appends to Google Sheet.
 * Updated to match the current frontend payload (March 2025).
 */
function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return ContentService.createTextOutput(JSON.stringify({
        status: 'error',
        message: 'No data received'
      })).setMimeType(ContentService.MimeType.JSON);
    }

    var data = JSON.parse(e.postData.contents);
    var doc = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = doc.getActiveSheet();

    // Auto-generate Headers if sheet is completely empty
    if (sheet.getLastRow() === 0) {
      var headers = [
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
      ];
      sheet.appendRow(headers);
    }

    // Read current headers from row 1
    var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];

    // Build row matching header order — any payload key maps to its header column
    var row = headers.map(function(h) {
      return data[h] !== undefined ? String(data[h]) : '';
    });

    // Append row
    sheet.appendRow(row);

    return ContentService.createTextOutput(JSON.stringify({
      status: 'ok',
      message: 'Row appended successfully',
      columns: row.length
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      status: 'error',
      message: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

// CORS preflight
function doOptions(e) {
  return ContentService.createTextOutput("")
    .setMimeType(ContentService.MimeType.TEXT)
    .setHeader("Access-Control-Allow-Origin", "*")
    .setHeader("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
    .setHeader("Access-Control-Allow-Headers", "Content-Type");
}
