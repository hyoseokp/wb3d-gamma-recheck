import sys, pandas as pd
src, dst, f = sys.argv[1], sys.argv[2], float(sys.argv[3])
d = pd.read_csv(src)
print("NaN masses:", int(d["mass_a"].isna().sum()), int(d["mass_b"].isna().sum()))
# missing masses default to 1.0 Msun in prepare_data(); scale that default too
d["mass_a"] = (d["mass_a"].fillna(1.0) * f).round(6)
d["mass_b"] = (d["mass_b"].fillna(1.0) * f).round(6)
d.to_csv(dst, index=False)
o = pd.read_csv(src)
print("rows", len(d), " ratio a min/max", (d.mass_a/o.mass_a).min(), (d.mass_a/o.mass_a).max(), " b", (d.mass_b/o.mass_b).min(), (d.mass_b/o.mass_b).max())
print("total mass orig median %.3f -> x110 median %.3f" % ((o.mass_a+o.mass_b).median(), (d.mass_a+d.mass_b).median()))
