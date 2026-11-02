"""Write tables/chain_table.tex (table only) and tables/chain_table_standalone.tex (compilable with pdflatex)."""
import json
import os

import numpy as np

W = os.path.dirname(os.path.abspath(__file__))

V = [("orig", r"original code (188\%)", W + "/out/gamma_orig_{k}"),
     ("f5", r"5\%", W + "/out_rerr/gamma_f5_{k}"),
     ("f01", r"0.1\%", W + "/out_rerr/gamma_f01_{k}")]

lines = []
for kind in ("baseline", "geometric"):
    lines.append(r"\midrule")
    lines.append(rf"\multicolumn{{6}}{{l}}{{\textit{{{kind}}}}} \\")
    for v, lab, p in V:
        g = np.load(p.format(k=kind) + ".npy").reshape(4, -1)
        d = json.load(open(p.format(k=kind) + ".json"))
        ok = d["r_hat"] <= 1.03 and d["ess_bulk"] >= 100
        cells = [f"{np.median(c):.2f}" for c in g]
        if ok:
            row = " & ".join(cells) + r" & converged"
        else:
            row = " & ".join(rf"\textcolor{{gray}}{{{c}}}" for c in cells) + r" & \textcolor{gray}{not converged}"
        lines.append(rf"\quad {lab} & {row} \\")

table = r"""\begin{tabular}{l cccc c}
\toprule
$\sigma_{r_\perp}/r_\perp$ & Chain 1 & Chain 2 & Chain 3 & Chain 4 & Status \\
""" + "\n".join(lines) + r"""
\bottomrule
\end{tabular}"""

caption = (r"Posterior median of $\gamma$ in each of four independent MCMC chains, when the public code of "
           r"Saad \& Ting (2026) is fitted to the 36 observed pairs and only the error $\sigma_{r_\perp}$ of the "
           r"projected-separation likelihood (their Eq.~13) is changed. "
           r"The original code sets $\sigma_{r_\perp}=\max(0.05\,r_\perp,\sigma_d)$, where $\sigma_d$ is the error of the "
           r"distance, so the median $\sigma_{r_\perp}/r_\perp$ is 188\%. "
           r"A fit is counted as converged when the four chains agree, i.e.\ $\hat{R}\le 1.03$ and the effective sample "
           r"size is at least 100. The effective sample size (ESS) is the number of independent draws that the "
           r"correlated MCMC draws are worth: the converged fits have ESS $=233$--849 out of 12\,000 draws. "
           r"Fits shown in grey did not converge ($\hat{R}=1.5$--1.8, ESS $=6$--7): the chains settle on different "
           r"values, so their results are not reliable. "
           r"All other settings follow the original code (3000 draws and 2000 tuning steps per chain, target "
           r"acceptance 0.98, seed 123, nutpie sampler).")

body = r"""\begin{table}
\centering
\caption{""" + caption + r"""}
\label{tab:chains}
""" + table + r"""
\end{table}
"""
open(f"{W}/tables/chain_table.tex", "w", encoding="utf-8").write(body)

standalone = r"""\documentclass[varwidth=15cm,border=8pt]{standalone}
\usepackage{booktabs}
\usepackage{xcolor}
\usepackage{caption}
\captionsetup{font=small,labelfont=bf,labelsep=period}
\begin{document}
\begin{minipage}{15cm}
\centering
\captionof{table}{""" + caption + r"""}
\vspace{4pt}
""" + table + r"""
\end{minipage}
\end{document}
"""
open(f"{W}/tables/chain_table_standalone.tex", "w", encoding="utf-8").write(standalone)
