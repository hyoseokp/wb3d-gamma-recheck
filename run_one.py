"""Run one Saad & Ting (2026) gamma model on one data set, model code unchanged.

usage: python run_one.py <orig|x110> <baseline|geometric>
Sampler: PyMC model compiled for nutpie (numba), because no C compiler is available
for PyTensor here. Draws, tune, chains, target_accept and seed match run_gamma_analysis.py.
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

tag, kind = sys.argv[1], sys.argv[2]
data = rga.prepare_data(f"{W}/data_{tag}/chae_2026_data.csv", f"{W}/data_{tag}/chae_2026_gaia.csv")
model = rga.build_gamma_model(data, include_sma=(kind == "baseline"), sma_prior="bpl")

t0 = time.time()
with model:
    idata = pm.sample(3000, tune=2000, chains=4, target_accept=0.98, random_seed=123,
                      nuts_sampler="nutpie", progressbar=False)
elapsed = time.time() - t0

g = idata.posterior["gamma"].values
flat = g.flatten()
import arviz as az  # noqa: E402
summ = az.summary(idata, var_names=["gamma"])
div = int(idata.sample_stats["diverging"].values.sum()) if "diverging" in idata.sample_stats else -1
out = {
    "data": tag, "model": kind, "elapsed_s": round(elapsed, 1),
    "median": float(np.median(flat)),
    "ci68": [float(x) for x in np.percentile(flat, [16, 84])],
    "ci95": [float(x) for x in np.percentile(flat, [2.5, 97.5])],
    "P_gamma_gt_1": float(np.mean(flat > 1)),
    "r_hat": float(summ["r_hat"].iloc[0]), "ess_bulk": float(summ["ess_bulk"].iloc[0]),
    "divergences": div,
}
np.save(f"{W}/out/gamma_{tag}_{kind}.npy", g)
with open(f"{W}/out/gamma_{tag}_{kind}.json", "w") as fh:
    json.dump(out, fh, indent=1)
print(json.dumps(out))
