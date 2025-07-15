from neo4j import GraphDatabase
import yaml, os
from dotenv import load_dotenv
from datetime import datetime
import os

# Import the memory management from the project
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, '..')

# Load environment variables from project root
dotenv_path = os.path.join(parent_dir, '.env')
load_dotenv(dotenv_path)

# Neo4j connection details from .env
uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

# Properties to exclude for each node
EXCLUDE_PROPERTIES = ["embedding"]

# Node types to exclude
EXCLUDE_NODES = ["embedding"]

# Additional node types and relationships to include
ADDITIONAL_NODES = {
    "LPRCache": {
        "properties": [
            {"name": "id", "type": "string", "required": True},
            {"name": "patient_id", "type": "string", "required": True},
            {"name": "timestamp", "type": "datetime", "required": True},
            {"name": "lpr_data", "type": "string", "required": True},
            {"name": "metadata", "type": "string", "required": True}
        ]
    }
}

ADDITIONAL_RELATIONSHIPS = [
    {
        "type": "HAS_LPR_CACHE",
        "source": "Patient",
        "target": "LPRCache",
        "properties": [
            {"name": "created_at", "type": "datetime", "required": True}
        ]
    }
]

# Initialize Neo4j driver
driver = GraphDatabase.driver(uri, auth=(username, password))

# Function to get all node types from the graph
def fetch_all_node_types(tx):
    query = """
    CALL db.labels()
    YIELD label
    RETURN label
    """
    result = tx.run(query)
    return [record["label"] for record in result]

# Function to get all properties of a given node type
def fetch_node_properties(tx, node_type):
    query = f"""
    MATCH (n:{node_type})
    WITH keys(n) AS props
    UNWIND props AS prop
    RETURN DISTINCT prop
    """
    result = tx.run(query)
    return [record["prop"] for record in result]


# Function to fetch relationship types with source and target node types
def fetch_relationships(tx):
    query = """
    MATCH (source)-[r]->(target)
    RETURN DISTINCT type(r) as relationshipType, labels(source) as sourceLabels, labels(target) as targetLabels
    """
    result = tx.run(query)
    relationships = []
    for record in result:
        rel_type = record["relationshipType"]
        source_labels = record["sourceLabels"]
        target_labels = record["targetLabels"]
        # Take the first label of each node as primary label
        if source_labels and target_labels:
            relationships.append({
                "type": rel_type,
                "source": source_labels[0],
                "target": target_labels[0]
            })
    return relationships

# Function to compare schemas and detect changes
def compare_schemas(previous_schema, current_schema):
    changes = {
        'new_nodes': [],
        'modified_nodes': [],
        'deleted_nodes': [],
        'new_relationships': [],
        'modified_relationships': [],
        'deleted_relationships': []
    }
    
    # Compare nodes
    prev_nodes = set(previous_schema['nodes'].keys())
    curr_nodes = set(current_schema['nodes'].keys())
    
    changes['new_nodes'] = list(curr_nodes - prev_nodes)
    changes['deleted_nodes'] = list(prev_nodes - curr_nodes)
    
    # Check for modified nodes (property changes)
    for node in prev_nodes & curr_nodes:
        if previous_schema['nodes'][node] != current_schema['nodes'][node]:
            changes['modified_nodes'].append({
                'node': node,
                'previous_props': previous_schema['nodes'][node],
                'current_props': current_schema['nodes'][node]
            })
    
    # Compare relationships
    prev_rels = {(r['type'], r['source'], r['target']) for r in previous_schema['relationships']}
    curr_rels = {(r['type'], r['source'], r['target']) for r in current_schema['relationships']}
    
    changes['new_relationships'] = [{'type': t, 'source': s, 'target': d} for t, s, d in curr_rels - prev_rels]
    changes['deleted_relationships'] = [{'type': t, 'source': s, 'target': d} for t, s, d in prev_rels - curr_rels]
    
    return changes

# Initialize the structured schema data with timestamp
schema_data = {
    "timestamp": datetime.utcnow().isoformat(),
    "nodes": {},
    "relationships": []
}

# Main extraction logic
with driver.session() as session:
    # Fetch all node types
    node_types = session.read_transaction(fetch_all_node_types)

    # Loop through each node type
    for node_type in node_types:
        print(f"Processing node type: {node_type}")

        # Skip excluded nodes
        if node_type.lower() in EXCLUDE_NODES:
            print(f"Skipping excluded node: {node_type}")
            continue

        # Initialize the node type in the dictionary
        schema_data["nodes"][node_type] = []

        # Fetch all properties of this node type
        properties = session.read_transaction(fetch_node_properties, node_type)

        # Add properties to the node (excluding those in EXCLUDE_PROPERTIES)
        for property_name in properties:
            if property_name not in EXCLUDE_PROPERTIES:
                schema_data["nodes"][node_type].append(property_name)
                print(f"Added property: {node_type}.{property_name}")
            else:
                print(f"Skipping excluded property: {property_name} in {node_type}")

    # Fetch relationship types with their source and target nodes
    relationships = session.read_transaction(fetch_relationships)
    for rel in relationships:
        schema_data["relationships"].append({
            "type": rel["type"],
            "source": rel["source"],
            "target": rel["target"]
        })
        print(f"Added relationship: {rel['source']}-[{rel['type']}]->{rel['target']}")

# Add additional nodes
print("\nAdding additional nodes and relationships...")
for node_type, node_data in ADDITIONAL_NODES.items():
    print(f"Adding node type: {node_type}")
    if node_type not in schema_data["nodes"]:
        schema_data["nodes"][node_type] = node_data["properties"]
    else:
        print(f"Node {node_type} already exists, updating properties...")
        existing_props = {p["name"] for p in schema_data["nodes"][node_type] if isinstance(p, dict) and "name" in p}
        for prop in node_data["properties"]:
            if prop["name"] not in existing_props:
                schema_data["nodes"][node_type].append(prop)

# Add additional relationships
for rel in ADDITIONAL_RELATIONSHIPS:
    print(f"Adding relationship: {rel['type']} ({rel['source']} -> {rel['target']})")
    existing_rels = {(r["source"], r["type"], r["target"]) for r in schema_data["relationships"]}
    if (rel["source"], rel["type"], rel["target"]) not in existing_rels:
        schema_data["relationships"].append(rel)
    else:
        print(f"Relationship {rel['type']} already exists")


# Write the schema to a YAML file
with open('kg_schema1.yaml', 'w') as f:
    yaml.dump(schema_data, f, default_flow_style=False)

print("\nSchema generation complete. New schema includes:")
print(f"Nodes: {list(schema_data['nodes'].keys())}")
print(f"Relationships: {[r['type'] for r in schema_data['relationships']]}")

# Close the driver connection
driver.close()
