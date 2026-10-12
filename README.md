# Leakage-Audited Solar Flare Forecasting Across Solar Cycles 24 and 25

Code and result tables for a study of M+ flare forecasting (24 h horizon) from
SDO/HMI SHARP parameters, comparing random, AR-grouped and forward-in-time
AR-disjoint evaluation, and transfer between Solar Cycle 24 and 25.

## Run
Open `solar_flare_leakage_audit.ipynb` in Google Colab and run the cells in order.
It downloads all data (JSOC SHARP via drms, SWAN-SF addenda, NOAA NCEI GOES-R flare
summary, HEK) and rebuilds every table and figure. Free Colab may reset after idle time;
the notebook saves checkpoints to Google Drive.

## Contents
- `solar_flare_leakage_audit.ipynb` - full pipeline
- `*.csv` - result tables
- `fig1`-`fig4` PNG - figures

## Data sources
JSOC hmi.sharp_cea_720s; SWAN-SF (Angryk et al., Harvard Dataverse); NOAA NCEI GOES-R XRS
flare summary; Heliophysics Event Knowledgebase.

## Licence
Code: MIT.

## Author
Avinash Kumar (ORCID 0009-0008-7613-1185)
