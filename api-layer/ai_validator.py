import json
import os
import logging
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError
try:
    from promptflow.azure import PFClient
    HAS_PROMPTFLOW = True
except ImportError:
    HAS_PROMPTFLOW = False

from openai import AzureOpenAI, OpenAI
from huggingface_hub import InferenceClient


import hashlib

class PromptFlowValidator:
    """Validates data using deployed Prompt Flows, Azure OpenAI, Standard OpenAI, Hugging Face, or Ollama"""

    def mask_pii(self, dataset: list, pii_fields: list) -> list:
        """Applies SHA-256 masking to flagged PII fields"""
        import copy
        masked_data = copy.deepcopy(dataset)
        
        for row in masked_data:
            for field in pii_fields:
                if field in row and row[field]:
                    # Create SHA-256 hash
                    row[field] = hashlib.sha256(str(row[field]).encode()).hexdigest()
        
        return masked_data
    
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_group = "xrs-nexus-dev-rg"
        self.workspace_name = "xrs-nexus-dev-ai-project"
        
        # Determine provider (azure, openai, huggingface, ollama)
        self.sys_provider = os.getenv("AI_PROVIDER", "azure").lower()
        
        # Initialize Prompt Flow client (only if using Azure and available)
        self.pf_client = None
        if self.sys_provider == "azure" and HAS_PROMPTFLOW:
            try:
                self.pf_client = PFClient(
                    credential=self.credential,
                    subscription_id=self.subscription_id,
                    resource_group_name=self.resource_group,
                    workspace_name=self.workspace_name
                )
            except Exception as e:
                logging.warning(f"Could not initialize PFClient: {e}")
                self.pf_client = None
        elif self.sys_provider == "azure" and not HAS_PROMPTFLOW:
             logging.warning("Prompt Flow libraries not installed. Azure path will use Direct SDK fallback.")

    def validate_pii(self, dataset_sample: list) -> dict:
        """
        Use PII Detection (Agnostic)
        Args:
            dataset_sample: List of dictionaries representing sample data
        Returns:
            PII validation results
        """
        try:
            # 1. Standard OpenAI Path
            if self.sys_provider == "openai":
                print("Using Standard OpenAI path...")
                return self._validate_pii_openai_standard(dataset_sample)

            # 2. Hugging Face Path
            if self.sys_provider == "huggingface":
                print("Using Hugging Face Inference API...")
                return self._validate_pii_huggingface(dataset_sample)

            # 3. Ollama Path (New!)
            if self.sys_provider == "ollama":
                print("Using Ollama (via OpenAI API)...")
                return self._validate_pii_ollama(dataset_sample)

            # 4. Azure Path (Prompt Flow first)
            if self.sys_provider == "azure" and self.pf_client:
                try:
                    # Prepare payload for PII detection flow
                    payload_sample = json.dumps(dataset_sample[0] if dataset_sample else {})
                    
                    # Invoke the PII detection flow
                    print(f"Attempting to invoke Prompt Flow 'pii_detection'...")
                    result = self.pf_client.flows.invoke(
                        flow="pii_detection",
                        inputs={"payload_sample": payload_sample}
                    )
                    
                    print(f"Prompt Flow invocation successful. Result: {result}")

                    # Parse result
                    if isinstance(result, str):
                        pii_report = json.loads(result)
                    else:
                        pii_report = result
                    
                    return {
                        "has_pii": pii_report.get("has_pii", False),
                        "pii_fields": pii_report.get("pii_fields", []),
                        "classification": pii_report.get("classification", "Public"),
                        "status": "warning" if pii_report.get("has_pii") else "passed",
                        "recommendations": ["Apply data masking", "Encrypt sensitive fields"] if pii_report.get("has_pii") else [],
                        "ai_powered": True
                    }
                    
                except Exception as e:
                    logging.error(f"PII validation via Prompt Flow failed: {e}")
                    print(f"⚠️ Prompt Flow failed. Error: {e}")
            
            # 5. Azure Direct SDK Fallback (if Prompt Flow failed or not init)
            if self.sys_provider == "azure":
                 print("Attempting Direct SDK call to Azure OpenAI...")
                 return self._validate_pii_direct_sdk(dataset_sample)
                 
            # Default Fallback
            return self._fallback_pii_detection(dataset_sample)
            
        except Exception as e:
            logging.error(f"AI validation failed: {e}")
            print(f"⚠️ AI Validation failed. Error: {e}")
            return self._fallback_pii_detection(dataset_sample)

    def _validate_pii_ollama(self, dataset_sample: list) -> dict:
        """Call to local Ollama instance (via ngrok/tunnel)"""
        try:
            base_url = os.getenv("OLLAMA_BASE_URL")
            model = os.getenv("OLLAMA_MODEL", "mistral")
            
            if not base_url:
                print("Missing OLLAMA_BASE_URL for 'ollama' provider.")
                return self._fallback_pii_detection(dataset_sample)
            
            # Ensure base_url has /v1 for OpenAI compatibility (if using older Ollama versions, adjust)
            # Ollama supports /v1/chat/completions natively now.
            # Example: https://ngrok-url/v1
            
            # Added headers to bypass localtunnel/ngrok warning pages
            client = OpenAI(
                base_url=f"{base_url}/v1",
                api_key="ollama",
                default_headers={
                    "Bypass-Tunnel-Reminder": "true",
                    "ngrok-skip-browser-warning": "true",
                    "User-Agent": "XRS-Nexus-AI"
                }
            )
            
            prompt = f"""
            Analyze the following data sample for PII (Personally Identifiable Information).
            Be extremely thorough. 
            Return a JSON object with:
            - has_pii (boolean)
            - pii_fields (list of strings)
            - classification (string: Public, Internal, Confidential, Restricted)
            - confidence (float between 0 and 1)
            - risk_level (string: Low, Medium, High, Critical)
            - pii_details (list of objects with keys: field, type, confidence, recommendation)
            - scan_stats (object with keys: records_scanned, fields_scanned)
            
            Data: {json.dumps(dataset_sample)}
            """
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional Data Privacy Auditor. You analyze datasets for leaked PII. You always speak in valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={ "type": "json_object" }
            )
            
            # Parse result
            content = response.choices[0].message.content
            pii_report = json.loads(content)
            
            # Ensure scan_stats existence
            if "scan_stats" not in pii_report:
                pii_report["scan_stats"] = {
                    "records_scanned": len(dataset_sample),
                    "fields_scanned": len(dataset_sample[0].keys()) if dataset_sample else 0
                }
            
            return {
                "has_pii": pii_report.get("has_pii", False),
                "pii_fields": pii_report.get("pii_fields", []),
                "pii_details": pii_report.get("pii_details", []),
                "classification": pii_report.get("classification", "Internal"),
                "confidence": pii_report.get("confidence", 0.85),
                "risk_level": pii_report.get("risk_level", "Low"),
                "scan_stats": pii_report["scan_stats"],
                "status": "warning" if pii_report.get("has_pii") else "passed",
                "recommendations": ["Apply data masking", "Encrypt sensitive fields"] if pii_report.get("has_pii") else [],
                "ai_powered": True,
                "masked_data": self.mask_pii(dataset_sample, pii_report.get("pii_fields", [])) if pii_report.get("has_pii") else dataset_sample
            }
        except Exception as e:
            logging.error(f"Ollama validation failed: {e}")
            print(f"⚠️ Ollama failed. Error: {e}")
            return self._fallback_pii_detection(dataset_sample)

    def _validate_pii_huggingface(self, dataset_sample: list) -> dict:
        """Direct call to Hugging Face Inference API (Free Tier)"""
        try:
            api_key = os.getenv("HF_API_KEY")
            model = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")
            
            if not api_key:
                print("Missing HF_API_KEY for 'huggingface' provider.")
                return self._fallback_pii_detection(dataset_sample)
                
            client = InferenceClient(token=api_key)
            
            # Mistral Instruct expects chat format
            messages = [
                {
                    "role": "system", 
                    "content": "You are a data privacy expert. Return ONLY valid JSON with keys: has_pii (bool), pii_fields (list), classification (str). Do NOT use markdown."
                },
                {
                    "role": "user", 
                    "content": f"Analyze this data for PII: {json.dumps(dataset_sample)}"
                }
            ]
            
            response = client.chat_completion(
                messages=messages,
                model=model,
                max_tokens=500,
                temperature=0.1
            )
            
            # Parse response
            content = response.choices[0].message.content
            clean_json = content.strip()
            
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_json:
                 clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
            print(f"HF Raw Response: {clean_json}")
            pii_report = json.loads(clean_json)
            
            return {
                "has_pii": pii_report.get("has_pii", False),
                "pii_fields": pii_report.get("pii_fields", []),
                "classification": pii_report.get("classification", "Public"),
                "status": "warning" if pii_report.get("has_pii") else "passed",
                "recommendations": ["Apply data masking"] if pii_report.get("has_pii") else [],
                "ai_powered": True
            }
        except Exception as e:
            logging.error(f"Hugging Face validation failed: {e}")
            print(f"⚠️ Hugging Face failed. Error: {e}")
            return self._fallback_pii_detection(dataset_sample)

    def _validate_pii_direct_sdk(self, dataset_sample: list) -> dict:
        """Direct call to GPT-4o-mini using Azure SDK"""
        try:
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
            
            if not endpoint or not api_key:
                print("Missing AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY. Skipping Direct SDK.")
                return self._fallback_pii_detection(dataset_sample)
                
            client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version="2024-12-01-preview"
            )
            
            prompt = f"""
            Analyze the following data sample for PII (Personally Identifiable Information).
            Return JSON with keys: has_pii (bool), pii_fields (list), classification (str).
            
            Data: {json.dumps(dataset_sample)}
            """
            
            response = client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": "You are a data privacy expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            pii_report = json.loads(content)
            
            return {
                "has_pii": pii_report.get("has_pii", False),
                "pii_fields": pii_report.get("pii_fields", []),
                "classification": pii_report.get("classification", "Public"),
                "status": "warning" if pii_report.get("has_pii") else "passed",
                "recommendations": ["Apply data masking"] if pii_report.get("has_pii") else [],
                "ai_powered": True
            }
            
        except Exception as e:
             logging.error(f"Direct SDK validation failed: {e}")
             print(f"⚠️ Direct SDK failed. Error: {e}")
             return self._fallback_pii_detection(dataset_sample)

    def _fallback_pii_detection(self, dataset_sample: list) -> dict:
        """Fallback PII detection using keywords with richer details"""
        pii_keywords = {
            'email': ('Contact Info', 'High'),
            'phone': ('Contact Info', 'Medium'),
            'ssn': ('Government ID', 'Critical'),
            'credit_card': ('Financial', 'Critical'),
            'address': ('Location', 'Medium'),
            'name': ('Identity', 'Low')
        }
        pii_details = []
        pii_fields = []
        
        if dataset_sample:
            for field in dataset_sample[0].keys():
                for kw, (p_type, risk) in pii_keywords.items():
                    if kw in field.lower():
                        pii_fields.append(field)
                        pii_details.append({
                            "field": field,
                            "type": p_type,
                            "confidence": 0.95,
                            "risk": risk,
                            "recommendation": f"Mask {field} using SHA-256"
                        })
                        break
        
        num_records = len(dataset_sample) if dataset_sample else 0
        num_fields = len(dataset_sample[0].keys()) if dataset_sample else 0
        
        return {
            "has_pii": len(pii_fields) > 0,
            "pii_fields": pii_fields,
            "pii_details": pii_details,
            "classification": "Confidential" if pii_fields else "Public",
            "confidence": 1.0 if pii_fields else 0.5,
            "risk_level": "High" if pii_fields else "Low",
            "scan_stats": {
                "records_scanned": num_records,
                "fields_scanned": num_fields
            },
            "status": "warning" if pii_fields else "passed",
            "recommendations": ["Apply data masking"] if pii_fields else [],
            "masked_data": self.mask_pii(dataset_sample, pii_fields) if pii_fields else dataset_sample
        }
    
    def validate_data_quality(self, dataset_sample: list, field_names: list) -> dict:
        """
        Comprehensive data quality validation
        
        Args:
            dataset_sample: Sample data rows
            field_names: List of field names
            
        Returns:
            Validation results
        """
        results = {
            "pii_validation": self.validate_pii(dataset_sample),
            "quality_checks": self._basic_quality_checks(dataset_sample),
            "timestamp": "now"
        }
        
        # Determine overall status
        if results["pii_validation"]["status"] == "warning":
            results["status"] = "warning"
        elif any(c.get("status") == "failed" for c in results["quality_checks"]):
            results["status"] = "failed"
        else:
            results["status"] = "passed"
        
        return results
    
    def _basic_quality_checks(self, dataset_sample: list) -> list:
        """Basic quality checks (nulls, duplicates)"""
        checks = []
        
        if not dataset_sample:
            return checks
        
        # Null check
        null_counts = {}
        for row in dataset_sample:
            for key, value in row.items():
                if value is None or value == '' or str(value).lower() == 'null':
                    null_counts[key] = null_counts.get(key, 0) + 1
        
        null_percentage = max(null_counts.values()) / len(dataset_sample) * 100 if null_counts else 0
        
        checks.append({
            "check_name": "null_value_check",
            "status": "failed" if null_percentage > 5 else "passed",
            "details": {"null_percentage": null_percentage},
            "recommendation": "Review data quality" if null_percentage > 5 else "No action needed"
        })
        
        # Duplicate check
        key_field = list(dataset_sample[0].keys())[0] if dataset_sample else "id"
        keys = [row.get(key_field) for row in dataset_sample]
        duplicate_count = len(keys) - len(set(keys))
        
        checks.append({
            "check_name": "duplicate_check",
            "status": "passed" if duplicate_count == 0 else "warning",
            "details": {"duplicate_count": duplicate_count},
            "recommendation": "No duplicates" if duplicate_count == 0 else "Implement deduplication"
        })
        
        return checks

    def _validate_pii_openai_standard(self, dataset_sample: list) -> dict:
        """Direct call to Standard OpenAI (api.openai.com)"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            
            if not api_key:
                print("Missing OPENAI_API_KEY for 'openai' provider.")
                return self._fallback_pii_detection(dataset_sample)
                
            client = OpenAI(api_key=api_key)
            
            prompt = f"""
            Analyze the following data sample for PII (Personally Identifiable Information).
            Return JSON with keys: has_pii (bool), pii_fields (list), classification (str).
            
            Data: {json.dumps(dataset_sample)}
            """
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a data privacy expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            pii_report = json.loads(content)
            
            return {
                "has_pii": pii_report.get("has_pii", False),
                "pii_fields": pii_report.get("pii_fields", []),
                "classification": pii_report.get("classification", "Public"),
                "status": "warning" if pii_report.get("has_pii") else "passed",
                "recommendations": ["Apply data masking"] if pii_report.get("has_pii") else [],
                "ai_powered": True
            }
        except Exception as e:
            logging.error(f"OpenAI Standard validation failed: {e}")
            return self._fallback_pii_detection(dataset_sample)

if __name__ == "__main__":
    # Simple CLI for dashboard/testing
    import sys
    validator = PromptFlowValidator()
    
    print("🛠️ Starting AI Data Validation (Ollama/Azure)...")
    
    # Sample data for validation
    sample_data = [
        {"id": 1, "name": "Ranit Sinha", "email": "ranit@example.com", "phone": "+91-9876543210", "city": "Bangalore"},
        {"id": 2, "name": "John Doe", "email": "john.doe@notreal.com", "phone": "555-0199", "city": "Seattle"}
    ]
    
    print(f"📊 Analyzing {len(sample_data)} sample records from Silver layer...")
    
    results = validator.validate_data_quality(sample_data, list(sample_data[0].keys()))
    
    print(f"🔍 PII Detection Result: {'🚨 PII DETECTED' if results['pii_validation']['has_pii'] else '✅ NO PII FOUND'}")
    if results['pii_validation']['has_pii']:
        print(f"🚩 Flagged Fields: {', '.join(results['pii_validation']['pii_fields'])}")
        print(f"🛡️ Recommendation: {results['pii_validation']['recommendations'][0]}")
    
    print(f"📈 Quality Status: {results['status'].upper()}")
    print(f"✨ Validation Complete via {validator.sys_provider.upper()}.")
    
    # Output JSON for potential parsing
    print(json.dumps(results))
