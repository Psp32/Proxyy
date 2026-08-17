source_id: openagrinet_training_pipeline
source_type: project
title: OpenAgriNet — Log-to-Training Pipeline
url: https://github.com/Premx24/openagri-agent-data-pipeline

# Overview

OpenAgriNet is a trajectory-aware data pipeline that converts raw production logs from an agentic agricultural Q&A system into clean, validated, training-ready datasets for language model fine-tuning.

The project was built as an open-source prototype for C4GT DMP 2026, addressing the OpenAgriNet issue for building a logs-to-training pipeline for agentic systems.

# Problem

Agentic agricultural Q&A systems generate production logs containing multi-step tool interactions, tool calls and returns, errors, retries, multilingual conversations, and potentially sensitive personal information.

Raw logs cannot be directly used for model training because they may contain:

* Personally identifiable information (PII)
* Invalid or inconsistent tool trajectories
* Near-duplicate conversations
* Different levels of interaction complexity
* Multilingual and bilingual conversations
* Failed or incomplete tool interactions

The project addresses these problems by transforming raw logs into validated and training-ready datasets.

# Solution

The pipeline processes raw Langfuse/Pydantic JSON logs through multiple stages:

1. Parse raw logs into a canonical schema.
2. Detect and redact PII.
3. Validate agent trajectories and tool-call consistency.
4. Tag trajectory complexity and language characteristics.
5. Remove near-duplicate trajectories.
6. Export SFT training data.
7. Generate DPO preference pairs.
8. Produce pipeline statistics and residual-risk reports.

# Pipeline Architecture

```text
Raw Langfuse/Pydantic JSON logs
        ↓
PII redaction
        ↓
Trajectory validation
        ↓
Complexity tagging
        ↓
Near-duplicate removal
        ↓
SFT JSONL export
        ↓
DPO JSONL export
        ↓
Pipeline report
```

# Project Information

* Project: OpenAgriNet — Log-to-Training Pipeline
* Type: Open-source data engineering / ML data pipeline
* Organization/Program: C4GT DMP 2026
* Repository: openagri-agent-data-pipeline
* Primary language: Python

# Key Features

## PII Redaction

The pipeline uses three layers of PII protection:

1. Structured field rules
2. Regex-based detection
3. Presidio pattern-based detection

Supported sensitive information includes:

* Name
* Phone number
* Aadhaar
* PAN
* Email
* Date of birth
* Bank account information

Consistent placeholders are used, such as:

* `[PHONE_1]`
* `[NAME_1]`
* `[AADHAAR_1]`
* `[PAN_1]`

The same detected value receives the same placeholder within a trajectory.

## Trajectory Validation

The pipeline validates consistency between agent tool calls and tool returns.

Validation rules include:

* V01 — Tool-name mismatch between call and return
* V02 — Tool call without a following tool return
* V03 — Tool return without a preceding tool call
* V04 — Unknown tool name
* V05 — Empty bot response
* V06 — Trajectory without tool calls
* V07 — Consecutive tool calls without an intervening return
* V08 — Trajectory ordering violation

Rules are categorized as EXCLUDE, FLAG, or INFO depending on severity.

## Complexity Tagging

Trajectories are analyzed for characteristics including:

* Number of steps
* Recovery behavior
* Language
* Multilingual behavior
* Overall trajectory complexity

This metadata can be used for later stratified sampling and dataset analysis.

## Multilingual and Hindi Support

The pipeline is designed to handle Indian-language conversations, including Hindi and Devanagari text.

Hindi and multilingual trajectories are explicitly tagged.

The deduplication system uses word-level rather than character-level similarity to better handle Indian-language text.

## Near-Duplicate Detection

The pipeline uses word-unigram MinHash with a threshold of `0.30`.

Word-level MinHash was selected because character-level shingles can be sparse for Devanagari text.

This approach is intended to identify highly similar or rephrased queries in multilingual datasets.

## SFT Dataset Generation

The pipeline exports training examples as JSONL compatible with TRL's `SFTTrainer`.

The generated format supports multi-turn conversations containing:

* System messages
* User messages
* Assistant responses
* Tool calls
* Tool responses
* Metadata

The output is intended to be compatible with chat templates used by models such as Gemma, Llama 3, and Qwen.

## DPO Dataset Generation

The pipeline can generate preference pairs containing:

* Prompt
* Chosen response/trajectory
* Rejected response/trajectory
* Rejection reason
* Metadata

One example is a tool-failure trajectory where the rejected example contains a tool-name mismatch.

## Audit Logging

PII redaction operations are recorded in an audit log.

The audit output provides visibility into:

* What type of PII was detected
* Which trajectory contained it
* Which placeholder was used
* Redaction activity across the dataset

## Pipeline Reporting

The pipeline generates a report containing statistics and residual-risk information.

The report can include:

* Number of processed trajectories
* Included trajectories
* Excluded trajectories
* Flagged trajectories
* PII redaction statistics
* Complexity breakdown
* Language breakdown
* Deduplication statistics
* Residual risks

# Architecture

```text
run_pipeline.py
        ↓
    ingest.py
        ↓
    redact.py
        ↓
   validate.py
        ↓
      tag.py
        ↓
    export.py
        ↓
    report.py
```

## Ingest

`pipeline/ingest.py`

Parses raw Langfuse/Pydantic JSON logs and converts them into the project's canonical event and trajectory schemas.

## Redaction

`pipeline/redact.py`

Performs multi-layer PII detection and replacement while maintaining consistent placeholders within each trajectory.

## Validation

`pipeline/validate.py`

Checks tool-call and tool-return consistency using validation rules V01–V08.

## Tagging

`pipeline/tag.py`

Calculates trajectory complexity, detects language characteristics, identifies recovery behavior, and performs near-duplicate detection.

## Export

`pipeline/export.py`

Generates SFT and DPO JSONL datasets.

## Reporting

`pipeline/report.py`

Generates pipeline statistics and residual-risk information.

# Project Structure

```text
openagri-pipeline/
│
├── run_pipeline.py
│
├── sample_logs/
│   ├── generate_logs.py
│   ├── log_01.json
│   ├── log_02.json
│   ├── log_03.json
│   ├── log_04.json
│   └── log_05.json
│
├── schemas/
│   └── models.py
│
├── pipeline/
│   ├── ingest.py
│   ├── redact.py
│   ├── validate.py
│   ├── tag.py
│   ├── export.py
│   └── report.py
│
├── tests/
│   └── test_pipeline.py
│
├── docs/
│   ├── schema_definitions.md
│   └── pipeline_architecture.md
│
├── exports/
└── requirements.txt
```

# Demo Scenarios

The project includes five synthetic logs demonstrating different pipeline behaviors.

## log_01

Clean Hindi agricultural query with two tool calls.

Demonstrates:

* Normal trajectory processing
* Hindi/Devanagari handling
* Multiple tool calls

## log_02

Contains a tool-name mismatch.

Demonstrates:

* V01 validation
* Automatic trajectory exclusion

## log_03

Contains multiple types of PII including Aadhaar, phone number, name, and email.

Demonstrates:

* Structured field detection
* Regex detection
* Presidio detection
* Placeholder consistency

## log_04

Near-duplicate of log_01.

Demonstrates:

* MinHash deduplication

## log_05

Contains an error, retry, and bilingual response.

Demonstrates:

* Recovery detection
* Multilingual tagging
* More complex trajectory behavior

# Test Coverage

The project contains 33 tests covering:

* Ingest parsing
* Error-turn detection
* Empty-turn handling
* PII detection
* Aadhaar Verhoeff validation
* Phone detection
* Email detection
* PAN detection
* Name detection
* Placeholder consistency
* Trajectory-level redaction
* Tool-call validation
* Tool-name mismatch
* Unknown tools
* Orphan tool calls
* Recovery detection
* Pure Q&A trajectories
* Complexity tagging
* Hindi detection
* Multilingual detection
* SFT export
* DPO export
* Duplicate exclusion
* JSONL roundtrip
* Schema integrity

# Outputs

The pipeline produces:

* `sft_train.jsonl` — Training-ready supervised fine-tuning examples
* `dpo_pairs.jsonl` — Preference pairs for DPO
* `audit_log.jsonl` — PII redaction audit information
* `pipeline_report.txt` — Pipeline statistics and residual-risk information
* `excluded_trajectories.jsonl` — Trajectories excluded by validation
* `flagged_trajectories.jsonl` — Trajectories requiring attention

# Demo Results

When run against the included synthetic logs, the pipeline produces:

* 3 SFT training rows
* 1 DPO preference pair
* 15 PII redaction audit entries
* 1 excluded trajectory due to tool-name mismatch

The demo dataset is synthetic and is intended to demonstrate pipeline behavior rather than represent production data.

# Technical Decisions

## Three-Layer PII Detection

Multiple detection layers are used because no single mechanism reliably covers all structured and free-text PII patterns.

Structured rules provide deterministic handling for known fields.

Regex provides pattern-based detection for formats such as Aadhaar, PAN, phone numbers, and email.

Presidio provides an additional pattern-based detection layer for remaining variants.

## Word-Level MinHash

Word-unigram MinHash was selected instead of character shingles because the project targets multilingual Indian-language data, including Hindi.

Word-level overlap provides a more useful similarity signal for rephrased Hindi queries.

## Trajectory-Level Validation

Validation operates on the complete interaction trajectory rather than treating each event independently.

This allows the pipeline to detect problems such as:

* Missing tool returns
* Tool-call mismatches
* Invalid event ordering
* Recovery sequences

# Residual Risks

The current prototype has known limitations.

* Hindi and regional-language PII in unstructured free text may not be completely detected.
* AI provider names and models are not part of this pipeline's scope.
* The prototype does not perform production-scale model training.
* DPO pairs currently depend on identifiable failure trajectories.
* Synthetic demo logs do not represent the full diversity of production traffic.

A manual audit of approximately 5% of Hindi sessions is recommended for additional PII verification.

# Future Work

Planned or possible extensions include:

* Synthetic data expansion using a mock tool executor
* LLM-as-judge persona scoring
* IndicNER integration for unstructured Hindi PII
* LoRA dry-run validation
* DPO dry-run validation
* Student-model filtering
* Evaluation harness
* Multi-node TRL training configuration

# Resume Facts

* Built an open-source trajectory-aware data pipeline for converting agentic agricultural Q&A logs into training-ready datasets.
* Implemented multi-layer PII redaction for Indian identifiers including Aadhaar, PAN, phone numbers, names, and email addresses.
* Designed trajectory validation rules for tool-call and tool-return consistency.
* Implemented multilingual-aware near-duplicate detection using word-unigram MinHash.
* Built SFT and DPO JSONL exporters compatible with TRL/HuggingFace training workflows.
* Added complexity tagging, audit logging, dataset statistics, and residual-risk reporting.
* Created 33 automated tests covering ingestion, redaction, validation, tagging, deduplication, and export.
* Built synthetic test scenarios covering Hindi, multilingual interactions, PII, tool failures, recovery, and duplicates.

# Grounding Rules

* Do not claim that the pipeline performs model fine-tuning itself. It produces training-ready datasets for fine-tuning.
* Do not claim that the pipeline guarantees complete PII removal.
* Do not claim production-scale performance unless supported by benchmark data.
* Do not claim that Presidio provides complete NLP-based entity recognition; the current configuration uses it as a pattern-based detection layer without requiring a spaCy model download.
* Do not claim that all Indian regional languages are fully supported.
* Do not claim that the pipeline has been deployed to production unless another source confirms it.
* Distinguish clearly between the synthetic demo results and real production data.
* Do not invent additional validation rules beyond V01–V08.
* If a requested implementation detail is not documented, state that the available OpenAgriNet project documentation does not provide that information.
