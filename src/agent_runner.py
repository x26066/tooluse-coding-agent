import time
from pathlib import Path
from typing import Dict

from tools.repo_search import search_repo, choose_best_file
from tools.file_reader import read_file
from tools.file_editor import replace_in_file, create_file, append_to_file
from tools.test_runner import run_python_file
from trajectory import TrajectoryRecorder
from selector import select_action
from llm_selector import llm_select_action
from retry_manager import should_retry, build_reflection, normalize_retry_task


def _run_once(
    task: str,
    repo_root: Path,
    selector_mode: str = "rule",
) -> Dict:
    start_time = time.perf_counter()
    recorder = TrajectoryRecorder(task=task)

    def finalize(final_status: str, extra: Dict) -> Dict:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 4)
        result = recorder.build(final_status=final_status, extra=extra)
        result["latency_ms"] = latency_ms
        return result

    if selector_mode == "llm":
        decision = llm_select_action(task)
        selector_tool_name = "llm_selector"
    else:
        decision = select_action(task)
        selector_tool_name = "tool_selector"

    recorder.add_step(
        selector_tool_name,
        {"task": task, "selector_mode": selector_mode},
        decision,
    )

    if not decision.get("ok"):
        return finalize(
            final_status="parse_failed",
            extra={
                "selector_mode": selector_mode,
                "error": decision.get("error", "任务解析失败"),
                "raw_output": decision.get("raw_output"),
            },
        )

    action_type = decision["action_type"]
    target_file = decision["target_file"]
    need_search = decision["need_search"]

    old_text = decision.get("old_text")
    new_text = decision.get("new_text")
    append_content = decision.get("content")

    search_results = []
    selected_file = target_file if action_type == "create" else None
    file_read_result = None
    edit_result = None
    test_result = None
    create_result = None
    append_result = None

    if need_search:
        search_results = search_repo(repo_root=repo_root, query=target_file, max_results=5)
        recorder.add_step(
            "repo_search",
            {"query": target_file, "max_results": 5},
            {"results": search_results},
        )

        if not search_results:
            return finalize(
                final_status="no_file_found",
                extra={
                    "selector_mode": selector_mode,
                    "action_type": action_type,
                    "target_file": target_file,
                    "search_results": [],
                },
            )

        selected_file = choose_best_file(search_results, target_file)
        recorder.add_step(
            "file_selector",
            {"target_file": target_file},
            {"selected_file": selected_file},
        )

        file_read_result = read_file(
            repo_root=repo_root,
            relative_path=selected_file,
            start_line=1,
            end_line=80,
        )
        recorder.add_step(
            "file_reader",
            {
                "relative_path": selected_file,
                "start_line": 1,
                "end_line": 80,
            },
            file_read_result,
        )

    if action_type == "edit":
        edit_result = replace_in_file(
            repo_root=repo_root,
            relative_path=selected_file,
            old_text=old_text,
            new_text=new_text,
        )
        recorder.add_step(
            "replace_in_file",
            {
                "relative_path": selected_file,
                "old_text": old_text,
                "new_text": new_text,
            },
            edit_result,
        )

        if edit_result.get("ok") and selected_file.endswith(".py"):
            test_result = run_python_file(
                repo_root=repo_root,
                relative_path=selected_file,
            )
            recorder.add_step(
                "run_python_file",
                {"relative_path": selected_file},
                test_result,
            )

    elif action_type == "create":
        create_result = create_file(
            repo_root=repo_root,
            relative_path=selected_file,
            initial_content="",
        )
        recorder.add_step(
            "create_file",
            {
                "relative_path": selected_file,
                "initial_content": "",
            },
            create_result,
        )

    elif action_type == "append":
        append_result = append_to_file(
            repo_root=repo_root,
            relative_path=selected_file,
            content=append_content,
        )
        recorder.add_step(
            "append_to_file",
            {
                "relative_path": selected_file,
                "content": append_content,
            },
            append_result,
        )

    # 判断当前动作是否真正成功
    task_success = True
    failure_reason = None

    if action_type == "read":
        task_success = bool(file_read_result and file_read_result.get("ok"))
        if not task_success:
            failure_reason = "file_read_failed"

    elif action_type == "create":
        task_success = bool(create_result and create_result.get("ok"))
        if not task_success:
            failure_reason = "create_failed"

    elif action_type == "append":
        task_success = bool(append_result and append_result.get("ok"))
        if not task_success:
            failure_reason = "append_failed"

    elif action_type == "edit":
        task_success = bool(edit_result and edit_result.get("ok"))
        if not task_success:
            failure_reason = "edit_failed"
        elif test_result is not None and not test_result.get("ok"):
            task_success = False
            failure_reason = "run_check_failed"

    final_status = "success" if task_success else "tool_failed"
    status = "success" if task_success else "failed"

    return finalize(
        final_status=final_status,
        extra={
            "selector_mode": selector_mode,
            "action_type": action_type,
            "target_file": target_file,
            "search_results": search_results,
            "selected_file": selected_file,
            "file_read_result": file_read_result,
            "edit_result": edit_result,
            "create_result": create_result,
            "append_result": append_result,
            "test_result": test_result,
            "status": status,
            "failure_reason": failure_reason,
        },
    )


def run_minimal_agent(
    task: str,
    repo_root: Path,
    selector_mode: str = "rule",
    max_retry: int = 1,
) -> Dict:
    total_start = time.perf_counter()

    first_result = _run_once(
        task=task,
        repo_root=repo_root,
        selector_mode=selector_mode,
    )

    first_result["retry_count"] = 0
    first_result["reflection"] = None

    if max_retry <= 0 or not should_retry(first_result):
        first_result["latency_ms"] = round((time.perf_counter() - total_start) * 1000, 4)
        return first_result

    reflection = build_reflection(first_result)
    retry_task = normalize_retry_task(task, reflection)

    second_result = _run_once(
        task=retry_task,
        repo_root=repo_root,
        selector_mode=selector_mode,
    )

    second_result["retry_count"] = 1
    second_result["reflection"] = reflection
    second_result["retry_from_task"] = task
    second_result["retry_task"] = retry_task
    second_result["latency_ms"] = round((time.perf_counter() - total_start) * 1000, 4)

    return second_result