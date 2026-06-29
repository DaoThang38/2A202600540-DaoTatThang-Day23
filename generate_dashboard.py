import json
import sqlite3
from pathlib import Path
from langgraph_agent_lab.graph import build_graph
from langgraph_agent_lab.persistence import build_checkpointer
from langgraph_agent_lab.state import initial_state
from langgraph_agent_lab.scenarios import Scenario
from langgraph_agent_lab.state import Route

def get_demo_trace():
    """Runs a single scenario and captures the state transitions (trace)."""
    checkpointer = build_checkpointer("memory")
    graph = build_graph(checkpointer)
    
    scenario = Scenario(id="demo-trace", query="Please refund my order 999 immediately!", expected_route=Route.RISKY)
    state = initial_state(scenario)
    config = {"configurable": {"thread_id": "demo-trace-thread"}}
    
    trace_steps = []
    
    # Run the graph and stream state updates
    try:
        for event in graph.stream(state, config=config):
            for node_name, node_state in event.items():
                state_summary = {}
                for k, v in node_state.items():
                    if k == "messages" and v:
                        msg = v[-1] if isinstance(v, list) else v
                        if hasattr(msg, "content"):
                            state_summary[k] = f"[{msg.__class__.__name__}] {msg.content[:100]}..."
                        else:
                            state_summary[k] = f"[{type(msg).__name__}] {str(msg)[:100]}..."
                    else:
                        state_summary[k] = str(v)
                
                trace_steps.append({
                    "node": node_name,
                    "state": state_summary
                })
    except Exception as e:
        print(f"API Error during trace: {e}. Falling back to mock trace.")
        trace_steps.append({
            "node": "API_ERROR_FALLBACK",
            "state": {"error": str(e), "note": "Showing a mocked trace due to network error."}
        })
        trace_steps.extend([
            {"node": "intake", "state": {"query": scenario.query}},
            {"node": "classify", "state": {"classification": "risky"}},
            {"node": "risky_action", "state": {"proposed_action": "refund user"}},
            {"node": "approval", "state": {"approval": "approved"}},
            {"node": "tool", "state": {"tool_output": "Refund processed."}},
            {"node": "finalize", "state": {"status": "done"}}
        ])
            
    return scenario.query, trace_steps

def main():
    # 1. Read Report
    try:
        with open("reports/lab_report.md", "r", encoding="utf-8") as f:
            report_md = f.read()
    except FileNotFoundError:
        report_md = "No lab_report.md found."
        
    # 2. Read Diagram
    try:
        with open("graph_diagram.md", "r", encoding="utf-8") as f:
            diagram_md = f.read()
        mermaid_code = diagram_md.split("```mermaid")[1].split("```")[0].strip()
    except Exception:
        mermaid_code = "graph TD;\n  A-->B;"
        
    # 3. Generate Trace
    print("Generating demo trace...")
    query, trace_steps = get_demo_trace()
    
    # 4. Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LangGraph Lab Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
      mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f0f2f5; }}
        header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .container {{ display: flex; flex-wrap: wrap; gap: 20px; padding: 20px; max-width: 1400px; margin: 0 auto; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex: 1; min-width: 400px; }}
        h2 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-top: 0; }}
        .mermaid {{ display: flex; justify-content: center; }}
        pre {{ background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; border: 1px solid #e9ecef; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f8f9fa; font-weight: 600; }}
        .trace-step {{ border-left: 4px solid #3498db; padding-left: 15px; margin-bottom: 20px; }}
        .trace-node {{ font-weight: bold; color: #3498db; font-size: 1.1em; }}
        .trace-state {{ font-family: monospace; background: #f8f9fa; padding: 10px; border-radius: 4px; margin-top: 5px; white-space: pre-wrap; }}
    </style>
</head>
<body>
    <header>
        <h1>LangGraph Agentic Orchestration - Dashboard</h1>
    </header>
    <div class="container">
        
        <!-- Left Column: Report & Trace -->
        <div style="flex: 1; display: flex; flex-direction: column; gap: 20px;">
            <div class="card" id="report-card">
                <h2>Evaluation Report</h2>
                <div id="report-content"></div>
            </div>
            
            <div class="card">
                <h2>Execution Trace Demo</h2>
                <p><strong>Simulated Query:</strong> "{query}"</p>
                <div id="trace-content"></div>
            </div>
        </div>

        <!-- Right Column: Architecture -->
        <div class="card" style="flex: 1.5;">
            <h2>Architecture Diagram</h2>
            <div class="mermaid">
{mermaid_code}
            </div>
        </div>
        
    </div>

    <script>
        // Render Markdown
        const markdownContent = {json.dumps(report_md)};
        document.getElementById('report-content').innerHTML = marked.parse(markdownContent);
        
        // Render Trace
        const traceSteps = {json.dumps(trace_steps)};
        const traceContainer = document.getElementById('trace-content');
        traceSteps.forEach((step, index) => {{
            const stepDiv = document.createElement('div');
            stepDiv.className = 'trace-step';
            stepDiv.innerHTML = `
                <div class="trace-node">Step ${{index + 1}}: Node [${{step.node}}]</div>
                <div class="trace-state">${{JSON.stringify(step.state, null, 2)}}</div>
            `;
            traceContainer.appendChild(stepDiv);
        }});
    </script>
</body>
</html>"""

    output_path = Path("reports/dashboard.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"Dashboard successfully written to {output_path.absolute()}")

if __name__ == "__main__":
    main()
