from config import PROJECT_ROOT

TEMP_FILES = [
    "notes_a.txt",
    "notes_b.txt",
    "notes_c.txt",
    "notes_d.txt",
    "notes_e.txt",
    "notes_f.txt",
    "notes_llm.txt",
]

def reset_temp_files():
    for rel in TEMP_FILES:
        path = PROJECT_ROOT / rel
        if path.exists() and path.is_file():
            path.unlink()

def reset_hello_py():
    hello_path = PROJECT_ROOT / "hello.py"
    hello_path.write_text('print("hello error")\n', encoding="utf-8")

def main():
    reset_temp_files()
    reset_hello_py()
    print("benchmark 环境已重置")
    print("已删除临时文件:", TEMP_FILES)
    print('hello.py 已重置为: print("hello error")')

if __name__ == "__main__":
    main()