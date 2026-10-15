import numpy as np
from .model import ACParams


def simulate_shortfall(x: np.ndarray, p: ACParams, n_paths: int = 20000, seed: int = 0,
                       eta_true: float | None = None, gamma_true: float | None = None) -> np.ndarray:
    """Monte Carlo implementation shortfall (in $) of trading schedule x under the model dynamics.

    eta_true / gamma_true let us execute a schedule designed with one impact estimate in a market with another.
    """
    eta = p.eta if eta_true is None else eta_true
    gam = p.gamma if gamma_true is None else gamma_true
    rng = np.random.default_rng(seed)
    n = -np.diff(x)                     # shares sold in each interval
    S = np.full(n_paths, p.S0)
    revenue = np.zeros(n_paths)
    for k in range(p.N):
        v = n[k] / p.tau
        exec_price = S - (p.eps * np.sign(n[k]) + eta * v)
        revenue += n[k] * exec_price
        S = S + p.sigma * np.sqrt(p.tau) * rng.standard_normal(n_paths) - p.tau * gam * v
    return p.X * p.S0 - revenue
