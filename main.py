"""
Main entry point for the Patient Query API application.
"""
import uvicorn
from src.app import app

if __name__ == "__main__":
    print("Starting Patient Query API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
