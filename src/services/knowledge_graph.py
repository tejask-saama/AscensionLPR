import os
from dotenv import load_dotenv
from neo4j import AsyncGraphDatabase
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

load_dotenv()

class KnowledgeGraphService:
    """
    Service for interacting with the Neo4j Knowledge Graph to fetch patient data.
    """
    
    def __init__(self):
        """Initialize basic configuration."""
        print("\nLoading Neo4j configuration...")
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        
        print(f"Neo4j URI: {self.uri}")
        print(f"Neo4j User: {self.user}")
        print(f"Password loaded: {bool(self.password)}")
        
        if not all([self.uri, self.user, self.password]):
            raise ValueError("Missing required Neo4j environment variables")
            
        self.driver = None

    async def initialize(self):
        """Async initialization of Neo4j connection and schema."""
        try:
            print("Initializing Neo4j connection...")
            self.driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Initialize LPRCache schema
            await self.init_lpr_cache_schema()
            print("Neo4j connection initialized successfully")
        except Exception as e:
            print(f"Failed to create the Neo4j driver: {str(e)}")
            raise

    async def init_lpr_cache_schema(self):
        """
        Initialize the schema for LPRCache nodes
        """
        print("Initializing LPRCache schema...")
        try:
            # Create unique constraint on LPRCache.id
            await self.run_query("""
            CREATE CONSTRAINT lpr_cache_id IF NOT EXISTS
            FOR (c:LPRCache)
            REQUIRE c.id IS UNIQUE
            """)
            
            # Create index on patient_id
            await self.run_query("""
            CREATE INDEX lpr_cache_patient_id IF NOT EXISTS
            FOR (c:LPRCache)
            ON (c.patient_id)
            """)
            
            # Create index on timestamp
            await self.run_query("""
            CREATE INDEX lpr_cache_timestamp IF NOT EXISTS
            FOR (c:LPRCache)
            ON (c.timestamp)
            """)
            
            # Create index on last_updated
            await self.run_query("""
            CREATE INDEX lpr_cache_last_updated IF NOT EXISTS
            FOR (c:LPRCache)
            ON (c.last_updated)
            """)
            
            # Drop any old nodes without last_updated (if migrating)
            await self.run_query("""
            MATCH (c:LPRCache)
            WHERE c.last_updated IS NULL
            DETACH DELETE c
            """)
            
            print("LPRCache schema initialized successfully")
        except Exception as e:
            print(f"Error initializing LPRCache schema: {str(e)}")
            raise
    
    async def close(self):
        """Close the Neo4j driver connection."""
        if self.driver:
            await self.driver.close()
    
    async def run_query(self, query, parameters=None):
        """
        Run a Cypher query and return the result.
        
        Args:
            query (str): The Cypher query to execute
            parameters (dict, optional): Parameters for the query
            
        Returns:
            dict: The result of the query
        """
        try:
            async with self.driver.session() as session:
                result = await session.run(query, parameters)
                records = await result.data()
                return records[0] if records else None
        except Exception as e:
            print(f"Error running query: {str(e)}")
            return None
    
    def _serialize_neo4j_result(self, data):
        """Helper method to serialize Neo4j types"""
        if isinstance(data, dict):
            return {k: self._serialize_neo4j_result(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._serialize_neo4j_result(item) for item in data]
        elif hasattr(data, 'isoformat'):  # For Neo4j DateTime objects
            return data.isoformat()
        return data

    async def get_lpr_cache(self, patient_id: str) -> Optional[Dict]:
        """
        Get the latest LPR cache for a patient
        """
        print("\n=== Fetching LPR cache from Neo4j ===")
        print(f"Patient ID: {patient_id}")
        
        query = """
        MATCH (p:Patient {id: $patient_id})-[:HAS_LPR_CACHE]->(cache:LPRCache)
        RETURN cache {
            id: cache.id,
            timestamp: toString(cache.timestamp),
            lpr_data: cache.lpr_data,
            metadata: cache.metadata,
            last_updated: toString(cache.last_updated),
            patient_id: cache.patient_id
        } as cache
        ORDER BY cache.timestamp DESC
        LIMIT 1
        """
        
        result = await self.run_query(query, {"patient_id": patient_id})
        print("\nRaw Neo4j result:")
        if result and 'cache' in result:
            cache_data = self._serialize_neo4j_result(result['cache'])
            print("Found cached LPR data:")
            print(f"- ID: {cache_data.get('id')}")
            print(f"- Timestamp: {cache_data.get('timestamp')}")
            print(f"- Last Updated: {cache_data.get('last_updated')}")
            try:
                lpr_data = json.loads(cache_data['lpr_data'])
                print("- LPR data structure:", list(lpr_data.keys()) if isinstance(lpr_data, dict) else "Not a dictionary")
            except json.JSONDecodeError as e:
                print(f"Warning: Could not parse LPR data: {str(e)}")
            return cache_data
        print("No cache found")
        return None

    async def store_lpr_cache(self, patient_id: str, lpr_data: Dict) -> None:
        """
        Store or update LPR data in cache node
        """
        print("\n=== Storing/updating LPR cache ===")
        current_time = datetime.utcnow().isoformat()
        
        # First try to find existing cache node
        query = """
        MATCH (p:Patient {id: $patient_id})-[r:HAS_LPR_CACHE]->(cache:LPRCache)
        RETURN cache {
            id: cache.id,
            timestamp: toString(cache.timestamp),
            metadata: cache.metadata
        } as cache
        ORDER BY cache.timestamp DESC
        LIMIT 1
        """
        
        result = await self.run_query(query, {"patient_id": patient_id})
        existing_cache = result.get('cache') if result else None
        
        if existing_cache:
            print(f"Updating existing cache node: {existing_cache.get('id')}")
            update_query = """
            MATCH (p:Patient {id: $patient_id})-[r:HAS_LPR_CACHE]->(cache:LPRCache)
            WHERE cache.id = $cache_id
            SET cache.timestamp = datetime($timestamp),
                cache.lpr_data = $lpr_data,
                cache.metadata = $metadata,
                cache.last_updated = datetime($timestamp)
            """
            
            try:
                existing_metadata = json.loads(existing_cache.get('metadata', '{}'))
            except json.JSONDecodeError:
                existing_metadata = {}
            
            await self.run_query(update_query, {
                "patient_id": patient_id,
                "cache_id": existing_cache['id'],
                "timestamp": current_time,
                "lpr_data": json.dumps(lpr_data),
                "metadata": json.dumps({
                    "version": "1.0",
                    "created_at": existing_metadata.get('created_at', current_time),
                    "last_updated": current_time
                })
            })
            print(f"Cache updated at: {current_time}")
        else:
            print(f"Creating new cache node for patient: {patient_id}")
            create_query = """
            MATCH (p:Patient {id: $patient_id})
            CREATE (p)-[:HAS_LPR_CACHE]->(cache:LPRCache {
                id: apoc.create.uuid(),
                timestamp: datetime($timestamp),
                lpr_data: $lpr_data,
                metadata: $metadata,
                last_updated: datetime($timestamp),
                patient_id: $patient_id
            })
            """
            
            await self.run_query(create_query, {
                "patient_id": patient_id,
                "timestamp": current_time,
                "lpr_data": json.dumps(lpr_data),
                "metadata": json.dumps({
                    "version": "1.0",
                    "created_at": current_time,
                    "last_updated": current_time
                })
            })
            print(f"New cache created at: {current_time}")

    async def get_changes_since_cache(self, patient_id: str, cache_timestamp: str) -> Dict:
        """
        Get all nodes and relationships that changed since the cache timestamp
        """

        print("\n=== Checking for data changes in Neo4j ===")
        print(f"\nPatient ID: {patient_id}")
        print(f"\nCache timestamp: {cache_timestamp}")
        print("\nChecking for data changes in Neo4j...")
        query = """
        // Find nodes that have been updated
        MATCH (p:Patient {id: $patient_id})-[*]-(n)
        WHERE (n.last_updated IS NOT NULL AND n.last_updated > datetime($cache_timestamp))
           OR (n.created_at IS NOT NULL AND n.created_at > datetime($cache_timestamp))
        WITH COLLECT(DISTINCT n) as updated_nodes
        
        // Find relationships involving updated nodes
        OPTIONAL MATCH (p:Patient {id: $patient_id})-[r]-(changed)
        WHERE changed IN updated_nodes
        WITH updated_nodes, COLLECT(DISTINCT r) as updated_rels
        
        RETURN {
            changed_nodes: updated_nodes,
            changed_relationships: updated_rels
        } as changes
        """

        result = await self.run_query(query, {
            "patient_id": patient_id,
            "cache_timestamp": cache_timestamp
        })

        print("\nData changes:", result)
        return result

    async def fetch_patient_data(self, patient_id):
        """
        Fetch comprehensive patient data from the knowledge graph using the predefined Cypher query.

        Args:
            patient_id (str): The ID of the patient to retrieve data for
            
        Returns:
            dict: Comprehensive patient data structured according to the query result
        """
        print("\n=== Fetching patient data from Neo4j ===")
        print(f"\nPatient ID: {patient_id}")
        print("\nFetching patient data from Neo4j...")

        # Read the Cypher query from the file
        with open("schema/lpr_cypher_query.txt", "r") as file:
            cypher_query = file.read()
        
        # Execute the query with the patient ID parameter
        try:
            async with self.driver.session() as session:
                result = await session.run(cypher_query, patientId=patient_id)
                record = await result.single()
                
                if record:
                    # Extract the comprehensive patient data from the result
                    return record["patient_comprehensive_data"]
                else:
                    return None
        except Exception as e:
            print(f"Error fetching patient data: {str(e)}")
            return None
