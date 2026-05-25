# Global Transportability Atlas

[![ci](https://github.com/mahmood726-cyber/global-transportability-atlas/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/mahmood726-cyber/global-transportability-atlas/actions/workflows/ci.yml) [![codeql](https://github.com/mahmood726-cyber/global-transportability-atlas/actions/workflows/codeql.yml/badge.svg?branch=master)](https://github.com/mahmood726-cyber/global-transportability-atlas/actions/workflows/codeql.yml) [![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![python: 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

An interactive HTML dashboard and rebuildable research artifact for country-level transportability scoring based on local F-drive transportability outputs and World Bank country metadata.

## Features
- **Source-backed rebuild:** `core/pipeline.py` rebuilds `data/atlas_results.json` from `transportability_ma/output/global_transportability_matrix.csv` plus World Bank country metadata when those local sources are available.
- **Fail-closed input discovery:** the pipeline searches candidate local roots and raises a clear error if the matrix or country metadata are missing instead of silently falling back to placeholder data.
- **Geographic dashboard shell:** the frontend renders source-backed country markers, effect ratios, transportability scores, and priority scores using coordinates resolved from local World Bank metadata.

## Verification
- `python -m pytest -q`
- `python core/pipeline.py`

## Local Inputs
- `GLOBAL_TRANSPORTABILITY_MATRIX`
- `WORLD_BANK_COUNTRIES_CSV`
- `WORLD_BANK_WDI_COUNTRY_CSV`

If these environment variables are unset, the pipeline searches common local candidate roots on available drives.

## Project Structure
- `core/`: Python rebuild pipeline and unit tests.
- `data/`: generated `atlas_results.json`.
- `index.html`: dashboard shell.
- `app.js`: frontend logic for map and charts.
- `E156.md`: submission-oriented project note.
