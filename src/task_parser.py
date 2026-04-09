import re
from typing import Dict


def parse_edit_task(task: str) -> Dict:
    task = task.strip()

    pattern = r"把\s+(.+?)\s+里[的]?\s+(.+?)\s+改成\s+(.+)"
    match = re.match(pattern, task)

    if not match:
        return {
            "ok": False,
            "error": "不是编辑任务"
        }

    return {
        "ok": True,
        "file_name": match.group(1).strip(),
        "old_text": match.group(2).strip(),
        "new_text": match.group(3).strip(),
    }


def parse_read_task(task: str) -> Dict:
    task = task.strip()

    patterns = [
        r"读取\s+(.+)",
        r"查看\s+(.+)",
        r"打开\s+(.+)",
    ]

    for pattern in patterns:
        match = re.match(pattern, task)
        if match:
            return {
                "ok": True,
                "file_name": match.group(1).strip(),
            }

    return {
        "ok": False,
        "error": "不是读取任务"
    }


def parse_create_task(task: str) -> Dict:
    task = task.strip()

    patterns = [
        r"创建\s+(.+)",
        r"新建\s+(.+)",
    ]

    for pattern in patterns:
        match = re.match(pattern, task)
        if match:
            return {
                "ok": True,
                "file_name": match.group(1).strip(),
            }

    return {
        "ok": False,
        "error": "不是创建任务"
    }


def parse_append_task(task: str) -> Dict:
    task = task.strip()

    pattern = r"在\s+(.+?)\s+里追加\s+(.+)"
    match = re.match(pattern, task)

    if not match:
        return {
            "ok": False,
            "error": "不是追加任务"
        }

    return {
        "ok": True,
        "file_name": match.group(1).strip(),
        "content": match.group(2),
    }