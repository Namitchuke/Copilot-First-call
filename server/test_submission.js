const SHEET_URL = 'https://copilot-first-call-backend.onrender.com/submit';

const payload = {
  userId: "TEST_USER_999",
  duration: "10m 30s",
  highest_edu: "Bachelors",
  edu_12_grade: "95%",
  edu_12_maths: "Yes",
  edu_bach_course: "B.Tech Computer Science",
  edu_bach_cgpa: "8.5",
  edu_bach_backlogs: "0",
  edu_bach_year: "2023",
  edu_mast_course: "",
  edu_mast_cgpa: "",
  edu_mast_backlogs: "",
  edu_mast_year: "",
  edu_12_board: "CBSE",
  edu_12_year: "2019",
  edu_12_english: "90",
  has_work_ex: "Yes",
  work_role: "Software Engineer",
  work_years: "2 Years",
  gap_years: "0",
  preferred_degree: "Master's",
  target_course: "Data Science",
  target_country: "USA, UK",
  target_intake: "Fall 2025",
  budget: "40 Lakhs",
  mode_financing: "Education Loan",
  preferences: "Preferred course, High job placement",
  five_year_goal: "To work in a top tech company",
  elt_status: "Appeared",
  elt_exam: "IELTS",
  elt_score: "7.5",
  elt_date: "Oct 2024",
  elt_willing: "",
  elt_plan: "",
  elt_prep_stage: "",
  elt_waiver: "",
  elt_reason: "",
  pref_course_notes: "",
  pref_location_notes: "",
  pref_ranking_notes: "",
  pref_low_fee_notes: "",
  pref_scholarship_notes: "",
  follow_up_date: "2025-04-01",
  follow_up_time: "14:00",
  counselor_notes: "Strong candidate, needs loan assistance.",
  student_questions: "Are there scholarships available?"
};

async function testSubmit() {
  console.log("Sending mock payload to:", SHEET_URL);
  try {
    const resp = await fetch(SHEET_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    const res = await resp.json();
    console.log("Response Status:", resp.status);
    console.log("Response Body:", res);
    
    if (res.status === 'ok') {
        console.log("----------");
        console.log("✅ SUCCESS");
        console.log("----------");
    } else {
      console.log("❌ ERROR:", res);
    }
  } catch (err) {
    console.error("❌ FETCH FAILED:", err);
  }
}

testSubmit();
