# Experiments

This document covers only the experimental side of the project. For repository layout, setup steps, and run commands, see [README.md](../README.md).

## Evaluation questions

The experiments are organized around three questions:

1. How far can a rule-based selector go when task phrasing is templated?
2. What happens when the same task types are expressed in more natural language?
3. How much engineering value comes from prompt constraints, output cleaning, fallback handling, and minimal retry / reflection support?

## Protocol

### Controlled comparison

All selector variants are evaluated under the same execution pipeline. The experiments are intended to isolate the **decision layer**, so differences in outcome are interpreted primarily as differences in task understanding and structured argument extraction.

### Benchmark sets

Two benchmark sets are used.

#### Template benchmark

This set contains highly regular instructions such as:

- `读取 hello.py`
- `创建 notes_a.txt`
- `在 notes_a.txt 里追加 alpha`
- `把 hello.py 里的 hello benchmark 改成 hello agent`

It measures correctness on explicit and predictable task phrasing.

#### Harder benchmark

This set contains more natural-language formulations such as:

- `帮我看看 hello.py 现在写了什么`
- `请新建一个 notes_d.txt`
- `把 gamma 追加到 notes_e.txt`
- `请把 hello.py 中的 hello harder 替换成 hello benchmark`

It is meant to test generalization beyond hand-written rule patterns.

### Metrics tracked

Each benchmark reports:

- overall success rate
- category success rate
- failed action distribution
- failed step distribution
- average step count
- average LLM call count
- average retry count
- average latency

Task categories are:

- `read`
- `create`
- `append`
- `edit`

### Execution notes

Benchmark runs should be performed on a reset workspace. This matters because create and edit tasks modify local state and can otherwise contaminate later runs.

## Results by selector version

### `rule_v1`

**Role in the study:** deterministic baseline on templated instructions.

**Benchmark:** template benchmark  
**Total tasks:** 20  
**Overall success rate:** **100.00%**

**Category breakdown**

- create: 3 / 3 = **100.00%**
- append: 6 / 6 = **100.00%**
- read: 7 / 7 = **100.00%**
- edit: 4 / 4 = **100.00%**

**Failure summary**

- failed_count: 0
- failed_action_distribution: {}
- failed_step_distribution: {}

**Interpretation**

When task phrasing is fixed and explicitly covered by parsing rules, a rule-based selector is fully reliable and provides a strong deterministic baseline.

---

### `rule_v1_harder`

**Role in the study:** stress test of the same rule logic under natural-language variation.

**Benchmark:** harder benchmark  
**Total tasks:** 20  
**Overall success rate:** **15.00%**

**Category breakdown**

- read: 2 / 7 = **28.57%**
- create: 0 / 3 = **0.00%**
- append: 0 / 6 = **0.00%**
- edit: 1 / 4 = **25.00%**

**Failure summary**

- failed_count: 17
- failed_action_distribution:
  - unknown: 17
- failed_step_distribution:
  - `tool_selector`: 17

**Interpretation**

The failure is concentrated before tool execution even begins. The bottleneck is task parsing, not file manipulation. This makes the harder benchmark a useful probe for selector robustness rather than tool quality.

---

### `llm_v1`

**Role in the study:** first functional proof that structured decision extraction with an LLM is workable.

**Observation**

This version showed that converting natural-language requests into structured JSON decisions was feasible, but argument extraction was not yet stable enough for a strong benchmark result.

Its main value was to establish the direction for later prompt refinement rather than to serve as the final comparison point.

---

### `llm_v2_prompt_tuned_harder`

**Role in the study:** prompt-tuned LLM selector with stricter output expectations.

**Key changes**

- stricter system prompt
- few-shot examples
- argument cleaning and validation

**Benchmark:** harder benchmark  
**Total tasks:** 20  
**Overall success rate:** **80.00%**

**Category breakdown**

- read: 7 / 7 = **100.00%**
- create: 0 / 3 = **0.00%**
- append: 5 / 6 = **83.33%**
- edit: 4 / 4 = **100.00%**

**Failure summary**

- failed_count: 4
- failed_action_distribution:
  - create: 3
  - unknown: 1
- failed_step_distribution:
  - `create_file`: 3
  - `tool_selector`: 1

**Interpretation**

This version already generalizes much better than the rule-based baseline on harder phrasing. The remaining weakness is concentrated in create tasks, which points to filename extraction and normalization issues rather than a broad failure of semantic understanding.

---

### `llm_v3_create_fixed_harder`

**Role in the study:** tightened LLM selector after targeting the create-task bottleneck.

**Key changes**

- more create-task few-shot examples
- stronger target-file cleaning
- create-task fallback parsing
- fair benchmark reset before comparison

**Benchmark:** harder benchmark  
**Total tasks:** 20  
**Overall success rate:** **100.00%**

**Category breakdown**

- read: 7 / 7 = **100.00%**
- create: 3 / 3 = **100.00%**
- append: 6 / 6 = **100.00%**
- edit: 4 / 4 = **100.00%**

**Failure summary**

- failed_count: 0
- failed_action_distribution: {}
- failed_step_distribution: {}

**Interpretation**

The harder-benchmark failures were not evidence that the LLM could not understand the tasks. They were mostly a structured extraction and normalization problem. Once those constraints were tightened, the selector reached full success on the benchmark.

## Retry / reflection mechanism

A lightweight retry-and-reflection mechanism was added to improve execution observability and make failures easier to diagnose.

### Design choices

The mechanism is intentionally minimal:

- at most one retry per task
- failed tasks remain failed unless a retry really resolves them
- failure metadata is recorded explicitly

Tracked fields include:

- `retry_count`
- `reflection`
- `failure_reason`
- `latency_ms`

### Example reflection

```json
{
  "failed_step": "replace_in_file",
  "reason": "未找到要替换的目标文本",
  "suggestion": "re-read file content before retrying edit"
}
```

### Why this matters

This is not a full Reflexion-style framework, but it is enough to support:

- failure detection
- retry triggering
- reflection logging
- retry-aware benchmark reporting

That moves the project from a simple tool demo toward a more engineering-oriented agent benchmark.

## Error patterns observed during iteration

### Rule-based selector

Primary failure modes:
- unsupported task phrasing
- parser mismatch under natural-language variation
- failure before tool execution

### LLM-based selector

Primary failure modes before stabilization:
- unstable target file extraction in create tasks
- occasional instability in old_text / new_text extraction for edit tasks
- formatting and argument normalization issues

### What reduced these failures

The largest gains came from:
- stricter prompts
- few-shot examples
- post-processing and validation
- create-specific fallback logic
- disciplined benchmark resets for fair comparison

## Why SFT was not prioritized yet

Selector SFT was not the immediate next step because:
- the benchmark is still small
- prompt tuning plus validation already addressed the main bottlenecks
- the best current variant already reaches 100% on the harder benchmark

At this stage, expanding task diversity and collecting more trajectories would likely produce more informative next experiments than fine-tuning immediately.

## Limits of the current study

- benchmark size remains small
- current tasks are file-operation oriented and relatively shallow
- workflows are short and only lightly chained
- retry / reflection is still minimal rather than a full agentic self-correction framework
- selector SFT has not been tested
- the project is still a prototype, not a production framework

## Practical takeaway

The main contribution of the LLM selector is not better file editing by itself. The core gain is a more robust decision layer under natural-language task formulations.

In this project:
- rule-based parsing is excellent on fixed templates but brittle under phrasing variation
- LLM-based selection preserves much stronger generalization on the harder set
- careful prompting, validation, fallback handling, and lightweight retry/reflection can substantially improve reliability without immediately requiring SFT

## Next directions

The most useful follow-up work is:
- expand the harder benchmark with more paraphrase diversity
- introduce longer multi-step tasks
- collect selector trajectories for future SFT data construction
- compare rule-based, prompt-tuned, and SFT-based selectors on a broader benchmark
- add richer evaluation dimensions such as argument extraction accuracy and paraphrase robustness