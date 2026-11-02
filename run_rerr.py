"""Refit the real data with a different projected-separation error (sigma of Eq. 13).

usage: python run_rerr.py <f5|f1|f01> <baseline|geometric>
  f5     r_err = 0.05 * r_obs   (as in the injection mocks)
  f1     r_err = 0.01 * r_obs
  f01    r_err = 0.001 * r_obs
Original code: r_err = max(0.05 r_obs, sigma_d), median 188% of r_obs.
Everything else, including the sampler settings, is as in run_one.py.
Also saves per-pair posterior medians of r_proj_model/r_obs and r_true/r_obs.
"""
import json
import os
import sys
import time

import numpy as np

W = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, W)
import run_gamma_analysis as rga  # noqa: E402
import pymc as pm  # noqa: E402
import arviz as az  # noqa: E402

FRAC = {"f5": 0.05, "f1": 0.01, "f01": 0.001}
mode, kind = sys.argv[1], sys.argv[2]
data = rga.prepare_data(f"{W}/data_orig/chae_2026_data.csv", f"{W}/data_orig/chae_2026_gaia.csv")
data["r_err"] = FRAC[mode] * data["r_obs"]
model = rga.build_gamma_model(data, include_sma=(kind == "baseline"), sma_prior="bpl")
t0 = time.time()
with model:
    idata = pm.sample(3000, tune=2000, chains=4, target_accept=0.98, random_seed=123,
                      nuts_sampler="nutpie", progressbar=False)
g = idata.posterior["gamma"].values.flatten()
s = az.summary(idata, var_names=["gamma"])
out = {"mode": mode, "model": kind, "draws": 3000, "elapsed_s": round(time.time() - t0, 1),
       "r_err_over_robs_median": float(np.median(data["r_err"] / data["r_obs"])),
       "median": float(np.median(g)), "ci68": [float(x) for x in np.percentile(g, [16, 84])],
       "ci95": [float(x) for x in np.percentile(g, [2.5, 97.5])],
       "P_gamma_gt_1": float(np.mean(g > 1)), "r_hat": float(s["r_hat"].iloc[0]),
       "ess_bulk": float(s["ess_bulk"].iloc[0]),
       "divergences": int(idata.sample_stats["diverging"].values.sum())}
robs = data["r_obs"].values
for v in ("r_proj_model", "r_true"):
    x = idata.posterior[v].values.reshape(-1, len(robs)) / robs
    out[f"{v}_over_robs_per_pair"] = [float(q) for q in np.median(x, axis=0)]
os.makedirs(f"{W}/out_rerr", exist_ok=True)
np.save(f"{W}/out_rerr/gamma_{mode}_{kind}.npy", g)
json.dump(out, open(f"{W}/out_rerr/gamma_{mode}_{kind}.json", "w"), indent=1)
print(json.dumps(out))
