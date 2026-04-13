from pathlib import Path

from tools.repo_search import search_repo


def test_search_repo_finds_filename(tmp_path: Path):
    (tmp_path / "hello.py").write_text('print("hello")\n', encoding="utf-8")

    results = search_repo(
        repo_root=tmp_path,
        query="hello.py",
        max_results=5,
    )

    assert len(results) >= 1
    assert results[0]["path"].endswith("hello.py")