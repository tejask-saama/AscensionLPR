# Patient Query API

This API accepts patient queries, analyzes the intent, retrieves relevant patient data from a Knowledge Graph, and generates structured responses using Azure OpenAI.

## Features

- Query intent classification using Azure OpenAI
- Template-based response generation based on intent type
- Knowledge Graph integration for comprehensive patient data access
- Structured API responses with clinical reasoning, recommendations, and provenance

## Setup

1. Configure environment variables in `.env`:

```
# Neo4j Knowledge Graph Connection
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_API_VERSION=2023-05-15
AZURE_OPENAI_DEPLOYMENT=gpt-4
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the API server:

```bash
python main.py
```

## API Usage

### Patient Query Endpoint

**Endpoint**: `POST /api/patient/query`

**Request Body**:
```json
{
    "query": "What medications is this patient taking?",
    "patient_id": "PT123456"
}
```

**Response**:
```json
{
    "response": "Patient John Doe is currently taking...",
    "clinical_reasoning": "The patient has been prescribed...",
    "recommendations": ["Consider follow-up in 3 months"],
    "provenance": ["Medication history from records dated 2023-02-15"],
    "limitations": ["Medication adherence data not available"],
    "metadata": {
        "intent": "MEDICATIONS",
        "generation_time": 1.25
    }
}
```

## Query Intent Types

The API supports the following query intents:

1. `CLINICAL_SUMMARY` - Overall patient health summary
2. `MEDICATIONS` - Current and past medications
3. `LAB_RESULTS` - Laboratory test results
4. `VITALS` - Vital signs like blood pressure, heart rate
5. `PROCEDURES` - Medical procedures and imaging
6. `FOLLOW_UPS` - Recommended follow-up actions
7. `TREATMENT_RECOMMENDATIONS` - Treatment plan recommendations

## Architecture

- `app.py`: FastAPI application and API endpoint definitions
- `services/query_processor.py`: Orchestrates the entire workflow
- `services/llm_service.py`: Azure OpenAI integration for intent detection and response generation
- `services/knowledge_graph.py`: Neo4j knowledge graph integration for patient data retrieval
- `templates/`: Response templates for different query intents

## Testing

Run unit tests:

```bash
python -m unittest discover
```
