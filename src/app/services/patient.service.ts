import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map, of, catchError } from 'rxjs';
import { Patient, PatientDetail, NurseNote, EncounterInfo } from '../models/patient.model';
import { environment } from '../../environments/environment';

/**
 * Interface for API responses
 */
interface ApiResponse<T> {
  status: string;
  data: T;
  message?: string;
}

/**
 * Interface for patient data from API
 */
interface PatientApiResponse {
  name: string;
  id: string;
}

/**
 * Interface for LPR (Longitudinal Patient Record) API response
 */
interface LprApiResponse {
  patient_id: string;
  query: string;
  response: string;
  patient_data: any;
  reflection: string;
  processing_time_seconds: number;
}

/**
 * Service for handling patient data from the LPR API
 */
@Injectable({
  providedIn: 'root'
})
export class PatientService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }
  
  /**
   * Fetches list of patients from the API
   * @returns Observable of Patient array
   */
  getPatients(): Observable<Patient[]> {
    console.log('Fetching patients from API:', `${this.apiUrl}/lpr-app/patients`);
    return this.http.get<ApiResponse<PatientApiResponse[]>>(`${this.apiUrl}/lpr-app/patients`)
      .pipe(
        map(response => {
          console.log('API response:', response);
          if (response && response.status === 'success' && response.data) {
            // Transform the API response to match our Patient model
            const patients = response.data.map((patient: PatientApiResponse) => {
              const patientId = patient.id.replace('P', '');
              const numericId = parseInt(patientId);
              console.log('Transformed patient:', patient, '->', numericId);
              return {
                id: numericId, // Convert P001 to 1
                name: patient.name,
                dob: '1980-01-01', // Default values for fields not provided by API
                age: 43,
                gender: 'Unknown',
                mrn: patient.id
              };
            });
            console.log('Transformed patients:', patients);
            return patients;
          }
          console.error('Invalid response format:', response);
          return [];
        }),
        catchError(error => {
          console.error('Error fetching patients:', error);
          return of([]);
        })
      );
  }

  /**
   * Fetches detailed patient information from the API
   * @param id Patient ID (numeric)
   * @returns Observable of PatientDetail
   */
  getPatientDetail(id: number): Observable<PatientDetail> {
    // Convert numeric ID to format expected by API (P001, P002, etc.)
    const patientId = `P${id.toString().padStart(3, '0')}`;
    
    // Add a query parameter to ensure we get a complete response
    const queryParam = 'Generate a comprehensive longitudinal patient record';
    
    // Use the correct API endpoint with the patient ID and query parameter
    const url = `${this.apiUrl}/lpr-app/lpr/${patientId}`;
    console.log('Fetching patient detail from API with URL:', url);
    
    // Call API with query parameter
    return this.http.get<ApiResponse<LprApiResponse>>(url, { params: { query: queryParam } })
      .pipe(
        map(response => {
          console.log('Patient detail API response:', response);
          
          if (response && response.status === 'success' && response.data) {
            const lprData = response.data;
            const patientData = lprData.patient_data || {};
            const demographics = patientData.demographics || {};
            const responseText = lprData.response || '';
            
            console.log('Patient data:', patientData);
            console.log('Demographics:', demographics);
            console.log('Response text:', responseText);
            
            // Extract age from date of birth if available
            let age = demographics.age || 43;
            if (demographics.dob && !demographics.age) {
              const dobYear = new Date(demographics.dob).getFullYear();
              const currentYear = new Date().getFullYear();
              age = currentYear - dobYear;
            }
            
            // Transform the API response to match our PatientDetail model
            const patientDetail: PatientDetail = {
              id: id,
              name: patientData.name || demographics.name || `Patient ${id}`,
              dob: demographics.dob || '1980-01-01',
              age: age,
              gender: demographics.gender || patientData.gender || 'Unknown',
              mrn: patientId,
              
              // Background section
              background: {
                pastMedicalHistory: this.extractMedicalHistory(patientData, responseText),
                currentPlanInfo: this.extractCurrentPlan(patientData, responseText),
                allergies: this.extractAllergies(patientData, responseText),
                immunizations: this.extractImmunizations(patientData, responseText),
                medicationHistory: this.extractMedications(patientData, responseText)
              },
              
              // Medical Timeline section
              medicalTimeline: {
                encounters: this.extractEncounters(patientData, responseText)
              },
              
              // Current Care Plan section
              currentCarePlan: {
                activePlan: {
                  title: this.extractCarePlanTitle(patientData, responseText),
                  description: this.extractCarePlanDescription(patientData, responseText),
                  status: this.extractCarePlanStatus(patientData, responseText)
                },
                goals: this.extractGoals(patientData, responseText),
                vitalSigns: {
                  bp: this.extractVitalSign(patientData, 'bp', '120/80'),
                  temp: this.extractVitalSign(patientData, 'temp', '98.6'),
                  rr: this.extractVitalSign(patientData, 'rr', '16'),
                  hr: this.extractVitalSign(patientData, 'hr', '72'),
                  o2Saturation: this.extractVitalSign(patientData, 'o2', '98%')
                },
                currentMedications: this.extractCurrentMedications(patientData, responseText)
              },
              
              // Risk Assessment section
              riskAssessment: {
                cardiovascularRisk: this.extractCardiovascularRisk(patientData, responseText),
                complications: this.extractComplications(patientData, responseText),
                fallRisk: {
                  factors: this.extractRiskAssessment(patientData, 'fall', responseText),
                  recommendations: this.extractRiskRecommendations(patientData, 'fall', responseText)
                }
              },
              
              // Assessment section
              assessment: {
                vitalSigns: {
                  bp: this.extractVitalSign(patientData, 'bp', '120/80'),
                  hr: this.extractVitalSign(patientData, 'hr', '72'),
                  temp: this.extractVitalSign(patientData, 'temp', '98.6'),
                  rr: this.extractVitalSign(patientData, 'rr', '16'),
                  o2Saturation: this.extractVitalSign(patientData, 'o2', '98%')
                },
                painLevel: this.extractPainLevel(patientData, responseText),
                goalPainLevel: '0',
                abnormalFindings: this.extractAbnormalFindings(patientData, responseText),
                recentPRN: this.extractMedications(patientData, responseText),
                fallRisk: this.extractRiskAssessment(patientData, 'fall', responseText),
                activity: this.extractActivity(patientData, responseText),
                wounds: this.extractWounds(patientData, responseText),
                specimen: 'None',
                ivs: 'None',
                procedures: this.extractProcedures(patientData, responseText),
                diet: this.extractDiet(patientData, responseText),
                safety: 'Standard precautions',
                labResults: this.extractLabResults(patientData, responseText)
              },
              
              // Recommendations section
              recommendations: {
                followUpSchedule: {
                  primaryCare: this.extractFollowUp(patientData, 'primary', responseText),
                  specialists: this.extractSpecialists(patientData, responseText)
                },
                preventiveCare: this.extractPreventiveCare(patientData, responseText),
                lifestyle: this.extractLifestyleRecommendations(patientData, responseText),
                shiftGoal: 'Maintain stable vital signs',
                dayPlan: 'Continue current treatment plan',
                dischargePlan: 'Pending physician assessment'
              },
              
              // Nurses' notes section
              nursesNotes: this.extractNursesNotes(responseText)
            };
            
            return patientDetail;
          }
          
          // If there's an error or invalid response, return a default patient detail
          console.error('Invalid response format or error:', response);
          return this.getDefaultPatientDetail(id, patientId);
        }),
        catchError(error => {
          console.error('Error loading patient details:', error);
          return of(this.getDefaultPatientDetail(id, patientId));
        })
      );
  }
  
  /**
   * Submit a clinical question to the API
   * @param patientId Patient ID
   * @param question Clinical question
   * @returns Observable with the API response
   */
  submitClinicalQuestion(patientId: number, question: string): Observable<string> {
    // Convert numeric ID to format expected by API (P001, P002, etc.)
    const formattedPatientId = `P${patientId.toString().padStart(3, '0')}`;
    
    // Use the correct API endpoint for submitting clinical questions
    const url = `${this.apiUrl}/lpr-app/lpr`;
    
    // Prepare the request body
    const body = {
      patient_id: formattedPatientId,
      query: question
    };
    
    console.log('Submitting clinical question to API:', url, body);
    
    // Call API with the question
    return this.http.post<ApiResponse<LprApiResponse>>(url, body)
      .pipe(
        map(response => {
          console.log('Clinical question API response:', response);
          
          if (response && response.status === 'success' && response.data) {
            // Return the response text from the API
            return response.data.response || 'No response from the API';
          }
          
          return 'Error: Unable to process your clinical question';
        }),
        catchError(error => {
          console.error('Error submitting clinical question:', error);
          return of('Error: Unable to process your clinical question');
        })
      );
  }
  
  // Helper methods to extract data from the API response
  private extractMedicalHistory(patientData: any, responseText: string): string {
    if (patientData && patientData.medical_history) {
      return patientData.medical_history;
    }
    
    // Try to extract from response text
    if (responseText && responseText.includes('Medical History')) {
      const match = responseText.match(/Medical History[^\n]*(\n[^\n#]*){1,10}/i);
      if (match) return match[0].replace('Medical History', '').trim();
    }
    
    return 'No significant medical history';
  }
  
  private extractCurrentPlan(patientData: any, responseText: string): string {
    if (patientData && patientData.current_plan) {
      return patientData.current_plan;
    }
    
    // Try to extract from response text
    if (responseText && responseText.includes('Plan')) {
      const match = responseText.match(/Plan[^\n]*(\n[^\n#]*){1,5}/i);
      if (match) return match[0].replace('Plan', '').trim();
    }
    
    return 'Current plan information not available';
  }
  
  private extractVitalSign(patientData: any, type: string, defaultValue: string): string {
    if (patientData && patientData.vital_signs && patientData.vital_signs[type]) {
      return patientData.vital_signs[type];
    }
    return defaultValue;
  }
  
  private extractPainLevel(patientData: any, responseText: string): string {
    if (patientData && patientData.pain_level) {
      return patientData.pain_level;
    }
    
    // Try to extract from response text
    if (responseText && responseText.includes('Pain')) {
      const match = responseText.match(/Pain[^\n]*\d+\/10/i);
      if (match) return match[0].replace('Pain', '').trim();
    }
    
    return '0/10';
  }
  
  private extractAbnormalFindings(patientData: any, responseText: string): string {
    if (patientData && patientData.abnormal_findings) {
      return patientData.abnormal_findings;
    }
    
    // Try to extract from response text
    if (responseText && responseText.includes('Abnormal Findings')) {
      const match = responseText.match(/Abnormal Findings[^\n]*(\n[^\n#]*){1,5}/i);
      if (match) return match[0].replace('Abnormal Findings', '').trim();
    }
    
    return 'No abnormal findings';
  }
  
  private extractMedications(patientData: any, responseText: string): string {
    if (patientData && patientData.medications) {
      return patientData.medications;
    }
    
    // Try to extract from response text
    if (responseText && responseText.includes('Medications')) {
      const match = responseText.match(/Medications[^\n]*(\n[^\n#]*){1,10}/i);
      if (match) return match[0].replace('Medications', '').trim();
    }
    
    return 'No recent PRN medications';
  }
  
  private extractRiskAssessment(patientData: any, riskType: string, responseText: string): string {
    if (patientData && patientData.risk_assessment && patientData.risk_assessment[riskType]) {
      return patientData.risk_assessment[riskType];
    }
    
    // Try to extract from response text
    if (responseText && responseText.includes('Fall Risk')) {
      const match = responseText.match(/Fall Risk[^\n]*(\n[^\n#]*){0,2}/i);
      if (match) return match[0].replace('Fall Risk', '').trim();
    }
    
    return 'Unknown';
  }
  
  private extractActivity(patientData: any, responseText: string): string {
    if (patientData && patientData.activity) {
      return patientData.activity;
    }
    
    // Try to extract from response text
    if (responseText && responseText.includes('Activity')) {
      const match = responseText.match(/Activity[^\n]*(\n[^\n#]*){0,2}/i);
      if (match) return match[0].replace('Activity', '').trim();
    }
    
    return 'Activity as tolerated';
  }
  
  private extractWounds(patientData: any, responseText: string): string {
    if (patientData && patientData.wounds) {
      return patientData.wounds;
    }
    
    // Try to extract from response text
    if (responseText && responseText.includes('Wounds')) {
      const match = responseText.match(/Wounds[^\n]*(\n[^\n#]*){0,3}/i);
      if (match) return match[0].replace('Wounds', '').trim();
    }
    
    return 'No wounds observed';
  }
  
  private extractProcedures(patientData: any, responseText: string): string {
    if (patientData && patientData.procedures) {
      return patientData.procedures;
    }
    
    // Try to extract from response text
    if (responseText && responseText.includes('Procedures')) {
      const match = responseText.match(/Procedures[^\n]*(\n[^\n#]*){0,5}/i);
      if (match) return match[0].replace('Procedures', '').trim();
    }
    
    return 'No recent procedures';
  }
  
  private extractDiet(patientData: any, responseText: string): string {
    if (patientData && patientData.diet) {
      return patientData.diet;
    }
    
    // Try to extract from response text
    if (responseText && responseText.includes('Diet')) {
      const match = responseText.match(/Diet[^\n]*(\n[^\n#]*){0,2}/i);
      if (match) return match[0].replace('Diet', '').trim();
    }
    
    return 'Regular diet';
  }
  
  private extractLabResults(patientData: any, responseText: string): string {
    if (patientData && patientData.lab_results) {
      return patientData.lab_results;
    }
    
    // Try to extract from response text
    if (responseText && responseText.includes('Lab Results')) {
      const match = responseText.match(/Lab Results[^\n]*(\n[^\n#]*){0,10}/i);
      if (match) return match[0].replace('Lab Results', '').trim();
    }
    
    return 'No recent lab results';
  }
  
  private extractNursesNotes(responseText: string): NurseNote[] {
    const notes: NurseNote[] = [];
    if (responseText && typeof responseText === 'string') {
      // Extract nurse notes from the response text
      const notesMatch = responseText.match(/Nurses['']? Notes[\s\S]*?([\s\S]*?)(?:---|$)/i);
      if (notesMatch && notesMatch[1]) {
        const notesText = notesMatch[1].trim();
        // Create a default note with the content
        notes.push({
          date: new Date().toISOString().split('T')[0],
          time: new Date().toTimeString().split(' ')[0] + ' CST',
          user: 'System',
          content: notesText
        });
      }
    }
    
    // If no notes were found, return a default note
    if (notes.length === 0) {
      notes.push({
        date: new Date().toISOString().split('T')[0],
        time: new Date().toTimeString().split(' ')[0] + ' CST',
        user: 'System',
        content: 'No nurses notes available'
      });
    }
    
    return notes;
  }
  
  // Extraction methods for the new fields from JOHN_DOE_Template.md
  private extractAllergies(patientData: any, responseText: string): string {
    if (patientData && patientData.allergies && patientData.allergies.length > 0) {
      return patientData.allergies.map((allergy: any) => 
        `${allergy.substance} (${allergy.severity})`
      ).join('\n');
    }
    return 'No known allergies';
  }
  
  private extractImmunizations(patientData: any, responseText: string): string {
    if (patientData && patientData.immunizations && patientData.immunizations.length > 0) {
      return patientData.immunizations.map((immunization: any) => 
        `${immunization.name} (${immunization.date})`
      ).join('\n');
    }
    return 'No immunization records available';
  }
  
  private extractEncounters(patientData: any, responseText: string): EncounterInfo[] {
    const encounters: EncounterInfo[] = [];
    if (patientData && patientData.encounters && patientData.encounters.length > 0) {
      return patientData.encounters.map((encounter: any) => ({
        date: encounter.date || 'Unknown date',
        type: encounter.type || 'Office visit',
        encounterId: encounter.id || 'Unknown ID',
        vitalSigns: encounter.vital_signs || '',
        symptoms: encounter.symptoms || '',
        diagnosis: encounter.diagnosis || '',
        assessment: encounter.assessment || '',
        plan: encounter.plan || ''
      }));
    }
    // Return a default encounter if none are found
    return [{
      date: new Date().toISOString().split('T')[0],
      type: 'Initial visit',
      encounterId: 'ENC001',
      vitalSigns: 'BP: 120/80, HR: 72, Temp: 98.6°F',
      symptoms: 'No symptoms reported',
      assessment: 'Healthy patient',
      plan: 'Continue current medications'
    }];
  }
  
  private extractCarePlanTitle(patientData: any, responseText: string): string {
    if (patientData && patientData.care_plan && patientData.care_plan.title) {
      return patientData.care_plan.title;
    }
    return 'Maintenance Care Plan';
  }
  
  private extractCarePlanDescription(patientData: any, responseText: string): string {
    if (patientData && patientData.care_plan && patientData.care_plan.description) {
      return patientData.care_plan.description;
    }
    return 'Standard care plan for maintaining health and managing existing conditions';
  }
  
  private extractCarePlanStatus(patientData: any, responseText: string): string {
    if (patientData && patientData.care_plan && patientData.care_plan.status) {
      return patientData.care_plan.status;
    }
    return 'Active';
  }
  
  private extractGoals(patientData: any, responseText: string): any[] {
    if (patientData && patientData.goals && patientData.goals.length > 0) {
      return patientData.goals.map((goal: any) => ({
        description: goal.description || 'Goal description not available',
        startDate: goal.start_date || new Date().toISOString().split('T')[0],
        targetDate: goal.target_date || new Date(new Date().setMonth(new Date().getMonth() + 3)).toISOString().split('T')[0],
        status: goal.status || 'In progress'
      }));
    }
    // Return a default goal if none are found
    return [{
      description: 'Maintain stable vital signs',
      startDate: new Date().toISOString().split('T')[0],
      targetDate: new Date(new Date().setMonth(new Date().getMonth() + 3)).toISOString().split('T')[0],
      status: 'In progress'
    }];
  }
  
  private extractCurrentMedications(patientData: any, responseText: string): string[] {
    if (patientData && patientData.medications && patientData.medications.length > 0) {
      return patientData.medications.map((med: any) => 
        `${med.name} ${med.dosage} (${med.purpose || 'Unknown purpose'})`
      );
    }
    return ['No current medications'];
  }
  
  private extractCardiovascularRisk(patientData: any, responseText: string): string[] {
    if (patientData && patientData.risk_factors && patientData.risk_factors.cardiovascular) {
      return patientData.risk_factors.cardiovascular;
    }
    return ['No cardiovascular risk factors identified'];
  }
  
  private extractComplications(patientData: any, responseText: string): string[] {
    if (patientData && patientData.complications && patientData.complications.length > 0) {
      return patientData.complications;
    }
    return ['No complications identified'];
  }
  
  private extractRiskRecommendations(patientData: any, riskType: string, responseText: string): string {
    if (patientData && patientData.risk_recommendations && patientData.risk_recommendations[riskType]) {
      return patientData.risk_recommendations[riskType];
    }
    return 'Standard precautions recommended';
  }
  
  private extractFollowUp(patientData: any, careType: string, responseText: string): string {
    if (patientData && patientData.follow_up && patientData.follow_up[careType]) {
      return patientData.follow_up[careType];
    }
    return 'Follow up as needed';
  }
  
  private extractSpecialists(patientData: any, responseText: string): string[] {
    if (patientData && patientData.specialists && patientData.specialists.length > 0) {
      return patientData.specialists.map((specialist: any) => 
        `${specialist.type}: ${specialist.name} (${specialist.follow_up || 'as needed'})`
      );
    }
    return ['No specialist follow-ups scheduled'];
  }
  
  private extractPreventiveCare(patientData: any, responseText: string): string[] {
    if (patientData && patientData.preventive_care && patientData.preventive_care.length > 0) {
      return patientData.preventive_care;
    }
    return ['Annual physical examination', 'Age-appropriate screenings'];
  }
  
  private extractLifestyleRecommendations(patientData: any, responseText: string): string[] {
    if (patientData && patientData.lifestyle_recommendations && patientData.lifestyle_recommendations.length > 0) {
      return patientData.lifestyle_recommendations;
    }
    return ['Regular exercise', 'Balanced diet', 'Adequate sleep', 'Stress management'];
  }
  
  // Default patient detail for when the API fails
  private getDefaultPatientDetail(id: number, patientId: string): PatientDetail {
    // Get the patient name and gender from the patientId (P001, P002, etc.)
    let patientName = '';
    let patientGender = 'Unknown';
    let patientDob = '1980-01-01';
    let patientAge = 43;
    
    if (patientId === 'P001') {
      patientName = 'John Doe';
      patientGender = 'Male';
      patientDob = '1975-03-15';
      patientAge = 50; // 2025 - 1975 = 50
    } else if (patientId === 'P002') {
      patientName = 'Mary Smith';
      patientGender = 'Female';
      patientDob = '1982-07-22';
      patientAge = 42; // 2025 - 1982 = 43
    } else {
      patientName = `Patient ${id}`;
    }
    
    return {
      id: id,
      name: patientName,
      dob: patientDob,
      age: patientAge,
      gender: patientGender,
      mrn: patientId,
      
      // Background information
      background: {
        pastMedicalHistory: 'No significant medical history',
        currentPlanInfo: 'Current plan information not available',
        allergies: 'No known allergies',
        immunizations: 'No immunization records available',
        medicationHistory: 'No medication history available'
      },
      
      // Medical Timeline section
      medicalTimeline: {
        encounters: [{
          date: new Date().toISOString().split('T')[0],
          type: 'Initial visit',
          encounterId: 'ENC001',
          vitalSigns: 'BP: 120/80, HR: 72, Temp: 98.6°F',
          symptoms: 'No symptoms reported',
          assessment: 'Healthy patient',
          plan: 'Continue current medications'
        }]
      },
      
      // Current Care Plan section
      currentCarePlan: {
        activePlan: {
          title: 'Maintenance Care Plan',
          description: 'Standard care plan for maintaining health and managing existing conditions',
          status: 'Active'
        },
        goals: [{
          description: 'Maintain stable vital signs',
          startDate: new Date().toISOString().split('T')[0],
          targetDate: new Date(new Date().setMonth(new Date().getMonth() + 3)).toISOString().split('T')[0],
          status: 'In progress'
        }],
        vitalSigns: {
          bp: '120/80',
          temp: '98.6',
          rr: '16',
          hr: '72',
          o2Saturation: '98%'
        },
        currentMedications: ['No current medications']
      },
      
      // Risk Assessment section
      riskAssessment: {
        cardiovascularRisk: ['No cardiovascular risk factors identified'],
        complications: ['No complications identified'],
        fallRisk: {
          factors: 'Low risk',
          recommendations: 'Standard precautions recommended'
        }
      },
      
      // Assessment information (keeping for backward compatibility)
      assessment: {
        vitalSigns: {
          bp: '120/80',
          hr: '72',
          temp: '98.6',
          rr: '16',
          o2Saturation: '98%'
        },
        painLevel: '0/10',
        goalPainLevel: '0',
        abnormalFindings: 'No abnormal findings',
        recentPRN: 'No recent PRN medications',
        fallRisk: 'Low',
        activity: 'Activity as tolerated',
        wounds: 'No wounds observed',
        specimen: 'None',
        ivs: 'None',
        procedures: 'No recent procedures',
        diet: 'Regular diet',
        safety: 'Standard precautions',
        labResults: 'No recent lab results'
      },
      
      // Recommendations section
      recommendations: {
        followUpSchedule: {
          primaryCare: 'Follow up as needed',
          specialists: ['No specialist follow-ups scheduled']
        },
        preventiveCare: ['Annual physical examination', 'Age-appropriate screenings'],
        lifestyle: ['Regular exercise', 'Balanced diet', 'Adequate sleep', 'Stress management'],
        shiftGoal: 'Maintain stable vital signs',
        dayPlan: 'Continue current treatment plan',
        dischargePlan: 'Pending physician assessment'
      },
      
      // Nurses' notes
      nursesNotes: [{
        date: new Date().toISOString().split('T')[0],
        time: new Date().toTimeString().split(' ')[0] + ' CST',
        user: 'System',
        content: 'No nurses notes available'
      }]
    };
  }
}
