# Associate Data Scientist (Data & AI) — Take-home Assessment (v1)

## Introduction

This assessment evaluates how you approach a realistic data science / AI problem: exploring semi-structured submission data, generating insights, building and evaluating a practical extraction prototype, and communicating your findings clearly. It is also an opportunity to demonstrate how you would collaborate with software engineers to move from a prototype towards a production-ready solution.

Building a working prototype is increasingly fast with modern tooling (including AI-assisted development). What we will focus on is the rigour behind your approach: identifying the right questions, applying sound reasoning, evaluating appropriately, and presenting evidence-based conclusions in a clear, structured way. We also value pragmatic engineering choices that would support a future production implementation.

In the next interview round, you will present your work (approximately 10 minutes), followed by Q&A.

### Time expectations
Please aim to timebox this exercise to a reasonable amount of effort (for example, a couple of hours if you are familiar with such assessments). We are not expecting a production-ready system—clarity of thinking and strong evaluation matter more than breadth of features.

### Use of AI tools
You may use AI tools (e.g., coding assistants or LLM APIs). If you do:
- Be prepared to explain your design choices and any key parts of the implementation.
- Clearly state (briefly) where AI tools were used (e.g., in the README or report).
- Do not hard-code ground-truth answers into your extractor (the ground-truth dataset should be used for evaluation only).

## Overview

In insurance, underwriters receive a high volume of emails from insurance brokers. Traditionally, underwriters read these emails and update information manually on our underwriting portal. With advances in technology, including OCR (Optical Character Recognition), programmatic data extraction, and LLMs, automatic submission intake solutions are now widely used in the industry.

Assume you are working for an insurance company as a data scientist. Your job is to analyse a volume of emails to generate insights for stakeholders, build a prototype submission-intake extraction solution, and evaluate that prototype. After evaluation and iteration, such prototypes are typically handed over to software engineers for production deployment.

This assessment comprises the following tasks:

- **Task 1:** Analyse the input email submission data to uncover patterns and generate insights.
- **Task 2:** Build a prototype of a data extraction pipeline with your selected technologies (e.g., Python).
- **Task 3:** Evaluate the prototype against the ground-truth dataset.

## Data extraction system

You are asked to build an extraction system that reads the supplied submissions and returns structured outputs such as:

| Field | Example output |
|---|---|
| `company_name` | BluePeak Manufacturing Ltd |
| `revenue` | 4800000 |
| `countries` | `["United Kingdom", "Germany"]` |
| `industry` | Manufacturing |
| `requested_coverages` | `["Cyber", "Professional Indemnity"]` |

- Consider using LLMs, prompting, rules, traditional NLP, or any combination of approaches.
- Return structured outputs for each submission (one output record per submission).
- Evaluate your results using an approach you define and justify.
- Identify failure modes and explain known limitations.
- Recommend what you would improve next if given more time.

## Data
- Input email submission data: 50 synthetic broker submission emails in the [`sample emails`](sample%20emails) folder. Files are provided in a flat, disorganised layout (emails and attachments are not grouped into per-submission folders). Some submissions include one or more attachment files in Markdown format.
- Ground-truth dataset: [`ground_truth.csv`](ground_truth.csv) — one row per submission for evaluation.

File naming convention:
- `E001_email.md` — broker email body for submission `E001`
- `E001_attachment_1.md`, `E001_attachment_2.md`, … — Markdown attachments linked to the same submission ID

### Ground-truth schema (`ground_truth.csv`)

| Column | Type | Description |
|---|---|---|
| `submission_id` | string | Submission identifier (e.g. `E001`) |
| `company_name` | string | Insured legal entity name |
| `revenue` | integer | Gross revenue in GBP (whole pounds, no currency symbol) |
| `countries` | JSON array string | Countries of operation, e.g. `["United Kingdom", "Germany"]` |
| `industry` | string | Industry / sector label |
| `requested_coverages` | JSON array string | Requested coverage lines, e.g. `["Cyber", "Professional Indemnity"]` |

Notes:
- The data is synthetic; company names, addresses, and financial figures are fabricated for assessment purposes and are not taken from live submissions.
- Focus on building a robust approach rather than memorising formats.
- Some source fields may be missing or ambiguous in the email/attachment text — your solution should handle this gracefully (e.g., nulls, “unknown”, or confidence scoring — your choice).
- Treat each email file (identified by its submission ID prefix, e.g. `E001`) as one submission record, even when related attachments are stored alongside other submissions in the same folder.
- Use `ground_truth.csv` for evaluation only. Do not hard-code these values into your extractor.


## Deliverables
- Source code (repository, notebook, or both).
- A README explaining how to run the solution end-to-end.
- A short written report covering:
  - analysis insights (Task 1)
  - solution design and key decisions (Task 2)
  - evaluation methodology and results (Task 3)
  - limitations / failure modes
  - recommended next steps
- Structured extraction outputs produced by your pipeline (in a machine-readable format such as JSON/JSONL/CSV).

## Hints

### Task 1: Analysis

- If you have 100 emails with slightly different formats, what are good ways to summarise patterns and generate insights?
- What metrics/graphs would best communicate findings to non-technical stakeholders?
- How would your approach scale to 10,000 emails rather than 100?

### Task 2: Prototype

- You can employ any techniques (packages, APIs, LLMs) to extract information effectively, but you should be able to explain and justify your implementation choices.
- You are not required to run a live demo in the next interview round, but we do expect you to walk us through your prototype as well as your analysis and evaluation work.
- How would you design the prototype to support a smooth handover to software engineers for production deployment? (It is normal for there to be a gap between a prototype and a production-ready system.)

### Task 3: Evaluation

- What would be the suitable evaluation metrics for unstructured data?
- How would you conclude that the prototype is “good” or “needs improvement”, and how would you communicate this to stakeholders?

## Assessment criteria

| Area | Criteria |
|---|---|
| **Analytical thinking** | Quality and depth of analysis, evaluation methodology, error analysis, edge-case investigation, and evidence-based conclusions presented in a structured and logical manner. |
| **Data Science / Statistical knowledge** | Depth of knowledge in exploratory analysis, statistics, and modelling; appropriate choice and application of AI/ML models; pre-processing decisions. |
| **Completion of task** | Prototype can produce structured outputs to evaluate against the ground-truth dataset. |
| **Design and engineering skills** | Python, basic software engineering practices, and how the solution could be deployed in a live environment. |
| **Working style** | Communication, pragmatism, and ability to explain trade-offs to technical and non-technical stakeholders. |
