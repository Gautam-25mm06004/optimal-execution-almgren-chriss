# Risk-Averse Liquidation under Market Impact: A Study of the Almgren–Chriss Model

**Gautam Jain** — IIT Bhubaneswar

## Abstract
We implement the discrete-time Almgren–Chriss (AC) execution model, verify its closed-form expected cost and variance
against Monte Carlo simulation, and use it to quantify three practical questions: how much risk an optimal schedule
removes relative to TWAP, how sensitive the schedule is to a misestimated impact coefficient, and how the trading
grid affects measured risk. For the paper's example (1M shares, $50, 5 days), the λ = 10⁻⁶ schedule costs $0.25M more in
expectation than TWAP but reduces the standard deviation of implementation shortfall from $1.04M to $0.60M.

## 1. Model
Holdings `x_0 = X > x_1 > … > x_N = 0` over intervals τ = T/N, trades `n_k = x_{k−1} − x_k`.
Permanent impact `g(v) = γv` shifts the price for all later trades; temporary impact `h(v) = ε + ηv` affects only the current
trade. Implementation shortfall has

- `E[IS] = ½γX² + εX + (η̃/τ) Σ n_k²`, with `η̃ = η − ½γτ`
- `Var[IS] = σ² τ Σ_{k≥1} x_k²`

Minimising `E + λ·Var` gives `x_j = X sinh(κ(T − t_j))/sinh(κT)` with `(2/τ²)(cosh κτ − 1) = λσ²/η̃`.

Parameters (the paper's example): S₀ = $50, X = 10⁶, T = 5 days, σ = 0.95 $/√day (≈30% annual), ε = 0.0625, η = 2.5×10⁻⁶,
γ = 2.5×10⁻⁷.

## 2. Verification
Tests confirm: the schedule hits both boundary conditions; λ → 0 recovers TWAP; TWAP minimises expected cost; the optimal
schedule beats 50 random perturbations on the objective; and 200,000 Monte Carlo paths reproduce the analytic mean (within
4 standard errors) and standard deviation (within 1%).

## 3. Results
**Strategy comparison.** Immediate liquidation has zero risk but $2.56M of impact cost. TWAP has the lowest expected cost
($0.66M) but a $1.04M standard deviation. AC with λ = 10⁻⁶ sells 46% on day one and reaches $0.91M ± $0.60M, the lowest
95% VaR ($1.91M) and CVaR ($2.16M) of the strategies tested.

**Misspecified impact.** We plan with η̂ = m·η but trade in a market with the true η. The regret in the risk-adjusted
objective is asymmetric: m = 0.25 → +24.8%, m = 0.5 → +6.1%, m = 2 → +4.7%, m = 4 → +14.3%. Underestimating impact
leads to trading too fast and paying heavy temporary impact.

**Grid refinement.** For a fixed 5-day horizon, the objective rises from $1.28M (N = 5) to $1.67M (N = 100) and κ converges
to 0.60/day. The coarse grid is not cheaper in reality; it simply executes each interval's block instantly at the
interval start, so less inventory is exposed to price moves.

## 4. Limitations
Linear impact, arithmetic Brownian motion with no drift, constant volatility and liquidity, and a static (pre-committed)
schedule. Empirical work finds concave (square-root) temporary impact, and adaptive strategies can improve on static ones
when prices trend.

## References
1. R. Almgren, N. Chriss. Optimal execution of portfolio transactions. *Journal of Risk* 3(2), 5–39, 2000.
2. D. Bertsimas, A. Lo. Optimal control of execution costs. *Journal of Financial Markets* 1, 1–50, 1998.
3. R. Almgren, C. Thum, E. Hauptmann, H. Li. Direct estimation of equity market impact. *Risk* 18(7), 2005.
