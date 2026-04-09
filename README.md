# Tool-Use File Agent: Rule vs LLM Selector Benchmark

一个面向文件操作任务的轻量 Agent 原型，支持 `read / create / append / edit / run` 等基础工具调用，并提供统一的 trajectory 记录、benchmark 批量评测和 error analysis。

项目的核心目标不是做一个前端 demo，而是构建一个**可执行、可评测、可比较**的 Agent 系统，并验证：

- 规则决策（rule-based selector）在模板化任务上是否足够稳定
- 大模型决策（LLM-based selector）在自然语言任务上是否具有更强泛化能力

---

## 项目亮点

- 实现了一个可执行的 Tool-Use Agent 原型，支持：
  - 文件搜索
  - 文件读取
  - 文件创建
  - 文本追加
  - 文本替换
  - Python 文件运行验证
- 设计并实现统一 trajectory 结构，记录每一步：
  - tool
  - input
  - output
- 构建了两套 benchmark：
  - 模板化任务 benchmark
  - 自然语言 harder benchmark
- 对比了 rule-based selector 与 LLM-based selector 的性能差异
- 基于 benchmark 和失败分析，迭代 LLM selector，最终在 harder benchmark 上达到 100% 成功率

---

## 项目结构

```text
tooluse-coding-agent/
├── src/
│   ├── main.py
│   ├── agent_runner.py
│   ├── selector.py
│   ├── llm_selector.py
│   ├── task_parser.py
│   ├── trajectory.py
│   ├── benchmark_runner.py
│   ├── benchmark_setup.py
│   ├── error_analyzer.py
│   └── tools/
│       ├── repo_search.py
│       ├── file_reader.py
│       ├── file_editor.py
│       └── test_runner.py
├── data/
│   └── benchmark/
│       ├── tasks.json
│       └── tasks_harder.json
├── logs/
├── outputs/
│   └── benchmarks/
├── docs/
│   └── experiments.md
├── hello.py
└── README.md