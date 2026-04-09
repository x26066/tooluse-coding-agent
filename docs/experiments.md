# Experiments

For project overview, repository structure, and usage instructions, see [README.md](../README.md).

## Project Goal

The goal of this project is to build a lightweight tool-use file agent with:

- a decision layer
- a tool execution layer
- structured trajectory logging
- benchmark evaluation
- error analysis

The project compares two decision strategies:

1. **rule-based selector**
2. **llm-based selector**

The execution layer is kept unchanged across experiments so that performance differences mainly reflect the quality of the decision layer.

---

## System Overview

### Tool Layer

The current agent supports the following tools:

- `repo_search`
- `file_reader`
- `create_file`
- `append_to_file`
- `replace_in_file`
- `run_python_file`

### Decision Layer

Two decision modes are implemented:

- `rule_v1`: parse tasks using rule-based logic
- `llm_v*`: parse tasks using an LLM and output structured JSON decisions

### Trajectory Logging

Each run is recorded as a structured trajectory containing:

- `tool`
- `input`
- `output`

This makes it possible to inspect decision quality, execution behavior, and failure locations.

---

## Benchmark Design

Two benchmark sets are used.

### 1. Template Benchmark

This benchmark contains highly regular task templates such as:

- `读取 hello.py`
- `创建 notes_a.txt`
- `在 notes_a.txt 里追加 alpha`
- `把 hello.py 里的 hello benchmark 改成 hello agent`

This benchmark mainly measures correctness on structured and predictable commands.

### 2. Harder Benchmark

This benchmark contains more natural-language task formulations such as:

- `帮我看看 hello.py 现在写了什么`
- `请新建一个 notes_d.txt`
- `把 gamma 追加到 notes_e.txt`
- `请把 hello.py 中的 hello harder 替换成 hello benchmark`

This benchmark is designed to measure generalization beyond hand-written rule patterns.

---

## Metrics

The following metrics are used:

- overall success rate
- category success rate
- failed action distribution
- failed step distribution

Task categories:

- `read`
- `create`
- `append`
- `edit`

---

## Baseline: `rule_v1`

### Version

- name: `rule_v1`
- selector: rule-based
- execution layer: unchanged

### Template Benchmark Result

- total tasks: 20
- overall success rate: **100.00%**

### Category Success

- create: 3 / 3 = **100.00%**
- append: 6 / 6 = **100.00%**
- read: 7 / 7 = **100.00%**
- edit: 4 / 4 = **100.00%**

### Error Summary

- failed_count: 0
- failed_action_distribution: {}
- failed_step_distribution: {}

### Interpretation

The rule-based selector is fully stable on templated tasks where task patterns are fixed and explicitly covered by the parser.

---

## Harder Benchmark: `rule_v1_harder`

### Version

- name: `rule_v1_harder`
- selector: rule-based
- execution layer: unchanged

### Harder Benchmark Result

- total tasks: 20
- overall success rate: **15.00%**

### Category Success

- read: 2 / 7 = **28.57%**
- create: 0 / 3 = **0.00%**
- append: 0 / 6 = **0.00%**
- edit: 1 / 4 = **25.00%**

### Error Summary

- failed_count: 17
- failed_action_distribution:
  - unknown: 17
- failed_step_distribution:
  - `tool_selector`: 17

### Interpretation

The rule-based selector collapses on natural-language task variants.

The main bottleneck is not tool execution, but task parsing itself: the selector fails before tool usage begins.

This result shows that hand-written rules are highly sensitive to expression style.

---

## LLM Selector: `llm_v1`

### Version

- name: `llm_v1`
- selector: llm-based
- execution layer: unchanged

### Notes

The first LLM version demonstrated that structured decision extraction was feasible, but stability on argument extraction was not yet sufficient.

This version was mainly used as a functional prototype before prompt refinement.

---

## LLM Selector: `llm_v2_prompt_tuned_harder`

### Version

- name: `llm_v2_prompt_tuned_harder`
- selector: llm-based
- improvements:
  - stricter system prompt
  - few-shot examples
  - argument cleaning and validation

### Harder Benchmark Result

- total tasks: 20
- overall success rate: **80.00%**

### Category Success

- read: 7 / 7 = **100.00%**
- create: 0 / 3 = **0.00%**
- append: 5 / 6 = **83.33%**
- edit: 4 / 4 = **100.00%**

### Error Summary

- failed_count: 4
- failed_action_distribution:
  - create: 3
  - unknown: 1
- failed_step_distribution:
  - `create_file`: 3
  - `tool_selector`: 1

### Interpretation

Compared with `rule_v1_harder`, the LLM selector shows significantly stronger generalization on natural-language task formulations.

The remaining bottleneck is concentrated in `create` tasks, indicating that the main issue is structured argument extraction and file-name normalization rather than overall task understanding.

---

## LLM Selector: `llm_v3_create_fixed_harder`

### Version

- name: `llm_v3_create_fixed_harder`
- selector: llm-based
- improvements:
  - more create-task few-shot examples
  - stronger target-file cleaning
  - create-task fallback parsing
  - benchmark environment reset for fair evaluation

### Harder Benchmark Result

- total tasks: 20
- overall success rate: **100.00%**

### Category Success

- read: 7 / 7 = **100.00%**
- create: 3 / 3 = **100.00%**
- append: 6 / 6 = **100.00%**
- edit: 4 / 4 = **100.00%**

### Error Summary

- failed_count: 0
- failed_action_distribution: {}
- failed_step_distribution: {}

### Interpretation

After prompt refinement, few-shot strengthening, argument cleaning, create-specific fallback handling, and proper benchmark reset, the LLM selector reaches full success on the harder benchmark.

This suggests that the harder benchmark failures were not due to a fundamental inability of the LLM to understand the tasks, but rather due to insufficiently constrained structured extraction.

---

## Comparison Summary

### Template Benchmark

- `rule_v1`: **100.00%**
- `llm-based selector`: can also achieve stable performance on templated tasks

### Harder Benchmark

- `rule_v1_harder`: **15.00%**
- `llm_v2_prompt_tuned_harder`: **80.00%**
- `llm_v3_create_fixed_harder`: **100.00%**

### Key Observation

On templated tasks, rule-based and LLM-based selectors can both perform well.

On natural-language task variants, the rule-based selector fails at the parsing stage, while the LLM-based selector preserves strong generalization.

### Main Conclusion

The core value of the LLM selector is not improving tool execution, but improving robustness and generalization of the decision layer under natural-language task formulations.

---

## Error Analysis Summary

The main failure modes observed during development were:

### Rule-Based Selector

- unsupported task phrasing
- parser mismatch under natural-language variation
- failure before tool execution

### LLM-Based Selector

- unstable `target_file` extraction in create tasks
- unstable `old_text / new_text` extraction in some edit cases
- formatting and argument normalization issues

These failures were progressively reduced through:

- stricter prompts
- few-shot examples
- post-processing and validation
- create-specific fallback logic
- benchmark environment reset

---

## Why SFT Was Not Applied Yet

SFT was not prioritized at the current stage for the following reasons:

1. the benchmark scale is still relatively small
2. prompt tuning and output validation already resolved the main bottlenecks
3. on the current benchmark, `llm_v3_create_fixed_harder` already achieves 100%

Given the current results, further work would benefit more from:

- expanding benchmark diversity
- increasing task complexity
- collecting more trajectory data

before introducing selector SFT.

---

## Current Limitations

- benchmark size is still small
- current tasks are file-operation oriented and relatively shallow
- execution workflows are short and mostly single-step or lightly chained
- selector SFT has not yet been tested
- current project is still a lightweight prototype, not a production agent framework

---

## Next Steps

Possible next steps include:

1. expand the harder benchmark with more natural-language diversity
2. introduce longer multi-step tasks
3. collect selector trajectories for SFT dataset construction
4. compare:
   - rule-based selector
   - prompt-tuned LLM selector
   - SFT-based selector
5. add richer benchmarking dimensions such as:
   - trajectory length
   - argument extraction accuracy
   - robustness to paraphrasing

---

## Final Takeaway

This project demonstrates a full experimental loop for a lightweight tool-use agent:

- baseline construction
- structured trajectory logging
- batch benchmark evaluation
- error attribution
- rule vs LLM comparison
- iterative selector optimization

The final result shows that:

- rule-based parsing is strong on fixed templates but brittle under natural-language variation
- LLM-based decision layers provide much better generalization
- careful prompt design, few-shot examples, validation, and post-processing can substantially improve selector reliability without immediately requiring SFT
