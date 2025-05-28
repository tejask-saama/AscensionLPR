import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { PatientService } from '../../services/patient.service';
import { PatientDetail } from '../../models/patient.model';

@Component({
  selector: 'app-patient-detail',
  templateUrl: './patient-detail.component.html',
  styleUrls: ['./patient-detail.component.scss']
})
export class PatientDetailComponent implements OnInit {
  patientId!: number;
  patient: PatientDetail | null = null;
  loading = false;
  error = '';
  activeSection: 'background' | 'assessment' | 'recommendations' | 'notes' = 'background';
  expandedSuggestions: { [key: string]: boolean } = {
    background: false,
    assessment: false,
    recommendations: false,
    notes: false
  };

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private patientService: PatientService
  ) { }

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.patientId = +params['id'];
      this.loadPatientDetails();
    });
  }

  loadPatientDetails(): void {
    this.loading = true;
    console.log('Loading patient details for ID:', this.patientId);
    this.patientService.getPatientDetail(this.patientId)
      .subscribe({
        next: (data) => {
          console.log('Patient detail data received:', data);
          this.patient = data;
          this.loading = false;
          console.log('Patient data set in component:', this.patient);
        },
        error: (error) => {
          this.error = 'Error loading patient details. Please try again.';
          this.loading = false;
          console.error('Error loading patient details:', error);
        }
      });
  }

  checkForUpdates(): void {
    this.loadPatientDetails();
  }
  
  toggleSuggestions(section: 'background' | 'assessment' | 'recommendations' | 'notes'): void {
    // Toggle the suggestions panel for the given section
    this.expandedSuggestions[section] = !this.expandedSuggestions[section];
  }

  editSection(section: string, event: Event): void {
    // Stop the event from propagating to the section header
    event.stopPropagation();
    
    // Implement edit logic for the specific section
    console.log(`Editing ${section} section...`);
    
    // You can add specific edit functionality for each section here
    switch(section) {
      case 'background':
        // Edit background section
        break;
      case 'assessment':
        // Edit assessment section
        break;
      case 'recommendations':
        // Edit recommendations section
        break;
      default:
        break;
    }
  }

  setActiveSection(section: 'background' | 'assessment' | 'recommendations' | 'notes'): void {
    // Set the active section
    this.activeSection = section;
  }

  addNewNote(event: Event): void {
    // Stop the event from propagating to the section header
    event.stopPropagation();
    
    // Implement add new note functionality
    console.log('Adding new nurse note...');
    // Here you would typically open a modal or form to add a new note
    // For now, we'll just log a message
  }
  
  openSuggestions(): void {
    // Implement suggestions functionality
    console.log('Open suggestions');
  }

  viewHistory(): void {
    // Redirect to the history page with the current patient ID
    this.router.navigate(['/history', this.patientId]);
  }

  printPatientInfo(): void {
    // Implement print functionality
    window.print();
  }
}
