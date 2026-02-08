import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_bronze_layer(input_path, output_path):
    """
    Simulates a Spark job reading raw JSON and writing to Delta (Bronze).
    """
    logger.info(f"Starting Bronze Layer Processing from {input_path}")
    
    with open(input_path, 'r') as f:
        raw_data = json.load(f)
        
    logger.info(f"Ingested {len(raw_data)} records.")
    
    # Simulation of "Raw to Bronze" transformation (adding ingestion metadata)
    processed_data = []
    for record in raw_data:
        record['_ingestion_timestamp'] = "2024-06-15T10:00:00Z"
        record['_source_system'] = record.get('system_id', 'UNKNOWN')
        processed_data.append(record)
        
    with open(output_path, 'w') as f:
        json.dump(processed_data, f, indent=2)
        
    logger.info(f"Written {len(processed_data)} records to Bronze Layer at {output_path}")

if __name__ == "__main__":
    process_bronze_layer("data/metadata_samples.json", "data/bronze_metadata.json")
