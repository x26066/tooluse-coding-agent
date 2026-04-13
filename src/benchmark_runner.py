import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from agent_runner import run_minimal_agent
from logger_utils import save_log, save_named_json
from config import PROJECT_ROOT, LOG_DIR
from error_analyzer import build_error_summary
from metrics import extract_task_metrics, build_metrics_summary
from benchmark_setup import reset_temp_files, reset_hello_py


def load_tasks(task_file: Path) -> List[Dict]:
    with open(task_file, "r", encoding="utf-8") as f:
        return json.load(f)


def is_task_success(result: Dict) -> bool:
    final_status = result.get("final_status")
    status = result.get("status")

    if final_status not in {"success"} and status not in {"success"}:
        return False

    action_type = result.get("action_type")

    if action_type == "read":
        file_read_result = result.get("file_read_result")
        return bool(file_read_result and file_read_result.get("ok"))

    if action_type == "create":
        create_result = result.get("create_result")
        return bool(create_result and create_result.get("ok"))

    if action_type == "append":
        append_result = result.get("append_result")
        return bool(append_result and append_result.get("ok"))

    if action_type == "edit":
        edit_result = result.get("edit_result")
        if not (edit_result and edit_result.get("ok")):
            return False
        test_result = result.get("test_result")
        if test_result is None:
            return True
        return bool(test_result.get("ok"))

    return False


def build_category_summary(results: List[Dict]) -> Dict:
    total_counter = Counter()
    success_counter = Counter()

    for result in results:
        category = result.get("category", "unknown")
        total_counter[category] += 1
        if result.get("benchmark_success", False):
            success_counter[category] += 1

    summary = {}
    for category, total in total_counter.items():
        success = success_counter.get(category, 0)
        summary[category] = {
            "total": total,
            "success": success,
            "success_rate": round(success / total, 4) if total > 0 else 0.0,
        }

    return summary


def run_benchmark(task_file: Path, selector_mode: str = "rule") -> Dict:
    repo_root = PROJECT_ROOT
    tasks = load_tasks(task_file)

    results = []
    success_count = 0

    for idx, item in enumerate(tasks, start=1):
        task = item["task"]
        category = item.get("category", "unknown")

        result = run_minimal_agent(
            task=task,
            repo_root=repo_root,
            selector_mode=selector_mode,
        )
        success = is_task_success(result)

        result["benchmark_index"] = idx
        result["benchmark_success"] = success
        result["category"] = category
        result["metrics"] = extract_task_metrics(result)

        results.append(result)

        if success:
            success_count += 1

        print(f"[{idx}/{len(tasks)}] ({category}) {task} -> {'PASS' if success else 'FAIL'}")

    error_summary = build_error_summary(results)
    category_summary = build_category_summary(results)
    metrics_summary = build_metrics_summary(results)

    return {
        "selector_mode": selector_mode,
        "task_file": str(task_file),
        "total_tasks": len(tasks),
        "success_count": success_count,
        "success_rate": round(success_count / len(tasks), 4) if tasks else 0.0,
        "category_summary": category_summary,
        "metrics_summary": metrics_summary,
        "error_summary": error_summary,
        "results": results,
    }


def build_default_run_name(selector_mode: str, task_file: Path) -> str:
    stamp = datetime.now().strftime("%Y%m%d")
    return f"{selector_mode}_{task_file.stem}_{stamp}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run benchmark for the tool-use file agent.")
    parser.add_argument(
        "--selector-mode",
        choices=["rule", "llm"],
        required=True,
        help="Decision layer to use."
    )
    parser.add_argument(
        "--task-file",
        required=True,
        help="Path to the benchmark task file."
    )
    parser.add_argument(
        "--run-name",
        default=None,
        help="Optional name for saved summary output."
    )
    parser.add_argument(
        "--reset-before-run",
        action="store_true",
        help="Reset benchmark environment before running."
    )
    parser.add_argument(
        "--save-summary",
        action="store_true",
        help="Save summary JSON to outputs/benchmarks/."
    )
    return parser.parse_args()


def main():
    args = parse_args()

    task_file = PROJECT_ROOT / args.task_file
    selector_mode = args.selector_mode
    run_name = args.run_name or build_default_run_name(selector_mode, task_file)

    if args.reset_before_run:
        reset_temp_files()
        reset_hello_py()
        print("benchmark 环境已重置")

    summary = run_benchmark(task_file, selector_mode=selector_mode)

    log_path = save_log(LOG_DIR, summary)

    output_path = None
    if args.save_summary:
        output_path = PROJECT_ROOT / "outputs" / "benchmarks" / f"{run_name}_summary.json"
        save_named_json(output_path, summary)

    print("\n=== Benchmark Summary ===")
    print(f"selector_mode: {summary['selector_mode']}")
    print(f"总任务数: {summary['total_tasks']}")
    print(f"成功数: {summary['success_count']}")
    print(f"成功率: {summary['success_rate']:.2%}")

    print("\n=== Category Summary ===")
    for category, info in summary["category_summary"].items():
        print(
            f"{category}: total={info['total']}, "
            f"success={info['success']}, "
            f"success_rate={info['success_rate']:.2%}"
        )

    print("\n=== Metrics Summary ===")
    metrics_summary = summary["metrics_summary"]
    print(f"平均步骤数: {metrics_summary['average_step_count']}")
    print(f"平均 LLM 调用次数: {metrics_summary['average_llm_call_count']}")
    print(f"平均重试次数: {metrics_summary['average_retry_count']}")
    print(f"平均耗时(ms): {metrics_summary['average_latency_ms']}")

    print("\n=== Error Summary ===")
    error_summary = summary["error_summary"]
    print(f"失败任务数: {error_summary['failed_count']}")
    print(f"失败动作分布: {error_summary['failed_action_distribution']}")
    print(f"失败步骤分布: {error_summary['failed_step_distribution']}")

    print(f"\n日志路径: {log_path}")
    if output_path is not None:
        print(f"冻结结果路径: {output_path}")


if __name__ == "__main__":
    main()