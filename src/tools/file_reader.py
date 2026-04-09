from pathlib import Path
from typing import Dict, Optional


def read_file(
    repo_root: Path,
    relative_path: str,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
    max_chars: int = 4000,
) -> Dict:
    """
    读取仓库中的文件。
    relative_path: 相对 repo_root 的路径
    start_line/end_line: 可选，按行截取
    """
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

    lines = text.splitlines()

    if start_line is not None or end_line is not None:
        start = 1 if start_line is None else max(1, start_line)
        end = len(lines) if end_line is None else min(len(lines), end_line)
        sliced = lines[start - 1:end]
        text = "\n".join(sliced)

    if len(text) > max_chars:
        text = text[:max_chars] + "\n...[TRUNCATED]"

    return {
        "ok": True,
        "path": relative_path,
        "content": text,
    }