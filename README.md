# Tool-Use File Agent: Rule vs LLM Selector Benchmark
A lightweight agent prototype for file-operation tasks. It supports `read`, `create`, `append`, `edit`, and `run`, and is built to be **executable, measurable, and comparable** rather than just demonstrative.

The project compares two decision strategies under the same execution pipeline:

- a **rule-based selector**
- an **LLM-based selector**

## What this repository is for

This repository is designed to answer one practical question:

> When file-operation tasks move from fixed templates to natural-language phrasing, how much does the **decision layer** matter?

The implementation therefore emphasizes:

- executable tool calls rather than mock outputs
- structured trajectories rather than opaque runs
- benchmark summaries rather than anecdotal examples
- observable failures rather than silent misclassification

## Snapshot

On fixed templates, the rule-based selector is fully stable.  
On harder natural-language variants, performance improves from **15%** with `rule_v1_harder` to **100%** with `llm_v3_create_fixed_harder` after prompt refinement, argument cleaning, create-task fallback handling, and minimal retry / reflection support.

Detailed benchmark design, per-version results, error analysis, and iteration notes are in [`docs/experiments.md`](docs/experiments.md).

## Repository Layout

```text
tooluse-coding-agent/
├── README.md
├── hello.py
├── src/
│   ├── main.py
│   ├── config.py
│   ├── logger_utils.py
│   ├── agent_runner.py
│   ├── selector.py
│   ├── llm_selector.py
│   ├── task_parser.py
│   ├── trajectory.py
│   ├── benchmark_runner.py
│   ├── benchmark_setup.py
│   ├── error_analyzer.py
│   ├── metrics.py
│   ├── retry_manager.py
│   └── tools/
│       ├── __init__.py
│       ├── repo_search.py
│       ├── file_reader.py
│       ├── file_editor.py
│       └── test_runner.py
├── data/
│   └── benchmark/
│       ├── tasks.json
│       └── tasks_harder.json
├── docs/
│   └── experiments.md
├── logs/
└── outputs/
    └── benchmarks/
```

## Main files to look at first

- **`src/selector.py`**: deterministic rule-based task parsing baseline
- **`src/llm_selector.py`**: natural-language to structured decision JSON
- **`src/agent_runner.py`**: end-to-end execution pipeline
- **`src/trajectory.py`**: step-level logging of tool calls
- **`src/benchmark_runner.py`**: batch evaluation entrypoint
- **`src/error_analyzer.py`**: failed-step attribution and summary
- **`src/metrics.py`**: benchmark-level metrics aggregation
- **`src/retry_manager.py`**: minimal retry / reflection handling

---

## Quick Start

### 1. Install dependencies

```bash
pip install -U pip setuptools wheel
pip install litellm python-dotenv pyyaml rich
```

### 2. Configure the LLM selector

If you want to run the LLM-based selector, create a `.env` file in the root directory:

```env
DASHSCOPE_API_KEY="your_key_here"
LLM_MODEL="openai/qwen-plus"
LLM_API_BASE="[https://dashscope.aliyuncs.com/compatible-mode/v1](https://dashscope.aliyuncs.com/compatible-mode/v1)"
```

### 3. Reset the benchmark workspace

Because `create` and `edit` tasks are stateful, reset the environment before each benchmark run:

```bash
python src/benchmark_setup.py
```

### 4. Debug a single task

```bash
python src/main.py
```

*Typical examples you can test:*
- `读取 hello.py`
- `创建 notes_llm.txt`
- `在 notes_llm.txt 里追加 hello llm`
- `把 hello.py 里的 hello error 改成 hello benchmark`

### 5. Run the batch benchmark

```bash
python src/benchmark_runner.py
```
**Configuration:**
Before running, set these variables inside `src/benchmark_runner.py`:
- `selector_mode = "rule"` or `selector_mode = "llm"`
- benchmark file: `data/benchmark/tasks.json` or `data/benchmark/tasks_harder.json`

**Recommended execution order:**
1. Reset environment
2. Run rule benchmark
3. Reset again
4. Run llm benchmark

### 6. Inspect outputs

Generated artifacts are written to:
- `logs/`
- `outputs/benchmarks/`

Common output files include summary JSON files such as `rule_v1_summary.json` and `rule_v1_harder_summary.json`.

---
## Reading Guide
- Read **this file (`README.md`)** for what the project is, how it is organized, and how to run it.
- Read **[`docs/experiments.md`](docs/experiments.md)** for benchmark setup, version-by-version results, failure patterns, retry/reflection notes, and conclusions.