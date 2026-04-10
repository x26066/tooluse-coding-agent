import re
from typing import Dict, Any


def should_retry(result: Dict[str, Any]) -> bool:
    final_status = result.get("final_status")
    action_type = result.get("action_type")

    if final_status in {"parse_failed", "no_file_found", "tool_failed"}:
        return True

    if action_type == "create":
        create_result = result.get("create_result")
        if create_result and not create_result.get("ok"):
            return True

    if action_type == "edit":
        edit_result = result.get("edit_result")
        if edit_result and not edit_result.get("ok"):
            return True

        test_result = result.get("test_result")
        if test_result is not None and not test_result.get("ok"):
            return True

    return False


def build_reflection(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据失败结果构造一条最小 reflection。
    不是复杂 Reflexion，只做工程上够用的失败解释。
    """
    final_status = result.get("final_status")
    action_type = result.get("action_type")

    if final_status == "parse_failed":
        return {
            "failed_step": "selector",
            "reason": result.get("error", "task parsing failed"),
            "suggestion": "retry task parsing once",
        }

    if final_status == "no_file_found":
        return {
            "failed_step": "repo_search",
            "reason": "target file not found",
            "suggestion": "retry search once",
        }

    if action_type == "create":
        create_result = result.get("create_result", {})
        error = create_result.get("error", "")
        if "文件已存在" in error:
            return {
                "failed_step": "create_file",
                "reason": error,
                "suggestion": "treat as environment/state issue or reset benchmark files",
            }
        return {
            "failed_step": "create_file",
            "reason": error or "create failed",
            "suggestion": "retry create once",
        }

    if action_type == "edit":
        edit_result = result.get("edit_result", {})
        error = edit_result.get("error", "")
        if "未找到要替换的目标文本" in error:
            return {
                "failed_step": "replace_in_file",
                "reason": error,
                "suggestion": "re-read file content before retrying edit",
            }
        return {
            "failed_step": "replace_in_file",
            "reason": error or "edit failed",
            "suggestion": "retry edit once",
        }

    return {
        "failed_step": "unknown",
        "reason": result.get("error", "unknown failure"),
        "suggestion": "retry once",
    }


def normalize_retry_task(original_task: str, reflection: Dict[str, Any]) -> str:
    """
    最小重试任务标准化：
    当前只对 edit 场景做一点保守处理，其余直接原样重试。
    """
    suggestion = reflection.get("suggestion", "")

    # 当前先保持最小可控：绝大多数场景原任务重试
    # 以后你可以在这里加更复杂的重写逻辑
    if "re-read file content" in suggestion:
        return original_task

    return original_task