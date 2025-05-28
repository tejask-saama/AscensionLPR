#!/usr/bin/env python3
"""
Longitudinal Patient Record (LPR) API Client

This script demonstrates how to fetch real-time patient data from the LPR API
and process the JSON response.
"""

import requests
import json
import time
from datetime import datetime
import argparse

BASE_URL = "http://localhost:3009"

def fetch_patient_list():
    """Fetch the list of all patients from the API."""
    url = f"{BASE_URL}/api/patients"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching patient list: {response.status_code}")
        return None

def fetch_patient_lpr(patient_id, use_realtime=True):
    """Fetch a patient's LPR data from the API.
    
    Args:
        patient_id (int): The ID of the patient
        use_realtime (bool): Whether to use the real-time API endpoint
        
    Returns:
        dict: The patient's LPR data
    """
    if use_realtime:
        url = f"{BASE_URL}/api/realtime/lpr/{patient_id}"
    else:
        url = f"{BASE_URL}/api/lpr/{patient_id}"
        
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching patient LPR: {response.status_code}")
        return None

def ask_assistant(patient_id, question):
    """Ask the smart assistant a question about a patient.
    
    Args:
        patient_id (int): The ID of the patient
        question (str): The question to ask
        
    Returns:
        dict: The assistant's response
    """
    url = f"{BASE_URL}/api/assistant"
    data = {
        "patientId": patient_id,
        "question": question
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error asking assistant: {response.status_code}")
        return None

def print_patient_summary(patient_data):
    """Print a summary of the patient's data."""
    if isinstance(patient_data, dict) and "data" in patient_data:
        # This is from the real-time API
        patient = patient_data["data"]
        print(f"\n=== REAL-TIME PATIENT DATA (Updated: {patient_data.get('timestamp', 'Unknown')}) ===")
    else:
        # This is from the standard API
        patient = patient_data
        print("\n=== PATIENT DATA ===")
    
    print(f"Name: {patient.get('name', 'Unknown')}")
    print(f"DOB: {patient.get('dob', 'Unknown')}")
    print(f"Age: {patient.get('age', 'Unknown')}")
    print(f"Gender: {patient.get('gender', 'Unknown')}")
    print(f"MRN: {patient.get('mrn', 'Unknown')}")
    
    # Print vital signs
    if "assessment" in patient and "vitalSigns" in patient["assessment"]:
        vitals = patient["assessment"]["vitalSigns"]
        print("\n--- Vital Signs ---")
        print(f"BP: {vitals.get('bp', 'Unknown')}")
        print(f"HR: {vitals.get('hr', 'Unknown')}")
        print(f"Temp: {vitals.get('temp', 'Unknown')}")
        print(f"RR: {vitals.get('rr', 'Unknown')}")
        print(f"O2 Saturation: {vitals.get('o2Saturation', 'Unknown')}")
    
    # Print latest nurse note
    if "nursesNotes" in patient and len(patient["nursesNotes"]) > 0:
        latest_note = patient["nursesNotes"][0]
        print("\n--- Latest Nurse Note ---")
        print(f"Date/Time: {latest_note.get('date', 'Unknown')} {latest_note.get('time', 'Unknown')}")
        print(f"User: {latest_note.get('user', 'Unknown')}")
        print(f"Content: {latest_note.get('content', 'Unknown')}")
    
    # Print lab results if available
    if "labResults" in patient and patient["labResults"]:
        print("\n--- Lab Results ---")
        for lab in patient["labResults"]:
            print(f"\n{lab.get('name', 'Unknown Test')} ({lab.get('timestamp', 'Unknown Time')})")
            for result in lab.get('results', []):
                flag_indicator = "⚠️ " if result.get('flag') == "high" or result.get('flag') == "low" else ""
                print(f"  {flag_indicator}{result.get('test', 'Unknown')}: {result.get('value', 'Unknown')} {result.get('unit', '')} ({result.get('reference', 'No ref')})")
    
    # Print medication administration if available
    if "medicationAdministration" in patient and patient["medicationAdministration"]:
        print("\n--- Recent Medications ---")
        for med in patient["medicationAdministration"]:
            print(f"  {med.get('medication', 'Unknown')} {med.get('dose', '')} {med.get('route', '')} - {med.get('date', 'Unknown')} {med.get('time', 'Unknown')}")

def monitor_patient_vitals(patient_id, interval=5, count=5):
    """Monitor a patient's vital signs in real-time.
    
    Args:
        patient_id (int): The ID of the patient
        interval (int): The interval in seconds between checks
        count (int): The number of checks to perform
    """
    print(f"Monitoring patient {patient_id} vitals every {interval} seconds for {count} checks...")
    
    for i in range(count):
        data = fetch_patient_lpr(patient_id, use_realtime=True)
        if data and "data" in data and "assessment" in data["data"] and "vitalSigns" in data["data"]["assessment"]:
            vitals = data["data"]["assessment"]["vitalSigns"]
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] BP: {vitals.get('bp', 'Unknown')}, HR: {vitals.get('hr', 'Unknown')}, O2: {vitals.get('o2Saturation', 'Unknown')}")
        else:
            print("Error fetching vital signs")
        
        if i < count - 1:  # Don't sleep after the last check
            time.sleep(interval)

def main():
    parser = argparse.ArgumentParser(description="LPR API Client")
    parser.add_argument("--list", action="store_true", help="List all patients")
    parser.add_argument("--patient", type=int, help="Patient ID to fetch")
    parser.add_argument("--monitor", action="store_true", help="Monitor patient vitals in real-time")
    parser.add_argument("--interval", type=int, default=5, help="Interval in seconds for monitoring")
    parser.add_argument("--count", type=int, default=5, help="Number of checks for monitoring")
    parser.add_argument("--standard", action="store_true", help="Use standard API instead of real-time")
    parser.add_argument("--question", type=str, help="Ask the assistant a question about the patient")
    
    args = parser.parse_args()
    
    if args.list:
        patients = fetch_patient_list()
        if patients:
            print("\n=== PATIENT LIST ===")
            for patient in patients:
                print(f"ID: {patient['id']}, Name: {patient['name']}, MRN: {patient['mrn']}")
    
    if args.patient:
        if args.question:
            response = ask_assistant(args.patient, args.question)
            if response:
                print(f"\n=== ASSISTANT RESPONSE ===")
                print(f"Question: {args.question}")
                print(f"Answer: {response.get('answer', 'No answer provided')}")
        elif args.monitor:
            monitor_patient_vitals(args.patient, args.interval, args.count)
        else:
            patient_data = fetch_patient_lpr(args.patient, use_realtime=not args.standard)
            if patient_data:
                print_patient_summary(patient_data)
    
    if not (args.list or args.patient):
        parser.print_help()

if __name__ == "__main__":
    main()
