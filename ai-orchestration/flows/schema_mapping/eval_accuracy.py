from promptflow import tool
import json

@tool
def eval_accuracy(ground_truth: str, prediction: str):
    try:
        pred_json = json.loads(prediction)
        predicted_target = pred_json.get("target")
        
        score = 1.0 if predicted_target == ground_truth else 0.0
        return {"score": score, "match": predicted_target == ground_truth}
    except:
        return {"score": 0.0, "error": "Invalid JSON format"}
