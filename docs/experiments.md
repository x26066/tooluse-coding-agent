# Experiments

This document records the benchmark protocol, result snapshots, and current limitations of the tool-use coding agent.

## 1. Goal

The main goal is to compare two selector strategies under the same execution pipeline:

- rule-based selector
- LLM-based selector

The comparison asks whether the decision layer matters more when tasks move from fixed templates to more natural phrasing.

---

## 2. Benchmark protocol

### Benchmark sets

- **`tasks.json`**
  - template-style benchmark
  - used to verify pipeline stability
- **`tasks_harder.json`**
  - more varied phrasing
  - used to evaluate selector robustness
- **`tasks_holdout.json`**
  - holdout benchmark
  - should be treated as the main reporting benchmark

### Success definition

A task counts as success only if:

- final status is success
- the corresponding tool result is valid
- for `edit` tasks, verification also passes if verification is present

### Reporting order

Recommended order:

1. holdout
2. harder
3. template

---

## 3. Current results

*Replace the `TODO` values after running the latest benchmark.*

### 3.1 Holdout benchmark (`tasks_holdout.json`)

#### Rule selector
- success rate: `TODO`
- notes:
  - `TODO`

#### LLM selector
- success rate: `TODO`
- notes:
  - `TODO`

### 3.2 Harder benchmark (`tasks_harder.json`)
*(optional if you want to show iteration progress)*

#### Rule selector
- success rate: `TODO`

#### LLM selector
- success rate: `TODO`

### 3.3 Template benchmark (`tasks.json`)
*(optional baseline for basic pipeline stability)*

#### Rule selector
- success rate: `TODO`

#### LLM selector
- success rate: `TODO`

---

## 4. Example commands

### Run holdout with rule selector

```bash
python src/benchmark_runner.py \
  --selector-mode rule \
  --task-file data/benchmark/tasks_holdout.json \
  --run-name rule_holdout
```

### Run holdout with LLM selector

```bash
python src/benchmark_runner.py \
  --selector-mode llm \
  --task-file data/benchmark/tasks_holdout.json \
  --run-name llm_holdout
```

---

## 5. Error analysis

Typical failure modes in this repository include:

### 5.1 Selector failure
- wrong action type
- missing structured fields
- unsupported phrasing

### 5.2 Repo search failure
- no file found
- wrong file selected
- ambiguous target names

### 5.3 Tool execution failure
- replacement target not found
- invalid append target
- missing file

### 5.4 Verification failure
- edited Python file cannot run
- test command returns non-zero
- output is syntactically valid but behaviorally wrong

---

## 6. Current limitations

This project is still a prototype. Main limitations:

- benchmark scale is small
- task types are intentionally narrow
- retry / reflection is lightweight
- repo search is not optimized for large repositories
- verification is still minimal compared with real engineering workflows

---

## 7. Recommended next steps

High-value next improvements:

- make holdout results the main headline
- strengthen verifier abstraction
- improve rule parser coverage
- improve repo search scoring
- add CI