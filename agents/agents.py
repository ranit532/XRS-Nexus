import os
from dotenv import load_dotenv

# Load env from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Ensure OPENAI_API_KEY is set
if "OPENAI_API_KEY" not in os.environ and "OPENAI_KEY" in os.environ:
    os.environ["OPENAI_API_KEY"] = os.environ["OPENAI_KEY"]

from typing import Annotated, TypedDict, Union
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
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
# Using standard ChatOpenAI - User expected to have keys in env
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# --- Agent Definitions ---

# 1. Orchestrator / Router
def orchestrator_node(state: AgentState):
    messages = state['messages']
    system_prompt = (
        "You are the Orchestrator for a Data Lineage & Quality System. "
        "Your goal is to route the user's request to the correct specialized agent.\n"
        "Available Agents:\n"
        "- 'structure_agent': For questions about file headers, database schemas, table columns.\n"
        "- 'lineage_agent': For questions about where data comes from, how it flows, what transformations happened.\n"
        "- 'quality_agent': For questions about missing values, nulls, stale dates, data anomalies.\n"
        "- 'final_answer': If the user's request is a greeting or general, or if you have enough info to answer directly.\n\n"
        "Respond with ONLY the name of the next agent, or 'final_answer' if you are answering directly."
    )
    
    # We can just ask the LLM to decide
    response = llm.invoke([SystemMessage(content=system_prompt)] + messages)
    decision = response.content.strip().lower()
    
    # Basic mapping/fallback
    if "structure" in decision or "schema" in decision: return {"next": "structure_agent"}
    if "lineage" in decision or "flow" in decision: return {"next": "lineage_agent"}
    if "quality" in decision or "stale" in decision: return {"next": "quality_agent"}
    
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

# --- Graph Contruction ---
workflow = StateGraph(AgentState)

workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("structure_agent", structure_node)
workflow.add_node("lineage_agent", lineage_node)
workflow.add_node("quality_agent", quality_node)

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
        "final_answer": END
    }
)

workflow.add_edge("structure_agent", END)
workflow.add_edge("lineage_agent", END)
workflow.add_edge("quality_agent", END)

app = workflow.compile()
