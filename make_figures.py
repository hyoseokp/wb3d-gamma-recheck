"""Draw the README figures from the saved results in out/ and out_mock/."""
import glob
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

W = os.path.dirname(os.path.abspath(__file__))
FIG = f"{W}/figures"
BASE, GEO = "#2a6fdb", "#e07b00"
INK, MUTED, GRID = "#1c1c1c", "#6b6b6b", "#e4e4e4"
# Newtonian mock recoveries reported in the authors' injection_recovery.json (Appendix C)
PAPER = {1100: 0.693, 1101: 1.044, 1102: 0.947, 1103: 1.097, 1104: 0.877}
plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED})


def load(path):
    return json.load(open(path))


def mock(seed, kind):
    return load(glob.glob(f"{W}/out_mock/*seed{seed}_{kind}.json")[0])


def forest(ax, rows, title):
    """rows: list of (label, [(kind, result-dict or None)])."""
    ys = np.arange(len(rows))[::-1]
    for y, (label, fits) in zip(ys, rows):
        for dy, (kind, r) in zip((0.15, -0.15), fits):
            if r is None:
                continue
            c, mk = (BASE, "o") if kind == "baseline" else (GEO, "s")
            lo, hi = r["ci68"]
            ax.plot([lo, hi], [y + dy] * 2, color=c, lw=2, solid_capstyle="round")
            ax.plot(r["median"], y + dy, mk, color=c, ms=8, mec="white", mew=1.5)
            ax.text(hi + 0.03, y + dy, f"{r['median']:.2f}", va="center", fontsize=9, color=INK)
    ax.set_yticks(ys, [r[0] for r in rows])
    ax.axvline(1.0, color=INK, lw=1, ls="--")
    ax.axvline(1.56, color=MUTED, lw=1, ls=":")
    ax.text(1.0, ys[0] + 0.6, "Newton  γ = 1", ha="center", fontsize=8.5, color=INK)
    ax.text(1.56, ys[0] + 0.6, "paper geometric 1.56", ha="center", fontsize=8.5, color=MUTED)
    ax.set_ylim(ys[-1] - 0.6, ys[0] + 0.9)
    ax.set_xlabel("γ  (posterior median and 68% interval)")
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.plot([], [], "o-", color=BASE, label="baseline (free a, BPL prior)")
    ax.plot([], [], "s-", color=GEO, label="geometric de-projection")
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    ax.set_title(title, loc="left", fontsize=11.5, weight="bold", color=INK)


# Figure 1: table of the Newtonian-mock fits
rows, b_all, g_all = [], [], []
for seed in sorted(PAPER):
    b, g = mock(seed, "baseline"), mock(seed, "geometric")
    b_all.append(b["median"]); g_all.append(g["median"])
    rows.append([str(seed), f"{PAPER[seed]:.3f}", f"{b['median']:.3f}",
                 f"{g['median']:.3f}  [{g['ci68'][0]:.2f}, {g['ci68'][1]:.2f}]"])
rows.append(["mean", f"{np.mean(list(PAPER.values())):.2f}", f"{np.mean(b_all):.2f}", f"{np.mean(g_all):.2f}"])
cols = ["mock seed\n(γ_true = 1)", "baseline\nauthors' json", "baseline\nthis rerun", "geometric, this rerun\nmedian [68%]"]
fig, ax = plt.subplots(figsize=(9, 4.0)); ax.axis("off")
t = ax.table(cellText=rows, colLabels=cols, loc="center", cellLoc="center", colWidths=[0.2, 0.18, 0.18, 0.34])
t.auto_set_font_size(False); t.set_fontsize(11); t.scale(1, 1.9)
for (r, c), cell in t.get_celld().items():
    cell.set_edgecolor("#bbbbbb")
    if r == 0:
        cell.set_facecolor("#eef2f8"); cell.set_text_props(weight="bold")
    if r == len(rows):
        cell.set_facecolor("#f4f4f4"); cell.set_text_props(weight="bold")
ax.set_title("Saad & Ting (2026) Newtonian mocks: baseline vs geometric γ", fontsize=13, weight="bold")
fig.savefig(f"{FIG}/fig1_mock_table.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# Figure 2: forest plot of the mock fits
fig, ax = plt.subplots(figsize=(8, 4.6))
forest(ax, [(f"mock {s}", [("baseline", mock(s, "baseline")), ("geometric", mock(s, "geometric"))])
            for s in sorted(PAPER)],
       "Newtonian mocks (γ_true = 1): geometric does not return 1.5")
fig.savefig(f"{FIG}/fig2_mock_forest.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# Figure 3: real data, original vs scaled inputs
def real(tag, kind):
    p = f"{W}/out/gamma_{tag}_{kind}.json"
    return load(p) if os.path.exists(p) else None

fig, ax = plt.subplots(figsize=(8, 3.6))
forest(ax, [("original data", [("baseline", real("orig", "baseline")), ("geometric", real("orig", "geometric"))]),
            ("masses × 1.10", [("baseline", real("x110", "baseline")), ("geometric", real("x110", "geometric"))]),
            ("velocities × 1.10", [("baseline", real("v110", "baseline")), ("geometric", None)])],
       "Real 36 pairs: γ scales as 1/M and roughly as v²")
fig.savefig(f"{FIG}/fig3_real_data_scaling.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("figures written to", FIG)
