"""Project task routing: one capability tier above the chosen baseline.

This is a local policy using the model IDs exposed in this session, not a
claim about a universal measured ordering. It emits collaboration arguments;
it does not start agents, read credentials, call an API or change root model.
"""
from __future__ import annotations

import argparse
import json

LADDER = ("gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol", "gpt-6-astra")
TASKS = {
    "mechanical": ("gpt-5.6-luna", "medium"),
    "implementation": ("gpt-5.6-terra", "high"),
    "literature": ("gpt-5.6-sol", "high"),
    "benchmark_design": ("gpt-5.6-sol", "high"),
    "theorem": ("gpt-5.6-sol", "xhigh"),
    "certificate": ("gpt-5.6-sol", "xhigh"),
    "skeptic": ("gpt-5.6-sol", "xhigh"),
    "scientific_audit": ("gpt-6-astra", "xhigh"),
}


class RoutingUnavailable(RuntimeError):
    pass


def route(task_kind, available_models=None):
    if task_kind not in TASKS:
        raise ValueError(f"Unknown task kind: {task_kind}")
    baseline, effort = TASKS[task_kind]
    index = min(LADDER.index(baseline) + 1, len(LADDER) - 1)
    available = set(LADDER if available_models is None else available_models)
    selected = next((m for m in LADDER[index:] if m in available), None)
    if selected is None:
        raise RoutingUnavailable(f"No available model at or above required tier {LADDER[index]}; no downgrade")
    return {"task_kind": task_kind, "baseline": baseline, "requested_tier": LADDER[index],
            "model": selected, "reasoning_effort": effort, "fork_turns": "none",
            "capped_at_highest_tier": baseline == LADDER[-1],
            "availability_verified": available_models is not None}


def spawn_arguments(task_kind, task_name, message, available_models=None):
    choice = route(task_kind, available_models)
    if not isinstance(task_name, str) or not task_name or not isinstance(message, str) or not message:
        raise ValueError("A concrete nonempty task name and message are required")
    return {"task_name": task_name, "message": message, "model": choice["model"],
            "reasoning_effort": choice["reasoning_effort"], "fork_turns": "none"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_kind", choices=TASKS)
    parser.add_argument("--available", nargs="*", default=None)
    args = parser.parse_args()
    try:
        print(json.dumps(route(args.task_kind, args.available), indent=2))
    except RoutingUnavailable as exc:
        parser.exit(2, str(exc) + "\n")
