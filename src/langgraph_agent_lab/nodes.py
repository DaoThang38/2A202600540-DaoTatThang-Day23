"""Node functions for the LangGraph workflow.

Each function receives AgentState and returns a partial state update dict.
Do NOT mutate input state — return new values only.

LLM REQUIREMENT:
- classify_node MUST use a real LLM call (structured output for intent classification)
- answer_node MUST use a real LLM call (grounded response generation)
- evaluate_node SHOULD use LLM-as-judge (bonus points; heuristic acceptable for base score)
"""

from __future__ import annotations
import os

from pydantic import BaseModel, Field
from .state import AgentState, make_event, Route
from .llm import get_llm
from langchain_core.messages import HumanMessage


# ─── EXAMPLE: working node (provided for reference) ──────────────────
def intake_node(state: AgentState) -> dict:
    """Normalize raw query. This node is provided as a working example."""
    query = state.get("query", "").strip()
    return {
        "query": query,
        "messages": [f"intake:{query[:40]}"],
        "events": [make_event("intake", "completed", "query normalized")],
    }


# ─── TODO(student): implement ALL nodes below ────────────────────────


class IntentClassification(BaseModel):
    route: Route = Field(description="The route classification for the query based on the specified priority: risky > tool > missing_info > error > simple.")

def classify_node(state: AgentState) -> dict:
    query = state.get("query", "")
    llm = get_llm()
    structured_llm = llm.with_structured_output(IntentClassification)
    prompt = f"""Classify the user's support-ticket query into one of the following routes:
- risky: Actions with side effects like refunds, deletions, sending emails, cancellations.
- tool: Information lookups like order status, tracking, search queries.
- missing_info: Vague/incomplete queries lacking actionable context.
- error: System failures like timeouts, crashes, service unavailable.
- simple: General questions answerable without tools or actions.

Priority: risky > tool > missing_info > error > simple.

Query: {query}"""
    classification = structured_llm.invoke([HumanMessage(content=prompt)])
    
    route = classification.route.value if hasattr(classification.route, 'value') else classification.route
    risk_level = "high" if route == Route.RISKY else "low"
    
    return {
        "route": route,
        "risk_level": risk_level,
        "events": [make_event("classify_node", "completed", f"Classified as {route}")],
    }


def tool_node(state: AgentState) -> dict:
    attempt = state.get("attempt", 0)
    route = state.get("route", "")
    
    if route == Route.ERROR and attempt < 2:
        result_string = "ERROR: Timeout failure while processing request."
    else:
        result_string = "SUCCESS: Tool executed successfully."
        
    return {
        "tool_results": [result_string],
        "events": [make_event("tool_node", "completed", f"Tool executed with result: {result_string}")],
    }


class Evaluation(BaseModel):
    result: str = Field(description="Must be 'success' or 'needs_retry'. Set 'needs_retry' if there was an ERROR.")

def evaluate_node(state: AgentState) -> dict:
    tool_results = state.get("tool_results", [])
    latest_result = tool_results[-1] if tool_results else ""
    
    # LLM-as-judge implementation
    llm = get_llm()
    structured_llm = llm.with_structured_output(Evaluation)
    prompt = f"Evaluate the following tool execution result. If the result contains an error or failure, return 'needs_retry'. Otherwise, return 'success'.\n\nResult: {latest_result}"
    evaluation = structured_llm.invoke([HumanMessage(content=prompt)])
    eval_res = evaluation.result
    
    return {
        "evaluation_result": eval_res,
        "events": [make_event("evaluate_node", "completed", f"Evaluation result: {eval_res}")],
    }


class FinalAnswer(BaseModel):
    answer: str = Field(description="The final answer to the user's query.")

def answer_node(state: AgentState) -> dict:
    query = state.get("query", "")
    tool_results = state.get("tool_results", [])
    approval = state.get("approval", {})
    
    llm = get_llm()
    structured_llm = llm.with_structured_output(FinalAnswer)
    
    context = f"Tool Results: {tool_results}\nApproval Decision: {approval}"
    prompt = f"Answer the user's query based on the following context. If context is empty, answer directly.\n\nContext: {context}\n\nQuery: {query}"
    
    response = structured_llm.invoke([HumanMessage(content=prompt)])
    final_ans = response.answer
    
    return {
        "final_answer": final_ans,
        "events": [make_event("answer_node", "completed", "Answer generated")],
    }


def ask_clarification_node(state: AgentState) -> dict:
    query = state.get("query", "")
    
    llm = get_llm()
    prompt = f"The following user query is vague or missing information. Ask a single, clear clarification question to get the required info.\n\nQuery: {query}"
    response = llm.invoke([HumanMessage(content=prompt)])
    question = response.content if hasattr(response, 'content') else str(response)
    
    return {
        "pending_question": question,
        "final_answer": question,
        "events": [make_event("ask_clarification_node", "completed", "Clarification requested")],
    }


def risky_action_node(state: AgentState) -> dict:
    query = state.get("query", "")
    proposed = f"Proposed action based on query: {query}. Requires explicit approval."
    return {
        "proposed_action": proposed,
        "events": [make_event("risky_action_node", "completed", "Risky action prepared")],
    }


def approval_node(state: AgentState) -> dict:
    # Check if real HITL is enabled
    if os.getenv("LANGGRAPH_INTERRUPT") == "true":
        from langgraph.types import interrupt
        decision = interrupt({"proposed_action": state.get("proposed_action", "")})
        approved = decision.get("approved", False)
        comment = decision.get("comment", "")
    else:
        approved = True
        comment = "Auto-approved in mock mode"

    approval = {
        "approved": approved,
        "reviewer": "mock-reviewer" if not os.getenv("LANGGRAPH_INTERRUPT") == "true" else "human",
        "comment": comment
    }
    return {
        "approval": approval,
        "events": [make_event("approval_node", "completed", f"Approval status: {approved}")],
    }


def retry_or_fallback_node(state: AgentState) -> dict:
    attempt = state.get("attempt", 0) + 1
    error_msg = f"Transient failure at attempt {attempt}"
    return {
        "attempt": attempt,
        "errors": [error_msg],
        "events": [make_event("retry_or_fallback_node", "completed", f"Retry attempt {attempt} recorded")],
    }


def dead_letter_node(state: AgentState) -> dict:
    msg = "The request could not be completed after maximum retry attempts."
    return {
        "final_answer": msg,
        "events": [make_event("dead_letter_node", "completed", "Max retries exceeded")],
    }


def finalize_node(state: AgentState) -> dict:
    return {
        "events": [make_event("finalize", "completed", "workflow finished")]
    }
