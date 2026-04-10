from config import LOG_DIR, PROJECT_ROOT
from logger_utils import save_log
from agent_runner import run_minimal_agent


def main():
    repo_root = PROJECT_ROOT

    task = "把 hello.py 里的 hello final 改成 hello llm"
    # task = "读取 hello.py"
    # task = "创建 notes_llm.txt"
    # task = "在 notes_llm.txt 里追加 hello llm\n"

    result = run_minimal_agent(
        task=task,
        repo_root=repo_root,
        selector_mode="llm",
    )

    log_path = save_log(LOG_DIR, result)

    print("LLM selector 单任务调试完成")
    print(f"任务: {task}")
    print(f"final_status: {result.get('final_status')}")
    print(f"selector_mode: {result.get('selector_mode')}")
    print(f"action_type: {result.get('action_type')}")
    print(f"target_file: {result.get('target_file')}")
    print(f"selected_file: {result.get('selected_file')}")
    print(f"retry_count: {result.get('retry_count')}")
    print(f"reflection: {result.get('reflection')}")
    print(f"retry_from_task: {result.get('retry_from_task')}")
    print(f"retry_task: {result.get('retry_task')}")
    print(f"failure_reason: {result.get('failure_reason')}")
    print(f"latency_ms: {result.get('latency_ms')}")
    print(f"日志路径: {log_path}")

    if result.get("error"):
        print(f"error: {result['error']}")
    if result.get("raw_output"):
        print(f"raw_output: {result['raw_output']}")

    print("\n=== steps ===")
    for step in result.get("steps", []):
        print(step["tool"], "=>", step["output"])


if __name__ == "__main__":
    main()