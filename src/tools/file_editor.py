from pathlib import Path
from typing import Dict


def replace_in_file(
    repo_root: Path,
    relative_path: str,
    old_text: str,
    new_text: str,
) -> Dict:
    file_path = repo_root / relative_path

    if not file_path.exists():
        return {
            "ok": False,
            "error": f"文件不存在: {relative_path}",
        }

    if not file_path.is_file():
        return {
            "ok": False,
            "error": f"不是文件: {relative_path}",
        }

    try:
        text = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return {
            "ok": False,
            "error": f"读取失败: {e}",
        }

    if old_text not in text:
        return {
            "ok": False,
            "error": "未找到要替换的目标文本",
        }

    updated_text = text.replace(old_text, new_text, 1)

    try:
        file_path.write_text(updated_text, encoding="utf-8")
    except Exception as e:
        return {
            "ok": False,
            "error": f"写入失败: {e}",
        }

    return {
        "ok": True,
        "path": relative_path,
        "message": "替换成功",
    }


def create_file(
    repo_root: Path,
    relative_path: str,
    initial_content: str = "",
) -> Dict:
    file_path = repo_root / relative_path

    if file_path.exists():
        return {
            "ok": False,
            "error": f"文件已存在: {relative_path}",
        }

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(initial_content, encoding="utf-8")
    except Exception as e:
        return {
            "ok": False,
            "error": f"创建失败: {e}",
        }

    return {
        "ok": True,
        "path": relative_path,
        "message": "创建成功",
    }


def append_to_file(
    repo_root: Path,
    relative_path: str,
    content: str,
) -> Dict:
    file_path = repo_root / relative_path

    if not file_path.exists():
        return {
            "ok": False,
            "error": f"文件不存在: {relative_path}",
        }

    if not file_path.is_file():
        return {
            "ok": False,
            "error": f"不是文件: {relative_path}",
        }

    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        return {
            "ok": False,
            "error": f"追加失败: {e}",
        }

    return {
        "ok": True,
        "path": relative_path,
        "message": "追加成功",
    }