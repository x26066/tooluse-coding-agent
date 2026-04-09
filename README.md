# Tool-Use File Agent: Rule vs LLM Selector Benchmark

A lightweight tool-use agent prototype for file-operation tasks, supporting `read / create / append / edit / run`, with structured trajectory logging, batch benchmark evaluation, and error analysis.

This project focuses on building an **executable, measurable, and comparable** agent system, and compares:

- a **rule-based selector**
- an **LLM-based selector**

## Core Result

### Template Benchmark
- `rule_v1`: **100%**

### Harder Benchmark
- `rule_v1_harder`: **15%**
- `llm_v2_prompt_tuned_harder`: **80%**
- `llm_v3_create_fixed_harder`: **100%**

## Key Takeaway

- Rule-based parsing is stable on fixed templates.
- Rule-based parsing collapses on natural-language variants.
- LLM-based selection generalizes much better on harder tasks.
- Prompt constraints, few-shot examples, argument cleaning, and create-task fallback improved the harder benchmark from **80%** to **100%**.

## What This Repo Includes

- Tool execution layer:
  - `repo_search`
  - `file_reader`
  - `create_file`
  - `append_to_file`
  - `replace_in_file`
  - `run_python_file`
- Decision layer:
  - rule-based selector
  - llm-based selector
- Structured trajectory logging
- Benchmark runner and error analysis

## Project Structure

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
│   └── tools/
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

## How to Run

### 1. Install dependencies

```bash
pip install -U pip setuptools wheel
pip install litellm python-dotenv pyyaml rich
```

If you want to use the LLM-based selector, configure `.env` like this:

```env
DASHSCOPE_API_KEY="your_key_here"
LLM_MODEL="openai/qwen-plus"
LLM_API_BASE="https://dashscope.aliyuncs.com/compatible-mode/v1"
```

### 2. Reset benchmark environment

```bash
python src/benchmark_setup.py
```

### 3. Run single-task debugging

```bash
python src/main.py
```

Typical tasks include:
- 读取 `hello.py`
- 创建 `notes_llm.txt`
- 在 `notes_llm.txt` 里追加 `hello llm`
- 把 `hello.py` 里的 `hello error` 改成 `hello benchmark`

### 4. Run benchmark evaluation

```bash
python src/benchmark_runner.py
```

Before running, set in `benchmark_runner.py`:
- `selector_mode = "rule"` or `selector_mode = "llm"`
- benchmark file: `data/benchmark/tasks.json` or `data/benchmark/tasks_harder.json`

**Recommended order:**
1. Reset environment
2. Run rule
3. Reset environment again
4. Run llm

### 5. Check outputs

Results are saved to:
- `logs/`
- `outputs/benchmarks/`

---

## Benchmark Summary

**Template Benchmark**
- `rule_v1`: 100%

**Harder Benchmark**
- `rule_v1_harder`: 15%
- `llm_v2_prompt_tuned_harder`: 80%
- `llm_v3_create_fixed_harder`: 100%

---

## Current Limitations

- Benchmark size is still small.
- Tasks are still relatively shallow.
- Workflows are mostly short and lightly chained.
- Selector SFT has not been tested yet.
- This project is still a lightweight prototype, not a production agent framework.

---

## Next Steps

- [ ] Expand the harder benchmark with more natural-language diversity.
- [ ] Introduce longer multi-step tasks.
- [ ] Collect selector trajectories for SFT dataset construction.
- [ ] Compare rule-based, prompt-tuned, and SFT-based selectors.

---

## More Details

For full experiment details, see [`docs/experiments.md`](docs/experiments.md).
