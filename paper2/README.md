# Paper 2 pilot: does magnetic-field evolution add skill?

Question, comparisons and decision rule are fixed in [`PREREGISTRATION.md`](PREREGISTRATION.md), committed before
any result.

| File | What it does |
| --- | --- |
| `p2_build.py` | Runs the paper 1 audit notebook unchanged, checks that the window and positive counts equal paper 1, and adds the flare-history (`hist_c24`, `hist_m24`) and 24-hour-change (`*_d24`, `ok24`) columns |
| `p2_pilot.py` | Runs the pre-registered comparisons (feature sets B0, B1, SH, EH, E24H; splits G, A, B; LR and HGB) with paired cluster-bootstrap intervals, and prints the verdict of the decision rule |
| `../.github/workflows/paper2.yml` | Runs both on GitHub Actions and commits the tables to `results/paper2/pilot/` |

The paper 1 code and results on `main` are not changed by anything in this folder.
