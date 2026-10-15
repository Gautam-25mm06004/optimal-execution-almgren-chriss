"""Almgren-Chriss optimal execution: trajectories, analytic cost/risk, Monte Carlo shortfall."""
from .model import ACParams, optimal_trajectory, twap_trajectory, front_loaded, expected_cost, cost_variance, kappa
from .simulate import simulate_shortfall

__all__ = ["ACParams", "optimal_trajectory", "twap_trajectory", "front_loaded", "expected_cost",
           "cost_variance", "kappa", "simulate_shortfall"]
