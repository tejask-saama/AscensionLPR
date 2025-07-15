import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
import json5,json
import httpx
from datetime import datetime
from typing import Dict, List, Optional, Any
import re

load_dotenv()

class LLMService:
    """
    Service for interacting with Azure OpenAI LLM for response generation.
    """
    
    def extract_json_from_text(self, text):
        """Extract JSON from text that might contain additional content.
        
        Args:
            text (str): Text that might contain JSON wrapped in markers
            
        Returns:
            dict: Parsed JSON object or None if no valid JSON found
        """
        try:
            # First try to parse the entire text as JSON
            print(text)
            return json5.loads(text)
        except json5.JSONDecodeError:
            # Try to find JSON between markers
            json_pattern = r'```(?:json)?\s*({[\s\S]*?})\s*```|{[\s\S]*?}'
            matches = re.findall(json_pattern, text)
            
            for match in matches:
                try:
                    # Remove any leading/trailing whitespace and backticks
                    cleaned_json = match.strip('`').strip()
                    return json5.loads(cleaned_json)
                except json5.JSONDecodeError:
                    continue
            
            # If no valid JSON found, raise error
            raise json5.JSONDecodeError("No valid JSON found in response", text, 0)
    
    def _serialize_for_json(self, obj):
        """Helper method to serialize objects for JSON storage"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._serialize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_for_json(item) for item in obj]
        return obj

    def __init__(self):
        """Initialize the LLM service with credentials from environment variables."""
        print("Initializing LLM Service...")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = "https://scdm-dev.openai.azure.com/"
        self.deployment_name = "gpt-4o"
        
        print(f"Using endpoint: {self.endpoint}")
        print(f"Using deployment: {self.deployment_name}")
        
        # Initialize Azure OpenAI client
        self.client = AzureChatOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            deployment_name=self.deployment_name,
            temperature=0,
            api_version="2024-02-15-preview",
            http_client=httpx.Client(verify=False)
        )
        print("LLM client initialized successfully")
    
    async def update_lpr(self, existing_lpr: Dict, changes: Dict) -> Dict:
        """
        Update an existing LPR with detected changes
        
        Args:
            existing_lpr (Dict): The current LPR data
            changes (Dict): Changes detected in the knowledge graph
            
        Returns:
            Dict: Updated LPR data
        """
        try:
            print("\n=== LLM Service: Updating LPR ===")
            print("Processing changes to update LPR")

            # Serialize data for JSON
            serialized_existing_lpr = self._serialize_for_json(existing_lpr)
            serialized_changes = self._serialize_for_json(changes)

            prompt = f"""
            You are a medical data processor. Update the existing LPR with the following changes.
            
            EXISTING LPR:
            {json5.dumps(serialized_existing_lpr)}
            
            DETECTED CHANGES:
            {json5.dumps(serialized_changes)}
            
            INSTRUCTIONS:
            1. Analyze the changes and update the LPR accordingly
            2. Preserve the existing structure
            3. Only modify sections affected by the changes
            4. Maintain clinical accuracy and relevance
            5. Add a note in metadata about what was updated
            
            Return the complete updated LPR as a JSON object.
            """
            
            messages = [
                {"role": "system", "content": "You are a medical data processor that updates LPR records based on changes in the knowledge graph. Only respond with valid JSON."},
                {"role": "user", "content": prompt}
            ]
            
            print("\nSending request to LLM...")
            response = await self.client.invoke(messages)
            print("Received response from LLM")
            
            print("\nExtracting JSON from response...")
            updated_lpr = self.extract_json_from_text(response.content)
            print(f"Extracted JSON structure: {list(updated_lpr.keys()) if isinstance(updated_lpr, dict) else 'Not a dictionary'}")
            
            # Add update metadata
            if "metadata" not in updated_lpr:
                updated_lpr["metadata"] = {}
            updated_lpr["metadata"]["last_updated"] = datetime.utcnow().isoformat()
            updated_lpr["metadata"]["update_type"] = "incremental"
            
            print("\nLPR update completed successfully")
            return updated_lpr
            
        except Exception as e:
            print(f"\nError updating LPR in LLM service: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            print("Returning original LPR without updates")
            return existing_lpr

    async def generate_natural_response(self, query: str, lpr_data: Dict[str, Any],
                                     conversation_id: str,
                                     message_id: str,
                                     conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a natural language response to a user query using the LPR data and conversation context.
        
        Args:
            query (str): The user's query
            lpr_data (Dict): The LPR data to use for generating the response
            conversation_id (str): ID of the ongoing conversation
            message_id (str): ID of the current message
            conversation_history (List[Dict]): Previous messages in the conversation
            
        Returns:
            Dict: Response containing natural language answer and conversation metadata
        """
        try:
            print("Generating natural language response for query:", query)
            
            # Format conversation history with explicit context tracking
            history_text = self._format_conversation_history(conversation_history)
            
            # Analyze previous context
            previous_context = self._analyze_previous_context(conversation_history)
            
            # Prepare prompt for natural language response
            prompt = f"""
            You are a medical assistant providing concise information to healthcare providers.
            You must handle conversation context intelligently and format your responses in a clean, readable way.
            
            RESPONSE FORMATTING RULES:
            1. Structure your response based on the type of data:
               • For lists (medications, symptoms, etc.): Use bullet points with • symbol
               • For important data (lab results, vitals): Present in clear sections with headers
               • For narrative content: Use clear paragraphs with descriptive headers
            
            2. Text formatting:
               • Use UPPERCASE for section headers (e.g., MEDICATIONS:, LAB RESULTS:)
               • Present important values clearly (e.g., "Blood Pressure: 120/80")
               • Use indentation for sub-points when needed
               • For warnings or critical information, prefix with "IMPORTANT:" or "NOTE:"
            
            3. Choose appropriate presentation:
               • Use clear sections for different types of information
               • Present related items in groups
               • Use natural language for descriptions
            
            CONVERSATION HISTORY:
            {history_text}
            
            PREVIOUS CONTEXT ANALYSIS:
            {previous_context}
            
            ADDITIONAL GUIDELINES:
            1. Keep responses concise and focused
            2. Format dates consistently as Month Day, Year
            3. Use appropriate medical terminology with explanations when needed
            
            2. Topic Handling:
               IF THE CONTEXT ANALYSIS INDICATES A NEW TOPIC:
               - Start fresh with the new topic
               - Do not reference previous topics unless explicitly asked
               - Focus only on the current question
               
               IF THE QUESTION REFERENCES PREVIOUS TOPICS:
               - Explicitly state which previous information you're referring to
               - Use phrases like "Based on the previously discussed [topic]..."
               - Connect the information clearly
               
               IF IT'S A COMPLETELY NEW TOPIC:
               - Start with a clear topic transition
               - Don't force connections to previous topics
               - Focus on providing clear, direct information about the new topic
               
            3. Context Rules:
               - Only reference previous context if it's directly relevant
               - If a question uses words like 'this', 'that', 'these', 'those', clarify what they refer to
               - Don't carry over context when the topic has clearly changed
            
            3. Special formatting:
               - Use 'Visit Date:' for dates
               - Use 'Medications:' for medication lists
               - Keep natural paragraph breaks
               - Maintain consistent indentation for lists
            
            PATIENT DATA:
            {json5.dumps(lpr_data)}
            
            CURRENT QUESTION:
            {query}
            
            Provide a clear, contextual response that builds on the conversation history.
            Focus on relevant information while maintaining continuity with previous answers.
            """
            
            messages = [
                {"role": "system", "content": """You are a medical assistant that provides clear, concise responses to patient data queries.
                Format your responses with clean, natural text - no HTML tags or markdown.
                Use bullet points (•) for lists and natural paragraphs for descriptions.
                Keep responses focused and well-structured while maintaining clinical accuracy."""},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.invoke(messages)
            content = response.content.strip()
            
            # Process HTML tags to make them more natural
            content = self._process_html_tags(content)
            
            return {
                "response": content,
                "conversation_id": conversation_id,
                "message_id": message_id,
                "metadata": {
                    "query": query,
                    "type": "natural_language",
                    "generated_at": datetime.utcnow().isoformat(),
                    "conversation_length": len(conversation_history) + 1
                }
            }
            
        except Exception as e:
            print(f"Error generating natural language response: {str(e)}")
            return {
                "response": f"I apologize, but I encountered an error while processing your query: {str(e)}",
                "metadata": {
                    "error": str(e),
                    "type": "error"
                }
            }

    def _analyze_previous_context(self, history: List[Dict[str, Any]]) -> str:
        """
        Analyze conversation history to extract key topics and context.
        Determines if previous context is relevant to the current query.
        
        Args:
            history: List of message dictionaries with sender, content, and messageId
            
        Returns:
            Analysis of previous context and topics discussed
        """
        if not history:
            return "No previous context available."

        # Get the current query (last message)
        current_query = history[-1]['content'].lower() if history else ""
        
        # Track topics by their order in conversation
        topic_sequence = []
        last_assistant_response = None

        # Medical topics and their related terms
        medical_topics = {
            'lab_results': ['lab', 'test', 'results', 'levels', 'values'],
            'medications': ['medication', 'drug', 'prescription', 'dose', 'medicine'],
            'vitals': ['vital', 'blood pressure', 'temperature', 'heart rate', 'pulse'],
            'symptoms': ['symptom', 'pain', 'feeling', 'experiencing'],
            'procedures': ['procedure', 'surgery', 'operation', 'scan'],
            'diagnosis': ['diagnosis', 'condition', 'disease', 'disorder'],
        }

        # Analyze conversation flow
        current_topic = None
        for msg in history[:-1]:  # Exclude current query
            content = msg['content'].lower()
            if msg['sender'] == 'assistant':
                last_assistant_response = msg['content']
            
            # Detect topics in this message
            for topic, keywords in medical_topics.items():
                if any(keyword in content for keyword in keywords):
                    topic_sequence.append(topic)
                    current_topic = topic

        # Check if current query is related to previous topics
        current_topic_matches = []
        reference_words = ['this', 'that', 'these', 'those', 'it', 'they']
        has_reference_words = any(word in current_query for word in reference_words)

        for topic, keywords in medical_topics.items():
            if any(keyword in current_query for keyword in keywords):
                current_topic_matches.append(topic)

        # Build context based on relevance
        context = []
        
        # If current query has reference words, include last topic
        if has_reference_words and topic_sequence:
            context.append(f"Current query contains reference to previous content and last topic was: {topic_sequence[-1]}")
            if last_assistant_response:
                context.append(f"Last response covered: {last_assistant_response[:200]}...")
        
        # If current query mentions new topics, don't include old context
        elif current_topic_matches and not has_reference_words:
            context.append("Query is about a new topic - previous context may not be relevant.")
        
        # If no clear topic match but has reference words, include recent context
        elif has_reference_words:
            context.append(f"Query may refer to previously discussed topics: {', '.join(topic_sequence[-2:])}")

        return "\n".join(context) if context else "No relevant previous context found."

    def _format_conversation_history(self, history: List[Dict[str, Any]]) -> str:
        """
        Format conversation history into a readable string for the LLM.
        
        Args:
            history: List of message dictionaries with sender, content, and messageId
            
        Returns:
            Formatted conversation history as a string
        """
        formatted = []
        for msg in history:
            role = "Patient" if msg["sender"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)

    async def generate_lpr_response(self, query, patient_data, template):
        """
        Generates a response to the user query based on patient data and the appropriate template.
        
        Args:
            query (str): The user's query
            patient_data (dict): The patient data retrieved from the knowledge graph
            template (str): The template to use for response generation
            
        Returns:
            dict: A structured response containing the answer and metadata
        """
        try:
            prompt = f"""
                You need to analyze patient data and provide a comprehensive response to a user query.
                Your response must be in JSON format ONLY - no markdown, no text explanations, just pure JSON.
                
                USER QUERY: {query}
                
                PATIENT DATA: {json5.dumps(patient_data)}
                
                INSTRUCTIONS:
                Return ONLY a JSON object with this exact structure (no markdown, no backticks, no explanations):
                {{
                    "response": {template},  # This should be a JSON object following the template structure
                }}
                
                CRITICAL RULES:
                1. DO NOT use markdown formatting (no ``` or other markers)
                2. DO NOT include any text outside the JSON structure
                3. Ensure the response is valid JSON that can be parsed
                4. Base your response ONLY on the provided patient data
                5. The 'response' field MUST be a JSON object following the template structure
                
                ANY OUTPUT THAT IS NOT PURE JSON WILL BE REJECTED.
                """

            print("\nGenerating response for query:", query)
            
            messages = [
                {"role": "system", "content": "You are a medical assistant that ONLY responds with pure JSON objects. Never use markdown or text explanations. Your responses must be parseable JSON objects with no surrounding text or formatting."},
                {"role": "user", "content": prompt}
            ]
            response = self.client.invoke(messages)
            
            # Extract and parse the JSON response
            content = response.content
            print("\nRaw LLM response:", content)

            print("\nContent type:", type(content))
            
            try:
                print("\nAttempting to parse JSON response...")
                # Extract and parse JSON from the response
                llm_response = self.extract_json_from_text(content)
                print("Parsed JSON response:", json5.dumps(llm_response))
                
                def ensure_list(value, default):
                    return list(value) if value is not None and isinstance(value, (list, tuple)) else default
                
                # Construct the final result with the LLM-generated content and type validation
                print("\nConstructing final result...")
                result = {
                    "response": llm_response.get("response", "No response provided"),
                    "metadata": {
                        "model": self.deployment_name,
                        "type": "patient_data"
                    }
                }
            except json.JSONDecodeError as e:
                # Fallback if JSON parsing fails
                print(f"\nJSON parsing error: {str(e)}")
                print(f"Raw content that failed to parse: {content[:200]}...")
                result = {
                    "response": str(content),  # Ensure string type
                    "metadata": {
                        "model": self.deployment_name
                    }
                }
            print("Result generated by generate response function")
            print("printed before returning")
            return result
            
        except Exception as e:
            print(f"\nError in response generation: {str(e)}")
            print("Exception type:", type(e).__name__)
            import traceback
            print("Traceback:", traceback.format_exc())
            return {
                "response": "Unable to generate a response at this time.",
                "metadata": {
                    "error": str(e)
                }
            }

    def _process_html_tags(self, content: str) -> str:
        """
        Process HTML tags to make them more natural and readable.
        """
        import re
        
        # Replace heading tags with bold text
        content = re.sub(r'<h[1-6]>(.*?)</h[1-6]>', r'**\1**', content)
        
        # Clean up list items
        content = re.sub(r'<li>•\s*', r'<li>', content)  # Remove duplicate bullets
        content = re.sub(r'<li>(.*?)</li>', r'• \1', content)  # Replace <li> with bullets
        
        # Remove ul tags but keep structure
        content = content.replace('<ul>', '\n').replace('</ul>', '\n')
        
        # Clean up paragraphs
        content = content.replace('<p>', '').replace('</p>', '\n\n')
        
        # Remove extra newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()
    