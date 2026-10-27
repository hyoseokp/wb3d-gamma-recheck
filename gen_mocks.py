"""Regenerate the Saad & Ting (2026) Appendix C synthetic catalogs with run_injection.simulate.

Seeds follow run_injection.main: seed = 1000 + int(gamma_true*100) + k, k = 0..4.
Template = prepare_data() on the public repo inputs (data_orig/).
Saved columns are the prepared-model inputs (SI units), not raw Gaia columns.
"""
import os, sys
W = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, W)
import run_gamma_analysis as rga
from run_injection import simulate

tpl = rga.prepare_data(f"{W}/data_orig/chae_2026_data.csv", f"{W}/data_orig/chae_2026_gaia.csv")
for gt in (1.0, 1.6):
    for k in range(5):
        seed = 1000 + int(gt * 100) + k
        sim = simulate(tpl, gt, seed)
        sim.to_csv(f"{W}/mocks/mock_g{gt:.1f}_k{k}_seed{seed}.csv", index=False)
        print(gt, k, seed, "r_err/r_obs median %.3f" % (sim.r_err / sim.r_obs).median())
