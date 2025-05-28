import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface AssistantQuestion {
  question: string;
  patientId: number;
}

export interface AssistantResponse {
  answer: string;
}

export interface ChatMessage {
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ApiResponse<T> {
  status: string;
  data: T;
  message?: string;
}

interface LprApiResponse {
  patient_id: string;
  query: string;
  response: string;
  patient_data: any;
  reflection: string;
  processing_time_seconds: number;
}

@Injectable({
  providedIn: 'root'
})
export class SmartAssistantService {
  private apiUrl = environment.apiUrl;
  private chatHistory: Map<number, ChatMessage[]> = new Map();

  constructor(private http: HttpClient) { }
  
  askQuestion(question: string, patientId: number): Observable<AssistantResponse> {
    // Convert numeric ID to format expected by API (P001, P002, etc.)
    const formattedPatientId = `P${patientId.toString().padStart(3, '0')}`;
    
    console.log('Asking question to API:', question, 'for patient:', formattedPatientId);
    
    // Call the API and pass the clinical question and patient ID
    const payload = {
      patient_id: formattedPatientId,
      query: question
    };
    
    // Use the correct API endpoint matching the Streamlit application
    const url = `${this.apiUrl}/lpr-app/lpr`;
    console.log('Request payload:', payload);
    console.log('API endpoint:', url);
    
    return this.http.post<ApiResponse<LprApiResponse>>(url, payload)
      .pipe(
        map(response => {
          console.log('Smart assistant API response:', response);
          console.log('Response type:', typeof response);
          console.log('Response data type:', typeof response.data);
          console.log('Response data:', JSON.stringify(response.data, null, 2));
          
          if (response && response.status === 'success' && response.data) {
            // Extract the answer from the response
            let answer = 'No response available';
            
            // Check if the response is a structured object with a 'response' field
            if (response.data.response) {
              if (typeof response.data.response === 'string') {
                // If it's already a string, use it directly
                answer = response.data.response;
              } else if (typeof response.data.response === 'object' && response.data.response !== null) {
                // If the response itself is an object with a 'response' field
                const responseObj = response.data.response as any;
                if (responseObj.response) {
                  answer = responseObj.response;
                } else {
                  // Otherwise stringify the object
                  answer = JSON.stringify(responseObj);
                }
              }
            }
            
            console.log('Extracted answer type:', typeof answer);
            console.log('Extracted answer:', answer);
            
            return {
              answer: answer
            };
          } else {
            console.error('API error response:', response);
            throw new Error(response?.message || 'Error processing query');
          }
        }),
        catchError(error => {
          console.error('Error asking question:', error);
          return of({ answer: 'Sorry, I encountered an error processing your question. Please try again later.' });
        })
      );
  }

  addUserMessage(patientId: number, content: string): void {
    this.addMessage(patientId, 'user', content);
  }

  addAssistantMessage(patientId: number, content: string): void {
    this.addMessage(patientId, 'assistant', content);
  }
  
  editUserMessage(patientId: number, message: ChatMessage, newContent: string): void {
    if (!this.chatHistory.has(patientId)) {
      return;
    }
    
    const messages = this.chatHistory.get(patientId)!;
    const index = messages.indexOf(message);
    
    if (index !== -1) {
      // Update the message content
      messages[index].content = newContent;
      
      // If there's a response after this message, remove it so we can get a new response
      if (index + 1 < messages.length && messages[index + 1].type === 'assistant') {
        messages.splice(index + 1, 1);
      }
    }
  }

  private addMessage(patientId: number, type: 'user' | 'assistant', content: string): void {
    if (!this.chatHistory.has(patientId)) {
      this.chatHistory.set(patientId, []);
    }
    
    const message: ChatMessage = {
      type,
      content,
      timestamp: new Date()
    };
    
    this.chatHistory.get(patientId)?.push(message);
  }

  getChatHistory(patientId: number): ChatMessage[] {
    return this.chatHistory.get(patientId) || [];
  }

  clearChatHistory(patientId: number): void {
    this.chatHistory.set(patientId, []);
  }
}
