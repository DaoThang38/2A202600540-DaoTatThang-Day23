"""Report generation helper.

TODO(student): implement report rendering using MetricsReport data
and the template in reports/lab_report_template.md.
"""

from __future__ import annotations

from pathlib import Path

from .metrics import MetricsReport


def render_report(metrics: MetricsReport) -> str:
    """Render a complete lab report from metrics data."""

    lines = []
    lines.append("# Day 08 Lab Report\n")
    lines.append("## 1. Metrics Summary\n")
    lines.append(f"- **Total Scenarios**: {metrics.total_scenarios}")
    lines.append(f"- **Success Rate**: {metrics.success_rate:.2%}")
    lines.append(f"- **Average Nodes Visited**: {metrics.avg_nodes_visited:.1f}")
    lines.append(f"- **Total Retries**: {metrics.total_retries}")
    lines.append(f"- **Total Interrupts**: {metrics.total_interrupts}\n")
    
    lines.append("## 2. Per-scenario Results\n")
    lines.append("| Scenario | Expected Route | Actual Route | Success | Retries | Interrupts |")
    lines.append("|---|---|---|---:|---:|---:|")
    for s in metrics.scenario_metrics:
        success = "Yes" if s.success else "No"
        lines.append(f"| {s.scenario_id} | {s.expected_route} | {s.actual_route} | {success} | {s.retry_count} | {s.interrupt_count} |")
    
    lines.append("\n## 3. Architecture & State Schema\n")
    lines.append("The LangGraph workflow consists of conditional routing from the classification step into specialized nodes. A retry loop is built via `route_after_evaluate`, and `route_after_approval` forms the HITL pattern.")
    lines.append("Additional state fields added:")
    lines.append("- `evaluation_result`: Controls retry logic loop.")
    lines.append("- `pending_question`: Tracks info needed from user.")
    lines.append("- `proposed_action`: For the HITL review step.")
    lines.append("- `approval`: Contains reviewer decision.\n")
    
    lines.append("## 4. Failure Analysis\n")
    lines.append("- **Tool Retry Exhaustion**: Simulated in scenario 7, triggering the `dead_letter` route.")
    lines.append("- **Invalid classifications**: Evaluated directly through LLM structured outputs to enforce enums.\n")
    
    lines.append("## 5. Improvement Plan\n")
    lines.append("- Add parallel execution for multiple tool scenarios.")
    lines.append("- Connect to a real database checkpointer for crash recovery.\n")

    return "\n".join(lines)


def write_report(metrics: MetricsReport, output_path: str | Path) -> None:
    """Write the rendered report to a file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_report(metrics), encoding="utf-8")
