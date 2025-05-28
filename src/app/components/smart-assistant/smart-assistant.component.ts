import { Component, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { ActivatedRoute, Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { SmartAssistantService, ChatMessage } from '../../services/smart-assistant.service';

@Component({
  selector: 'app-smart-assistant',
  templateUrl: './smart-assistant.component.html',
  styleUrls: ['./smart-assistant.component.scss']
})
export class SmartAssistantComponent implements OnInit, AfterViewChecked {
  @ViewChild('chatContainer') private chatContainer: ElementRef;
  isExpanded = false; // Start collapsed by default
  showChatModal = false; // Modal is hidden by default
  currentPatientId: number | null = null;
  question = '';
  chatMessages: ChatMessage[] = [];
  loading = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private smartAssistantService: SmartAssistantService
  ) { }

  // Flag to track if we need to scroll to bottom
  private shouldScrollToBottom = false;

  ngAfterViewChecked() {
    if (this.shouldScrollToBottom && this.chatContainer) {
      this.scrollToBottom();
      this.shouldScrollToBottom = false;
    }
  }

  // Helper method to scroll to the bottom of the chat
  private scrollToBottom(): void {
    try {
      this.chatContainer.nativeElement.scrollTop = this.chatContainer.nativeElement.scrollHeight;
    } catch (err) {
      console.error('Error scrolling to bottom:', err);
    }
  }

  ngOnInit(): void {
    // Listen for route changes to update current patient ID
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe(() => {
      this.updateCurrentPatientId();
    });

    // Initial check for patient ID
    this.updateCurrentPatientId();
  }

  private updateCurrentPatientId(): void {
    const urlSegments = this.router.url.split('/');
    if (urlSegments.length > 2 && (urlSegments[1] === 'patients' || urlSegments[1] === 'history')) {
      const patientId = parseInt(urlSegments[2], 10);
      if (!isNaN(patientId)) {
        // Only update chat messages if patient ID has changed
        if (this.currentPatientId !== patientId) {
          this.currentPatientId = patientId;
          this.chatMessages = this.smartAssistantService.getChatHistory(patientId);
        }
      }
    } else {
      this.currentPatientId = null;
    }
  }

  toggleExpand(): void {
    this.isExpanded = !this.isExpanded;
  }
  
  selectQuickOption(questionText: string): void {
    this.question = questionText;
    this.sendQuestion();
  }

  clearChat(): void {
    if (this.currentPatientId) {
      if (confirm('Are you sure you want to clear the conversation history?')) {
        this.smartAssistantService.clearChatHistory(this.currentPatientId);
        this.chatMessages = [];
      }
    }
  }
  
  editLastMessage(): void {
    if (!this.currentPatientId || this.chatMessages.length === 0) {
      return;
    }
    
    // Find the last user message
    const userMessages = this.chatMessages.filter(msg => msg.type === 'user');
    if (userMessages.length === 0) {
      return;
    }
    
    const lastUserMessage = userMessages[userMessages.length - 1];
    const newQuestion = prompt('Edit your message:', lastUserMessage.content);
    
    if (newQuestion && newQuestion.trim() && newQuestion !== lastUserMessage.content) {
      // Update the message
      this.smartAssistantService.editUserMessage(this.currentPatientId, lastUserMessage, newQuestion.trim());
      this.chatMessages = this.smartAssistantService.getChatHistory(this.currentPatientId);
      
      // Re-send the question
      this.loading = true;
      this.smartAssistantService.askQuestion(newQuestion.trim(), this.currentPatientId)
        .subscribe({
          next: (response) => {
            // Add assistant message to chat
            this.smartAssistantService.addAssistantMessage(this.currentPatientId!, response.answer);
            this.chatMessages = this.smartAssistantService.getChatHistory(this.currentPatientId!);
            this.loading = false;
            
            // Scroll to bottom of chat
            setTimeout(() => {
              this.scrollToBottom();
            }, 100);
          },
          error: (error) => {
            console.error('Error getting assistant response:', error);
            this.smartAssistantService.addAssistantMessage(
              this.currentPatientId!, 
              'Sorry, I encountered an error. Please try again.'
            );
            this.chatMessages = this.smartAssistantService.getChatHistory(this.currentPatientId!);
            this.loading = false;
          }
        });
    }
  }

  closeAssistant(): void {
    // This method is kept for compatibility but doesn't do anything now
    // since the assistant is always visible
  }

  sendQuestion(): void {
    // Prevent empty questions or when no patient is selected
    if (!this.question?.trim() || !this.currentPatientId) {
      return;
    }

    const questionText = this.question.trim();
    this.loading = true;

    // Add user message to chat
    this.smartAssistantService.addUserMessage(this.currentPatientId, questionText);
    this.chatMessages = this.smartAssistantService.getChatHistory(this.currentPatientId);
    
    // Clear input immediately
    this.question = '';
    
    // Set flag to scroll to bottom after view is updated
    this.shouldScrollToBottom = true;
    
    // We'll let ngAfterViewChecked handle the scrolling

    // Get response from API
    this.smartAssistantService.askQuestion(questionText, this.currentPatientId)
      .subscribe({
        next: (response) => {
          console.log('Component received response:', response);
          console.log('Response answer type:', typeof response.answer);
          
          // Make sure we have a string to display
          let answerText = response.answer;
          if (typeof answerText !== 'string') {
            answerText = JSON.stringify(answerText);
          }
          
          // Add assistant message to chat
          this.smartAssistantService.addAssistantMessage(this.currentPatientId!, answerText);
          this.chatMessages = this.smartAssistantService.getChatHistory(this.currentPatientId!);
          this.loading = false;
          
          // Set flag to scroll to bottom after view is updated
          this.shouldScrollToBottom = true;
        },
        error: (error) => {
          console.error('Error getting assistant response:', error);
          this.smartAssistantService.addAssistantMessage(
            this.currentPatientId!, 
            'Sorry, I encountered an error. Please try again.'
          );
          this.chatMessages = this.smartAssistantService.getChatHistory(this.currentPatientId!);
          this.loading = false;
        }
      });
  }

  selectSuggestion(suggestion: string): void {
    this.question = suggestion;
    this.sendQuestion();
  }

  // scrollToBottom method is now implemented above

  formatTime(date: Date): string {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' CST';
  }
  
  shouldShowTimestamp(currentMessage: ChatMessage, previousMessage: ChatMessage): boolean {
    if (!previousMessage) return true;
    
    // Show timestamp if messages are more than 5 minutes apart
    const fiveMinutes = 5 * 60 * 1000;
    return currentMessage.timestamp.getTime() - previousMessage.timestamp.getTime() > fiveMinutes;
  }
  
  copyToClipboard(text: string): void {
    navigator.clipboard.writeText(text)
      .then(() => {
        // Show a brief notification that text was copied
        alert('Text copied to clipboard');
      })
      .catch(err => {
        console.error('Could not copy text: ', err);
      });
  }
  
  // Modal methods
  openChatModal(): void {
    this.showChatModal = true;
    // Prevent body scrolling when modal is open
    document.body.style.overflow = 'hidden';
    // The expanded container will be hidden via the *ngIf condition
  }
  
  closeChatModal(event: MouseEvent): void {
    // Only close if clicking on the overlay or close button
    if (
      (event.target as HTMLElement).classList.contains('chat-modal-overlay') ||
      (event.target as HTMLElement).closest('.action-button.close')
    ) {
      this.showChatModal = false;
      // Restore body scrolling
      document.body.style.overflow = 'auto';
      // Make sure the expanded container is visible
      this.isExpanded = true;
      // Stop event propagation
      event.stopPropagation();
    }
  }
}
