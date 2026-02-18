import os
from dotenv import load_dotenv

# Load env from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

from typing import Annotated, TypedDict, Union
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent, ToolNode
from langgraph.graph import StateGraph, END
import operator
from agents.tools import (
    inspect_excel_structure, 
    inspect_database_schema, 
    get_etl_lineage_logs, 
    check_data_quality, 
    push_lineage_to_graph
)

# --- State Application ---
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    next: str

# --- LLM Setup ---
# Using Ollama as requested
ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
ollama_model = os.getenv("OLLAMA_MODEL", "llama3")

print(f"Initializing Agents with Ollama (Model: {ollama_model}, URL: {ollama_base_url})...")
llm = ChatOllama(model=ollama_model, base_url=ollama_base_url, temperature=0)

# --- Agent Definitions ---

# 1. Orchestrator / Router
def orchestrator_node(state: AgentState):
    system_prompt = (
        "You are the Orchestrator for a Data Lineage & Quality System. "
        "Your goal is to route the user's request to the correct specialized agent.\n"
        "Available Agents:\n"
        "- 'structure_agent': For questions about file headers, database schemas, table columns.\n"
        "- 'lineage_agent': For questions about where data comes from, how it flows, what transformations happened.\n"
        "- 'quality_agent': For questions about missing values, nulls, stale dates, data anomalies.\n"
        "- 'glossary_agent': For definitions of business terms (e.g., 'what is a vendor_id', 'define transaction').\n"
        "- 'final_answer': If the user's request is a greeting or general, or if you have enough info to answer directly.\n\n"
        "Respond with ONLY the name of the next agent, or 'final_answer' if you are answering directly."
    )
    
    # We can just ask the LLM to decide
    response = llm.invoke([SystemMessage(content=system_prompt)] + messages)
    decision = response.content.strip().lower()
    
    # Basic mapping/fallback
    if "structure" in decision or "schema" in decision: return {"next": "structure_agent"}
    if "lineage" in decision or "flow" in decision or "where" in decision: return {"next": "lineage_agent"}
    if "quality" in decision or "stale" in decision: return {"next": "quality_agent"}
    if "glossary" in decision or "define" in decision or "what is" in decision: return {"next": "glossary_agent"}
    
    return {"next": "final_answer"}

# 2. Structure Agent
structure_tools = [inspect_excel_structure, inspect_database_schema]
structure_agent_executor = create_react_agent(llm, structure_tools)

def structure_node(state: AgentState):
    result = structure_agent_executor.invoke(state)
    return {"messages": [AIMessage(content=result["messages"][-1].content, name="structure_agent")], "next": "END"}

# 3. Lineage Agent
lineage_tools = [get_etl_lineage_logs, push_lineage_to_graph]
lineage_agent_executor = create_react_agent(llm, lineage_tools)

def lineage_node(state: AgentState):
    # Specialized prompt injection if needed, but ReAct handles it
    result = lineage_agent_executor.invoke(state)
    return {"messages": [AIMessage(content=result["messages"][-1].content, name="lineage_agent")], "next": "END"}

# 4. Quality Agent
quality_tools = [check_data_quality]
quality_agent_executor = create_react_agent(llm, quality_tools)

def quality_node(state: AgentState):
    result = quality_agent_executor.invoke(state)
    return {"messages": [AIMessage(content=result["messages"][-1].content, name="quality_agent")], "next": "END"}

# 5. Glossary Agent
@tool
def lookup_glossary_term(term: str):
    """Looks up a term in the Data Glossary."""
    glossary = {
        "customer_id": "Unique identifier for a customer. Source: SQLite DB.",
        "transaction_id": "Unique identifier for a transaction. Source: Excel Sheet 'Raw_Transactions'.",
        "amount": "The value of the transaction. Must be a positive float.",
        "vendor_id": "Unique ID for external vendors. Source: CSV 'vendor_contracts'.",
    }
    return glossary.get(term.lower(), f"Term '{term}' not found in glossary.")

glossary_tools = [lookup_glossary_term]
glossary_agent_executor = create_react_agent(llm, glossary_tools)

def glossary_node(state: AgentState):
    result = glossary_agent_executor.invoke(state)
    return {"messages": [AIMessage(content=result["messages"][-1].content, name="glossary_agent")], "next": "END"}

# 6. HITL (Human-In-The-Loop) Approval Node
def hitl_node(state: AgentState):
    """
    This node interrupts the graph flow to ask for human approval.
    In a real app, this would use `interrupt_before`.
    For this POC API, we return a special state that the Frontend interprets as "Needs Approval".
    """
    # Check if the last message contains a request for correction from lineage agent
    last_msg = state['messages'][-1]
    content = last_msg.content
    
    # If the Lineage Agent found a PENDING_APPROVAL status in the logs
    if "PENDING_APPROVAL" in content or "correction" in content.lower():
        # We return a specific structure that the API/Frontend will parse
        return {
            "messages": [AIMessage(content="[HITL_REQUIRED] I have found a lineage issue that requires your approval. Please review the suggested correction.", name="hitl_agent")],
            "next": "END"
        }
    
    # Otherwise, just end (or route back if needed)
    return {"next": "END"}

# --- Graph Contruction ---
workflow = StateGraph(AgentState)

workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("structure_agent", structure_node)
workflow.add_node("lineage_agent", lineage_node)
workflow.add_node("quality_agent", quality_node)
workflow.add_node("glossary_agent", glossary_node)
workflow.add_node("hitl_agent", hitl_node)

workflow.set_entry_point("orchestrator")

# Conditional edges based on orchestrator output
def router(state: AgentState):
    return state["next"]

workflow.add_conditional_edges(
    "orchestrator",
    router,
    {
        "structure_agent": "structure_agent",
        "lineage_agent": "lineage_agent",
        "quality_agent": "quality_agent",
        "glossary_agent": "glossary_agent",
        "hitl_agent": "hitl_agent",
        "final_answer": END
    }
)

workflow.add_edge("structure_agent", END)
workflow.add_edge("lineage_agent", "hitl_agent") # Check for approval after lineage analysis
workflow.add_edge("quality_agent", END)
workflow.add_edge("glossary_agent", END)
workflow.add_edge("hitl_agent", END)

app = workflow.compile()
