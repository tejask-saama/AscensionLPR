import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

class QueryProcessor:
    """
    Service that orchestrates the entire query processing workflow:
    1. Fetch patient data from knowledge graph
    2. Generate response using LLM
    """
    
    def __init__(self, llm_service, kg_service):
        """
        Initialize the query processor with the required services.
        
        Args:
            llm_service: The LLM service for response generation
            kg_service: The Knowledge Graph service for fetching patient data
        """
        self.llm_service = llm_service
        self.kg_service = kg_service
        self.templates_dir = "templates"
    
    def load_template(self):
        """
        Load the default template for patient data.
        
        Returns:
            str: The template content
        """
        template_path = os.path.join(self.templates_dir, "longitudinal_patient_record.json")
        
        try:
            with open(template_path, "r") as file:
                return file.read()
        except Exception as e:
            print(f"Error loading template {template_path}: {str(e)}")
            # Return a basic template as fallback
            return "Please provide a detailed response to the following query based on the patient's data."
    
    async def process_db_query(self, query: str, patient_id: str, conversation_id: str = None, message_id: str = None, conversation_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a natural language query using data fetched directly from the database.
        
        Args:
            query (str): The user's query
            patient_id (str): The patient ID to fetch data for
            conversation_id (str, optional): ID of the ongoing conversation
            message_id (str, optional): ID of the current message
            conversation_history (List[Dict], optional): Previous messages in the conversation
            
        Returns:
            Dict[str, Any]: Response containing the natural language answer and metadata
        """
        try:
            print("\nProcessing database query...")
            
            # 1. Fetch patient data directly from database
            db_data = await self.kg_service.fetch_patient_data(patient_id)
            
            if not db_data:
                return {
                    "error": "No patient data found",
                    "metadata": {
                        "source": "database",
                        "patient_id": patient_id,
                        "query": query
                    }
                }
            
            # 2. Generate natural language response using database data
            response = await self.llm_service.generate_natural_response(
                query=query,
                lpr_data=db_data,
                conversation_id=conversation_id or str(uuid.uuid4()),  # Ensure we always have a conversation_id
                message_id=message_id,
                conversation_history=conversation_history
            )
            
            # Ensure conversation_id is always a string
            if response.get('conversation_id') is None:
                response['conversation_id'] = str(uuid.uuid4())
            
            # 3. Add metadata about the data source
            if "metadata" not in response:
                response["metadata"] = {}
            response["metadata"].update({
                "source": "database",
                "patient_id": patient_id
            })
            
            return response
            
        except Exception as e:
            print(f"Error processing database query: {str(e)}")
            return {
                "error": f"Failed to process query: {str(e)}",
                "metadata": {
                    "source": "database",
                    "patient_id": patient_id,
                    "query": query
                }
            }

    async def process_lpr(self, query: str, patient_id: str, is_initial_request: bool = True):
        """
        Process LPR query with Neo4j caching
        """
        try:
            print("\n=== Processing LPR request ===")
            print(f"Patient ID: {patient_id}")
            print(f"Is initial request: {is_initial_request}")
            
            # 1. Check for cached LPR in Neo4j
            cached_lpr = await self.kg_service.get_lpr_cache(patient_id)
            print("\nCache check result:")
            print(f"Cache found: {bool(cached_lpr)}")

            if cached_lpr and cached_lpr.get('lpr_data'):
                try:
                    # Try to parse the cached LPR data
                    cached_data = json.loads(cached_lpr['lpr_data'])
                    print("\nCached LPR data structure:")
                    print(cached_data)
                    
                    # 2. Check for changes since cache timestamp
                    if cached_lpr.get('timestamp'):
                        changes = await self.kg_service.get_changes_since_cache(
                            patient_id,
                            cached_lpr['timestamp']
                        )
                        print("\nDetected changes:")
                        print(changes)

                        if changes and (changes.get('changed_nodes') or changes.get('changed_relationships')):
                            print(f"\nChanges detected for patient {patient_id}, updating LPR")
                            # 3. Update existing LPR with changes
                            updated_lpr = await self.update_lpr_with_changes(
                                cached_data,
                                changes
                            )
                            # 4. Store updated LPR
                            await self.kg_service.store_lpr_cache(patient_id, updated_lpr)
                            print("\nUpdated LPR:")
                            print(updated_lpr)
                            return updated_lpr
                    
                    print(f"\nNo changes detected, using cached LPR data for patient {patient_id}")
                    return cached_data
                    
                except json.JSONDecodeError as e:
                    print(f"\nInvalid JSON in cached LPR data for patient {patient_id}")
                    print(f"Error: {str(e)}")
                    # Fall through to generate new LPR
            
            # Generate fresh LPR if no cache or invalid cache
            print(f"\nGenerating fresh LPR for patient {patient_id}")
            patient_data = await self.kg_service.fetch_patient_data(patient_id)
            
            if not patient_data:
                print("No patient data found")
                return {
                    "error": f"No data found for patient ID: {patient_id}",
                    "metadata": {
                        "type": "error",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            
            # Generate LPR using template
            template = self.load_template()
            print("\nGenerating LPR response using template")
            lpr_data = await self.llm_service.generate_lpr_response(query, patient_data, template)
            
            # Store in Neo4j
            print("\nStoring new LPR in cache")
            await self.kg_service.store_lpr_cache(patient_id, lpr_data)
            return lpr_data
            
        except Exception as e:
            print(f"Error in process_lpr: {str(e)}")
            return {
                "error": f"Failed to process LPR request: {str(e)}",
                "metadata": {
                    "type": "error",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

    async def update_lpr_with_changes(self, cached_lpr: Dict, changes: Dict) -> Dict:
        """
        Update existing LPR with detected changes
        """
        # Format changes for LLM
        formatted_changes = self.format_changes_for_llm(changes)
        
        # Get LLM to update the LPR
        updated_lpr = await self.llm_service.update_lpr(
            cached_lpr,
            formatted_changes
        )
        return updated_lpr

    def format_changes_for_llm(self, changes: Dict) -> Dict:
        """
        Format Neo4j changes into a structure the LLM can understand
        """
        print("\n=== Formatting changes for LLM ===")
        formatted = {
            'modified_nodes': [],
            'new_nodes': [],
            'deleted_nodes': [],
            'modified_relationships': []
        }

        def serialize_node(node):
            """Helper to serialize a Neo4j node"""
            if not node:
                return None
            data = dict(node)
            # Convert any datetime objects to ISO format
            for key, value in data.items():
                if hasattr(value, 'isoformat'):
                    data[key] = value.isoformat()
            # Add node labels if available
            if hasattr(node, 'labels'):
                data['_labels'] = list(node.labels)
            return data

        nodes = changes.get('changed_nodes', [])
        for node in nodes:
            node_data = serialize_node(node)
            if not node_data:
                continue
                
            if node_data.get('created_at'):
                formatted['new_nodes'].append(node_data)
            elif node_data.get('last_updated'):
                formatted['modified_nodes'].append(node_data)

        # Format relationships
        relationships = changes.get('changed_relationships', [])
        for rel in relationships:
            if not rel:
                continue
            rel_data = {
                'type': rel.get('type'),
                'properties': rel.get('properties', {}),
                'start_node': serialize_node(rel.get('start_node')),
                'end_node': serialize_node(rel.get('end_node'))
            }
            formatted['modified_relationships'].append(rel_data)

        print("\nFormatted changes summary:")
        print(f"- New nodes: {len(formatted['new_nodes'])}")
        print(f"- Modified nodes: {len(formatted['modified_nodes'])}")
        print(f"- Deleted nodes: {len(formatted['deleted_nodes'])}")
        print(f"- Modified relationships: {len(formatted['modified_relationships'])}")
        
        if formatted['new_nodes']:
            print("\nNew nodes:")
            for node in formatted['new_nodes']:
                print(f"- Type: {node.get('_labels', ['Unknown'])[0]}")
                print(f"  Properties: {node}")

        return formatted

    async def process_query(self, query: str, patient_id: str,
                          conversation_id: Optional[str] = None,
                          message_id: Optional[str] = None,
                          conversation_history: Optional[List[Dict]] = None):
        """
        Process a patient query using cached LPR data and generate natural language response.
        
        Args:
            query (str): The user's query
            patient_id (str): The ID of the patient
            conversation_id (str, optional): ID of the ongoing conversation
            message_id (str, optional): ID of the current message
            conversation_history (List[Dict], optional): Previous messages in the conversation
            
        Returns:
            dict: Natural language response with conversation context
        """
        print("\nProcessing query:", query)
        
        try:
            # Generate new conversation ID if not provided
            if not conversation_id:
                conversation_id = str(uuid.uuid4())

            # Use cached LPR data
            lpr_data = await self.process_lpr(query, patient_id, is_initial_request=False)
            
            if "error" in lpr_data:
                return {
                    **lpr_data,
                    "conversation_id": conversation_id,
                    "message_id": message_id
                }
            
            # Step 2: Generate response
            print("Generating response...")
            response = await self.llm_service.generate_natural_response(
                query=query,
                lpr_data=lpr_data,
                conversation_id=conversation_id,
                message_id=message_id,
                conversation_history=conversation_history or [],
            )
            
            return response
            
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            return {
                "error": f"Failed to process query: {str(e)}",
                "metadata": {
                    "type": "error",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
