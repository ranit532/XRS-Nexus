"""
Logical Flow Generator Agent
- Generates logical data flow graphs from canonical metadata.
"""
class LogicalFlowGeneratorAgent:
    def run(self, input_json):
        try:
            canonical_metadata = input_json['canonicalMetadata']
            target_system = input_json['targetSystem']
            # Example: create a trivial flow with one source and one target
            nodes = [
                {"id": "source", "type": "source", "label": canonical_metadata['objectName']},
                {"id": "target", "type": "target", "label": target_system['name']}
            ]
            edges = [
                {"from": "source", "to": "target", "transformation": "identity"}
            ]
            return {
                "logicalFlow": {"nodes": nodes, "edges": edges},
                "status": "success",
                "errors": []
            }
        except Exception as e:
            return {
                "logicalFlow": None,
                "status": "error",
                "errors": [str(e)]
            }

    @staticmethod
    def prompt_template():
        return (
            "Given this canonical metadata and a target system, generate a logical data flow graph with nodes and edges, including transformation steps. Output as JSON."
        )
