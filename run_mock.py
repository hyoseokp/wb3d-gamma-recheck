"""Fit one regenerated synthetic catalog with the unchanged Saad & Ting model.

usage: python run_mock.py <mock_csv> <baseline|geometric>
Settings follow injection_recovery.json: draws 1500, tune 2000, 4 chains,
target_accept 0.99, max tree depth 12, random_seed = 1000 + k (nutpie sampler).
"""
import json, os, sys, time
import numpy as np, pandas as pd
W = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, W)
import run_gamma_analysis as rga
import pymc as pm
import arviz as az

path, kind = sys.argv[1], sys.argv[2]
name = os.path.splitext(os.path.basename(path))[0]
k = int(name.split("_k")[1].split("_")[0])
sim = pd.read_csv(path)
model = rga.build_gamma_model(sim, include_sma=(kind == "baseline"), sma_prior="bpl")
t0 = time.time()
with model:
    idata = pm.sample(1500, tune=2000, chains=4, target_accept=0.99, random_seed=1000 + k,
                      nuts_sampler="nutpie", nuts_sampler_kwargs={"maxdepth": 12}, progressbar=False)
g = idata.posterior["gamma"].values.flatten()
s = az.summary(idata, var_names=["gamma"])
out = {"mock": name, "model": kind, "elapsed_s": round(time.time() - t0, 1),
       "median": float(np.median(g)), "ci68": [float(x) for x in np.percentile(g, [16, 84])],
       "P_gamma_gt_1": float(np.mean(g > 1)), "r_hat": float(s["r_hat"].iloc[0]),
       "ess_bulk": float(s["ess_bulk"].iloc[0]),
       "divergences": int(idata.sample_stats["diverging"].values.sum())}
np.save(f"{W}/out_mock/{name}_{kind}.npy", g)
json.dump(out, open(f"{W}/out_mock/{name}_{kind}.json", "w"), indent=1)
print(json.dumps(out))
