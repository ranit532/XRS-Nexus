"""
Lineage & Impact Analysis Agent
- Traces data lineage, assesses downstream impact, and exposes lineage as JSON.
"""
class LineageImpactAnalysisAgent:
    def run(self, input_json):
        try:
            pipeline_id = input_json['pipelineId']
            change_set = input_json['changeSet']
            # Example: dummy lineage graph
            nodes = [
                {"id": "source", "type": "source", "label": "SourceTable"},
                {"id": "target", "type": "target", "label": "TargetTable"}
            ]
            edges = [
                {"from": "source", "to": "target", "impact": "schema_change"}
            ]
            impacted_objects = ["TargetTable"]
            return {
                "lineageGraph": {"nodes": nodes, "edges": edges},
                "impactedObjects": impacted_objects,
                "status": "success",
                "errors": []
            }
        except Exception as e:
            return {
                "lineageGraph": None,
                "impactedObjects": [],
                "status": "error",
                "errors": [str(e)]
            }

    @staticmethod
    def prompt_template():
        return (
            "Given a pipeline and a change set, trace the data lineage and list all impacted downstream objects. Output as a lineage graph and impacted object list."
        )
