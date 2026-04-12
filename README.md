# Global Transportability Atlas

An interactive HTML dashboard and research pipeline for assessing the transportability of clinical prognostic models across 204 countries using GBD 2023 data.

## Features
- **TruthCert V4 Pipeline:** Proof-carrying research artifact with end-to-end cryptographic signing.
- **Methodological Hardening:** 
  - **DML Cross-Fitting:** Orthogonalized nuisance estimation on split-sample folds.
  - **Conformal Validity:** Exchangeable calibration set ($n=1000$) for finite-sample coverage.
  - **Stochastic Sensitivity:** Monte Carlo uncertainty propagation (N=100) reflecting GBD uncertainty.
  - **Spatial Manifold:** Spatially-weighted Wasserstein-2 (Haversine) for regional spillover.
- **GBD 2023 Integration:** Uses the latest IHME covariates (1980-2023).

## Verification (TruthCert V4)
The current research package is verified by the following signatures:
- **Input Hash:** `SHA256:f21c868682abeb775237aab33ccf0496d5d029a23b17a03a1fedea79fe5aa882`
- **Output Hash:** `SHA256:801bef7987881e902e09fbd8ec0ce3a49c46df413e69e83b53c0d88be32e9ad4`
- **Composition Hash:** `SHA256:f7c09271faf5113a7aab3ef54000e8cfdb9b488ace6a479365b746df8c7ec3dc`

## Project Structure
- `core/`: Python pipeline (DML, Conformal, Spatial Math).
- `data/`: `atlas_results.json` containing signed transportability metrics.
- `index.html`: Interactive dashboard (servable via GitHub Pages).
- `app.js`: Frontend logic for map and charts.
- `E156.md`: Submission-ready micro-paper protocol.

## Target Journals
- *The Lancet Global Health*
- *Statistics in Medicine*
- *Journal of Clinical Epidemiology*
