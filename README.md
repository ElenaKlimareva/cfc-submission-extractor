# Insurance Submission Intake Extractor

Prototype pipeline for converting semi-structured broker emails and attachments into structured underwriting data. It includes exploratory analysis, an email-only heuristic baseline, a Mistral extractor, and a self-contained evaluation notebook.

## Extracted fields

Each prediction is one JSON object with:

- `submission_id`
- `company_name`
- `revenue`
- `countries`
- `industry`
- `requested_coverages`

Example:

```json
{
  "submission_id": "E001",
  "company_name": "Everstead Pharma Ltd",
  "revenue": 14608818,
  "countries": ["Sweden", "Canada", "Singapore"],
  "industry": "Manufacturing",
  "requested_coverages": ["Property", "Kidnap & Ransom"]
}
```

## Approach and evaluation boundary

The project compares:

1. **Email-only heuristic baseline** — deterministic regular expressions, country validation, and aliases applied only to the email. It is a transparent benchmark, not a complete submission extractor.
2. **Mistral extractor** — structured LLM extraction over the email and all associated attachments, with semantic precedence rules and Pydantic validation.

Prediction generation is separate from evaluation. Neither extraction script reads `data/ground_truth.csv`; the ground truth is loaded only by `notebooks/evaluate_models.ipynb` after prediction files already exist.

## Current benchmark results

The saved evaluation notebook was run from a fresh Python 3.13 kernel against all 50 supplied records and the checked-in prediction JSONL files.

| Field | Email-only heuristic | Mistral | Difference |
|---|---:|---:|---:|
| Company name | 90% (45/50) | 96% (48/50) | +6 pp |
| Revenue | 98% (49/50) | 92% (46/50) | -6 pp |
| Industry | 70% (35/50) | 94% (47/50) | +24 pp |
| Countries | 72% (36/50) | 90% (45/50) | +18 pp |
| Requested coverages | 80% (40/50) | 98% (49/50) | +18 pp |
| Full record | 64% (32/50) | 76% (38/50) | +12 pp |

The paired full-record outcomes are 31 both correct, 7 Mistral only, 1 rule only, and 11 both incorrect. Mistral improves the context-heavy fields but regresses on revenue, where entity and reporting-period precedence remain difficult.

These are prototype benchmark results on 50 synthetic records used during development, not an unbiased production-performance estimate. At 76% full-record accuracy, the system is suitable only for an assisted workflow with evidence and human review.

See [report.md](report.md) for the full interpretation and `notebooks/evaluate_models.ipynb` for the executable methodology, counts, charts, paired comparison, and record-level error investigation.

## Project structure

```text
.
├── data/
│   ├── ground_truth.csv
│   └── sample_emails/
├── notebooks/
│   ├── analyze_data.ipynb
│   └── evaluate_models.ipynb
├── outputs/
│   ├── rule_predictions.jsonl
│   └── mistral_predictions.jsonl
├── prompts/
│   └── extraction_system_prompt.txt
├── scripts/
│   ├── run_rule_extraction.py
│   └── run_llm_extraction.py
├── src/
│   ├── load_data.py
│   ├── rules_extractor.py
│   ├── mistral_extractor.py
│   └── schemas.py
├── tests/
├── .env.example
├── AGENT.md
├── pyproject.toml
├── report.md
├── uv.lock
└── README.md
```

## Requirements and installation

- Python 3.13 or later
- [uv](https://docs.astral.sh/uv/)
- A Mistral API key only when generating new LLM predictions

From the project root:

```bash
uv sync --dev
```

Development dependencies include the Jupyter kernel and execution client needed to rerun the evaluation notebook and Jinja2 for its styled pandas tables.

## Run the workflow

All commands below assume the project root as the working directory.

### 1. Explore the inputs

Open and run `notebooks/analyze_data.ipynb`. It owns input sanity checks, attachment and word-count summaries, currency-value analysis, and the supporting exploratory figures.

### 2. Generate the deterministic baseline

```bash
uv run python scripts/run_rule_extraction.py
```

This writes `outputs/rule_predictions.jsonl` for all indexed submissions.

### 3. Generate or refresh Mistral predictions

The repository includes `outputs/mistral_predictions.jsonl`, so this step is not needed to reproduce the saved evaluation. To generate a new run, copy the environment template and add a key:

```bash
cp .env.example .env
```

```text
MISTRAL_API_KEY=your_api_key_here
```

Then run:

```bash
uv run python scripts/run_llm_extraction.py
```

Each run starts a fresh output file and saves every successful prediction immediately. A failed request stops the command, leaving predictions completed earlier in that run on disk. The Mistral retry policy handles transient failures automatically. The runner uses `ministral-8b-latest` and `prompts/extraction_system_prompt.txt`.

The `ministral-8b-latest` alias can change. A refreshed prediction file may therefore produce different metrics; treat any discrepancy as a new model run, review it, and update the notebook and documentation together. Pinning a model version would require a code change.

### 4. Evaluate both models

Open `notebooks/evaluate_models.ipynb` and restart/run all cells, or execute it non-interactively:

```bash
uv run jupyter execute notebooks/evaluate_models.ipynb --inplace --timeout=120
```

The notebook:

- locates the project root whether launched from the root or `notebooks/`;
- loads the CSV and JSONL artifacts directly with Pandas and checks required files, columns, values, and one-to-one IDs;
- relies on the extraction schema for prediction field validation rather than duplicating it during evaluation;
- reshapes both models into one tidy model/submission/field table used by every calculation;
- displays compact scorecards with raw counts, list precision/recall/F1, paired outcomes, and error drill-downs;
- renders comparison charts inline; and
- does not invoke extractors, call an API, write CSVs, or save chart files.

The executed notebook is the evaluation artifact. Its saved outputs should be refreshed whenever either prediction JSONL changes.

### 5. Run code checks

```bash
uv run pytest -q
uv run ruff check .
uv run pyright
```

## Metric semantics

- Company name and industry use exact match after case-folding and repeated-whitespace normalisation.
- Revenue uses exact whole-number equality; fractional values are rejected rather than silently truncated.
- Countries and requested coverages use order-independent exact-set match.
- List fields also report micro precision, recall, and F1 with TP/FP/FN counts.
- Coverage means a non-null scalar or non-empty list prediction.
- Full-record accuracy requires all five extracted fields to match.
- A missing prediction is never correct merely because the expected value is empty; an explicitly predicted empty list may exactly match an expected empty list while remaining uncovered.

## Output policy

The required machine-readable outputs are:

```text
outputs/rule_predictions.jsonl
outputs/mistral_predictions.jsonl
```

Each contains one JSON object per submission. Evaluation tables and charts are retained only as outputs inside `notebooks/evaluate_models.ipynb`; the notebook does not create derived CSV or image artifacts.

## Limitations and production direction

- The dataset contains only 50 synthetic submissions and was used during iteration.
- Some supplied labels may be ambiguous and require independent adjudication.
- The LLM result represents one model configuration and one run.
- Markdown input does not test OCR, PDFs, spreadsheets, images, or email-thread reconstruction.
- The current schema has no source spans, confidence, or review-routing fields.
- Latency, cost, privacy, security, availability, and drift were not evaluated.

The next sensible step is a larger held-out and adjudicated pilot with evidence spans, fixed prompt/model versions, repeated runs, canonical validation, and business-risk-based human review thresholds.

## Use of AI tools

Mistral is the extraction model evaluated in the prototype. AI-assisted development tools helped scaffold and review parts of the implementation and documentation. The methodology, results, and conclusions were checked locally. Ground-truth values were not passed to the extraction model or hard-coded into either extractor.
