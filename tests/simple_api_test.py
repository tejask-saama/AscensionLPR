"""
Simple test script to test the Patient Query API with a specific payload.
"""
import requests
import json
import time

def test_patient_query_api():
    """
    Send a test request to the Patient Query API and print the response.
    """
    # API endpoint URL
    url = "http://localhost:8000/api/patient/query"
    
    # Request payload
    payload = {
        "query": "Longitudinal Patient Record",
        "patient_id": "a4a2eaf4-3e41-471c-aea5-89497add41d9"
    }
    
    # Headers
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Sending request to {url} with payload: {json.dumps(payload, indent=2)}")
    start_time = time.time()
    
    try:
        # Send POST request
        response = requests.post(url, json=payload, headers=headers)
        
        # Print status code
        print(f"Status Code: {response.status_code}")
        
        # Print elapsed time
        elapsed_time = time.time() - start_time
        print(f"Request completed in {elapsed_time:.2f} seconds")
        
        # Print response data regardless of status code
        print("Response:")
        try:
            response_data = response.json()
            print(json.dumps(response_data, indent=2))
        except json.JSONDecodeError:
            print(f"Raw response: {response.text}")
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    test_patient_query_api()
