"""
Runtime Telemetry Agent
- Monitors pipeline execution, collects metrics, and detects anomalies.
"""
from datetime import datetime

class RuntimeTelemetryAgent:
    def run(self, input_json):
        try:
            pipeline_id = input_json['pipelineId']
            execution_context = input_json['executionContext']
            # Example: dummy metrics
            metrics = {
                "status": "success",
                "latencySeconds": 42,
                "recordsProcessed": 1000,
                "anomalies": []
            }
            return {
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }
        except Exception as e:
            return {
                "metrics": None,
                "timestamp": datetime.utcnow().isoformat() + 'Z',
                "anomalies": [str(e)]
            }

    @staticmethod
    def prompt_template():
        return (
            "Monitor the execution of pipeline {pipelineId}. Report status, latency, records processed, and any detected anomalies."
        )
