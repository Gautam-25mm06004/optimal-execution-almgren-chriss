# Interview guide — Optimal Execution (Almgren–Chriss)

## 30-second version
"If you need to sell a million shares, selling fast pushes the price down (impact cost), selling slowly exposes you to
the price moving (risk). Almgren–Chriss minimise expected cost plus λ times variance and get a closed-form schedule: a
sinh curve that sells faster the more risk-averse you are. I implemented it, checked the formulas against 50,000
simulations, and showed that the optimal schedule cuts cost risk by about 42% versus TWAP for about $0.25M more expected cost.
I also showed that mis-estimating impact by 4× costs up to 25% on the objective."

## Must-know concepts
- **Implementation shortfall**: value at the decision price minus what you actually received.
- **Temporary impact** (ηv): a cost only on the shares you trade now, recovering afterwards. **Permanent impact** (γv): moves the price
  for all later trades. Linear permanent impact gives a fixed cost ½γX² whatever the schedule, so it cannot be optimised away.
- **κ ("urgency")**: `κ² ≈ λσ²/η`. High volatility or high risk aversion → sell faster; high impact → sell slower.
  The *half-life* of the trade is about 1/κ ≈ 1.6 days for λ = 10⁻⁶.
- **Why TWAP minimises expected cost**: the cost `Σ n_k²` is convex, so equal slices minimise it (Jensen).

## Likely questions
1. *What does λ mean in practice?* The trader's price of risk; choose it from a VaR budget, or pick a point on the frontier.
2. *Is linear impact realistic?* No — empirical impact is closer to a square root of participation. With nonlinear impact the
   optimum is found numerically (dynamic programming or convex optimisation).
3. *Static vs dynamic?* AC shows that with arithmetic Brownian motion and mean-variance over the whole trade, the optimal
   pre-planned schedule is fine. Later work shows adaptive schedules can do better (e.g., Almgren & Lorenz 2007).
4. *How would you estimate η?* Regress per-trade slippage on participation rate across many executions (Almgren et al. 2005).
5. *Why did a finer grid look riskier?* With N = 5 the first fifth of the trade happens instantly, so it carries no price
   risk; as N grows the model approaches continuous trading and the true risk.

## Numbers to remember
TWAP $0.66M ± $1.04M · AC(λ=10⁻⁶) $0.91M ± $0.60M · 4× impact underestimate → +24.8% objective.
