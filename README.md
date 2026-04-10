# Global Transportability Atlas

An interactive HTML dashboard and research pipeline for assessing the transportability of clinical prognostic models across 204 countries using GBD 2023 data.

## Features
- **TruthCert Pipeline:** Proof-carrying numbers for transportability metrics.
- **GBD 2023 Integration:** Uses the latest IHME covariates (1980-2023).
- **Interactive Map:** Visualizes calibration drift and recalibration needs in the Global South.

## Project Structure
- `data/`: GBD covariates and model coefficients.
- `core/`: Python pipeline for transportability math (SMD, HR recalibration).
- `site/`: HTML/JS dashboard for visualization.
- `E156.md`: Micro-paper protocol.

## Target Journals
- *The Lancet Global Health*
- *Statistics in Medicine*
- *Journal of Clinical Epidemiology*
