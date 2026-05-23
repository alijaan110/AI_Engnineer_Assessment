# AI Engineer Assessment — Local Intelligent Document Processing System

A fully **offline**, open-source AI system that ingests PDF/TXT documents, classifies them, extracts structured fields, and enables semantic search — all without any paid or hosted AI APIs.

---

## Features

| Feature | Implementation |
|---|---|
| Document Ingestion | `pdfminer.six` + `PyPDF2` fallback |
| Classification | Keyword-rule engine + optional zero-shot HuggingFace model |
| Structured Extraction | Regex + NLP heuristics per document type |
| Semantic Search | `SentenceTransformers` (all-MiniLM-L6-v2) + `FAISS` |
| Bonus QA | Local `flan-t5-small` LLM over retrieved context |

**No OpenAI. No Claude. No Gemini. 100% local.**

---

## Project Structure

```
AI Assessment/
├── main.py                      # CLI entrypoint — orchestrates the full pipeline
├── generate_samples.py          # Generate 8 basic test documents
├── generate_20_samples.py       # Generate 20 realistic test documents (diverse formats)
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── src/
│   ├── processor.py             # Document ingestion & text extraction (PDF/TXT)
│   ├── classifier.py            # Document classification (keyword rules + optional ML)
│   ├── extractor.py             # Structured field extraction (regex + NLP heuristics)
│   └── retrieval.py             # FAISS semantic search + local LLM-based QA
├── sample_docs/                 # Input folder — place your PDF/TXT files here
│   ├── invoice_001.txt ... invoice_006.txt
│   ├── resume_001.txt  ... resume_005.txt
│   ├── utility_bill_001.txt ... utility_bill_005.txt
│   ├── other_001.txt, other_002.txt
│   └── unclassifiable_001.txt, unclassifiable_002.txt
└── output/
    ├── output.json              # Classification + extraction results
    ├── faiss_index.pkl           # Serialised FAISS index + document data
    └── hf_cache/                # Cached HuggingFace models (auto-downloaded)
```

---

## Installation

### 1. Clone / extract the project

```bash
cd AI Assessment
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv

# Activate:
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (CMD):
.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** On first run, `SentenceTransformers` downloads the `all-MiniLM-L6-v2` model (~90MB) and `flan-t5-small` (~300MB for QA). After that, everything runs fully offline.

---

## Quick Start (Full Pipeline)

Run the entire pipeline in three commands:

```bash
# 1. Process documents (classify + extract + build search index)
python main.py process --folder ./sample_docs

# 2. Semantic search
python main.py search --query "Find all documents mentioning payments due in January"

# 3. Ask a question (bonus QA)
python main.py ask --question "What is the total amount on invoice INV-1234?"
```

---

## Detailed Usage

### Step 1 — Add Your Documents

Place your PDF or TXT files into the `sample_docs/` folder.

Or generate sample test documents:

```bash
# Generate 8 basic sample documents
python generate_samples.py

# Generate 20 realistic documents (6 invoices, 5 resumes, 5 utility bills, 2 other, 2 unclassifiable)
python generate_20_samples.py
```

### Step 2 — Process Documents

```bash
python main.py process --folder ./sample_docs
```

**What this does (in order):**

1. **Ingest** — Reads all `.pdf` and `.txt` files from the specified folder
2. **Classify** — Classifies each document into one of: `Invoice`, `Resume`, `Utility Bill`, `Other`, `Unclassifiable`
3. **Extract** — Extracts structured fields based on the document class (see table below)
4. **Save** — Writes all results to `output/output.json`
5. **Index** — Builds a FAISS semantic search index and saves it to `output/faiss_index.pkl`

**Optional flag — ML-based zero-shot classification:**

```bash
python main.py process --folder ./sample_docs --use-ml
```

When `--use-ml` is enabled, documents with low keyword-confidence are also evaluated by a HuggingFace zero-shot model (`typeform/distilbart-mnli-12-3`) as a second opinion. This is useful for ambiguous documents but slower on first run due to model download.

### Step 3 — Semantic Search

```bash
python main.py search --query "Find all documents mentioning payments due in January"
```

**Options:**

| Flag | Default | Description |
|---|---|---|
| `--query` | *(required)* | Natural language search query |
| `--top-k` | `5` | Number of top results to return |

**More examples:**

```bash
python main.py search --query "invoices from ACME" --top-k 3
python main.py search --query "resumes with Python experience"
python main.py search --query "electricity bills in Karachi"
python main.py search --query "meeting minutes"
```

**Output format:**

```
[1] invoice_001.txt  (score=0.4523)
    NEXUS DIGITAL SOLUTIONS LTD 22 Innovation Park, ...

[2] utility_bill_001.txt  (score=0.3891)
    KARACHI ELECTRIC SUPPLY COMPANY (KESC) ...
```

### Step 4 — Bonus: Local QA (Question Answering)

Ask natural language questions about your documents:

```bash
python main.py ask --question "What is the total amount on invoice INV-1234?"
```

**How it works:**

1. **Structured lookup** — First checks `output.json` for exact matches (fast, precise)
2. **LLM fallback** — If no structured match, retrieves top-3 relevant docs via FAISS and generates an answer using `google/flan-t5-small` (instruction-tuned seq2seq model)

**Example queries:**

```bash
# Invoice queries (structured lookup)
python main.py ask --question "What is the total amount on invoice INV-1234?"
python main.py ask --question "What is the date on invoice INV-5678?"

# Resume queries (structured lookup)
python main.py ask --question "How many years of experience does John Doe have?"
python main.py ask --question "What is Sara Ahmed's email?"
python main.py ask --question "What is James Peterson's phone number?"

# General queries (LLM fallback — uses flan-t5-small)
python main.py ask --question "Which companies are based in Dubai?"
python main.py ask --question "What certifications does Michael Okonkwo have?"
```

**Output format:**

```
💡 Answer: The total amount on INV-1234 is 350.5
📄 Sources: invoice_1.txt
```

---

## Output Format

`output/output.json` — Contains classification and extracted fields for every document:

```json
{
  "invoice_1.txt": {
    "class": "Invoice",
    "invoice_number": "INV-1234",
    "date": "2025-01-15",
    "company": "Beta Technologies LLC",
    "total_amount": 350.5
  },
  "resume_1.txt": {
    "class": "Resume",
    "name": "John Doe",
    "email": "john.doe@email.com",
    "phone": "(123)456-7890",
    "experience_years": 5
  },
  "utility_bill_1.txt": {
    "class": "Utility Bill",
    "account_number": "CE-8876543",
    "date": "February 20, 2025",
    "usage_kwh": 387.0,
    "amount_due": 58.0
  },
  "other_1.txt": {
    "class": "Other"
  },
  "unclassifiable_001.txt": {
    "class": "Unclassifiable"
  }
}
```

### Extracted Fields by Document Type

| Document Type | Fields Extracted |
|---|---|
| **Invoice** | `invoice_number`, `date`, `company`, `total_amount` |
| **Resume** | `name`, `email`, `phone`, `experience_years` |
| **Utility Bill** | `account_number`, `date`, `usage_kwh`, `amount_due` |
| **Other** | No extraction (classified only) |
| **Unclassifiable** | No extraction (classified only) |

---

## File-by-File Documentation

### `main.py` — CLI Entrypoint

The main entry point that orchestrates the entire pipeline. Provides three CLI subcommands:

| Subcommand | Function Called | Description |
|---|---|---|
| `process` | `run_pipeline()` | Full ingestion → classification → extraction → indexing pipeline |
| `search` | `run_search()` | Semantic search over previously indexed documents |
| `ask` | `run_qa()` | Question answering over documents (bonus feature) |

**Key functions:**
- `run_pipeline(folder, use_ml)` — Runs steps 1–4: ingest → classify → extract → save JSON → build FAISS index
- `run_search(query, top_k)` — Loads saved FAISS index and runs semantic similarity search
- `run_qa(question)` — Loads FAISS index, creates `LocalQA` instance, returns answer + sources

---

### `src/processor.py` — Document Ingestion & Text Extraction

Handles reading and cleaning raw text from PDF and TXT files.

| Function | Description |
|---|---|
| `extract_text_from_pdf(filepath)` | Extracts text from PDF using `pdfminer.six` (primary) with `PyPDF2` fallback |
| `extract_text_from_txt(filepath)` | Reads plain text files with UTF-8 encoding |
| `clean_text(text)` | Normalises whitespace, removes non-printable characters, collapses blank lines |
| `ingest_documents(folder)` | Scans folder for `.pdf`/`.txt` files, returns `{filename → cleaned_text}` dict |

**Design decisions:**
- **Dual PDF backend** — `pdfminer.six` handles most PDFs well; `PyPDF2` is the fallback for edge cases
- **Text cleaning** — Strips non-ASCII noise (common in PDF extraction) while preserving structure
- **Sorted iteration** — Documents are processed in alphabetical order for deterministic output

---

### `src/classifier.py` — Document Classification

Classifies documents into 5 categories using keyword pattern matching with an optional ML fallback.

| Function | Description |
|---|---|
| `classify_by_keywords(text)` | Counts regex pattern matches per category, returns `(label, confidence)` |
| `classify_document(text, use_ml)` | Main entry point — runs keyword rules, optionally boosts with zero-shot ML |
| `classify_with_zero_shot(text)` | Uses `typeform/distilbart-mnli-12-3` for zero-shot classification (optional) |
| `_count_matches(text, patterns)` | Helper — counts how many patterns match in text |

**Classification categories:** `Invoice`, `Resume`, `Utility Bill`, `Other`, `Unclassifiable`

**How keyword classification works:**
1. Each category has 12–17 regex patterns (e.g., Invoice: `\binvoice\b`, `\btotal amount\b`, `\bdue date\b`)
2. Text is matched against all patterns for all categories
3. Category with the most matches wins (minimum 2 matches required to avoid false positives)
4. Confidence = matched patterns / total patterns for that category
5. Documents with < 30 characters or > 65% non-alpha characters → `Unclassifiable`

**When `--use-ml` is enabled:**
- Documents with keyword confidence < 0.6 are also evaluated by the zero-shot model
- The higher-confidence result (keyword vs ML) is used
- Model: `typeform/distilbart-mnli-12-3` (~250MB, downloaded on first run)

---

### `src/extractor.py` — Structured Field Extraction

Extracts specific fields from classified documents using regex patterns and NLP heuristics.

| Function | Description |
|---|---|
| `extract_fields(doc_class, text)` | Dispatcher — routes to the correct extractor based on class |
| `extract_invoice_fields(text)` | Extracts `invoice_number`, `date`, `company`, `total_amount` |
| `extract_resume_fields(text)` | Extracts `name`, `email`, `phone`, `experience_years` |
| `extract_utility_bill_fields(text)` | Extracts `account_number`, `date`, `usage_kwh`, `amount_due` |
| `_search(pattern, text, group, flags)` | Safe regex wrapper — returns first match group or `None` |
| `_clean_amount(raw)` | Converts currency strings like `$1,234.56` or `Rs.12,176.10` to float |

**Extraction strategies:**

| Field | Strategy |
|---|---|
| Invoice number | Multiple patterns: `INV-XXXX`, `Invoice No: XXX`, `Inv No.: XXX` |
| Dates | Handles: `2025-01-15`, `15/01/2025`, `03-Feb-2025`, `20 January 2025`, `February 3, 2025` |
| Company name | Looks for `Bill To:`, `From:`, `Vendor:`, or company suffixes (Ltd, LLC, Inc, Corp, Co) |
| Amounts | Multi-currency: `$`, `£`, `€`, `Rs.`, `AED` — strips to float |
| Resume name | Handles ALL CAPS (`SARA AHMED` → `Sara Ahmed`) and Title Case names |
| Phone | Handles `(123) 456-7890`, `+971-50-987-6543`, `0300-1234567`, `+44 7911 234567` |
| Experience years | Explicit mentions (`5 years of experience`) + fallback: sums year spans from work history |
| kWh usage | Labeled usage lines; avoids raw meter readings; skips `kWh equivalent` |

---

### `src/retrieval.py` — Semantic Search & QA

Provides two classes for document retrieval and question answering.

#### Class: `DocumentRetriever`

Manages the FAISS vector index for semantic search.

| Method | Description |
|---|---|
| `build_index(documents)` | Encodes all documents with `all-MiniLM-L6-v2`, builds FAISS index, saves to disk |
| `load_index()` | Loads previously saved index from `output/faiss_index.pkl` |
| `search(query, top_k)` | Encodes query, performs L2 nearest-neighbour search, returns ranked results |

**Index details:**
- Embedding model: `all-MiniLM-L6-v2` (384-dimensional vectors, ~90MB)
- Index type: `IndexFlatL2` (exact search — fast enough for < 10,000 documents)
- Score: Normalised similarity = `1 / (1 + L2_distance)` (higher = more similar)
- Documents are truncated to 2,000 characters before embedding

#### Class: `LocalQA`

Question answering with a two-tier strategy:

| Method | Description |
|---|---|
| `answer(question, top_k)` | Main entry — tries structured lookup first, then LLM fallback |
| `_answer_from_structured_data(question)` | Pattern-matches question against `output.json` for instant answers |
| `_load_model()` | Lazy-loads `google/flan-t5-small` tokenizer + model |
| `_generate(prompt)` | Runs seq2seq generation with beam search |

**Tier 1 — Structured Data Lookup (instant, precise):**
- Detects invoice numbers (`INV-1234`, `BSE-0099`, `AC-INV-8821`) in the question
- Matches person names from resumes (`John Doe`, `Sara Ahmed`)
- Returns exact values from `output.json` without loading the LLM

**Tier 2 — LLM Fallback (slower, generative):**
- Retrieves top-k relevant documents via FAISS
- Builds a context prompt with document snippets
- Generates answer using `google/flan-t5-small` (instruction-tuned T5, ~300MB)
- Uses beam search (num_beams=2) for better quality

---

### `generate_samples.py` — Basic Sample Generator

Generates 8 simple test documents:
- 2 invoices, 2 resumes, 2 utility bills, 2 other

```bash
python generate_samples.py
```

### `generate_20_samples.py` — Extended Sample Generator

Generates 20 realistic documents with diverse formats, currencies, and languages:
- 6 invoices (USD, CAD, PKR, AED formats)
- 5 resumes (international names, varying layouts)
- 5 utility bills (electric, gas, water — US, UK, Pakistan)
- 2 other documents (memo, meeting minutes)
- 2 unclassifiable (binary data, single character)

```bash
python generate_20_samples.py
```

---

## Libraries Used

| Library | Version | Purpose | License |
|---|---|---|---|
| `pdfminer.six` | ≥ 20221105 | PDF text extraction (primary) | MIT |
| `PyPDF2` | ≥ 3.0.0 | PDF extraction fallback | BSD |
| `sentence-transformers` | ≥ 2.2.2 | Local text embeddings (`all-MiniLM-L6-v2`) | Apache 2.0 |
| `faiss-cpu` | ≥ 1.7.4 | Vector similarity search (FAISS) | MIT |
| `transformers` | ≥ 4.35.0 | Zero-shot classification + local QA models | Apache 2.0 |
| `torch` | ≥ 2.0.0 | ML backend for transformers | BSD |
| `numpy` | ≥ 1.24.0 | Numerical operations | BSD |

All libraries are open-source. No paid APIs are used anywhere.

---

## Classification Logic

### Primary: Keyword Rules

Fast pattern matching using Python's `re` module:
- Checks 12–17 domain-specific regex patterns per class
- Requires **2+ pattern matches** to classify (reduces false positives)
- Short documents (< 500 chars) with 1 match are classified at low confidence (0.4)

**Classes:** `Invoice`, `Resume`, `Utility Bill`, `Other`, `Unclassifiable`

**Example patterns:**

| Class | Sample Patterns |
|---|---|
| Invoice | `\binvoice\b`, `\btotal amount\b`, `\bpayment due\b`, `\bsubtotal\b` |
| Resume | `\bresume\b`, `\bwork experience\b`, `\beducation\b`, `\byears? of experience\b` |
| Utility Bill | `\bkwh\b`, `\bbilling period\b`, `\bmeter reading\b`, `\bservice address\b` |

### Optional: Zero-Shot ML

When enabled via `--use-ml`:
- Uses `typeform/distilbart-mnli-12-3` (a small MNLI model) as a second opinion
- Only activates for low-confidence keyword results (< 0.6)
- The higher-confidence result wins

---

## Retrieval Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  User Query  │────▶│  Embed with  │────▶│  FAISS L2    │
│              │     │  MiniLM-L6   │     │  Search      │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                 │
                                                 ▼
                                          ┌──────────────┐
                                          │  Top-K Docs  │
                                          │  + Scores    │
                                          └──────┬───────┘
                                                 │
                              ┌──────────────────┼──────────────────┐
                              ▼                                     ▼
                    ┌──────────────────┐                  ┌──────────────────┐
                    │  search command  │                  │   ask command    │
                    │  Return results  │                  │  Build context   │
                    └──────────────────┘                  │  → flan-t5-small │
                                                         │  → Generate ans  │
                                                         └──────────────────┘
```

1. **Embedding:** Each document is embedded using `all-MiniLM-L6-v2` (384-dim vectors)
2. **Indexing:** Vectors stored in a FAISS `IndexFlatL2` index (exact nearest-neighbour)
3. **Search:** Query embedded → L2 distance → top-k documents returned with similarity score
4. **QA (bonus):** Top-k retrieved docs used as context → `flan-t5-small` generates answer

---

## Running Offline

After the first run (which downloads models):

1. Models are cached in `output/hf_cache/` and `~/.cache/huggingface/`
2. Delete internet access entirely
3. The system will run fully offline using cached models

**Model sizes (one-time download):**

| Model | Size | Used For |
|---|---|---|
| `all-MiniLM-L6-v2` | ~90 MB | Semantic search embeddings |
| `google/flan-t5-small` | ~300 MB | QA answer generation (bonus) |
| `typeform/distilbart-mnli-12-3` | ~250 MB | Zero-shot classification (optional, only with `--use-ml`) |

---

## Testing & Verification

### Test 1 — Full Pipeline

```bash
python main.py process --folder ./sample_docs
```

**Expected:** All 28 documents classified and extracted. Check `output/output.json` for results.

### Test 2 — Verify Classification Accuracy

```bash
python -c "import json; d=json.load(open('output/output.json')); [print(f'{k}: {v[\"class\"]}') for k,v in d.items()]"
```

**Expected:** All `invoice_*.txt` → Invoice, `resume_*.txt` → Resume, `utility_bill_*.txt` → Utility Bill, `other_*.txt` → Other, `unclassifiable_*.txt` → Unclassifiable.

### Test 3 — Verify Extraction Completeness

```bash
python -c "
import json
d = json.load(open('output/output.json'))
total, filled = 0, 0
for rec in d.values():
    for k, v in rec.items():
        if k != 'class':
            total += 1
            filled += v is not None
print(f'Extraction rate: {filled}/{total} ({filled/total*100:.1f}%)')
"
```

**Expected:** ~97% extraction rate (86/88 fields). The 2 nulls are `usage_kwh` for water utility bills (they use gallons, not kWh).

### Test 4 — Semantic Search

```bash
python main.py search --query "Find all documents mentioning payments due in January"
python main.py search --query "invoices from ACME" --top-k 3
python main.py search --query "resumes with data science experience"
python main.py search --query "electricity bills in Pakistan"
```

**Expected:** Relevant documents ranked by similarity score.

### Test 5 — QA: Structured Data Lookup

```bash
python main.py ask --question "What is the total amount on invoice INV-1234?"
python main.py ask --question "How many years of experience does John Doe have?"
python main.py ask --question "What is Sara Ahmed's email?"
python main.py ask --question "How many years of experience does James Peterson have?"
```

**Expected:** Instant, precise answers sourced from `output.json`.

### Test 6 — QA: LLM Fallback

```bash
python main.py ask --question "Which companies are based in Dubai?"
python main.py ask --question "What certifications does Michael Okonkwo have?"
```

**Expected:** Answers generated by `flan-t5-small` using retrieved document context. (First run slower due to model loading.)

### Test 7 — ML Classification (Optional)

```bash
python main.py process --folder ./sample_docs --use-ml
```

**Expected:** Same classifications, but ambiguous documents may be reclassified using the zero-shot model.

---

## Technical Decisions

- **Why keyword rules first?** Structured documents (invoices, bills, resumes) follow very predictable patterns. Regex is fast, interpretable, and doesn't require GPU/internet.
- **Why `all-MiniLM-L6-v2`?** Best balance of speed (CPU-friendly) and quality for semantic search. Only 90MB.
- **Why FAISS over other vector DBs?** Zero dependencies, pure C++, fast even on CPU, no server needed.
- **Why `flan-t5-small` for QA?** Lightweight enough to run on CPU without issues, instruction-tuned, handles Q&A prompts well. For better quality, swap to `flan-t5-base` if your system has enough RAM (~1GB).
- **Why two-tier QA?** Structured lookup is instant and 100% accurate for known entities. LLM fallback handles open-ended questions that don't map to extracted fields.
- **Why multi-currency regex?** The sample dataset includes documents in USD, CAD, PKR, AED, and GBP. The extractors handle `$`, `£`, `€`, `Rs.`, and `AED` prefixes.
