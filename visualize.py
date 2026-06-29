from langgraph_agent_lab.graph import build_graph
from langgraph_agent_lab.persistence import build_checkpointer

def main():
    graph = build_graph(build_checkpointer("memory"))
    mermaid_code = graph.get_graph().draw_mermaid()
    
    with open("graph_diagram.md", "w", encoding="utf-8") as f:
        f.write("# LangGraph Architecture Diagram\n\n")
        f.write("```mermaid\n")
        f.write(mermaid_code)
        f.write("\n```\n")
        
    print("Successfully generated graph_diagram.md")

if __name__ == "__main__":
    main()
