from typing import Dict, List, Any


def extract_task_metrics(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    从单条任务结果中提取统一指标。
    当前尽量复用已有字段，不强依赖 agent_runner 立即升级。
    """

    steps: List[Dict[str, Any]] = result.get("steps", []) or []

    step_count = len(steps)

    # 当前用 llm_selector 作为一次 LLM 调用的近似统计
    llm_call_count = sum(1 for step in steps if step.get("tool") == "llm_selector")

    # 如果以后 agent_runner 显式返回 retry_count / latency_ms，这里会自动读取
    retry_count = result.get("retry_count", 0)
    latency_ms = result.get("latency_ms", None)

    return {
        "step_count": step_count,
        "llm_call_count": llm_call_count,
        "retry_count": retry_count,
        "latency_ms": latency_ms,
    }


def build_metrics_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    对 benchmark 全量结果做统一指标汇总。
    """

    if not results:
        return {
            "average_step_count": 0.0,
            "average_llm_call_count": 0.0,
            "average_retry_count": 0.0,
            "average_latency_ms": None,
        }

    total_steps = 0
    total_llm_calls = 0
    total_retries = 0

    latency_values: List[float] = []

    for result in results:
        metrics = extract_task_metrics(result)
        total_steps += metrics["step_count"]
        total_llm_calls += metrics["llm_call_count"]
        total_retries += metrics["retry_count"]

        if metrics["latency_ms"] is not None:
            latency_values.append(metrics["latency_ms"])

    count = len(results)

    return {
        "average_step_count": round(total_steps / count, 4),
        "average_llm_call_count": round(total_llm_calls / count, 4),
        "average_retry_count": round(total_retries / count, 4),
        "average_latency_ms": round(sum(latency_values) / len(latency_values), 4)
        if latency_values
        else None,
    }