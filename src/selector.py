from typing import Dict

from task_parser import (
    parse_edit_task,
    parse_read_task,
    parse_create_task,
    parse_append_task,
)


def select_action(task: str) -> Dict:
    """
    一个最简单的工具选择器：
    - 先判断任务类型
    - 再给出目标文件
    - 决定是否需要 repo_search
    """

    edit_task = parse_edit_task(task)
    if edit_task.get("ok"):
        return {
            "ok": True,
            "action_type": "edit",
            "target_file": edit_task["file_name"],
            "need_search": True,
            "old_text": edit_task["old_text"],
            "new_text": edit_task["new_text"],
        }

    read_task = parse_read_task(task)
    if read_task.get("ok"):
        return {
            "ok": True,
            "action_type": "read",
            "target_file": read_task["file_name"],
            "need_search": True,
        }

    create_task = parse_create_task(task)
    if create_task.get("ok"):
        return {
            "ok": True,
            "action_type": "create",
            "target_file": create_task["file_name"],
            "need_search": False,
        }

    append_task = parse_append_task(task)
    if append_task.get("ok"):
        return {
            "ok": True,
            "action_type": "append",
            "target_file": append_task["file_name"],
            "need_search": True,
            "content": append_task["content"],
        }

    return {
        "ok": False,
        "error": "暂不支持该任务格式",
    }