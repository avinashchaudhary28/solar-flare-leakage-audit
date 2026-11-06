# Leakage-Audited Solar Flare Forecasting Across Solar Cycles 24 and 25

Code, workflows and result tables for a study of M-class-or-above flare forecasting
(24-hour horizon) from SDO/HMI SHARP parameters. It compares random-row, HARP-grouped
and forward-in-time evaluation, tests transfer between Solar Cycle 24 and Cycle 25
(to December 2025), and audits the flare labels.

Preprint: Kumar, A. (2026), ESS Open Archive, doi:[10.22541/essoar.15010619](https://doi.org/10.22541/essoar.15010619).
Version 2 of the preprint uses the version 2 code and results in this repository.

## Main results (version 2)

- The SWAN-SF integrated flare list carries the operational 0.7 scaling of GOES XRS-B
  (median flux ratio 1.445 against the NOAA GOES Flare Report over 1,663 Cycle 24 flares).
  Both cycles are therefore labelled from the GOES Flare Report in true flux.
- Random-row splits inflate TSS by 0.20 (default gradient boosting) and 0.30 (default
  perceptron) and reverse the model ranking; tuned models inflate by at most 0.05.
- Models trained only on Cycle 24 score at least as well on Cycle 25 (2023–2025) as
  models trained on early Cycle 25.
- Logistic-regression probabilities calibrated on Cycle 24 are close to the Cycle 25
  flare rate; most of the base-rate shift reported in version 1 came from the label scaling.

## Repository layout

| Path | What it is |
| --- | --- |
| `audit/solar_flare_audit_v2.ipynb` | Downloads all inputs, audits the labels (GOES scaling, HEK region matching, HARP/NOAA overlap, recurrent regions, split dates) and builds the window tables with every label variant |
| `phase3/solar_flare_phase3.ipynb` | Reruns every experiment for one label set: leakage audit, tuning, cross-cycle transfer, size-matched training, per-year skill, calibration, figures |
| `.github/workflows/phase3.yml` | Runs both notebooks on GitHub Actions (labels `v1`, `v2c`, and `v2c` with Cycle 25 to 2025) and commits the results |
| `results/phase3/v2c_2025/` | **Results used in the version 2 paper** (corrected labels, Cycle 25 to 2025) |
| `results/phase3/v2c/` | Corrected labels, Cycle 25 to 2024 (comparison with version 1) |
| `results/phase3/v1/` | Version 1 labels rerun with the version 2 code, and `reproduction_check.csv` |
| `results/phase3/audit_tables/` | Label and split audit tables |
| `results/phase3_repeat_run/` | A second run of the same code, showing run-to-run variation between runner machines |
| `solar_flare_leakage_audit.ipynb`, root `*.csv`, `fig*.png` | Version 1 (release v1.0.0), kept unchanged |

## Run

GitHub Actions: any change to one of the two notebooks on the branch triggers
`phase3.yml`, which downloads the inputs (cached between runs), runs everything and
commits the tables and figures. Google Colab: open the audit notebook, then the
Phase 3 notebook, and run all cells (set `LABEL` and `C25_TABLE` as described in the
first cell).

## Data sources

JSOC `hmi.sharp_cea_720s` (drms); SWAN-SF integrated flare list (Angryk et al. 2020,
Harvard Dataverse, CC0); NOAA NCEI GOES-16 XRS science flare summary and GOES Flare
Report; Heliophysics Event Knowledgebase (HEK).

## Licence

Code: MIT.

## Author

Avinash Kumar, independent researcher (ORCID 0009-0008-7613-1185)
