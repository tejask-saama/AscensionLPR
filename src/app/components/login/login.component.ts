import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  username = '';
  password = '';
  returnUrl = '';
  error = '';
  loading = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService
  ) {
    // Redirect to patients page if already logged in
    if (this.authService.currentUserValue) {
      this.router.navigate(['/patients']);
    }
  }

  ngOnInit(): void {
    // Get return url from route parameters or default to '/patients'
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/patients';
  }

  onSubmit(): void {
    this.error = '';
    this.loading = true;

    // Stop if form is invalid
    if (!this.username || !this.password) {
      this.error = 'Username and password are required';
      this.loading = false;
      return;
    }

    this.authService.login(this.username, this.password)
      .subscribe({
        next: () => {
          this.router.navigate([this.returnUrl]);
        },
        error: error => {
          this.error = error;
          this.loading = false;
        }
      });
  }
}
