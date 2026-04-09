from collections import Counter
from typing import Dict, List, Any


def infer_failed_step(result: Dict[str, Any]) -> str:
    """
    根据结果推断最可能失败的步骤
    """
    if result.get("final_status") == "parse_failed":
        return "tool_selector"

    if result.get("final_status") == "no_file_found":
        return "repo_search"

    action_type = result.get("action_type")

    if action_type == "read":
        file_read_result = result.get("file_read_result")
        if not (file_read_result and file_read_result.get("ok")):
            return "file_reader"

    elif action_type == "create":
        create_result = result.get("create_result")
        if not (create_result and create_result.get("ok")):
            return "create_file"

    elif action_type == "append":
        append_result = result.get("append_result")
        if not (append_result and append_result.get("ok")):
            return "append_to_file"

    elif action_type == "edit":
        edit_result = result.get("edit_result")
        if not (edit_result and edit_result.get("ok")):
            return "replace_in_file"

        test_result = result.get("test_result")
        if test_result is not None and not test_result.get("ok"):
            return "run_python_file"

    return "unknown"


def build_error_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    failed_results = [r for r in results if not r.get("benchmark_success", False)]

    action_counter = Counter()
    step_counter = Counter()
    failed_tasks = []

    for result in failed_results:
        action_type = result.get("action_type", "unknown")
        failed_step = infer_failed_step(result)

        action_counter[action_type] += 1
        step_counter[failed_step] += 1

        failed_tasks.append(
            {
                "task": result.get("task"),
                "action_type": action_type,
                "failed_step": failed_step,
                "selected_file": result.get("selected_file"),
                "final_status": result.get("final_status"),
            }
        )

    return {
        "failed_count": len(failed_results),
        "failed_action_distribution": dict(action_counter),
        "failed_step_distribution": dict(step_counter),
        "failed_tasks": failed_tasks,
    }