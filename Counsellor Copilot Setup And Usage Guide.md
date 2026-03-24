# Counsellor Co-Pilot — Setup & Usage Guide

**Tool:** Counsellor Co-Pilot (`counsellor-copilot.html`)
**Purpose:** Structured call assistant for Leap Finance counsellors during first student calls
**Type:** Self-contained HTML app — no installation, no backend, works in any browser

---

## What It Does

Guides counsellors through a strict, linear 1st call flow:

```
Login → Introduction → Academics → Work Experience → Study Abroad Intent → Profile Capture → Next Steps → Summary → Submit to Google Sheets
```

- **Checklists** for each section — all items must be ticked before proceeding
- **Live call timer** from the moment the call starts
- **Profile capture** with conditional fields (education level, ELT, gap years)
- **Slot booking** for the follow-up call
- **Editable summary** reviewed before submitting
- **Submits to Google Sheets** — one row per call, 36 columns

---

## Step 1 — Deploy the App

### Option A: Netlify Drop (Recommended — 60 seconds)

1. Go to **[app.netlify.com/drop](https://app.netlify.com/drop)**
2. Drag and drop `counsellor-copilot.html` onto the page
3. You'll get a URL like `https://random-name.netlify.app`
4. Share this URL with your counsellor team — they can bookmark it

### Option B: Share the File Directly

Send `counsellor-copilot.html` to counsellors. They open it in Chrome or Safari — works fully offline (except Google Fonts).

---

## Step 2 — Connect Google Sheets

### 2a. Create Your Google Sheet

Open a new Google Sheet. Name it (e.g. *Leap CRM — 1st Call Data*).

### 2b. Set Up the Apps Script

1. In the Sheet: **Extensions → Apps Script**
2. Delete any existing code, then paste the following:

```javascript
function doPost(e) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    const data  = JSON.parse(e.postData.contents);

    // Auto-add headers on first run
    if (sheet.getLastRow() === 0) {
      sheet.appendRow([
        'Timestamp','Counsellor','Call Duration','Call Date',
        'First Name','Last Name','Phone','Email',
        'Education Level',
        "Master's Degree","Master's Course","Master's Year","Master's Institute","Master's Grading","Master's Grade",
        "Bachelor's Degree","Bachelor's Course","Bachelor's Year","Bachelor's Institute","Bachelor's Grading","Bachelor's Grade",
        'Backlogs','12th Grade Score (%)','Gap Years','Gap Reason','Work Ex (months)',
        'Target Countries','Course of Interest','Target Intake','Other Preferences',
        'Max Budget (INR)',
        'ELT Status','ELT Details','12th English Score (%)',
        'Follow-up Date','Follow-up Time'
      ]);
    }

    sheet.appendRow([
      new Date().toLocaleString('en-IN'),
      data.counsellor, data.callDuration, data.callDate,
      data.firstName, data.lastName, data.phone, data.email,
      data.eduLevel,
      data.mDegree, data.mCourse, data.mYear, data.mInstitute, data.mGrading, data.mGrade,
      data.bDegree, data.bCourse, data.bYear, data.bInstitute, data.bGrading, data.bGrade,
      data.backlogs, data.score12th, data.gapYears, data.gapReason, data.workMonths,
      data.countries, data.coursePref, data.intake, data.otherPrefs,
      data.budgetMax,
      data.eltStatus, data.eltDetails, data.engScore12th,
      data.slotDate, data.slotTime
    ]);

    return ContentService
      .createTextOutput(JSON.stringify({ status: 'success' }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch(err) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'error', message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
```

### 2c. Deploy as Web App

1. Click **Deploy → New Deployment**
2. Select type: **Web App**
3. Execute as: **Me**
4. Who has access: **Anyone**
5. Click **Deploy**
6. **Copy the Web App URL** (looks like `https://script.google.com/macros/s/ABC.../exec`)

### 2d. Paste URL into the HTML File

Open `counsellor-copilot.html` in a text editor. Find this line near the bottom (in the `<script>` section):

```javascript
const SHEET_URL = 'YOUR_APPS_SCRIPT_URL_HERE';
```

Replace `YOUR_APPS_SCRIPT_URL_HERE` with the URL you copied. Save the file.

> **Important:** After pasting the URL, re-upload the updated file to Netlify (just drag and drop again — it will replace the old deployment).

---

## Login Credentials

| Username | Display Name | Password |
|----------|-------------|----------|
| `priya` | Priya Sharma | `leap123` |
| `rahul` | Rahul Mehta | `leap123` |
| `ananya` | Ananya Singh | `leap123` |
| `vikram` | Vikram Nair | `leap123` |
| `sneha` | Sneha Kapoor | `leap123` |

> To add or change users, edit the `USERS` object in the `<script>` section of the HTML file.

---

## Call Flow — Quick Reference

| Step | Section | What to do |
|------|---------|-----------|
| 1 | **Introduction** | Read the expectation-setting script aloud, then start the call timer |
| 2 | **Academics** | Tick all 5 checklist items as you cover them |
| 3 | **Work Experience** | Tick all 6 checklist items |
| 4 | **Study Abroad Intent** | Tick all 7 (Part 1) + 3 (Part 2) items |
| 5 | **Profile Capture** | Fill all required fields (*) — education, preferences, budget, ELT |
| 6 | **Next Steps** | Ask for questions → read plan delivery script → book follow-up slot |
| 7 | **Summary** | Review all captured data, edit if needed |
| 8 | **Submit** | Hit Submit — data goes live into Google Sheets |

> Sections are **locked in order** — you cannot skip ahead.

---

## What Gets Captured in the Sheet

36 columns per submission:

| Category | Fields |
|----------|--------|
| Call Info | Timestamp, Counsellor, Call Duration, Call Date |
| Personal | First Name, Last Name, Phone, Email |
| Academic | Education Level, Master's (6 fields), Bachelor's (6 fields), Backlogs, 12th Score, Gap Years, Gap Reason, Work Ex (months) |
| Preferences | Target Countries, Course of Interest, Target Intake, Other Preferences |
| Budget | Max Budget (INR) |
| ELT | ELT Status, ELT Details, 12th English Score (%) |
| Follow-up | Slot Date, Slot Time |

Headers are auto-created on the very first submission.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Submit button does nothing / spins forever | Check that `SHEET_URL` in the HTML has been updated with the real Apps Script URL |
| Data not appearing in Sheet | Re-deploy the Apps Script (Deploy → Manage Deployments → Edit → Deploy) |
| Can't proceed to next section | All checklist items in the current section must be ticked first |
| App not loading fonts | Requires internet connection for Google Fonts (layout still works offline) |
| Need to add a new counsellor | Edit the `USERS` object in the HTML `<script>` section |
