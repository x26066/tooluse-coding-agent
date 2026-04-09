from typing import Any, Dict, List


class TrajectoryRecorder:
    def __init__(self, task: str):
        self.task = task
        self.steps: List[Dict[str, Any]] = []

    def add_step(self, tool: str, tool_input: Dict[str, Any], tool_output: Dict[str, Any]):
        self.steps.append(
            {
                "tool": tool,
                "input": tool_input,
                "output": tool_output,
            }
        )

    def build(self, final_status: str, extra: Dict[str, Any] | None = None) -> Dict[str, Any]:
        data = {
            "task": self.task,
            "steps": self.steps,
            "final_status": final_status,
        }
        if extra:
            data.update(extra)
        return data