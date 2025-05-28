import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { PatientService } from '../../services/patient.service';
import { Patient } from '../../models/patient.model';

@Component({
  selector: 'app-patient-list',
  templateUrl: './patient-list.component.html',
  styleUrls: ['./patient-list.component.scss']
})
export class PatientListComponent implements OnInit {
  patients: Patient[] = [];
  loading = false;
  error = '';
  selectedPatientId: number | null = null;

  constructor(
    private patientService: PatientService,
    private router: Router,
    private route: ActivatedRoute
  ) { }

  ngOnInit(): void {
    this.loadPatients();
    this.checkCurrentPatient();
    
    // Subscribe to route changes to update selected patient
    this.router.events.subscribe(() => {
      this.checkCurrentPatient();
    });
  }
  
  private checkCurrentPatient(): void {
    const urlParts = this.router.url.split('/');
    if (urlParts.length > 2 && urlParts[1] === 'patients') {
      const patientId = parseInt(urlParts[2], 10);
      if (!isNaN(patientId)) {
        this.selectedPatientId = patientId;
      }
    }
  }

  loadPatients(): void {
    this.loading = true;
    this.patientService.getPatients()
      .subscribe({
        next: (data) => {
          this.patients = data;
          this.loading = false;
        },
        error: (error) => {
          this.error = 'Error loading patients. Please try again.';
          this.loading = false;
          console.error('Error loading patients:', error);
        }
      });
  }

  selectPatient(id: number): void {
    this.selectedPatientId = id;
    this.router.navigate(['/patients', id]);
  }
}
