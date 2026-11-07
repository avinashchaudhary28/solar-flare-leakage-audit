"""Paper 2 pilot, step 1: build the paper 1 window tables and add the pre-registered columns.

Runs every code cell of the paper 1 audit notebook unchanged (downloads, label audit, window tables), then adds
flare-history and 24-hour-change columns (see paper2/PREREGISTRATION.md). The paper 1 columns and rows are not
changed; the script stops if the window or positive counts differ from the paper 1 audit table.

Usage: python paper2/p2_build.py <repo root>     (environment AUDIT_WORK = working folder)
Output in AUDIT_WORK: p2_c24.pkl, p2_c25ext.pkl, p2_out/build_summary.csv
"""
import json, os, re, sys, time
import numpy as np, pandas as pd

REPO = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
T0 = time.time()

# 1) paper 1 audit notebook, cell by cell, in one namespace
nb = json.load(open(os.path.join(REPO, "audit", "solar_flare_audit_v2.ipynb")))
ns = {"__name__": "__main__"}
for i, cell in enumerate(nb["cells"]):
    if cell["cell_type"] != "code": continue
    src = "".join(cell["source"])
    src = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith(("!", "%")))   # shell lines (pip) are Colab-only
    exec(compile(src, f"audit_cell_{i}", "exec"), ns)
print(f"audit notebook done in {(time.time() - T0) / 60:.1f} min", flush=True)

FL, P, SAMPLES = ns["FL"], ns["P"], ns["SAMPLES"]
to_time, nearest_pairs, hek_assign = ns["to_time"], ns["nearest_pairs"], ns["hek_assign"]
assert "flrpt" in FL, "GOES Flare Report not loaded"
os.makedirs("p2_out", exist_ok=True)

# 2) paper 1 counts must be reproduced exactly
ref = pd.read_csv(os.path.join(REPO, "results", "phase3", "audit_tables", "audit2_label_variants.csv"))
ref = ref[ref.variant == "v2c"].set_index("cycle")
for key, cyc in [(24, "24"), ("25ext", "25 (to 2025-12-30)")]:
    S = SAMPLES[key]
    got = (len(S), int(S.y_v2c.sum())); want = (int(ref.loc[cyc, "windows"]), int(ref.loc[cyc, "positive_windows"]))
    print(f"table {key}: windows, positives = {got}; paper 1 = {want}")
    assert got == want, f"table {key} differs from paper 1"

# 3) flares above a threshold with a region: report, else SWAN-SF (Cycle 24, +-5 min), else nearest HEK (+-10 min)
def flares_with_region(cycle, thr):
    t0, t1 = ("2010-05-01", "2019-01-01") if cycle == 24 else ("2019-01-01", "2026-01-02")
    f = FL["flrpt"]; f = f[(f.time >= t0) & (f.time < t1) & (f.flux >= thr)].copy().reset_index(drop=True)
    if cycle == 24:
        sw = FL["swan"][(FL["swan"].flux >= 0.5 * thr) & (FL["swan"].ar > 0)][["time", "ar"]]
        A = f[["time"]].copy(); A["i"] = A.index
        m = nearest_pairs(A, sw, 5).set_index("i_a")
        need = (f.ar == 0) & f.index.isin(m.index)
        f.loc[need, "ar"] = m.loc[f.index[need], "ar_b"].astype(int).values
    need = f.ar == 0
    if need.any(): f.loc[need, "ar"] = hek_assign(f[need], FL["hek"], 10).ar_v2nearest.values
    return f[f.ar > 0][["time", "ar"]]

def extra_columns(cycle, ext):
    """hist_c24, hist_m24, <param>_d24 and ok24 for every (harp, time) of the SHARP records of one table."""
    if cycle == 24: c = pd.read_csv("pinn_data/sharp_2010_2018_1h.csv.gz")
    elif not ext: c = pd.read_csv("pinn_data/sharp_2019_2024_1h.csv.gz")
    else: c = pd.concat([pd.read_csv("pinn_data/sharp_2019_2024_1h.csv.gz"), pd.read_csv("pinn_data/sharp_2025_1h.csv.gz")], ignore_index=True)
    c["time"] = to_time(c.T_REC)
    c = c[c.QUALITY == 0].sort_values(["HARPNUM", "time"]).reset_index(drop=True)
    c = c.drop_duplicates(["HARPNUM", "time"]).reset_index(drop=True)    # one record per HARP and hour
    c["arset"] = c.NOAA_ARS.astype(str).apply(lambda s: [int(x) for x in re.findall(r"\b\d{5}\b", s)])
    hp_ars = c.groupby("HARPNUM").arset.apply(lambda L: set(a for l in L for a in l))
    keep = hp_ars[hp_ars.apply(len) > 0].index; c = c[c.HARPNUM.isin(keep)]
    span = c.groupby("HARPNUM").time.agg(["min", "max"])
    ar2h = {}
    for h in keep:
        for a in hp_ars[h]: ar2h.setdefault(a, []).append(h)
    out = c[["HARPNUM", "time"]].rename(columns={"HARPNUM": "harp"}).copy()
    summary = {}
    for name, thr in [("hist_c24", 1e-6), ("hist_m24", 1e-5)]:
        ft = flares_with_region(cycle, thr); summary[name + "_flares_with_region"] = len(ft)
        ev = {h: [] for h in keep}
        for t, a in zip(ft.time, ft.ar):           # same flare-to-HARP rule as the paper 1 labels
            for h in ar2h.get(int(a), []):
                if span.loc[h, "min"] <= t <= span.loc[h, "max"] + pd.Timedelta("24h"): ev[h].append(np.datetime64(t, "ns"))
        col = np.zeros(len(out), dtype="int16")
        for h, idx in out.groupby("harp").indices.items():
            e = np.sort(np.array(ev[h], dtype="datetime64[ns]")); t = out.time.values[idx].astype("datetime64[ns]")
            col[idx] = np.searchsorted(e, t, side="right") - np.searchsorted(e, t - np.timedelta64(24, "h"), side="right")
        out[name] = col
    prev = c[["HARPNUM", "time"] + P].rename(columns={"HARPNUM": "harp"}).copy()
    prev["time"] = prev.time + pd.Timedelta("24h")
    cur = c[["HARPNUM", "time"] + P].rename(columns={"HARPNUM": "harp"})
    j = cur.merge(prev, on=["harp", "time"], how="left", suffixes=("", "_prev"))
    for p in P: out[p + "_d24"] = (j[p].astype("float64") - j[p + "_prev"].astype("float64")).values
    out["ok24"] = out[[p + "_d24" for p in P]].notna().all(axis=1).astype("int8")
    out[[p + "_d24" for p in P]] = out[[p + "_d24" for p in P]].replace([np.inf, -np.inf], np.nan).fillna(0).astype("float32")
    return out, summary

rows = []
for key, cycle, ext, fname in [(24, 24, False, "p2_c24.pkl"), ("25ext", 25, True, "p2_c25ext.pkl")]:
    S = SAMPLES[key].copy(); n0 = len(S)
    S["time"] = S.time.astype("datetime64[ns]")
    X, summ = extra_columns(cycle, ext); X["time"] = X.time.astype("datetime64[ns]")
    S = S.merge(X, on=["harp", "time"], how="left", validate="many_to_one")
    assert len(S) == n0 and S.hist_c24.notna().all(), f"merge lost rows for {key}"
    S.to_pickle(fname)
    rows.append(dict(table=key, windows=len(S), positives_v2c=int(S.y_v2c.sum()), ok24_windows=int(S.ok24.sum()),
                     ok24_positives=int(S.y_v2c[S.ok24 == 1].sum()), windows_with_C_in_24h=int((S.hist_c24 > 0).sum()),
                     windows_with_M_in_24h=int((S.hist_m24 > 0).sum()), **summ))
    print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv("p2_out/build_summary.csv", index=False)
print(f"done in {(time.time() - T0) / 60:.1f} min")
