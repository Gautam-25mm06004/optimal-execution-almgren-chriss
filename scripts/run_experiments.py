"""Almgren-Chriss experiments: efficient frontier, trajectories, Monte Carlo check, impact misspecification,
and a finer trading grid. Writes results/results.json, results/summary.md, results/figures/*.png."""
import json, sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ac import (ACParams, optimal_trajectory, twap_trajectory, front_loaded, expected_cost,  # noqa: E402
                cost_variance, kappa, simulate_shortfall)

OUT, FIG = ROOT / "results", ROOT / "results" / "figures"
FIG.mkdir(parents=True, exist_ok=True)


def tbl(rows, cols):
    return ("| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n" +
            "".join("| " + " | ".join(str(r[c]) for c in cols) + " |\n" for r in rows))


def stats(sf):
    return {"mc_mean_$": round(float(sf.mean())), "mc_std_$": round(float(sf.std(ddof=1))),
            "VaR95_$": round(float(np.percentile(sf, 95))), "CVaR95_$": round(float(sf[sf >= np.percentile(sf, 95)].mean()))}


def main():
    p = ACParams()
    res = {"params": p.__dict__}

    # 1) Strategy comparison with analytic and Monte Carlo cost
    strategies = {"immediate (all in first interval)": front_loaded(p), "TWAP (linear)": twap_trajectory(p)}
    for lam in (1e-7, 1e-6, 1e-5):
        strategies[f"Almgren-Chriss lambda={lam:g}"] = optimal_trajectory(lam, p)
    comp = []
    for name, x in strategies.items():
        E, V = expected_cost(x, p), cost_variance(x, p)
        sf = simulate_shortfall(x, p, 50000, seed=1)
        comp.append({"strategy": name, "E[IS]_$": round(E), "std[IS]_$": round(np.sqrt(V)),
                     **stats(sf), "E+1e-6*Var": round(E + 1e-6 * V),
                     "holdings_after_day1_%": round(100 * x[1] / p.X, 1)})
    res["strategies"] = comp

    # 2) Efficient frontier
    lams = np.geomspace(1e-9, 1e-4, 40)
    front = [{"lambda": float(l), "E": expected_cost(optimal_trajectory(l, p), p),
              "std": float(np.sqrt(cost_variance(optimal_trajectory(l, p), p))),
              "kappa_per_day": kappa(l, p)} for l in lams]
    res["frontier"] = front

    # 3) Impact misspecification: plan with eta_hat, trade in a market with the true eta
    mis = []
    for mult in (0.25, 0.5, 1.0, 2.0, 4.0):
        plan_p = replace(p, eta=p.eta * mult)
        x = optimal_trajectory(1e-6, plan_p)
        sf = simulate_shortfall(x, p, 50000, seed=2)
        true_opt = optimal_trajectory(1e-6, p)
        best = expected_cost(true_opt, p) + 1e-6 * cost_variance(true_opt, p)
        U = expected_cost(x, p) + 1e-6 * cost_variance(x, p)
        mis.append({"eta_hat / eta_true": mult, "E[IS]_$": round(expected_cost(x, p)), "std_$": round(np.sqrt(cost_variance(x, p))),
                    "objective_$": round(U), "objective_regret_%": round(100 * (U - best) / best, 2), "mc_mean_$": round(float(sf.mean()))})
    res["misspecification"] = mis

    # 4) Finer trading grid: same 5 days, more intervals
    grid = []
    for N in (5, 10, 25, 50, 100):
        q = replace(p, N=N)
        x = optimal_trajectory(1e-6, q)
        grid.append({"N_intervals": N, "kappa_per_day": round(kappa(1e-6, q), 4), "E[IS]_$": round(expected_cost(x, q)),
                     "std_$": round(np.sqrt(cost_variance(x, q))), "objective_$": round(expected_cost(x, q) + 1e-6 * cost_variance(x, q))})
    res["grid"] = grid

    # Figures
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.plot([f["std"] / 1e3 for f in front], [f["E"] / 1e3 for f in front], "-", label="efficient frontier")
    for r, x in zip(comp, strategies.values()):
        ax.plot(np.sqrt(cost_variance(x, p)) / 1e3, expected_cost(x, p) / 1e3, "o", label=r["strategy"])
    ax.set_xlabel("std of shortfall ($k)"); ax.set_ylabel("expected shortfall ($k)"); ax.legend(fontsize=7)
    ax.set_title("Almgren-Chriss efficient frontier (sell 1M shares in 5 days)")
    fig.tight_layout(); fig.savefig(FIG / "frontier.png", dpi=130); plt.close(fig)

    q = replace(p, N=50)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    t = np.arange(q.N + 1) * q.tau
    for lam in (0, 1e-7, 1e-6, 1e-5, 1e-4):
        x = twap_trajectory(q) if lam == 0 else optimal_trajectory(lam, q)
        ax.plot(t, x / 1e3, label=f"lambda={lam:g}")
    ax.set_xlabel("day"); ax.set_ylabel("shares held (k)"); ax.legend(); ax.set_title("Optimal holdings vs risk aversion")
    fig.tight_layout(); fig.savefig(FIG / "trajectories.png", dpi=130); plt.close(fig)

    (OUT / "results.json").write_text(json.dumps(res, indent=2))
    md = "# Results\n\n## Strategy comparison (analytic + 50,000 Monte Carlo paths)\n\n" + tbl(comp, list(comp[0]))
    md += "\n## Impact misspecification (lambda = 1e-6)\n\n" + tbl(mis, list(mis[0]))
    md += "\n## Finer trading grid over the same 5 days (lambda = 1e-6)\n\n" + tbl(grid, list(grid[0]))
    (OUT / "summary.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
