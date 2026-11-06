# Phase 3 — rerun on corrected labels

`solar_flare_phase3.ipynb` reruns every experiment of the v1 paper (leakage audit with default and tuned models, tuning, cross-cycle transfer A–D, per-year skill, calibration) for one label column at a time (`LABEL` = `v1` published labels, or `v2c` GOES Flare Report labels in true flux for both cycles).

`.github/workflows/phase3.yml` builds the window tables with `../audit/solar_flare_audit_v2.ipynb`, runs this notebook for each label in parallel, and commits the tables and figures to `../results/phase3/<label>/`. The `v1` run also writes `reproduction_check.csv`, comparing its numbers with the published CSVs in the repository root.
