"""Paper 2 figures, drawn only from the committed CSV tables.
Usage: python paper2/figures/make_figures.py <repo root>   -> results/paper2/figures/fig1_skill.png, fig2_gains.png
"""
import os, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
D = os.path.join(REPO, "results", "paper2", "pilot_a2"); OUT = os.path.join(REPO, "results", "paper2", "figures"); os.makedirs(OUT, exist_ok=True)
BLUE, ORANGE, INK, INK2, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e6e5e1"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 300, "savefig.bbox": "tight"})
def lohi(s): a, b = s.strip("[]").split(","); return float(a), float(b)
SPLIT = {"G": "Grouped CV, Cycle 24", "B": "Cycle 24 to Cycle 25 (2023-2025)"}
COL = {"LR": BLUE, "HGB": ORANGE}; NAME = {"LR": "Logistic regression", "HGB": "Gradient boosting"}

# Figure 1: tuned TSS by feature set
s = pd.read_csv(os.path.join(D, "p2t_skill.csv")); s = s[s.windows == "all"]
FS = ["B0", "B1", "SH", "EH"]; LAB = ["B0\nsize", "B1\n+ flare\nhistory", "SH\n+ magnetic\nstate", "EH\n+ evolution"]
fig, axs = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
for ax, sp in zip(axs, ["G", "B"]):
    for k, m in enumerate(["LR", "HGB"]):
        r = s[(s.split == sp) & (s.model == m)].set_index("features").loc[FS]
        lo = np.array([lohi(c)[0] for c in r.CI95]); hi = np.array([lohi(c)[1] for c in r.CI95]); x = np.arange(4) + (k - .5) * .22
        ax.errorbar(x, r.TSS, yerr=[r.TSS - lo, hi - r.TSS], fmt="o" if m == "LR" else "s", color=COL[m], ms=6, capsize=3, lw=1.4, label=NAME[m])
    ax.set_xticks(range(4)); ax.set_xticklabels(LAB); ax.set_title(SPLIT[sp], fontsize=10.5, color=INK, loc="left")
    ax.grid(axis="y", color=GRID, lw=.8); ax.set_axisbelow(True); ax.set_ylim(.5, .78)
axs[0].set_ylabel("TSS (tuned models)"); axs[0].legend(frameon=False, loc="lower right")
fig.savefig(os.path.join(OUT, "fig1_skill.png")); plt.close(fig)

# Figure 2: paired gains, tuned (filled) and default (open)
pt = pd.read_csv(os.path.join(D, "p2t_paired.csv")); pd_ = pd.read_csv(os.path.join(D, "p2_paired.csv"))
CMP = [("B1 - B0", "Flare history\nbeyond size"), ("SH - B1", "Magnetic state\nbeyond size + history"),
       ("EH - SH", "12-hour evolution\nbeyond state + history"), ("E24H - EH", "24-hour change\nbeyond 12-hour evolution")]
fig, axs = plt.subplots(1, 2, figsize=(10, 4.4), sharey=True)
for ax, sp in zip(axs, ["G", "B"]):
    for i, (c, _) in enumerate(CMP):
        for k, m in enumerate(["LR", "HGB"]):
            for tab, off, filled in [(pt, .09, True), (pd_, -.09, False)]:
                r = tab[(tab.comparison == c) & (tab.split == sp) & (tab.model == m)].iloc[0]; lo, hi = lohi(r.CI95)
                y = len(CMP) - 1 - i + (.5 - k) * .36 + off
                ax.errorbar(r.dTSS, y, xerr=[[r.dTSS - lo], [hi - r.dTSS]], fmt="o" if m == "LR" else "s", color=COL[m], ms=5.5, capsize=2.5, lw=1.3,
                            mfc=COL[m] if filled else "white")
    ax.axvline(0, color=INK2, lw=1); ax.grid(axis="x", color=GRID, lw=.8); ax.set_axisbelow(True)
    ax.set_title(SPLIT[sp], fontsize=10.5, color=INK, loc="left"); ax.set_xlabel("Paired TSS difference (95% interval)"); ax.set_xlim(-.07, .12); ax.set_xticks([-.05, 0, .05, .1])
axs[0].set_yticks(range(len(CMP))); axs[0].set_yticklabels([l for _, l in CMP][::-1])
from matplotlib.lines import Line2D
h = [Line2D([], [], marker="o", color=BLUE, lw=0, label="Logistic regression"), Line2D([], [], marker="s", color=ORANGE, lw=0, label="Gradient boosting"),
     Line2D([], [], marker="o", color=INK2, lw=0, label="tuned"), Line2D([], [], marker="o", color=INK2, mfc="white", lw=0, label="default")]
fig.legend(handles=h, frameon=False, loc="lower center", ncol=4, fontsize=9, bbox_to_anchor=(.55, -.07))
fig.savefig(os.path.join(OUT, "fig2_gains.png")); plt.close(fig)
print("figures written to", OUT)
