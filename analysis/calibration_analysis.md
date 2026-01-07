# Bayesian Calibration Analysis

**Generated:** 2026-01-07
**Data Source:** Empirica production database
**Analysis Period:** 2024-2026

## Executive Summary

Analysis of 1,184 Bayesian belief updates (35,268 total evidence observations) reveals **systematic calibration bias across all 13 epistemic vectors**:

- **12/13 vectors are underestimated** - AI self-reports lower values than actual outcomes
- **Only uncertainty is overestimated** - AI thinks it's more uncertain than warranted
- **Mean absolute bias: 0.328** - significant correction needed for accurate self-assessment

## Key Finding: The Humility-Uncertainty Paradox

AI systems exhibit a **systematic humility bias** - they underestimate their own capabilities across nearly all dimensions. Paradoxically, the only exception is uncertainty, which they *overestimate*. This creates a double-conservative profile:

1. AI reports knowing less than it does (know: +0.33 correction needed)
2. AI reports being more uncertain than warranted (uncertainty: -0.31 correction needed)

**Implication:** Uncorrected AI self-assessments will be systematically pessimistic about capabilities while being overly cautious about uncertainty.

## Calibration Table

| Vector | Evidence | Posterior Mean | Bias | Direction | Correction |
|--------|----------|----------------|------|-----------|------------|
| know | 7,811 | 0.830 | +0.330 | Underestimate | +0.33 |
| uncertainty | 7,811 | 0.189 | -0.311 | Overestimate | -0.31 |
| context | 6,970 | 0.845 | +0.345 | Underestimate | +0.34 |
| engagement | 3,581 | 0.866 | +0.366 | Underestimate | +0.37 |
| completion | 1,739 | 0.821 | +0.321 | Underestimate | +0.32 |
| clarity | 1,193 | 0.873 | +0.373 | Underestimate | +0.37 |
| impact | 1,116 | 0.812 | +0.312 | Underestimate | +0.31 |
| do | 1,043 | 0.855 | +0.355 | Underestimate | +0.35 |
| change | 941 | 0.809 | +0.309 | Underestimate | +0.31 |
| signal | 819 | 0.842 | +0.342 | Underestimate | +0.34 |
| density | 791 | 0.699 | +0.199 | Underestimate | +0.20 |
| state | 764 | 0.847 | +0.347 | Underestimate | +0.35 |
| coherence | 689 | 0.854 | +0.354 | Underestimate | +0.35 |

## Bias Magnitude Ranking

### Largest Underestimates (need positive correction)
1. **clarity** (+0.373) - AI drastically underestimates how clear requests are
2. **engagement** (+0.366) - AI underestimates quality of collaboration
3. **do** (+0.355) - AI underestimates its execution capability
4. **coherence** (+0.354) - AI underestimates its logical consistency
5. **state** (+0.347) - AI underestimates its state understanding

### Only Overestimate
1. **uncertainty** (-0.311) - AI overestimates its uncertainty

### Most Well-Calibrated (still biased)
1. **density** (+0.199) - Closest to calibrated, but still underestimated

## Implications for Paper

### Current Paper Claims (Section 5.2)
The paper references calibration data but doesn't include the comprehensive bias analysis. Key updates needed:

1. **Add calibration table** to empirical validation section
2. **Discuss humility-uncertainty paradox** as novel finding
3. **Explain correction mechanism** in Sentinel protocol
4. **Update N** from 186 to include calibration evidence (35,268)

### Theoretical Implications
The systematic underestimation across 12/13 vectors suggests:

1. **Training bias toward caution** - RLHF may have created excessive humility
2. **Asymmetric error costs** - Models penalized more for overconfidence than underconfidence
3. **Calibration as learned behavior** - Bias patterns are consistent, suggesting learned rather than random

## Bayesian Update Formula

The calibration uses conjugate normal-normal updates:

$$\mu_{posterior} = \frac{\sigma^2_{prior} \cdot x + \sigma^2_{likelihood} \cdot \mu_{prior}}{\sigma^2_{prior} + \sigma^2_{likelihood}}$$

With:
- Prior: μ = 0.5, σ² = 0.1 (uninformative)
- Updates: Evidence from actual task outcomes vs. AI self-assessment

## Data Files

- `bayesian_beliefs.csv` - Raw belief updates (1,184 rows)
- `cascades.csv` - CASCADE workflow metadata (149 rows)
- `analysis_results.json` - Computed statistics

## Next Steps

1. Add temporal analysis (has bias changed over time?)
2. Cross-model comparison (different AI systems)
3. Task-type stratification (does bias vary by task?)
4. Integrate with epistemic snapshots for vector trajectory analysis
