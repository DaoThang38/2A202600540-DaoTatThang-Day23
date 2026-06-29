import json
from langgraph_agent_lab.graph import build_graph
from langgraph_agent_lab.persistence import build_checkpointer
from langgraph_agent_lab.state import initial_state, Route
from langgraph_agent_lab.scenarios import Scenario

def run():
    print("Loading grading_questions.json...")
    with open("grading_questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)
        
    checkpointer = build_checkpointer("memory")
    graph = build_graph(checkpointer)
    
    results = []
    
    for q in questions:
        print(f"Running {q['id']}...")
        scenario = Scenario(id=q["id"], query=q["question"], expected_route=Route.TOOL)
        state = initial_state(scenario)
        config = {"configurable": {"thread_id": f"thread_{q['id']}"}}
        
        try:
            final_state = graph.invoke(state, config=config)
            route = final_state.get("route", "unknown")
            answer = final_state.get("final_answer", "")
            
            must_contain = q.get("must_contain_any", [])
            must_not_contain = q.get("must_not_contain", [])
            
            passed_contain = any(c.lower() in answer.lower() for c in must_contain) if must_contain else True
            passed_not_contain = not any(c.lower() in answer.lower() for c in must_not_contain) if must_not_contain else True
            
            success = passed_contain and passed_not_contain
        except Exception as e:
            route = "api_error"
            answer = f"Error: {e}"
            success = False
            
        results.append({
            "id": q["id"],
            "question": q["question"],
            "route": route,
            "answer": answer,
            "success": success
        })
        
    # Write Markdown Report
    report_lines = ["# KẾT QUẢ CHẠY GRADING QUESTIONS QUA LANGGRAPH AGENT\n"]
    report_lines.append("*Lưu ý: Agent Day 08 chưa được tích hợp RAG thực tế, nên các câu trả lời sẽ phụ thuộc vào kiến thức nền của LLM.*")
    report_lines.append("\n| ID | Phân Loại (Route) | Trạng thái (Pass/Fail) | Trích xuất câu trả lời |")
    report_lines.append("|---|---|---|---|")
    
    total_success = 0
    for r in results:
        status = "✅ Pass" if r["success"] else "❌ Fail"
        if r["success"]: total_success += 1
        snippet = r["answer"][:120].replace("\n", " ").replace("|", " ") + "..."
        report_lines.append(f"| {r['id']} | `{r['route']}` | {status} | {snippet} |")
        
    report_lines.append(f"\n**Tỷ lệ pass tiêu chí answer:** {total_success}/{len(questions)}\n")
    
    # Save as MD and show user
    with open("grading_questions_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print("Done. Wrote grading_questions_report.md")

if __name__ == "__main__":
    run()
