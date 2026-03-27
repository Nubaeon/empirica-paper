# Grounding Empirica in Epistemic Mathematics: The Brier Score

**Companion Guide to:** *Empirica: Epistemic Measurement for AI Agents*
**Version:** 1.0 | **Date:** 2026-03-27
**Authors:** David S. L. Van Assche, Philipp Schwinger
**Data:** 1,190,265 evidence observations, 456 learning pairs, 234 sessions
**DOI:** [10.5281/zenodo.19252052](https://doi.org/10.5281/zenodo.19252052)

---

## Overview

This companion guide provides the mathematical foundation connecting the Empirica framework to the Brier score — a strictly proper scoring rule from forecasting theory. While the main paper describes the system architecture and empirical results, this guide explains *why* the mathematics guarantees that honest self-assessment is the optimal strategy.

---

## 1. The Epistemic Objective Function

The Brier score calculates the mean squared difference between a forecasted probability and the actual outcome. In Empirica, this maps to the Grounded Verification phase (Track 2):

```
BS(vector) = (1/N) * SUM[ (V_postflight(i) - V_evidence(i))^2 ]
```

Where:

- **V_postflight** is the AI's self-assessed credence after investigation and execution.
- **V_evidence** is the objective ground truth collected during the POST-TEST phase (e.g., git metrics, test results, code quality scores).
- **N** is the number of epistemic transactions.

Because the Brier score is a *strictly proper scoring rule*, the mathematically optimal strategy for the AI to minimize its error penalty is to report its true, unbiased belief. Track 2 calibration actively measures this exact error and uses it to correct future assessments.

---

## 2. Decomposition: Calibration and Resolution

The Brier score decomposes into three components. Empirica's dual-track architecture optimizes the two the AI can control:

**Calibration (The Grounded Track):** Measures whether the AI's confidence matches reality. An AI trapped in the overconfidence trap reports V_postflight = 0.9 when actual capability is low. Empirica's Track 2 Bayesian updates force calibration by applying historical bias corrections at the Sentinel gate.

**Resolution (The Learning Delta):** Measures the ability to confidently distinguish between states — moving away from an uninformative default prior of 0.50. Empirica's Learning Delta measures resolution acquisition directly:

```
Delta_learning = V_postflight - V_preflight
```

The noetic phase (investigation) provides grounded evidence to push credences toward 1.0 or 0.0, thereby improving the resolution component of the Brier score.

---

## 3. Epistemic Gating as Brier Penalty Avoidance

If an AI bypasses investigation and acts on raw PREFLIGHT assessment, it makes a high-confidence prediction based on low-resolution evidence. Predicting 0.90 when the actual outcome is 0.0 yields a massive quadratic penalty of 0.81.

The Sentinel protocol acts as an algorithmic safeguard against catastrophic Brier penalties. By enforcing dynamic thresholds (Brier-inflated based on historical accuracy), the gate forces the AI back into investigation until its resolution is high enough to mathematically justify action.

---

## 4. Bayesian Updating: Continuous Optimization

Because AI model weights are frozen during inference, an AI cannot natively correct its Brier penalties across sessions. Empirica resolves this by externalizing the optimization using a conjugate normal update:

```
mu_posterior = (sigma_prior^2 * x + sigma_obs^2 * mu_prior) / (sigma_prior^2 + sigma_obs^2)
```

Where:

- **mu_prior** is the historical belief about the AI's bias for this vector
- **x** is the new observation (POSTFLIGHT self-assessment or grounded evidence)
- **sigma** values control the weighting between prior belief and new evidence

**Observation variance weighting:**

| Track | Source | Variance (sigma_obs^2) | Weight |
|-------|--------|----------------------|--------|
| Track 1 (Self-Referential) | AI's own POSTFLIGHT self-report | 0.10 | 1x |
| Track 2 (Grounded Verification) | Objective post-test evidence | 0.05 | 2x |

Track 2 exerts **twice the pull** on the posterior, ensuring optimization is anchored in what actually happened. Empirically, belief variance drops up to **107x** as evidence accumulates, producing mathematically certain bias profiles.

The Sentinel pre-applies the learned correction before evaluating readiness:

```
V_corrected = V_raw + delta_vector
```

This zeroes out the AI's historical calibration error, so the decision to proceed or investigate uses a mathematically corrected vector.

---

## 5. Earned Agency: Autonomy as Brier Performance

AI autonomy becomes a computable metric tied to historical Brier performance:

| Agency Level | Evidence Threshold | Brier Behavior | Gating Response |
|-------------|-------------------|----------------|-----------------|
| Conservative | < 3 observations | High variance, unreliable | Raw vectors, tight thresholds |
| Standard | 3–10 observations | Converging, partially validated | Weighted Bayesian corrections applied |
| Extended | > 10 observations | Optimized, proven accurate | Full corrections, relaxed thresholds |

Because Track 2 represents continuous Brier auditing, earned agency is **inherently revocable**. If self-assessments diverge from outcomes in a novel domain, the score degrades and gating tightens automatically — no human intervention required.

---

## 6. From Theory to Practice

This guide describes the mathematics. The main paper presents the empirical evidence:

- **1,190,265** evidence observations across **234** sessions
- Bayesian convergence demonstrated with **107x** variance reduction
- Noetic phase calibration: **0.08–0.13** (consistently better than praxic: **0.20–0.40**)
- The system catches its own gaming attempts (see: investigate cool-down, EPP)

The question is no longer "Is this AI aligned?" but "Has this AI demonstrated accurate self-assessment in this domain?" If the long-term Brier score approaches zero, autonomous operation is mathematically justified — not assumed.

---

## References

**Main Paper:** Van Assche, D. S. L., & Schwinger, P. (2026). *Empirica: Epistemic Measurement for AI Agents.*

**Dataset & This Guide:** [10.5281/zenodo.19252052](https://doi.org/10.5281/zenodo.19252052) — 1,190,265 evidence observations, 792 sessions, CC BY 4.0

**Code:** [github.com/Nubaeon/empirica](https://github.com/Nubaeon/empirica) — MIT License

**Brier, G. W. (1950).** Verification of forecasts expressed in terms of probability. *Monthly Weather Review*, 78(1), 1–3.

**Murphy, A. H. (1973).** A new vector partition of the probability score. *Journal of Applied Meteorology and Climatology*, 12(4), 595–600.
