# Tool-Use Coding Agent Benchmark

A lightweight tool-use coding agent for file operation tasks, with rule-based vs LLM-based selector benchmarking.

## What this project does

This project focuses on a narrow but practical agent setting:

- read a file
- create a file
- append to a file
- edit a file

The goal is not to build a full autonomous software engineer.  
The goal is to compare how different decision layers behave under the same executable tool pipeline.

## Pipeline

```text
task -> selector -> repo search / file selection -> tool execution -> optional verification -> metrics
```

## Why this project is useful

This repository is designed to be:

- executable
- benchmarkable
- comparable
- easy to explain in an internship interview

Instead of only showing a demo, it includes:

- structured execution flow
- benchmark runner
- metrics summary
- error summary
- saved outputs

## Repository layout

```text
tooluse-coding-agent/
├─ data/
│  └─ benchmark/
│     ├─ tasks.json
│     ├─ tasks_harder.json
│     └─ tasks_holdout.json
├─ docs/
│  └─ experiments.md
├─ logs/
├─ outputs/
│  └─ benchmarks/
├─ src/
│  ├─ agent_runner.py
│  ├─ benchmark_runner.py
│  ├─ config.py
│  ├─ error_analyzer.py
│  ├─ llm_selector.py
│  ├─ logger_utils.py
│  ├─ metrics.py
│  ├─ retry_manager.py
│  ├─ selector.py
│  ├─ task_parser.py
│  ├─ trajectory.py
│  └─ tools/
│     ├─ file_editor.py
│     ├─ file_reader.py
│     ├─ path_utils.py
│     ├─ repo_search.py
│     └─ test_runner.py
├─ tests/
│  ├─ test_task_parser.py
│  └─ test_path_utils.py
├─ requirements.txt
└─ README.md
```

## Quick start

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

**2. Configure environment**

If you want to run the LLM selector, create a `.env` file under the project root.
Example:

```env
LLM_MODEL=openai/qwen-plus
LLM_API_BASE=[https://dashscope.aliyuncs.com/compatible-mode/v1](https://dashscope.aliyuncs.com/compatible-mode/v1)
DASHSCOPE_API_KEY=your_api_key_here
```

*If you only want to run the rule-based selector, this is not required.*

**3. Run benchmark**

Run the default benchmark:

```bash
python src/benchmark_runner.py
```

Run LLM selector on holdout:

```bash
python src/benchmark_runner.py \
  --selector-mode llm \
  --task-file data/benchmark/tasks_holdout.json \
  --run-name llm_holdout
```

Run rule selector on holdout:

```bash
python src/benchmark_runner.py \
  --selector-mode rule \
  --task-file data/benchmark/tasks_holdout.json \
  --run-name rule_holdout
```

**4. Run tests**

```bash
pytest -q
```

## Benchmark sets

- **`tasks.json`**: Template-style benchmark used to verify basic pipeline stability.
- **`tasks_harder.json`**: More natural-language-like benchmark used to measure selector robustness.
- **`tasks_holdout.json`**: Holdout benchmark used as the most important summary result.

## Results

Use holdout as the main result for reporting.

**Current snapshot**

- Holdout benchmark (rule): `TODO`
- Holdout benchmark (llm): `TODO`

You can fill the numbers after running:

```bash
python src/benchmark_runner.py --selector-mode rule --task-file data/benchmark/tasks_holdout.json --run-name rule_holdout
python src/benchmark_runner.py --selector-mode llm --task-file data/benchmark/tasks_holdout.json --run-name llm_holdout
```

## Notes on interpretation

This project is still a prototype. That means:

- the task space is intentionally narrow
- benchmark scale is small
- retry / reflection is lightweight
- verification is minimal compared with full software engineering workflows
- repo search is designed for small repositories, not production-scale systems

So this repository should be interpreted as:

- a compact tool-use agent prototype
- a selector comparison benchmark
- a portfolio project for applied AI / agent internships

*not as:*
- a production-ready autonomous engineer
- a full-scale code agent platform

## Next improvements

High-value next steps:

- strengthen verifier abstraction
- improve parser coverage
- improve repo search ranking
- add CI
- report holdout results more prominently