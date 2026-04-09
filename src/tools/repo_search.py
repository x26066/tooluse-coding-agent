from pathlib import Path
from typing import List, Dict


IGNORED_DIRS = {
    ".git",
    ".idea",
    ".venv",
    "__pycache__",
    "logs",
    "outputs",
    "node_modules",
}


def _should_skip(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def search_repo(
    repo_root: Path,
    query: str,
    max_results: int = 10,
) -> List[Dict]:
    """
    在仓库里搜索和 query 相关的文件。
    先按文件名匹配，再按文件内容匹配。
    返回统一结构，便于后面接 agent。
    """
    query = query.strip().lower()
    if not query:
        return []

    results: List[Dict] = []

    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        if _should_skip(path):
            continue

        rel_path = path.relative_to(repo_root)
        path_str = str(rel_path).lower()

        score = 0
        match_type = []

        # 1) 文件名匹配
        if query in path.name.lower():
            score += 3
            match_type.append("filename")

        if query in path_str:
            score += 2
            match_type.append("filepath")

        # 2) 文件内容匹配
        content_hit_line = None
        try:
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            for i, line in enumerate(lines, start=1):
                if query in line.lower():
                    score += 1
                    match_type.append("content")
                    content_hit_line = i
                    break
        except Exception:
            # 非文本文件或编码问题，直接跳过内容匹配
            pass

        if score > 0:
            results.append(
                {
                    "path": str(rel_path),
                    "score": score,
                    "match_type": list(dict.fromkeys(match_type)),
                    "hit_line": content_hit_line,
                }
            )

    results.sort(key=lambda x: (-x["score"], x["path"]))
    return results[:max_results]
def choose_best_file(results, target_file: str):
    """
    优先选精确文件名命中的结果，否则选第一条。
    """
    target_file = target_file.strip().lower()

    for item in results:
        if item["path"].replace("\\", "/").lower().endswith(target_file):
            return item["path"]

    return results[0]["path"] if results else None