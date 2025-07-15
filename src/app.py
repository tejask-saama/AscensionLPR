from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import time
import json
import uuid
from src.services.query_processor import QueryProcessor
from src.services.knowledge_graph import KnowledgeGraphService
from src.services.llm_service import LLMService
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Patient Query API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageHistory(BaseModel):
    content: str
    sender: str
    messageId: str

class QueryRequest(BaseModel):
    query: str
    patientId: str
    conversationId: Optional[str] = None
    messageId: str
    conversationHistory: List[MessageHistory] = []

class LPRRequest(BaseModel):
    patient_id: str

class LPRResponse(BaseModel):
    response: Any  # Can be either string or dictionary
    metadata: Dict[str, Any] = {
        "generation_time": 0.0
    }

class QueryResponse(BaseModel):
    response: str
    conversation_id: str
    message_id: str
    metadata: Dict[str, Any] = {
        "type": "natural_language",
        "generation_time": 0.0,
        "query": "",
        "conversation_length": 0
    }

kg_service = None
llm_service = None

@app.on_event("startup")
async def startup_event():
    global kg_service, llm_service
    print("Initializing services...")
    llm_service = LLMService()
    kg_service = KnowledgeGraphService()
    await kg_service.initialize()
    print("Services initialized")

@app.on_event("shutdown")
async def shutdown_event():
    if kg_service:
        await kg_service.close()

@app.post("/api/patient/lpr", response_model=LPRResponse)
async def process_patient_lpr(request: LPRRequest):
    """
    Process a patient query and return relevant information based on the query intent.
    """
    print(f"\nReceived request: {request}")
    start_time = time.time()
    
    try:
        # Use global services
        query_processor = QueryProcessor(llm_service, kg_service)
        # Process the query
        print(f"Processing LPR for patient: {request.patient_id}")
        response = await query_processor.process_lpr("LPR", request.patient_id)
        
        # Add generation time to metadata
        if "metadata" not in response:
            response["metadata"] = {}
        response["metadata"]["generation_time"] = round(time.time() - start_time, 2)
        
        # Validate response structure
        print("Response before validation in patient_lpr:", response)
        
        # Ensure all required fields exist
        response.setdefault("response", "No response available")
        
        print("Final response in lpr data:", response)
        return response
        
    except Exception as e:
        import traceback
        print(f"Error processing request: {str(e)}")
        print("Traceback:", traceback.format_exc())
        raise

@app.post("/api/patient/query", response_model=QueryResponse)
async def process_patient_query(request: QueryRequest):
    """
    Process a patient query and return relevant information based on the query intent.
    """
    print(f"\nReceived request: {request}")
    start_time = time.time()
    
    try:
        query_processor = QueryProcessor(llm_service, kg_service)
        
        # Process the query with conversation context
        print(f"Processing query for patient: {request.patientId}")
        response = await query_processor.process_query(
            query=request.query,
            patient_id=request.patientId,
            conversation_id=request.conversationId,
            message_id=request.messageId,
            conversation_history=[{
                'content': msg.content,
                'sender': msg.sender,
                'message_id': msg.messageId  # Convert to snake_case for internal use
            } for msg in request.conversationHistory]
        )
        
        print("Response received:", response)
        
        # Ensure response has required fields
        if not isinstance(response, dict):
            response = {
                "response": str(response),
                "conversation_id": request.conversationId or str(uuid.uuid4()),
                "message_id": request.messageId,
                "metadata": {}
            }
        
        # Add generation time and query to metadata
        if "metadata" not in response:
            response["metadata"] = {}
        response["metadata"].update({
            "generation_time": round(time.time() - start_time, 2),
            "query": request.query,
            "type": "natural_language",
            "conversation_length": len(request.conversationHistory) + 1
        })
        
        return response
        
    except Exception as e:
        import traceback
        print(f"Error processing request: {str(e)}")
        print("Traceback:", traceback.format_exc())
        raise


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
