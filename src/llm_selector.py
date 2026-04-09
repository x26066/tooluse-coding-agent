import json
import re
from typing import Any, Dict

from litellm import completion

from config import LLM_MODEL, LLM_API_BASE, DASHSCOPE_API_KEY


ALLOWED_ACTIONS = {"read", "create", "append", "edit"}


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()

    if len(text) >= 2 and text[0] == text[-1] and text[0] in {"'", '"', "`"}:
        text = text[1:-1].strip()

    text = text.replace("```json", "").replace("```", "").strip()
    return text


def _clean_target_file(value: Any) -> str:
    text = _clean_text(value)

    prefixes = [
        "创建 ",
        "新建 ",
        "读取 ",
        "查看 ",
        "打开 ",
        "帮我创建 ",
        "帮我新建 ",
        "请创建 ",
        "请新建 ",
        "建个 ",
        "建一个 ",
        "创建文件 ",
        "新建文件 ",
        "file ",
    ]
    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()

    suffixes = [
        " 这个文件",
        " 文件",
        " 一下",
        " 吧",
        " 呀",
        " 啊",
        " 呢",
    ]
    for suffix in suffixes:
        if text.endswith(suffix):
            text = text[: -len(suffix)].strip()

    # 去掉中文和英文引号包裹
    text = text.strip("“”\"'` ")

    return text


def _looks_like_create_task(task: str) -> bool:
    task = task.strip()
    create_keywords = [
        "创建",
        "新建",
        "建个",
        "建一个",
        "帮我创建",
        "帮我新建",
        "请创建",
        "请新建",
    ]
    return any(k in task for k in create_keywords)


def _fallback_create_parse(task: str) -> Dict[str, Any]:
    """
    当 LLM 在 create 任务上输出不稳时，使用轻量 fallback。
    """
    task = task.strip()

    patterns = [
        r"请新建一个\s+([A-Za-z0-9_\-./]+\.[A-Za-z0-9]+)",
        r"帮我创建\s+([A-Za-z0-9_\-./]+\.[A-Za-z0-9]+)",
        r"帮我新建\s+([A-Za-z0-9_\-./]+\.[A-Za-z0-9]+)",
        r"创建文件\s+([A-Za-z0-9_\-./]+\.[A-Za-z0-9]+)",
        r"新建文件\s+([A-Za-z0-9_\-./]+\.[A-Za-z0-9]+)",
        r"创建\s+([A-Za-z0-9_\-./]+\.[A-Za-z0-9]+)",
        r"新建\s+([A-Za-z0-9_\-./]+\.[A-Za-z0-9]+)",
        r"建个\s+([A-Za-z0-9_\-./]+\.[A-Za-z0-9]+)",
        r"建一个\s+([A-Za-z0-9_\-./]+\.[A-Za-z0-9]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, task)
        if match:
            target_file = _clean_target_file(match.group(1))
            if target_file:
                return {
                    "ok": True,
                    "action_type": "create",
                    "target_file": target_file,
                    "need_search": False,
                    "fallback_used": True,
                }

    return {
        "ok": False,
        "error": "create fallback failed",
    }


def build_selector_messages(task: str) -> list[dict]:
    system_prompt = """
你是一个文件操作 Agent 的决策器。
你的职责不是执行工具，而是把用户任务解析成一个 JSON 对象。

你必须只输出 JSON。
不要输出 markdown。
不要输出解释。
不要输出代码块。
不要输出 JSON 以外的任何字符。

支持的 action_type 只有：
- read
- create
- append
- edit

字段要求：

1. read
{
  "ok": true,
  "action_type": "read",
  "target_file": "<文件名>",
  "need_search": true
}

2. create
{
  "ok": true,
  "action_type": "create",
  "target_file": "<文件名>",
  "need_search": false
}

3. append
{
  "ok": true,
  "action_type": "append",
  "target_file": "<文件名>",
  "need_search": true,
  "content": "<要追加的内容>"
}

4. edit
{
  "ok": true,
  "action_type": "edit",
  "target_file": "<文件名>",
  "need_search": true,
  "old_text": "<旧文本>",
  "new_text": "<新文本>"
}

强约束：
- target_file 必须只包含文件名或路径
- target_file 不能包含“创建”“新建”“读取”“打开”等动词
- create 任务中，target_file 只能是文件名，不能是整句话
- edit 任务中，old_text 必须是被替换的原始文本
- edit 任务中，new_text 必须是新的替换文本
- 不允许把文件名写进 old_text 或 new_text
- append 任务中，content 只能是追加内容本身

如果无法解析，输出：
{
  "ok": false,
  "error": "无法解析任务"
}
""".strip()

    messages = [
        {"role": "system", "content": system_prompt},

        # read few-shot
        {"role": "user", "content": "任务：读取 hello.py"},
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "ok": True,
                    "action_type": "read",
                    "target_file": "hello.py",
                    "need_search": True,
                },
                ensure_ascii=False,
            ),
        },

        {"role": "user", "content": "任务：帮我看看 hello.py 现在写了什么"},
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "ok": True,
                    "action_type": "read",
                    "target_file": "hello.py",
                    "need_search": True,
                },
                ensure_ascii=False,
            ),
        },

        # create few-shot (强化)
        {"role": "user", "content": "任务：创建 notes_a.txt"},
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "ok": True,
                    "action_type": "create",
                    "target_file": "notes_a.txt",
                    "need_search": False,
                },
                ensure_ascii=False,
            ),
        },

        {"role": "user", "content": "任务：请新建一个 notes_d.txt"},
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "ok": True,
                    "action_type": "create",
                    "target_file": "notes_d.txt",
                    "need_search": False,
                },
                ensure_ascii=False,
            ),
        },

        {"role": "user", "content": "任务：帮我创建 notes_e.txt 这个文件"},
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "ok": True,
                    "action_type": "create",
                    "target_file": "notes_e.txt",
                    "need_search": False,
                },
                ensure_ascii=False,
            ),
        },

        {"role": "user", "content": "任务：建个 notes_f.txt"},
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "ok": True,
                    "action_type": "create",
                    "target_file": "notes_f.txt",
                    "need_search": False,
                },
                ensure_ascii=False,
            ),
        },

        # append few-shot
        {"role": "user", "content": "任务：在 notes_a.txt 里追加 alpha"},
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "ok": True,
                    "action_type": "append",
                    "target_file": "notes_a.txt",
                    "need_search": True,
                    "content": "alpha",
                },
                ensure_ascii=False,
            ),
        },

        {"role": "user", "content": "任务：把 gamma 追加到 notes_e.txt"},
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "ok": True,
                    "action_type": "append",
                    "target_file": "notes_e.txt",
                    "need_search": True,
                    "content": "gamma",
                },
                ensure_ascii=False,
            ),
        },

        # edit few-shot
        {"role": "user", "content": "任务：把 hello.py 里的 hello benchmark 改成 hello agent"},
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "ok": True,
                    "action_type": "edit",
                    "target_file": "hello.py",
                    "need_search": True,
                    "old_text": "hello benchmark",
                    "new_text": "hello agent",
                },
                ensure_ascii=False,
            ),
        },

        {"role": "user", "content": "任务：请把 hello.py 中的 hello harder 替换成 hello benchmark"},
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "ok": True,
                    "action_type": "edit",
                    "target_file": "hello.py",
                    "need_search": True,
                    "old_text": "hello harder",
                    "new_text": "hello benchmark",
                },
                ensure_ascii=False,
            ),
        },

        # real task
        {"role": "user", "content": f"任务：{task}"},
    ]

    return messages


def validate_decision(decision: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(decision, dict):
        return {"ok": False, "error": "model output is not a JSON object"}

    if not decision.get("ok"):
        return {
            "ok": False,
            "error": _clean_text(decision.get("error", "model cannot parse task")),
        }

    action_type = _clean_text(decision.get("action_type")).lower()
    if action_type not in ALLOWED_ACTIONS:
        return {"ok": False, "error": f"invalid action_type: {action_type}"}

    target_file = _clean_target_file(decision.get("target_file"))
    if not target_file:
        return {"ok": False, "error": "target_file is missing or invalid"}

    need_search = decision.get("need_search")
    if not isinstance(need_search, bool):
        return {"ok": False, "error": "need_search is missing or invalid"}

    cleaned = {
        "ok": True,
        "action_type": action_type,
        "target_file": target_file,
        "need_search": need_search,
    }

    if action_type == "append":
        content = _clean_text(decision.get("content"))
        if not content:
            return {"ok": False, "error": "append task missing content"}
        cleaned["content"] = content

    if action_type == "edit":
        old_text = _clean_text(decision.get("old_text"))
        new_text = _clean_text(decision.get("new_text"))

        if not old_text:
            return {"ok": False, "error": "edit task missing old_text"}
        if not new_text:
            return {"ok": False, "error": "edit task missing new_text"}

        if target_file in old_text or target_file in new_text:
            return {"ok": False, "error": "edit arguments contain file name unexpectedly"}

        cleaned["old_text"] = old_text
        cleaned["new_text"] = new_text

    return cleaned


def llm_select_action(task: str) -> Dict[str, Any]:
    if not DASHSCOPE_API_KEY:
        return {"ok": False, "error": "DASHSCOPE_API_KEY is empty"}

    messages = build_selector_messages(task)

    try:
        response = completion(
            model=LLM_MODEL,
            api_key=DASHSCOPE_API_KEY,
            api_base=LLM_API_BASE,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0,
        )
    except Exception as e:
        # create 任务失败时优先 fallback
        if _looks_like_create_task(task):
            fallback = _fallback_create_parse(task)
            if fallback.get("ok"):
                fallback["llm_error"] = f"{e}"
                return fallback

        return {"ok": False, "error": f"LLM 调用失败: {e}"}

    try:
        content = response.choices[0].message.content
    except Exception as e:
        if _looks_like_create_task(task):
            fallback = _fallback_create_parse(task)
            if fallback.get("ok"):
                fallback["llm_error"] = f"{e}"
                return fallback

        return {"ok": False, "error": f"无法读取模型输出: {e}"}

    try:
        decision = json.loads(content)
    except Exception as e:
        if _looks_like_create_task(task):
            fallback = _fallback_create_parse(task)
            if fallback.get("ok"):
                fallback["raw_output"] = content
                fallback["json_error"] = f"{e}"
                return fallback

        return {
            "ok": False,
            "error": f"模型输出不是合法 JSON: {e}",
            "raw_output": content,
        }

    validated = validate_decision(decision)
    if validated.get("ok"):
        return validated

    # create 专用 fallback
    if _looks_like_create_task(task):
        fallback = _fallback_create_parse(task)
        if fallback.get("ok"):
            fallback["raw_output"] = content
            fallback["validation_error"] = validated.get("error")
            return fallback

    validated["raw_output"] = content
    return validated