"""Paper 2 pilot, step 2: the pre-registered comparisons (paper2/PREREGISTRATION.md).

Input in AUDIT_WORK: p2_c24.pkl, p2_c25ext.pkl from p2_build.py. Output: p2_out/*.csv and run_info.json.
Helper functions (thresholds, per-region counts, cluster bootstrap) are copied unchanged from the paper 1
Phase 3 notebook.
"""
import os, json, time, platform, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score

os.chdir(os.environ.get("AUDIT_WORK", "."))
NB = int(os.environ.get("NBOOT", "1000"))
OUT = "p2_out"; os.makedirs(OUT, exist_ok=True)
T0 = time.time()

def save(df, name):
    df.to_csv(f"{OUT}/{name}.csv", index=False)
    print(f"\n--> {OUT}/{name}.csv   [{(time.time() - T0) / 60:.1f} min]\n" + df.to_string(index=False), flush=True); return df

A = pd.read_pickle("p2_c24.pkl").reset_index(drop=True)
B = pd.read_pickle("p2_c25ext.pkl").reset_index(drop=True)
A["y"] = A.y_v2c.astype(int); B["y"] = B.y_v2c.astype(int)
P = [c[:-5] for c in A.columns if c.endswith("_last")]; assert len(P) == 17, P
HIST = ["hist_c24", "hist_m24"]
SETS = {"B0": ["USFLUX_last"],
        "B1": ["USFLUX_last"] + HIST,
        "SH": [p + "_last" for p in P] + [p + "_mean" for p in P] + HIST}
SETS["EH"] = SETS["SH"] + [p + "_delta" for p in P] + [p + "_std" for p in P]
SETS["E24H"] = SETS["EH"] + [p + "_d24" for p in P]
COMPARE = [("EH", "SH", "all", "primary: evolution beyond state and history"),
           ("SH", "B1", "all", "full magnetic state beyond size and history"),
           ("B1", "B0", "all", "flare history beyond size"),
           ("E24H", "EH", "ok24", "24-hour change beyond 12-hour evolution (ok24 windows)")]
print("C24", A.shape, "pos", round(A.y.mean(), 4), "| C25", B.shape, "pos", round(B.y.mean(), 4))

# ---- helpers copied from the paper 1 Phase 3 notebook ----
def mk(name):
    if name == "LR": return make_pipeline(StandardScaler(), LogisticRegression(C=0.1, class_weight="balanced", max_iter=300))
    return HistGradientBoostingClassifier(max_iter=150, learning_rate=0.08, class_weight="balanced", random_state=0)
def tss_pt(p, yy, t):
    pr = p >= t; tp = (pr & (yy == 1)).sum(); fn = ((~pr) & (yy == 1)).sum(); fp = (pr & (yy == 0)).sum(); tn = ((~pr) & (yy == 0)).sum()
    return tp / max(tp + fn, 1) - fp / max(fp + tn, 1)
def best_t(p, yy):
    ts = np.unique(np.quantile(p, np.linspace(.5, .999, 120))); return max(ts, key=lambda t: tss_pt(p, yy, t))
def counts(p, yy, codes, n, t):
    pr = p >= t; f = lambda w: np.bincount(codes, weights=w.astype(float), minlength=n)
    return np.c_[f(pr & (yy == 1)), f((~pr) & (yy == 1)), f(pr & (yy == 0)), f((~pr) & (yy == 0))]
def tss_c(c): s = c.sum(0); return s[0] / max(s[0] + s[1], 1) - s[2] / max(s[2] + s[3], 1)
def boot_idx(n, seed=1): return np.random.RandomState(seed).randint(0, n, (NB, n))
def ci(vals): return f"[{np.percentile(vals, 2.5):.3f}, {np.percentile(vals, 97.5):.3f}]"
def boot(c, seed=1):
    c = c[c.sum(1) > 0]; idx = boot_idx(len(c), seed); return np.array([tss_c(c[i]) for i in idx])
def boot_paired(c1, c2, seed=2):
    keep = (c1.sum(1) > 0) & (c2.sum(1) > 0); c1, c2 = c1[keep], c2[keep]; idx = boot_idx(len(c1), seed)
    return tss_c(c1) - tss_c(c2), np.array([tss_c(c1[i]) - tss_c(c2[i]) for i in idx])
def val_split(D, seed=0):
    ars = D.ar.unique(); v = set(np.random.RandomState(seed).choice(ars, int(.2 * len(ars)), replace=False))
    return D[~D.ar.isin(v)], D[D.ar.isin(v)]

# ---- splits (same rules and seeds as paper 1) ----
def split_G(D):
    """5-fold GroupKFold over HARPs; in each fold 20% of training HARPs hold out the threshold."""
    codes = pd.factorize(D.ar)[0]; rng = np.random.RandomState(0); out = []
    for a, te in GroupKFold(5).split(D, D.y, codes):
        ua = np.unique(codes[a]); vs = rng.choice(ua, int(.2 * len(ua)), replace=False)
        isv = np.isin(codes[a], vs); out.append((D.iloc[a[~isv]], D.iloc[a[isv]], D.iloc[te]))
    return out
def split_A(D):
    tr0 = D[D.time < "2014-01-01"]; te = D[(D.time >= "2014-01-15") & (~D.ar.isin(set(tr0.ar)))]
    tr, va = val_split(tr0); return [(tr, va, te)]
def split_B(DA, DB):
    tr0 = DA[DA.time < "2014-01-01"]; b0 = DB[DB.time < "2023-01-01"]
    te = DB[(DB.time >= "2023-01-15") & (~DB.ar.isin(set(b0.ar)))]
    tr, va = val_split(tr0); return [(tr, va, te)]

def evaluate(folds, feats, model):
    """Pooled per-region counts and test predictions over the folds."""
    te_all = pd.concat([f[2] for f in folds]); codes, uars = pd.factorize(te_all.ar)
    C = np.zeros((len(uars), 4)); ps, ys = [], []; pos = 0
    for tr, va, te in folds:
        m = mk(model).fit(tr[feats].values, tr.y.values)
        t = best_t(m.predict_proba(va[feats].values)[:, 1], va.y.values)
        p = m.predict_proba(te[feats].values)[:, 1]
        C += counts(p, te.y.values, codes[pos:pos + len(te)], len(uars), t); pos += len(te); ps.append(p); ys.append(te.y.values)
    return C, roc_auc_score(np.concatenate(ys), np.concatenate(ps))

res, prs, CN = [], [], {}
for subset in ["all", "ok24"]:
    DA = A if subset == "all" else A[A.ok24 == 1]; DB = B if subset == "all" else B[B.ok24 == 1]
    SPLITS = {"G": split_G(DA), "A": split_A(DA), "B": split_B(DA, DB)}
    names = ["B0", "B1", "SH", "EH"] if subset == "all" else ["EH", "E24H"]
    for sn, folds in SPLITS.items():
        te = pd.concat([f[2] for f in folds])
        for model in ["LR", "HGB"]:
            for fs in names:
                C, auc = evaluate(folds, SETS[fs], model); CN[(subset, sn, model, fs)] = C
                res.append(dict(windows=subset, split=sn, model=model, features=fs, n_features=len(SETS[fs]), n_test=len(te),
                                test_regions=te.ar.nunique(), test_pos_rate=round(te.y.mean(), 4),
                                TSS=round(tss_c(C), 3), CI95=ci(boot(C)), AUC=round(auc, 3)))
            print(subset, sn, model, "done", round((time.time() - T0) / 60, 1), "min", flush=True)
r = save(pd.DataFrame(res), "p2_skill")

for a_, b_, subset, what in COMPARE:
    for sn in ["G", "A", "B"]:
        for model in ["LR", "HGB"]:
            d, bd = boot_paired(CN[(subset, sn, model, a_)], CN[(subset, sn, model, b_)])
            lo, hi = np.percentile(bd, 2.5), np.percentile(bd, 97.5)
            prs.append(dict(comparison=f"{a_} - {b_}", meaning=what, windows=subset, split=sn, model=model,
                            dTSS=round(d, 3), CI95=ci(bd), above_zero=bool(lo > 0), below_zero=bool(hi < 0)))
pp = save(pd.DataFrame(prs), "p2_paired")

prim = pp[(pp.comparison == "EH - SH") & pp.split.isin(["G", "B"])]
verdict = "evolution helps" if bool(prim.above_zero.all()) else "no clear gain from evolution"
info = {"verdict_preregistered_rule": verdict, "rule": "EH - SH interval above zero for LR and HGB on splits G and B",
        "n_boot": NB, "python": platform.python_version(), "sklearn": sklearn.__version__, "pandas": pd.__version__,
        "numpy": np.__version__, "minutes": round((time.time() - T0) / 60, 1)}
json.dump(info, open(f"{OUT}/run_info.json", "w"), indent=1)
print("\nPRE-REGISTERED VERDICT:", verdict)
