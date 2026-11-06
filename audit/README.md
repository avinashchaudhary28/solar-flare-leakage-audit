# Audit v2 (Phase 2)

Data and label audit for *Leakage-Audited Solar Flare Forecasting Across Solar Cycles 24 and 25*.
The published version is the `v1.0.0` release on `main`; nothing here changes it.

- `solar_flare_audit_v2.ipynb` — the audit (GOES scaling, label variants, HEK matching, HARP/NOAA overlap, recurrent regions, split dates). Runs in Google Colab or on GitHub Actions.
- `../.github/workflows/audit-v2.yml` — runs the notebook on GitHub's servers on every push to this branch and commits the tables to `../results/audit_v2/`.
