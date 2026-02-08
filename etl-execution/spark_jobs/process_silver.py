import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_silver_layer(input_path, output_path):
    """
    Simulates a Spark job reading Bronze and writing to Silver (Cleaned).
    """
    logger.info(f"Starting Silver Layer Processing from {input_path}")
    
    with open(input_path, 'r') as f:
        bronze_data = json.load(f)
        
    silver_data = []
    for record in bronze_data:
        # Transformation: Standardize specific fields
        if 'system_type' in record:
            record['system_type'] = record['system_type'].upper()
            
        # DQ Check: Filter out invalid records (Simulation)
        if record.get('object_name'):
            silver_data.append(record)
            
    with open(output_path, 'w') as f:
        json.dump(silver_data, f, indent=2)
        
    logger.info(f"Written {len(silver_data)} records to Silver Layer at {output_path}")

if __name__ == "__main__":
    process_silver_layer("data/bronze_metadata.json", "data/silver_metadata.json")
