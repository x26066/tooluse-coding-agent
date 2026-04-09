from pathlib import Path
from typing import Dict

from tools.repo_search import search_repo, choose_best_file
from tools.file_reader import read_file
from tools.file_editor import replace_in_file, create_file, append_to_file
from tools.test_runner import run_python_file
from trajectory import TrajectoryRecorder
from selector import select_action
from llm_selector import llm_select_action


def run_minimal_agent(
    task: str,
    repo_root: Path,
    selector_mode: str = "rule",
) -> Dict:
    recorder = TrajectoryRecorder(task=task)

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
        return recorder.build(
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
            return recorder.build(
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

    return recorder.build(
        final_status="success",
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
            "status": "success",
        },
    )