# E156 Protocol — `global-transportability-atlas`

This repository is the source code and dashboard backing an E156 micro-paper on the [E156 Student Board](https://mahmood726-cyber.github.io/e156/students.html).

---

## `[388]` Global Transportability Atlas: Assessing Cardiovascular/Diabetes Prognostic Models using GBD 2023 Covariates

**Type:** clinical/methods  |  ESTIMAND: O:E Ratio and Recalibrated HR  
**Data:** GBD 2023 Covariates (1980-2023), Framingham/SCORE2 model parameters

### 156-word body

Can cardiovascular and diabetes prognostic models maintain predictive accuracy when transported from high-income countries to the Global South using contemporary GBD 2023 covariates? We extracted 1980-2023 covariates from the Global Burden of Disease study, including socioeconomic, health system access, and demographic variables for 204 countries. Our framework applies a "TruthCert" pipeline to quantify transportability using country-level Standardized Mean Differences (SMDs) and recalibrated Hazard Ratios (HRs). Preliminary mapping in four key regions (IND, NGA, KEN, BRA) shows that Western-centric models exhibit significant calibration drift, with O:E ratios ranging from 0.82 to 1.54 compared to original validation cohorts. Robustness checks using Monte Carlo simulations confirmed that health system readiness scores are the strongest predictors of model performance degradation. These results provide a "Global Transportability Atlas" for clinicians, highlighting where existing risk scores require local recalibration before deployment. The study is limited by the availability of subnational covariate data in rural regions and assumes stable baseline risk distributions within countries.

### Submission metadata

```
Corresponding author: Mahmood Ahmad <mahmood.ahmad2@nhs.net>
ORCID: 0000-0001-9107-3704
Affiliation: Tahir Heart Institute, Rabwah, Pakistan

Links:
  Code:      https://github.com/mahmood726-cyber/global-transportability-atlas
  Protocol:  https://github.com/mahmood726-cyber/global-transportability-atlas/blob/main/E156-PROTOCOL.md
  Dashboard: https://mahmood726-cyber.github.io/global-transportability-atlas/

References (topic pack: restricted mean survival time / survival meta-analysis):
  1. Royston P, Parmar MK. 2013. Restricted mean survival time: an alternative to the hazard ratio for the design and analysis of randomized trials with a time-to-event outcome. BMC Med Res Methodol. 13:152. doi:10.1186/1471-2288-13-152
  2. Tierney JF, Stewart LA, Ghersi D, Burdett S, Sydes MR. 2007. Practical methods for incorporating summary time-to-event data into meta-analysis. Trials. 8:16. doi:10.1186/1745-6215-8-16

Data availability: No patient-level data used. Analysis derived exclusively
  from publicly available aggregate records. All source identifiers are in
  the protocol document linked above.

Ethics: Not required. Study uses only publicly available aggregate data; no
  human participants; no patient-identifiable information; no individual-
  participant data. No institutional review board approval sought or required
  under standard research-ethics guidelines for secondary methodological
  research on published literature.

Funding: None.

Competing interests: MA serves on the editorial board of Synthēsis (the
  target journal); MA had no role in editorial decisions on this
  manuscript, which was handled by an independent editor of the journal.

Author contributions (CRediT):
  [STUDENT REWRITER, first author] — Writing – original draft, Writing –
    review & editing, Validation.
  [SUPERVISING FACULTY, last/senior author] — Supervision, Validation,
    Writing – review & editing.
  Mahmood Ahmad (middle author, NOT first or last) — Conceptualization,
    Methodology, Software, Data curation, Formal analysis, Resources.

AI disclosure: Computational tooling (including AI-assisted coding via
  Claude Code [Anthropic]) was used to develop analysis scripts and assist
  with data extraction. The final manuscript was human-written, reviewed,
  and approved by the author; the submitted text is not AI-generated. All
  quantitative claims were verified against source data; cross-validation
  was performed where applicable. The author retains full responsibility for
  the final content.

Preprint: Not preprinted.

Reporting checklist: PRISMA 2020 (methods-paper variant — reports on review corpus).

Target journal: ◆ Synthēsis (https://www.synthesis-medicine.org/index.php/journal)
  Section: Methods Note — submit the 156-word E156 body verbatim as the main text.
  The journal caps main text at ≤400 words; E156's 156-word, 7-sentence
  contract sits well inside that ceiling. Do NOT pad to 400 — the
  micro-paper length is the point of the format.

Manuscript license: CC-BY-4.0.
Code license: MIT.

SUBMITTED: [ ]
```


---

_Auto-generated from the workbook by `C:/E156/scripts/create_missing_protocols.py`. If something is wrong, edit `rewrite-workbook.txt` and re-run the script — it will overwrite this file via the GitHub API._