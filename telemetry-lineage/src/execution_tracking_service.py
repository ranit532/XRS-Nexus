"""
Runtime Execution Tracking Service
- Captures pipeline run IDs
- Tracks stage-level progress (extract/transform/load)
- Computes percentage completion
- Estimates time remaining
- Detects SLA breach risks
"""
import time
from typing import Dict, Any, List

class ExecutionTrackingService:
    def __init__(self):
        # In production, use Cosmos DB or Delta Lake; here, use in-memory dict
        self.telemetry_store = {}

    def start_run(self, pipeline_id: str, stages: List[str], sla_minutes: int) -> str:
        run_id = f"run-{int(time.time() * 1000)}"
        now = time.time()
        self.telemetry_store[run_id] = {
            "pipelineId": pipeline_id,
            "runId": run_id,
            "stages": {stage: {"status": "pending", "startTime": None, "endTime": None} for stage in stages},
            "currentStage": None,
            "startTime": now,
            "endTime": None,
            "slaMinutes": sla_minutes,
            "slaBreached": False,
            "percentComplete": 0,
            "estimatedTimeRemaining": None
        }
        return run_id

    def update_stage(self, run_id: str, stage: str, status: str):
        now = time.time()
        run = self.telemetry_store[run_id]
        stage_info = run["stages"][stage]
        if status == "running":
            stage_info["startTime"] = now
            run["currentStage"] = stage
        elif status == "completed":
            stage_info["endTime"] = now
        stage_info["status"] = status
        self._recompute_progress(run_id)

    def _recompute_progress(self, run_id: str):
        run = self.telemetry_store[run_id]
        total = len(run["stages"])
        completed = sum(1 for s in run["stages"].values() if s["status"] == "completed")
        run["percentComplete"] = int((completed / total) * 100)
        # Estimate time remaining
        now = time.time()
        elapsed = now - run["startTime"]
        if completed > 0:
            avg_stage = elapsed / completed
            remaining = (total - completed) * avg_stage
            run["estimatedTimeRemaining"] = int(remaining)
        else:
            run["estimatedTimeRemaining"] = None
        # SLA breach detection
        if elapsed > run["slaMinutes"] * 60:
            run["slaBreached"] = True
        else:
            run["slaBreached"] = False

    def get_status(self, run_id: str) -> Dict[str, Any]:
        return self.telemetry_store[run_id]

# Example usage
if __name__ == "__main__":
    service = ExecutionTrackingService()
    run_id = service.start_run("pipeline-123", ["extract", "transform", "load"], sla_minutes=30)
    print("Started run:", run_id)
    service.update_stage(run_id, "extract", "running")
    time.sleep(1)
    service.update_stage(run_id, "extract", "completed")
    service.update_stage(run_id, "transform", "running")
    time.sleep(1)
    service.update_stage(run_id, "transform", "completed")
    service.update_stage(run_id, "load", "running")
    time.sleep(1)
    service.update_stage(run_id, "load", "completed")
    print("Final status:")
    print(service.get_status(run_id))
