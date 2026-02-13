import json
from promptflow import tool

@tool
def aggregate_results(pii_result: str, quality_result: str, validation_type: str) -> str:
    """Aggregate PII and quality validation results"""
    
    try:
        # Parse results
        pii_data = json.loads(pii_result) if isinstance(pii_result, str) else pii_result
        quality_data = json.loads(quality_result) if isinstance(quality_result, str) else quality_result
        
        # Determine overall status
        statuses = []
        if pii_data.get("has_pii"):
            statuses.append(pii_data.get("status", "warning"))
        if quality_data.get("has_issues"):
            statuses.append(quality_data.get("status", "warning"))
        
        # Overall status priority: failed > warning > passed
        if "failed" in statuses:
            overall_status = "failed"
        elif "warning" in statuses:
            overall_status = "warning"
        else:
            overall_status = "passed"
        
        # Aggregate results
        result = {
            "status": overall_status,
            "validation_type": validation_type,
            "pii_validation": pii_data,
            "quality_validation": quality_data,
            "summary": {
                "has_pii": pii_data.get("has_pii", False),
                "has_quality_issues": quality_data.get("has_issues", False),
                "pii_fields_count": len(pii_data.get("pii_fields", [])),
                "quality_issues_count": len(quality_data.get("issues", [])),
                "overall_quality_score": quality_data.get("overall_quality_score", 1.0)
            },
            "recommendations": (
                pii_data.get("recommendations", []) + 
                [issue.get("recommendation") for issue in quality_data.get("issues", [])]
            )
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e),
            "pii_result": pii_result,
            "quality_result": quality_result
        })
