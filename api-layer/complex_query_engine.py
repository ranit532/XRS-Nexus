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

TOOLS AVAILABLE:
{tool_desc}

RULES:
1. To use a tool, you MUST output a JSON object in this format:
   {{"tool": "tool_name", "args": {{...}}}}
2. If you have the final answer, output a JSON object in this format:
   {{"final_answer": "Your answer here"}}
3. ONLY output the JSON object. Do not add commentary outside the JSON.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ]
        
        yield {"type": "start", "question": user_question}

        # Max turns to prevent infinite loops
        for turn in range(15):
            try:
                # 1. Inference Step
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.1,
                    response_format={ "type": "json_object" } # Force JSON mode if supported
                )
                
                content = response.choices[0].message.content
                # Yield raw thought
                yield {"type": "thought", "content": content, "turn": turn}
                
                # 2. Parsing Step
                try:
                    action = json.loads(content)
                except json.JSONDecodeError:
                    import re
                    match = re.search(r'\{.*\}', content, re.DOTALL)
                    if match:
                        action = json.loads(match.group(0))
                    else:
                        yield {"type": "error", "content": "Failed to parse JSON response."}
                        messages.append({"role": "user", "content": "Error: Your response was not valid JSON. Please try again, outputting ONLY the JSON object."})
                        continue

                # 3. Execution Step
                if "final_answer" in action:
                    yield {"type": "final_answer", "content": action['final_answer']}
                    return
                
                if "tool" in action:
                    func_name = action["tool"]
                    args = action.get("args", {})
                    
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
                    
                    # If APPROVE or None (default), proceed
                    yield {"type": "tool_call", "tool": func_name, "args": args}
                    
                    result = ""
                    if func_name == "get_all_table_names":
                        result = self._get_all_table_names()
                    elif func_name == "get_table_schema":
                        result = self._get_table_schema(args.get("table_name"))
                    elif func_name == "run_sql_query":
                        result = self._run_sql_query(args.get("query"))
                    elif func_name == "list_files":
                        result = self._list_files()
                    elif func_name == "read_file":
                        result = self._read_file(args.get("filename"))
                    
                    # Truncate result
                    truncated_result = result
                    if len(result) > 2000:
                        truncated_result = result[:2000] + "... [truncated]"

                    yield {"type": "tool_result", "tool": func_name, "content": truncated_result}
                    
                    # Append result to history
                    messages.append({"role": "assistant", "content": content})
                    messages.append({"role": "user", "content": f"Tool '{func_name}' Output: {result}"})
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
