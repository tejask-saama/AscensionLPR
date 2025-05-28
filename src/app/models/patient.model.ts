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
    allergies: string; // Patient allergies
    immunizations: string; // Patient immunizations
    medicationHistory: string; // Medication history
  };
  
  // Section 3: Medical Timeline
  medicalTimeline: {
    encounters: EncounterInfo[];
  };
  
  // Section 4: Current Care Plan
  currentCarePlan: {
    activePlan: {
      title: string;
      description: string;
      status: string;
    };
    goals: {
      description: string;
      startDate: string;
      targetDate: string;
      status: string;
    }[];
    vitalSigns: {
      bp: string; // Blood Pressure
      temp: string; // Temperature
      rr: string; // Respiratory Rate
      hr: string; // Heart Rate
      o2Saturation: string; // SpO2
    };
    currentMedications: string[];
  };
  
  // Section 5: Risk Assessment
  riskAssessment: {
    cardiovascularRisk: string[];
    complications: string[];
    fallRisk: {
      factors: string;
      recommendations: string;
    };
  };
  
  // Section 6: Recommendations
  recommendations: {
    followUpSchedule: {
      primaryCare: string;
      specialists: string[];
    };
    preventiveCare: string[];
    lifestyle: string[];
    shiftGoal: string; // Goal for the Shift (keeping from original)
    dayPlan: string; // Plan for the Day (keeping from original)
    dischargePlan: string; // Discharge Plan (keeping from original)
  };
  
  // Section 7: Nurses' Notes (keeping from original)
  nursesNotes: NurseNote[];
  
  // Original Assessment fields (keeping for backward compatibility)
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
}

export interface NurseNote {
  date: string; // Date of the note
  time: string; // Time of the note (with CST)
  user: string; // Nurse name and credentials
  content: string; // Content of the note
}

export interface EncounterInfo {
  date: string;
  type: string;
  encounterId: string;
  vitalSigns?: string;
  symptoms?: string;
  physicalExam?: string;
  diagnosis?: string;
  labs?: string[];
  assessment?: string;
  plan?: string;
  procedures?: string;
  hospitalCourse?: string;
  imaging?: string;
  dischargePlan?: string;
}
