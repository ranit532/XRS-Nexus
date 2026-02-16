import os
import sqlite3
import json
import glob
from openai import OpenAI, AzureOpenAI
from dotenv import load_dotenv

# Load env vars
load_dotenv()

DB_PATH = "data/complex_erp.db"
UNSTRUCTURED_DIR = "data/unstructured"

class ComplexQueryEngine:
    def __init__(self):
        # Determine provider (default to ollama for local dev as per user request)
        self.provider = os.getenv("AI_PROVIDER", "ollama").lower()
        self.client = None
        self.model = None

        print(f"Initializing ComplexQueryEngine with provider: {self.provider}")

        if self.provider == "azure":
            self.client = AzureOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2024-02-01"
            )
            self.model = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        
        elif self.provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY"))
            self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
        
        elif self.provider == "ollama":
            base_url = os.getenv('OLLAMA_BASE_URL') or "http://localhost:11434"
            self.client = OpenAI(
                base_url=f"{base_url}/v1",
                api_key="ollama", 
                 default_headers={
                    "Bypass-Tunnel-Reminder": "true",
                    "ngrok-skip-browser-warning": "true"
                }
            )
            self.model = os.getenv("OLLAMA_MODEL", "phi3")

        elif self.provider == "mock":
            print("WARNING: Using MOCK provider. AI responses are simulated.")
            self.client = None
            self.model = "mock-gpt"

        # Define Tools
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_all_table_names",
                    "description": "Returns a list of all tables in the database to understand the schema overview.",
                    "parameters": {"type": "object", "properties": {}, "required": []}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_table_schema",
                    "description": "Returns the CREATE TABLE statement for a specific table to understand columns and foreign keys.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "table_name": {"type": "string", "description": "Name of the table"}
                        },
                        "required": ["table_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_sql_query",
                    "description": "Executes a SQL query against the database and returns the results. Use this to fetch structured data.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                             "query": {"type": "string", "description": "The SQL query to execute"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "Lists all available unstructured files (documents, spreadsheets).",
                    "parameters": {"type": "object", "properties": {}, "required": []}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Reads the content of a specific file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string", "description": "Name of the file to read"}
                        },
                        "required": ["filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_file",
                    "description": "Updates a text file by replacing a specific string with a new one. Use for fixing discrepancies in unstructured data.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string", "description": "Name of the file to update"},
                            "search_text": {"type": "string", "description": "The exact text to find and replace"},
                            "replacement_text": {"type": "string", "description": "The new text to insert"}
                        },
                        "required": ["filename", "search_text", "replacement_text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_sql_update",
                    "description": "Executes a SQL data modification query (UPDATE, INSERT, DELETE). Use for fixing discrepancies in structured data.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The SQL query to execute (must be UPDATE, INSERT, or DELETE)"}
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    # --- Tool Implementations ---

    def _get_all_table_names(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        conn.close()
        return json.dumps(tables)

    def _get_table_schema(self, table_name):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        schema = cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,)).fetchone()
        conn.close()
        return schema[0] if schema else "Table not found."

    def _run_sql_query(self, query):
        try:
            # Handle list input (AI edge case)
            if isinstance(query, list):
                if not query: return "Error: Empty query list."
                query = query[0]

            conn = sqlite3.connect(DB_PATH)
            # Use dictionary cursor for readability
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            rows = cursor.execute(query).fetchall()
            conn.close()
            # Convert to list of dicts
            return json.dumps([dict(row) for row in rows], default=str)
        except Exception as e:
            return f"Error executing SQL: {e}"

    def _execute_sql_update(self, query):
        try:
            # Handle list input
            if isinstance(query, list): query = query[0]
            
            # Simple security check (in real app, use stricter granular permissions)
            if not any(kw in query.upper() for kw in ["UPDATE", "INSERT", "DELETE"]):
                return "Error: Only UPDATE, INSERT, or DELETE queries are allowed for this tool."

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            changes = conn.total_changes
            conn.close()
            return f"Success: {changes} rows affected."
        except Exception as e:
            return f"Error executing SQL Update: {e}"

    def _list_files(self):
        files = glob.glob(f"{UNSTRUCTURED_DIR}/*")
        return json.dumps([os.path.basename(f) for f in files])

    def _read_file(self, filename):
        filepath = os.path.join(UNSTRUCTURED_DIR, filename)
        if not os.path.exists(filepath):
            return "File not found."
        try:
            with open(filepath, "r", encoding="utf-8", errors='ignore') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def _update_file(self, filename, search_text, replacement_text):
        filepath = os.path.join(UNSTRUCTURED_DIR, filename)
        if not os.path.exists(filepath):
            return "File not found."
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            if search_text not in content:
                return "Error: 'search_text' not found in file. Please ensure exact match including whitespace."
            
            new_content = content.replace(search_text, replacement_text)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
                
            return "Success: File updated."
        except Exception as e:
            return f"Error updating file: {e}"

    # --- Agent Logic ---

    def ask(self, user_question):
        """
        Backward compatible synchronous method.
        """
        print(f"\n🤖 Agent received: {user_question}")
        final_answer = "No answer found."
        
        # Create the generator
        generator = self.run_step_by_step(user_question)
        
        try:
            for event in generator:
                # Log events to console similar to the old print statements
                if event["type"] == "thought":
                    print(f"  🤔 Agent thought: {event['content']}")
                elif event["type"] == "tool_call":
                    print(f"  🛠️ Calling Request: {event['tool']}({event['args']})")
                elif event["type"] == "tool_result":
                    print(f"  ✅ Tool Result: {event['content'][:100]}...")
                elif event["type"] == "error":
                    print(f"  ❌ Error: {event['content']}")
                elif event["type"] == "final_answer":
                    print(f"  🏁 Final Answer: {event['content']}")
                    final_answer = event['content']
        except Exception as e:
            return f"Agent Error: {e}"
            
        return final_answer

    def run_step_by_step(self, user_question):
        """
        Generator that yields events for each step of the agent's reasoning.
        Useful for streaming UI updates.
        """
# System Prompt with Tool Definitions for ReAct
        tool_desc = json.dumps([t["function"] for t in self.tools], indent=2)
        system_prompt = f"""You are a 'Synergy Bot', a highly capable enterprise assistant. 
You have access to a complex database (30 tables) and a repository of unstructured documents.

Your goal is to answer User questions by connecting the dots between Structured Data (SQL) and Unstructured Data (Files).
CRITICAL: If you find a discrepancy, you must PROPOSE A FIX using `update_file` or `execute_sql_update`.

DATABASE HINTS & FILES:
1. BUDGETS:
   - SQL: 'departments' table (id, budget)
   - FILE: 'Budget_Review.md'
   - HINT: Check for 'SLASH BUDGET' recommendations in the file and match with SQL 'budget'.

2. LEGACY SYSTEMS:
   - SQL: 'projects' table (project_name, priority, budget, status)
   - FILE: 'Legacy_System_Notes.md'
   - HINT: If file says "Decommissioning" or "Deprecated", SQL should NOT list it as "Critical" or have high budget.

3. PRODUCT STRATEGY:
   - SQL: 'products' table (product_name, launch_date, priority)
   - FILE: 'Product_Strategy.csv'
   - HINT: CSV 'Launch_Date' is the source of truth. If SQL differs, update SQL.

4. VENDOR LEGAL:
   - SQL: 'vendors' table (vendor_name, status)
   - FILE: 'Vendor_Legal_Notes.md'
   - HINT: If Legal says "Dispute" or "Do not process", SQL status must be "On Hold" or "Suspended", NOT "Active".

TOOLS AVAILABLE:
{tool_desc}

RULES:
1. To use a tool, you MUST output a JSON object in this format:
   {{"tool": "tool_name", "args": {{...}}}}
2. If you have the final answer, output a JSON object in this format:
   {{"final_answer": "Your answer here"}}
3. ONLY output the JSON object. Do not add commentary outside the JSON.
4. OBSERVE the 'Tool Output' from the user carefully. Do NOT repeat the same tool call if you already have the output.
5. If you have enough information to answer the user's question, IMMEDIATELY output 'final_answer'.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ]
        
        yield {"type": "start", "question": user_question}

        # Track previous actions to prevent loops
        previous_actions = []

        # Track domains covered for smart prompting
        covered_domains = {
            "budget": False,
            "legacy": False,
            "product": False,
            "vendor": False
        }

        # Max turns to prevent infinite loops (Increased for multi-step audit)
        for turn in range(35):
            # --- SMART CHECKLIST HEURISTIC ---
            # Check what has been covered based on tools used
            action_history = str(previous_actions).lower()
            if "budget_review.md" in action_history: covered_domains["budget"] = True
            if "legacy_system_notes.md" in action_history: covered_domains["legacy"] = True
            if "product_strategy.csv" in action_history: covered_domains["product"] = True
            if "vendor_legal_notes.md" in action_history: covered_domains["vendor"] = True
            
            pending_domains = [k for k, v in covered_domains.items() if not v]

            try:
                print(f"--- Calling LLM (Turn {turn+1})... Please wait. ---")
                # 1. Inference Step
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.1,
                    response_format={ "type": "json_object" }
                )
                
                content = response.choices[0].message.content
                print(f"DEBUG RAW LLM OUTPUT (Turn {turn+1}): {content[:500]}")
                # Yield raw thought
                yield {"type": "thought", "content": content, "turn": turn}
                
                # 2. Parsing Step
                import re
                action = None
                parse_content = content.strip()
                
                if "```" in parse_content:
                    code_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", parse_content, re.DOTALL)
                    if code_match: parse_content = code_match.group(1)
                
                try:
                    action = json.loads(parse_content)
                except json.JSONDecodeError:
                    pass
                
                if action is None:
                    match = re.search(r'\{.*\}', parse_content, re.DOTALL)
                    if match:
                        try:
                            action = json.loads(match.group(0))
                        except:
                            pass
                            
                # --- HARD FALLBACK ---
                if action is None:
                     if turn > 5:
                        action = {"final_answer": content}
                     else:
                        yield {"type": "error", "content": "Failed to parse JSON response."}
                        messages.append({"role": "user", "content": "Error: Invalid JSON. Output ONLY JSON."})
                        continue

                # 3. Execution Step
                if "final_answer" in action:
                    # BLOCK EARLY EXIT if pending domains exist
                    if pending_domains and turn < 25:
                        yield {"type": "thought", "content": f"Agent tried to exit but pending domains remain: {pending_domains}"}
                        messages.append({"role": "user", "content": f"SYSTEM: You have NOT completed the full audit. You still need to check: {pending_domains}. Continue working."})
                        continue
                        
                    yield {"type": "final_answer", "content": action['final_answer']}
                    return
                
                if "tool" in action:
                    func_name = action["tool"]
                    args = action.get("args", {})

                    # --- LOOP DETECTION ---
                    action_signature = f"{func_name}:{json.dumps(args, sort_keys=True)}"
                    if action_signature in previous_actions:
                         yield {"type": "error", "content": f"Loop Detected: You already called {func_name} with these args."}
                         messages.append({"role": "user", "content": f"SYSTEM: You already executed '{func_name}' with these arguments. Do NOT repeat it."})
                         continue
                    previous_actions.append(action_signature)
                    
                    # HUMAN-IN-THE-LOOP: Request Approval
                    feedback = yield {
                        "type": "request_approval", 
                        "tool": func_name, 
                        "args": args,
                        "thought": content
                    }

                    # Handle Feedback
                    if feedback and str(feedback).startswith("REJECT"):
                        # User rejected the action with feedback
                        yield {"type": "user_feedback", "content": f"User Feedback: {feedback}"}
                        messages.append({"role": "assistant", "content": content})
                        messages.append({"role": "user", "content": f"User stopped execution. Feedback: {feedback}"})
                        continue
                    
                    # NEW: Allow feedback to OVERRIDE args (e.g., "APPROVE: {new_args}")
                    if feedback and str(feedback).startswith("APPROVE_WITH_ARGS:"):
                         try:
                             new_args_json = feedback.replace("APPROVE_WITH_ARGS:", "", 1).strip()
                             args = json.loads(new_args_json)
                             yield {"type": "user_feedback", "content": f"User Modified Args: {args}"}
                         except Exception as e:
                             print(f"Error parsing modified args: {e}")

                    # If APPROVE or None (default), proceed
                    yield {"type": "tool_call", "tool": func_name, "args": args}
                    
                    result = ""
                    if func_name == "get_all_table_names":
                        result = self._get_all_table_names()
                    elif func_name == "get_table_schema":
                        result = self._get_table_schema(args.get("table_name"))
                    elif func_name == "run_sql_query":
                        result = self._run_sql_query(args.get("query"))
                    elif func_name == "execute_sql_update":
                        result = self._execute_sql_update(args.get("query"))
                    elif func_name == "list_files":
                        result = self._list_files()
                    elif func_name == "read_file":
                        result = self._read_file(args.get("filename"))
                    elif func_name == "update_file":
                        result = self._update_file(args.get("filename"), args.get("search_text"), args.get("replacement_text"))
                    
                    # Truncate result
                    truncated_result = result
                    if len(result) > 2000:
                        truncated_result = result[:2000] + "... [truncated]"

                    yield {"type": "tool_result", "tool": func_name, "content": truncated_result}
                    
                    # Append result to history with HINTS
                    conversation_content = f"Tool '{func_name}' Output: {result}"
                    
                    # INTELLIGENT HINTING
                    if func_name == "run_sql_query" and "no such table" in str(result).lower():
                         conversation_content += "\nSYSTEM HINT: The table name seems incorrect. Use 'get_all_table_names' to see the correct schema."
                    
                    elif func_name == "read_file":
                        conversation_content += "\nSYSTEM HINT: You have the file content. Now cross-reference this with your SQL data calculation. If you see a discrepancy (e.g., Budget vs Recommendation), call `update_file` or `execute_sql_update` to fix it. If everything matches, output 'final_answer'."

                    elif func_name in ["update_file", "execute_sql_update"] and "Success" in str(result):
                        conversation_content += "\nSYSTEM HINT: Fix executed. Now you can provide the 'final_answer' summarizing what was fixed."
                    
                    messages.append({"role": "assistant", "content": content})
                    messages.append({"role": "user", "content": conversation_content})
                else:
                    yield {"type": "error", "content": "No tool or final_answer in response."}
                    messages.append({"role": "user", "content": "Error: Response must contain 'tool' or 'final_answer'."})

            except Exception as e:
                yield {"type": "error", "content": str(e)}
                return

        yield {"type": "error", "content": "Step limit reached."}

if __name__ == "__main__":
    # Test script
    engine = ComplexQueryEngine()
    
    # Simple Test
    # engine.ask("List all departments and their budgets.")
    
    # Synergy Test
    print(engine.ask("Find the budget for the 'Engineering' department from the database, and then check the 'Budget_Review.md' file to see if there are any notes about it."))
