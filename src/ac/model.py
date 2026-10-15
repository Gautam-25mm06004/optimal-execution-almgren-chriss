"""Discrete-time Almgren & Chriss (2000) model, 'Optimal execution of portfolio transactions', J. Risk 3(2).

We sell X shares over N intervals of length tau = T/N. Holdings x_0 = X, ..., x_N = 0; trade n_k = x_{k-1} - x_k.
Price dynamics:  S_k = S_{k-1} + sigma sqrt(tau) xi_k - tau g(n_k/tau),       g(v) = gamma v   (permanent impact)
Execution price: S~_k = S_{k-1} - h(n_k/tau),                                  h(v) = eps sgn(v) + eta v (temporary)
Implementation shortfall  IS = X S_0 - sum n_k S~_k.
"""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class ACParams:
    S0: float = 50.0          # $/share
    X: float = 1e6            # shares to sell
    T: float = 5.0            # days
    N: int = 5                # trading intervals
    sigma: float = 0.95       # $/share/sqrt(day)  (~30% annual vol at $50)
    eps: float = 0.0625       # fixed cost per share (half the bid-ask spread)
    eta: float = 2.5e-6       # temporary impact, $/share per (share/day)
    gamma: float = 2.5e-7     # permanent impact, $/share per share

    @property
    def tau(self) -> float:
        return self.T / self.N

    @property
    def eta_tilde(self) -> float:
        return self.eta - 0.5 * self.gamma * self.tau


def kappa(lam: float, p: ACParams) -> float:
    """Solve (2/tau^2)(cosh(kappa tau) - 1) = lam sigma^2 / eta_tilde for kappa."""
    k2 = lam * p.sigma ** 2 / p.eta_tilde
    if k2 <= 0:
        return 0.0
    return float(np.arccosh(1.0 + 0.5 * k2 * p.tau ** 2) / p.tau)


def optimal_trajectory(lam: float, p: ACParams) -> np.ndarray:
    """Holdings x_j = X sinh(kappa (T - t_j)) / sinh(kappa T), j = 0..N."""
    t = np.arange(p.N + 1) * p.tau
    k = kappa(lam, p)
    if k * p.T < 1e-10:
        return twap_trajectory(p)
    return p.X * np.sinh(k * (p.T - t)) / np.sinh(k * p.T)


def twap_trajectory(p: ACParams) -> np.ndarray:
    """Linear liquidation (the lam -> 0, risk-neutral solution)."""
    return p.X * (1.0 - np.arange(p.N + 1) / p.N)


def front_loaded(p: ACParams) -> np.ndarray:
    """Sell everything in the first interval."""
    x = np.zeros(p.N + 1)
    x[0] = p.X
    return x


def expected_cost(x: np.ndarray, p: ACParams) -> float:
    """E[IS] = 1/2 gamma X^2 + eps sum|n_k| + (eta_tilde / tau) sum n_k^2."""
    n = -np.diff(x)
    return float(0.5 * p.gamma * p.X ** 2 + p.eps * np.sum(np.abs(n)) + p.eta_tilde / p.tau * np.sum(n ** 2))


def cost_variance(x: np.ndarray, p: ACParams) -> float:
    """Var[IS] = sigma^2 tau sum_{k=1}^{N} x_k^2 (holdings after each trade carry price risk)."""
    return float(p.sigma ** 2 * p.tau * np.sum(x[1:] ** 2))
