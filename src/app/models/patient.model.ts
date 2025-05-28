export interface Patient {
  id: number;
  name: string;
  dob: string;
  age: number;
  gender: string;
  mrn: string;
}

export interface PatientDetail extends Patient {
  // Section 2: Background
  background: {
    pastMedicalHistory: string; // Narrative summary of chronic conditions, significant medical events, etc.
    currentPlanInfo: string; // Information leading to current plan of care
  };
  
  // Section 3: Assessment
  assessment: {
    vitalSigns: {
      bp: string; // Blood Pressure
      hr: string; // Heart Rate
      temp: string; // Temperature
      rr: string; // Respiratory Rate
      o2Saturation: string; // SpO2
    };
    painLevel: string; // Current Pain Level
    goalPainLevel: string; // Goal Pain Level
    abnormalFindings: string; // Narrative of abnormal clinical findings
    recentPRN: string; // Recent PRN Medications
    fallRisk: string; // Fall Risk & Expectations
    activity: string; // Activity level
    wounds: string; // Observe Wounds / Drugs / Site
    specimen: string; // Specimen information
    ivs: string; // IV information
    procedures: string; // Procedures
    diet: string; // NPO / Diet
    safety: string; // Safety Precautions
    labResults: string; // Lab Results
  };
  
  // Section 4: Recommendations
  recommendations: {
    shiftGoal: string; // Goal for the Shift
    dayPlan: string; // Plan for the Day
    dischargePlan: string; // Discharge Plan
  };
  
  // Section 5: Nurses' Notes
  nursesNotes: NurseNote[];
}

export interface NurseNote {
  date: string; // Date of the note
  time: string; // Time of the note (with CST)
  user: string; // Nurse name and credentials
  content: string; // Content of the note
}
