# Grounding Empirica in Epistemic Mathematics: The Brier Score

**Companion Guide to:** *Empirica: Epistemic Measurement for AI Agents*
**Version:** 1.0 | **Date:** 2026-03-27
**Authors:** David S. L. Van Assche, Philipp Schwinger
**Data:** 1,190,265 evidence observations, 456 learning pairs, 234 sessions

---

## Overview

This companion guide provides the mathematical foundation connecting the Empirica framework to the Brier score — a strictly proper scoring rule from forecasting theory. While the main paper describes the system architecture and empirical results, this guide explains *why* the mathematics guarantees that honest self-assessment is the optimal strategy.

---

## 1. The Epistemic Objective Function

The Brier score calculates the mean squared difference between a forecasted probability and the actual outcome. In Empirica, this maps to the Grounded Verification phase (Track 2):

$$BS_{vector} = \frac{1}{N} \sum_{i=1}^{N} (V_{POSTFLIGHT, i} - V_{evidence, i})^2$$

- **$V_{POSTFLIGHT}$** is the AI's self-assessed credence after investigation and execution.
- **$V_{evidence}$** is the objective ground truth collected during the POST-TEST phase (e.g., git metrics, test results, code quality scores).
- **$N$** is the number of epistemic transactions.

Because the Brier score is a *strictly proper scoring rule*, the mathematically optimal strategy for the AI to minimize its error penalty is to report its true, unbiased belief. Track 2 calibration actively measures this exact error and uses it to correct future assessments.

## 2. Decomposition: Calibration and Resolution

The Brier score decomposes into three components. Empirica's dual-track architecture optimizes the two the AI can control:

**Calibration (The Grounded Track):** Measures whether the AI's confidence matches reality. An AI trapped in the overconfidence trap reports $V_{POSTFLIGHT} = 0.9$ when actual capability is low. Empirica's Track 2 Bayesian updates force calibration by applying historical bias corrections at the Sentinel gate.

**Resolution (The Learning Delta):** Measures the ability to confidently distinguish between states — moving away from an uninformative default prior of $0.50$. Empirica's Learning Delta ($\Delta_{learning} = V_{POSTFLIGHT} - V_{PREFLIGHT}$) directly measures resolution acquisition. The noetic phase provides grounded evidence to push credences toward $1.0$ or $0.0$.

## 3. Epistemic Gating as Brier Penalty Avoidance

If an AI bypasses investigation and acts on raw PREFLIGHT assessment, it makes a high-confidence prediction based on low-resolution evidence. Predicting $0.90$ when the actual outcome is $0.0$ yields a massive quadratic penalty.

The Sentinel protocol acts as an algorithmic safeguard. By enforcing dynamic thresholds (historically: KNOW $\ge 0.70$, UNCERTAINTY $\le 0.35$, now Brier-inflated), the gate forces the AI back into investigation until its resolution justifies action.

## 4. Bayesian Updating: Continuous Optimization

Because AI model weights are frozen during inference, an AI cannot natively correct its Brier penalties across sessions. Empirica resolves this by externalizing the optimization using a conjugate normal update:

$$\mu_{posterior} = \frac{\sigma_{prior}^2 \cdot x + \sigma_{obs}^2 \cdot \mu_{prior}}{\sigma_{prior}^2 + \sigma_{obs}^2}$$

**Observation variance weighting:**
- **Track 1 (Self-Referential):** $\sigma_{obs}^2 = 0.10$ — AI's own POSTFLIGHT self-report
- **Track 2 (Grounded Verification):** $\sigma_{obs}^2 = 0.05$ — Objective post-test evidence

Track 2 exerts twice the pull on the posterior, ensuring optimization is anchored in what actually happened. Empirically, belief variance drops up to $107\times$ as evidence accumulates, producing mathematically certain bias profiles.

The Sentinel pre-applies the learned correction:

$$V_{corrected} = V_{raw} + \delta_{vector}$$

## 5. Earned Agency: Autonomy as Brier Performance

AI autonomy becomes a computable metric tied to historical Brier performance:

| Agency Level | Evidence | Brier Behavior | Gating |
|-------------|----------|----------------|--------|
| Conservative | < 3 observations | High variance | Raw vectors, tight thresholds |
| Standard | 3-10 observations | Converging | Weighted corrections applied |
| Extended | > 10 observations | Optimized | Full corrections, relaxed thresholds |

Because Track 2 represents continuous Brier auditing, earned agency is inherently revocable. If self-assessments diverge from outcomes in a novel domain, the score degrades and gating tightens automatically.

## 6. From Theory to Practice

This guide describes the mathematics. The main paper presents the empirical evidence:

- **1,190,265** evidence observations across **234** sessions
- Bayesian convergence demonstrated with **$107\times$** variance reduction
- Noetic phase calibration: **0.08-0.13** (consistently better than praxic: **0.20-0.40**)
- The system catches its own gaming attempts (see: investigate cool-down, EPP)

The question is no longer "Is this AI aligned?" but "Has this AI demonstrated accurate self-assessment in this domain?" If the long-term Brier score approaches zero, autonomous operation is mathematically justified — not assumed.

---

**Citation:** Van Assche, D. S. L., & Schwinger, P. (2026). *Empirica: Epistemic Measurement for AI Agents.* Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX

**Code:** https://github.com/Nubaeon/empirica (MIT License)

**Data:** https://zenodo.org/records/XXXXXXX (Zenodo dataset)
