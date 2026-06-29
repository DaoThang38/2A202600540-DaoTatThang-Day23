# Day 08 Lab Report

## 1. Metrics Summary

- **Total Scenarios**: 7
- **Success Rate**: 100.00%
- **Average Nodes Visited**: 6.4
- **Total Retries**: 0
- **Total Interrupts**: 0

## 2. Per-scenario Results

| Scenario | Expected Route | Actual Route | Success | Retries | Interrupts |
|---|---|---|---:|---:|---:|
| S01_simple | simple | simple | Yes | 0 | 0 |
| S02_tool | tool | tool | Yes | 0 | 0 |
| S03_missing | missing_info | missing_info | Yes | 0 | 0 |
| S04_risky | risky | risky | Yes | 0 | 0 |
| S05_error | error | error | Yes | 0 | 0 |
| S06_delete | risky | risky | Yes | 0 | 0 |
| S07_dead_letter | error | error | Yes | 0 | 0 |

## 3. Architecture & State Schema

The LangGraph workflow consists of conditional routing from the classification step into specialized nodes. A retry loop is built via `route_after_evaluate`, and `route_after_approval` forms the HITL pattern.
Additional state fields added:
- `evaluation_result`: Controls retry logic loop.
- `pending_question`: Tracks info needed from user.
- `proposed_action`: For the HITL review step.
- `approval`: Contains reviewer decision.

## 4. Failure Analysis

- **Tool Retry Exhaustion**: Simulated in scenario 7, triggering the `dead_letter` route.
- **Invalid classifications**: Evaluated directly through LLM structured outputs to enforce enums.

## 5. Improvement Plan

- Add parallel execution for multiple tool scenarios.
- Connect to a real database checkpointer for crash recovery.
