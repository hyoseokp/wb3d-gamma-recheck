"""Scale observed relative velocities by F (RV difference and PM difference), masses and errors unchanged."""
import sys, pandas as pd, numpy as np
src, dst, F = sys.argv[1], sys.argv[2], float(sys.argv[3])
c = pd.read_csv(f"{src}/chae_2026_data.csv")
c["vr_kms"] = c["vr_kms"] * F
c.to_csv(f"{dst}/chae_2026_data.csv", index=False)
g = pd.read_csv(f"{src}/chae_2026_gaia.csv")
o = g.copy()
for col in ("pmra", "pmdec"):  # keep star A, move star B so that (B - A) scales by F
    g[f"{col}_b"] = g[f"{col}_a"] + F * (g[f"{col}_b"] - g[f"{col}_a"])
g["rv_diff"] = g["rv_diff"] * F  # not read by the code; scaled for consistency
g.to_csv(f"{dst}/chae_2026_gaia.csv", index=False)
r = ((g.pmra_b - g.pmra_a) / (o.pmra_b - o.pmra_a))
print("RV ratio", np.unique((c.vr_kms / pd.read_csv(f"{src}/chae_2026_data.csv").vr_kms).round(9)), " dPMra ratio min/max", r.min(), r.max())
