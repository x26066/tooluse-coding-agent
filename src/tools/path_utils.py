from pathlib import Path


def safe_resolve_path(repo_root: Path, relative_path: str) -> Path:
    """
    将 relative_path 解析为绝对路径，并确保它仍然位于 repo_root 内部。
    """
    root = repo_root.resolve()
    target = (root / relative_path).resolve()

    try:
        target.relative_to(root)
    except ValueError:
        raise ValueError(f"非法路径，目标超出仓库根目录: {relative_path}")

    return target