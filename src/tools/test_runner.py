import subprocess
from pathlib import Path
from typing import Dict


def run_python_file(
    repo_root: Path,
    relative_path: str,
    timeout: int = 10,
) -> Dict:
    """
    直接运行某个 Python 文件，用来做最小验证
    """
    file_path = repo_root / relative_path

    if not file_path.exists():
        return {
            "ok": False,
            "error": f"文件不存在: {relative_path}",
        }

    try:
        result = subprocess.run(
            ["python", str(file_path)],
            cwd=repo_root,
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