import subprocess
import sys
from pathlib import Path
from typing import Dict

from tools.path_utils import safe_resolve_path


def run_python_file(
    repo_root: Path,
    relative_path: str,
    timeout: int = 10,
) -> Dict:
    """
    直接运行某个 Python 文件，用来做最小验证
    使用当前 Python 解释器，避免环境不一致。
    """
    try:
        file_path = safe_resolve_path(repo_root, relative_path)
    except Exception as e:
        return {
            "ok": False,
            "error": f"路径校验失败: {e}",
        }

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
        result = subprocess.run(
            [sys.executable, str(file_path)],
            cwd=repo_root.resolve(),
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
        )
    except Exception as e:
        return {
            "ok": False,
            "error": f"运行失败: {e}",
        }

    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }