# Competences Framework Experiments

This repository contains scripts and utilities to compare competency resources across three sources:

- RNCP training fiche(s)
- ROME fiche(s)
- Job offers extracted as JSON

The workflow is based on:

1. Building FAISS indexes from ROME references (problem families + resources)
2. Aligning each skills base against these indexes
3. Computing comparative indicators (Spearman-like correlation, raw deltas, coverage/entropy metrics)

## Project Structure

Main layout:

```text
.
├── README.md
├── requirements.txt
├── data/
│   ├── fiches_rncp/
│   ├── fiches_rome/
│   ├── offres_emploi_JSON/
│   └── offres_emploi_JSON_enssat/
├── RNCP38637_problems_family.idx/
├── RNCP38637_resources.idx/
└── src/
		├── createindexes.py
		├── run_experiments.py
		├── run_experiments_ENSSAT.py
		├── resultats_ENSSAT.txt
		├── skill_def/
		│   ├── skill_base.py
		│   └── rom_skill.py
		└── utils/
				├── comparators.py
				├── dataextractorllm.py
				├── indexer.py
				└── skill_loader.py
```

## Core Scripts

### `src/createindexes.py`

Builds (or reloads) the FAISS indexes used by experiments:

- `<RNCPCODE>_problems_family.idx`
- `<RNCPCODE>_resources.idx`

Current default in code:

- `RNCPCODE = RNCP38637`
- ROME files from `data/fiches_rome/`

### `src/run_experiments.py`

Default IMT Atlantique FIP experiment (`RNCP38637`):

- Loads RNCP fiche `data/fiches_rncp/RNCP38637.json`
- Loads associated ROME fiches
- Loads job offers from `data/offres_emploi_JSON/`
- Loads FAISS indexes (`RNCP38637_*`)
- Aligns each base with the ROME reference space

Important: this script currently contains `sys.exit(0)` right after alignment, so later analysis blocks in the file are not executed unless you remove/comment that line.

### `src/run_experiments_ENSSAT.py`

ENSSAT-oriented experiment variant:

- Uses `RNCPCODE = RNCP35781` for metadata context
- Loads the same ROME reference indexes from `RNCP38637_*`
- Compares ROME vs job offers split by year directories:
	- `data/offres_emploi_JSON_enssat/2022`
	- `data/offres_emploi_JSON_enssat/2023`
	- `data/offres_emploi_JSON_enssat/2024`
	- `data/offres_emploi_JSON_enssat/2025`
- Runs additional contrastive indicators (Jaccard, coverage, weighted coverage, Gini, entropy)

Note: RNCP loading is currently commented out in this script.

## Internal Code Architecture

### Domain model (`src/skill_def/skill_base.py`)

- `FamilyOfProblems`: problem-family label/description + aligned index id
- `Resource`: resource text/type/category + aligned index id + computed degree
- `Skill`: one competence item loaded from JSON
- `SkillsBase`: collection of `Skill` objects with methods to:
	- align against indexes
	- infer necessary/sufficient resources per problem family
	- assign per-resource relevance degrees

### Data loading (`src/utils/skill_loader.py`)

- `load_from_json`: load RNCP/ROME-like skill JSON
- `load_from_job_offer`: load job-offer JSON into `Skill`
- `load_base_from_directory`: bulk-load all JSON job offers in a directory

### Indexing (`src/utils/indexer.py`)

- Wrapper around `langchain_community.vectorstores.FAISS`
- Uses `OllamaEmbeddings` (`base_url=http://localhost:11434`)
- Supports index load, save, query, and document retrieval by id

### Comparators (`src/utils/comparators.py`)

- `spearman_correlation`
- `raw_differences`

## Prerequisites

## 1) Python

Use Python 3.10+ (recommended).

## 2) Dependencies

Install from `requirements.txt`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 3) Local Ollama service

The indexer uses `OllamaEmbeddings` and expects a local Ollama server at:

- `http://localhost:11434`

Start Ollama before running scripts.

## 4) Data files

Expected directories are already present under `data/`.

For `run_experiments_ENSSAT.py`, check that any files referenced in the script exist in your local dataset (for example RNCP files if you uncomment related lines).

## How To Run

All commands below are executed from the repository root.

### Step A: Build indexes (first run only, or after data/model changes)

```bash
python src/createindexes.py
```

Expected result:

- `RNCP38637_problems_family.idx/`
- `RNCP38637_resources.idx/`

### Step B1: Run standard experiment (`run_experiments.py`)

```bash
python src/run_experiments.py
```

What it currently executes:

- Loads RNCP, ROME, and job-offer bases
- Loads both indexes
- Aligns ROME and job-offer bases with indexes
- Stops at `sys.exit(0)`

If you want the full metrics section in that script, remove/comment `sys.exit(0)` and rerun.

### Step B2: Run ENSSAT experiment (`run_experiments_ENSSAT.py`)

```bash
python src/run_experiments_ENSSAT.py
```

What it executes:

- Loads ROME base and yearly ENSSAT job-offer bases
- Aligns each base
- Computes pairwise comparison outputs per year directory
- Prints additional indicators

If you want to keep a log file:

```bash
python src/run_experiments_ENSSAT.py | tee src/resultats_ENSSAT.txt
```

## Typical Workflow

1. Update or replace JSON datasets under `data/`
2. Rebuild indexes with `src/createindexes.py` if ROME reference data changed
3. Run one or both experiment scripts
4. Inspect terminal outputs (or saved log files)

## Configuration Points You May Edit

In each experiment script, you can adapt:

- `university_program`
- `RNCPCODE`
- `rncp_file`
- `rome_files`
- `job_offers_directory` or `job_offers_directories`
- index names (`pbs_indexer_name`, `resources_indexer_name`)

These are hard-coded at the top of each script for reproducible experiment settings.

## Troubleshooting

### Error: index does not exist

Message like:

```text
Index RNCP38637_problems_family.idx does not exist. Create it first using the createindexes.py script
```

Run:

```bash
python src/createindexes.py
```

### Error connecting to Ollama

If embedding calls fail, verify:

- Ollama is running locally
- Port `11434` is reachable
- The embedding/model used by `src/utils/indexer.py` is available

### Import issues

Run scripts as `python src/<script>.py` from repository root so relative imports and data paths resolve correctly.

## Reproducibility Notes

- The FAISS index contents depend on embedding model behavior.
- If you change embedding model/version in `src/utils/indexer.py`, rebuild indexes before comparing new runs to old outputs.
- Keep data snapshots fixed per experiment batch for consistent results.
