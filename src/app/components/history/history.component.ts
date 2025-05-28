import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { PatientService } from '../../services/patient.service';
import { PatientDetail } from '../../models/patient.model';

@Component({
  selector: 'app-history',
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.scss']
})
export class HistoryComponent implements OnInit {
  patientId!: number;
  patient: PatientDetail | null = null;
  loading = false;
  error = '';
  activeTab: 'today' | 'previous' = 'today';
  historyEntries: any[] = []; // This would be replaced with a proper type
  summaries: any[] = [];
  expandedSummaries: { [key: string]: boolean } = {};

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private patientService: PatientService
  ) { }

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.patientId = +params['id'];
      this.loadPatientDetails();
      this.loadHistoryData();
    });
  }

  loadPatientDetails(): void {
    this.loading = true;
    this.patientService.getPatientDetail(this.patientId)
      .subscribe({
        next: (data) => {
          this.patient = data;
          this.loading = false;
        },
        error: (error) => {
          this.error = 'Error loading patient details. Please try again.';
          this.loading = false;
          console.error('Error loading patient details:', error);
        }
      });
  }

  loadHistoryData(): void {
    // Mock data for today's revisions
    this.historyEntries = [
      {
        time: '16:20 CST',
        nurse: 'Alexis Smith, RN',
        section: 'BACKGROUND',
        content: {
          title: 'Past Medical History',
          text: 'History of GI bleed due to esophageal varices, hypertension, hepatic mass, cirosis, HCC, hepatitis C (completed treatment), esophageal banding, appendectomy, tonsillectomy, adenoidectomy. Hospitalized in December 2024 for hemoptysis, during which a 7 cm liver mass and pulmonary nodules (suggestive of metastatic disease) were discovered. Biopsy confirmed metastatic HCC. Discharged on 2L NC continuous. Reined first immunotherapy treatment on 1/13/2025.'
        }
      },
      {
        time: '07:15 CST',
        nurse: 'Alexis Smith, RN',
        section: 'ASSESSMENT',
        content: {
          vitalSigns: {
            bp: '114/72',
            hr: '88',
            temp: '37 °C (oral)',
            rr: '18',
            o2: '92% on 4L NC'
          },
          painLevel: {
            current: 'Not specified in most recent notes, previously reported pain improvement',
            goal: 'Not specified'
          },
          findings: 'Black, bloody stools. Chronic hemoptysis with small episodes overnight. Course rhonchi in bilateral lower lobes. Labs: Hb 10.3 (low), Hct 32.5% (low), Plts 99 (low), INR 1.6 (high), Lactic acid 5.2 (critical on 2/26, not repeated)',
          activity: 'Independent ambulation to bathroom with assistance. Independent movement in bed.',
          specimen: 'Sputum, legionella, Strep urine antigen ordered by Pulmonary.',
          ivs: 'Octreotide drip (50 mcg/hr) in NS, LR at 126 mL/hr',
          procedures: 'Recent EGD with banding of esophageal varices'
        }
      },
      {
        time: '06:45 CST',
        nurse: 'Alexis Smith, RN',
        section: 'BACKGROUND',
        content: {
          title: 'Past Medical History',
          text: 'History of GI bleed due to esophageal varices, hypertension, hepatic mass, cirosis, HCC, hepatitis C (completed treatment), esophageal banding, appendectomy, tonsillectomy, adenoidectomy. Hospitalized in December 2024 for hemoptysis, during which a 7 cm liver mass and pulmonary nodules (suggestive of metastatic disease) were discovered. Biopsy confirmed metastatic HCC. Discharged on 2L NC continuous. Reined first immunotherapy treatment on 1/13/2025.'
        }
      },
      {
        time: '06:45 CST',
        nurse: 'Alexis Smith, RN',
        section: 'RECOMMENDATIONS',
        content: {
          shiftGoal: 'Monitor hemodynamic stability, respiratory status (including hemoptysis), and GI bleeding. Maintain oxygen saturation >92%. Manage pain.',
          dayPlan: 'Continue current IV medications. Monitor labs (CBC, coags). Pulmonary recommends continuing Pulmicort and DuoNeb, resuming Trelegy on discharge. Continue Zosyn per ID. Avoid anticoagulation/antiplatelet therapy. GI and Heme/Onc following',
          dischargePlan: {
            destination: 'Likely discharge tomorrow if stable and cleared by GI and Pulmonary',
            needs: 'oxygen, medications (Trelegy, pulmicort, DuoNeb), potential home health services depending on stability and needs assessment. Clarify discharge plan with MD'
          }
        }
      }
    ];

    // Mock data for previous summaries
    this.summaries = [
      {
        date: '02/28/2025',
        time: '06:45 CST',
        expanded: false,
        content: {
          background: {
            title: 'Past Medical History',
            text: 'History of GI bleed due to esophageal varices, hypertension, hepatic mass, cirosis, HCC, hepatitis C (completed treatment), esophageal banding, appendectomy, tonsillectomy, adenoidectomy. Hospitalized in December 2024 for hemoptysis, during which a 7 cm liver mass and pulmonary nodules (suggestive of metastatic disease) were discovered. Biopsy confirmed metastatic HCC. Discharged on 2L NC continuous. Reined first immunotherapy treatment on 1/13/2025.'
          },
          currentPlan: {
            title: 'Information Leading to Current Plan of Care',
            text: 'Prescribed NS for PO intolerance, recent hemoptysis. Aggressive bronchial and pulmonary toileting. Hemoptysis ongoing. Reported using old, unsealed water in his home oxygen humidifier. ED findings included significant lactic acidosis. CTA showed no acute GI bleed, but did show hepatic metastasis, wall thickening in colon concerning for colitis, and cirrhotic liver. CT showed interval progression of pulmonary nodules. Admitted for workup and management. GI, Heme/Onc, and Pulmonary consults obtained. EGD on 1/21/25 revealed and banded 6 esophageal varices.'
          }
        },
        assessment: {
          vitalSigns: {
            bp: '114/72',
            hr: '88',
            temp: '37 °C (oral)',
            rr: '18',
            o2: '92% on 4L NC'
          },
          painLevel: {
            current: 'Not specified in most recent notes, previously reported pain improvement',
            goal: 'Not specified'
          },
          findings: 'Black, bloody stools. Chronic hemoptysis with small episodes overnight. Course rhonchi in bilateral lower lobes. Labs: Hb 10.3 (low), Hct 32.5% (low), Plts 99 (low), INR 1.6 (high), Lactic acid 5.2 (critical on 2/26, not repeated)',
          prnMeds: 'Not specified in recent notes',
          fallRating: 'Not specified - assess and document',
          activity: 'Independent ambulation to bathroom with assistance. Independent movement in bed.',
          wounds: 'Not specified. Monitor for post-EGD complications.',
          specimen: 'Sputum, legionella, Strep urine antigen ordered by Pulmonary.',
          ivs: 'Octreotide drip (50 mcg/hr) in NS, LR at 126 mL/hr',
          procedures: 'Recent EGD with banding of esophageal varices',
          diet: 'Advance to full liquid diet post-EGD',
          safety: 'Bed alarm on in low position. Call light and personal items within reach.',
          labResults: 'See "abnormal/pertinent findings."'
        },
        recommendations: {
          shiftGoal: 'Monitor hemodynamic stability, respiratory status (including hemoptysis), and GI bleeding. Maintain oxygen saturation >92%. Manage pain.',
          dayPlan: 'Continue current IV medications. Monitor labs (CBC, coags). Pulmonary recommends continuing Pulmicort and DuoNeb, resuming Trelegy on discharge. Continue Zosyn per ID. Avoid anticoagulation/antiplatelet therapy. GI and Heme/Onc following',
          dischargePlan: {
            destination: 'Likely discharge tomorrow if stable and cleared by GI and Pulmonary',
            needs: 'oxygen, medications (Trelegy, pulmicort, DuoNeb), potential home health services depending on stability and needs assessment. Clarify discharge plan with MD'
          }
        }
      },
      {
        date: '02/27/2025',
        time: '06:45 CST',
        expanded: false
      },
      {
        date: '02/26/2025',
        time: '06:45 CST',
        expanded: false
      }
    ];
  }

  setActiveTab(tab: 'today' | 'previous'): void {
    this.activeTab = tab;
  }

  toggleSummary(index: number): void {
    const key = this.summaries[index].date;
    this.expandedSummaries[key] = !this.expandedSummaries[key];
  }

  expandAllSummaries(): void {
    this.summaries.forEach(summary => {
      this.expandedSummaries[summary.date] = true;
    });
  }

  backToHome(): void {
    this.router.navigate(['/patients', this.patientId]);
  }
}
