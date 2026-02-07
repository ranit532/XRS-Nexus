"""
ETL Strategy Agent
- Selects and parameterizes the optimal ETL/ELT strategy for the logical flow.
"""
class ETLStrategyAgent:
    def run(self, input_json):
        try:
            logical_flow = input_json['logicalFlow']
            canonical_metadata = input_json['canonicalMetadata']
            constraints = input_json.get('constraints', {})
            # Example: always select batch/ADF for demo
            etl_strategy = {
                "mode": "batch",
                "pipelineTemplate": "ADF",
                "parameters": {"objectName": canonical_metadata['objectName']}
            }
            return {
                "etlStrategy": etl_strategy,
                "status": "success",
                "errors": []
            }
        except Exception as e:
            return {
                "etlStrategy": None,
                "status": "error",
                "errors": [str(e)]
            }

    @staticmethod
    def prompt_template():
        return (
            "Given this logical flow and metadata, select the best ETL/ELT strategy (batch, streaming, CDC) and output the recommended pipeline template and parameters."
        )
