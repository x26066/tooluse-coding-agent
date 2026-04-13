from task_parser import (
    parse_edit_task,
    parse_read_task,
    parse_create_task,
    parse_append_task,
)


def test_parse_edit_task_success():
    result = parse_edit_task("把 hello.py 里的 hello error 改成 hello benchmark")
    assert result["ok"] is True
    assert result["file_name"] == "hello.py"
    assert result["old_text"] == "hello error"
    assert result["new_text"] == "hello benchmark"


def test_parse_edit_task_fail():
    result = parse_edit_task("读取 hello.py")
    assert result["ok"] is False
    assert result["error"] == "不是编辑任务"


def test_parse_read_task_read():
    result = parse_read_task("读取 hello.py")
    assert result["ok"] is True
    assert result["file_name"] == "hello.py"


def test_parse_read_task_view():
    result = parse_read_task("查看 notes.txt")
    assert result["ok"] is True
    assert result["file_name"] == "notes.txt"


def test_parse_read_task_open():
    result = parse_read_task("打开 demo.py")
    assert result["ok"] is True
    assert result["file_name"] == "demo.py"


def test_parse_read_task_fail():
    result = parse_read_task("创建 notes.txt")
    assert result["ok"] is False
    assert result["error"] == "不是读取任务"


def test_parse_create_task_create():
    result = parse_create_task("创建 notes_a.txt")
    assert result["ok"] is True
    assert result["file_name"] == "notes_a.txt"


def test_parse_create_task_new():
    result = parse_create_task("新建 notes_b.txt")
    assert result["ok"] is True
    assert result["file_name"] == "notes_b.txt"


def test_parse_create_task_fail():
    result = parse_create_task("读取 hello.py")
    assert result["ok"] is False
    assert result["error"] == "不是创建任务"


def test_parse_append_task_success():
    result = parse_append_task("在 notes_a.txt 里追加 alpha")
    assert result["ok"] is True
    assert result["file_name"] == "notes_a.txt"
    assert result["content"] == "alpha"


def test_parse_append_task_fail():
    result = parse_append_task("把 hello.py 里的 hello error 改成 hello benchmark")
    assert result["ok"] is False
    assert result["error"] == "不是追加任务"