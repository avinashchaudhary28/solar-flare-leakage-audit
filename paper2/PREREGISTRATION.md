# Paper 2 pilot: pre-registration

Author: Avinash Kumar (ORCID 0009-0008-7613-1185), independent researcher.
Written and committed on 7 November 2026, **before** any pilot result exists. The git history of this file
is the record. The plan may be extended later, but the questions, comparisons and decision rule below will
not be changed after the first result is seen. Any later change is listed under "Amendments" with its date
and reason.

## Question

On leakage-safe splits, does the time evolution of SHARP magnetic parameters improve 24-hour M-class-or-above
flare forecasts beyond what region size and recent flare history already give?

## Data

- SDO/HMI SHARP (`hmi.sharp_cea_720s`), 1-hour cadence, `QUALITY == 0`, 17 parameters, exactly as in paper 1
  (Kumar 2026, doi:10.22541/essoar.15010619; code release v2.0.0, doi:10.5281/zenodo.23996020).
- Windows and labels: the paper 1 window tables with the corrected `v2c` labels (GOES Flare Report, true flux).
  Cycle 24: June 2010 to December 2018. Cycle 25: February 2019 to December 2025.
- The window counts and positive counts must equal those of paper 1. The build script stops if they do not.

## New columns (added to the paper 1 tables, nothing else changes)

| Column | Definition |
| --- | --- |
| `hist_c24` | Number of C1.0+ flares (GOES Flare Report, true flux) in the same HARP in the 24 hours up to and including the window end time *t*, i.e. peak time in (t - 24 h, t]. Region of each flare: report, else SWAN-SF (Cycle 24), else nearest HEK record, the same rule as the `v2c` labels. |
| `hist_m24` | Same, for M1.0+ flares. |
| `<param>_d24` | Value at *t* minus value of the same HARP at exactly *t* - 24 h (both records `QUALITY == 0`). |
| `ok24` | 1 when all 17 `_d24` values exist, else 0. |

No column uses information after *t*.

## Feature sets

| Name | Features |
| --- | --- |
| B0 | `USFLUX_last` |
| B1 | B0 + `hist_c24`, `hist_m24` |
| SH | 17 `_last` + 17 `_mean` + `hist_c24`, `hist_m24` (state + history, no evolution) |
| EH | SH + 17 `_delta` (11-hour change) + 17 `_std` (12-hour variability) |
| E24H | EH + 17 `_d24` (24-hour change); only on windows with `ok24 == 1` |

## Splits

1. **G (grouped CV):** 5-fold `GroupKFold` over HARPs on all Cycle 24 windows. In each fold, 20% of the
   training HARPs are held out to choose the decision threshold (maximum TSS). Counts are pooled over folds.
2. **A (in-cycle forward):** train Cycle 24 2010–2013, test Cycle 24 from 15 January 2014, test HARPs
   disjoint from training HARPs. Same as paper 1, setup A.
3. **B (cross-cycle):** train Cycle 24 2010–2013, test Cycle 25 from 15 January 2023 to 30 December 2025,
   HARPs not in the early Cycle 25 pool. Same as paper 1, setup B.

Thresholds are always chosen on held-out training HARPs, never on the test set.

## Models

Logistic regression (standardised features, C = 0.1, balanced class weights) and histogram gradient boosting
(150 iterations, learning rate 0.08, balanced class weights, random state 0). These are the paper 1 default
settings. No tuning in the pilot.

## Metrics and tests

- Primary metric: TSS. Secondary: ROC AUC (reported, not used for the decision).
- Each comparison is a paired difference of TSS on the same test windows, with a 95% interval from 1,000
  bootstrap resamples of test HARPs (cluster bootstrap, paper 1 code).

## Comparisons

1. **Primary: EH - SH** (does evolution add anything beyond state and history?).
2. Secondary: SH - B1 (does the full magnetic state add beyond size and history?), B1 - B0 (does flare history
   add beyond size?), and E24H - EH on the `ok24` windows (does a 24-hour change add beyond the 12-hour one?).
   For E24H - EH, both sets are trained and tested on `ok24` windows only.

## Decision rule (the gate in the paper 2 plan)

- "Evolution helps" only if the EH - SH interval lies entirely above zero for **both** models on **both**
  split G and split B.
- If the interval includes zero in any of these four cases, the pilot result is reported as "no clear gain from
  evolution", and paper 2 becomes the negative-result paper (question Q2 in the plan).
- Split A is reported but does not enter the rule.

## Amendments

None yet.
