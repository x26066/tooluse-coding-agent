from pathlib import Path

import pytest

from tools.path_utils import safe_resolve_path


def test_safe_resolve_path_allows_repo_internal_path(tmp_path: Path):
    repo_root = tmp_path
    target = safe_resolve_path(repo_root, "a/b.txt")
    assert target == (repo_root / "a/b.txt").resolve()


def test_safe_resolve_path_blocks_escape(tmp_path: Path):
    repo_root = tmp_path
    with pytest.raises(ValueError):
        safe_resolve_path(repo_root, "../../secret.txt")