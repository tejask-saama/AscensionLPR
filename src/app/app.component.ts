import { Component, OnInit, HostListener } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'Longitudinal Patient Record';
  isLoggedIn = false;
  isLoginPage = false;
  isHistoryPage = false;
  isPatientsListPage = false;
  currentUser: any = null;
  showProfileMenu = false;
  
  constructor(
    private router: Router,
    private authService: AuthService
  ) {}
  
  ngOnInit(): void {
    // Check login status on route changes
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe(() => {
      this.checkLoginStatus();
    });
    
    // Initial check
    this.checkLoginStatus();
    
    // Subscribe to auth changes
    this.authService.currentUser.subscribe(user => {
      this.currentUser = user;
      this.isLoggedIn = !!user;
    });
  }
  
  private checkLoginStatus(): void {
    this.isLoggedIn = this.authService.isLoggedIn();
    this.isLoginPage = this.router.url.includes('/login');
    this.isHistoryPage = this.router.url.includes('/history');
    this.isPatientsListPage = this.router.url === '/patients';
  }
  
  toggleProfileMenu(): void {
    this.showProfileMenu = !this.showProfileMenu;
  }
  
  viewProfile(): void {
    // For demo purposes, we'll just close the menu
    this.showProfileMenu = false;
    // In a real app, you would navigate to the profile page
    // this.router.navigate(['/profile']);
  }
  
  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
  
  // Close the dropdown when clicking outside
  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    const userInfoElement = document.querySelector('.user-info');
    
    if (userInfoElement && !userInfoElement.contains(target)) {
      this.showProfileMenu = false;
    }
  }
}
