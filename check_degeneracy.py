"""Check that the likelihood is unchanged under M -> 1.10 M, gamma -> gamma / 1.10.

Evaluates the observed-data log-likelihood of the original-mass model at random
parameter points and of the x1.10-mass model at the mapped points.
"""
import os
import sys

import numpy as np

W = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, W)
import run_gamma_analysis as rga  # noqa: E402

F = 1.10
rng = np.random.default_rng(0)


def interval_fwd(x, a=-1.0, b=1.0):
    return np.log((x - a) / (b - x))


def interval_back(y, a=-1.0, b=1.0):
    return a + (b - a) / (1.0 + np.exp(-y))


for kind in ("baseline", "geometric"):
    models = {}
    for tag in ("orig", "x110"):
        d = rga.prepare_data(f"{W}/data_{tag}/chae_2026_data.csv", f"{W}/data_{tag}/chae_2026_gaia.csv")
        m = rga.build_gamma_model(d, include_sma=(kind == "baseline"), sma_prior="bpl")
        models[tag] = (m, m.compile_logp(vars=m.observed_RVs, jacobian=False))
    m0, lik0 = models["orig"]
    _, lik1 = models["x110"]
    diffs = []
    for _ in range(20):
        p = {k: v + rng.normal(0, 0.3, np.shape(v)) for k, v in m0.initial_point().items()}
        q = dict(p)
        q["M1_sol_log__"] = p["M1_sol_log__"] + np.log(F)
        q["M2_sol_log__"] = p["M2_sol_log__"] + np.log(F)
        gam = interval_back(p["Gam_interval__"])
        q["Gam_interval__"] = interval_fwd(gam - 0.5 * np.log10(F))  # gamma = 10**(2 Gam)
        diffs.append(float(lik1(q) - lik0(p)))
    print(f"{kind}: max |lnL(x1.10 mass, gamma/1.10) - lnL(orig)| over 20 points = {max(map(abs, diffs)):.2e}")
