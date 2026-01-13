# 6. The Sentinel Protocol

Sentinel is the epistemic gating mechanism that operationalizes noetic-before-praxic. It evaluates whether an AI system has sufficient knowledge to proceed with action, enforcing investigation when knowledge is insufficient.

## 6.1 Design Principles

### 6.1.1 Gate, Don't Filter

Traditional AI safety mechanisms filter outputs—scanning generated content for harmful patterns. Sentinel operates upstream: it gates *action*, not output. The distinction matters:

| Approach | Intervention Point | Failure Mode |
|----------|-------------------|--------------|
| Output filtering | After generation | Confident wrong outputs pass |
| Epistemic gating | Before action | Insufficient knowledge blocks action |

An AI that lacks knowledge to solve a problem correctly also lacks knowledge to recognize its solution is wrong. Output filtering cannot catch this. Epistemic gating intervenes earlier—at the knowledge assessment stage.

### 6.1.2 Calibration-Aware

Raw self-assessments are systematically biased (Section 5). Sentinel applies learned corrections before making gate decisions:

```python
corrected_know = raw_know + calibration_delta['know']
corrected_uncertainty = raw_uncertainty + calibration_delta['uncertainty']
```

This allows the gate to function accurately despite self-assessment biases. As calibration improves with evidence, gate decisions become more precise.

### 6.1.3 Conservative by Default

For vectors without sufficient calibration evidence (< 3 observations), Sentinel applies no correction—defaulting to the conservative raw assessment. This prevents overcorrection early in deployment while allowing learned corrections to take effect as evidence accumulates.

## 6.2 Gate Logic

### 6.2.1 Readiness Condition

The core gate evaluates two primary vectors:

```
PROCEED if:
    corrected_know >= 0.70
    AND corrected_uncertainty <= 0.35
```

Both conditions must be met. High knowledge with high uncertainty still triggers investigation—the AI knows things but isn't confident in their relevance or completeness.

### 6.2.2 Engagement Override

The ENGAGEMENT vector functions as a meta-gate:

```
if ENGAGEMENT < 0.60:
    return STOP  # Cannot proceed or investigate meaningfully
```

Low engagement indicates fundamental communication failure—the AI and human are not aligned on goals or understanding. Neither action nor investigation will be productive until engagement is restored.

### 6.2.3 Decision Flow

```
┌─────────────────────────────────────┐
│          CHECK Submission           │
│   (vectors + action description)    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Apply Calibration Corrections   │
│   know += delta_know                │
│   uncertainty += delta_uncertainty  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         ENGAGEMENT Check            │
│         engagement >= 0.60?         │
└──────────┬─────────────┬────────────┘
           │             │
         [NO]          [YES]
           │             │
           ▼             ▼
┌──────────────┐  ┌─────────────────────────┐
│    STOP      │  │    Readiness Check      │
│  (disengage) │  │  know >= 0.70 AND       │
└──────────────┘  │  uncertainty <= 0.35?   │
                  └─────────┬─────────┬─────┘
                            │         │
                          [NO]      [YES]
                            │         │
                            ▼         ▼
                  ┌──────────────┐ ┌──────────────┐
                  │ INVESTIGATE  │ │   PROCEED    │
                  │   (noetic)   │ │   (praxic)   │
                  └──────────────┘ └──────────────┘
```

## 6.3 The Investigation Loop

When Sentinel returns INVESTIGATE, the AI enters or continues the noetic phase:

### 6.3.1 Investigation Actions

Typical noetic actions include:
- Reading files, documentation, or context
- Searching codebases or knowledge bases
- Asking clarifying questions
- Forming and testing hypotheses
- Synthesizing information from multiple sources

### 6.3.2 Re-CHECK

After investigation, the AI re-submits to CHECK with updated vectors:

```
Loop:
    1. CHECK submission
    2. If INVESTIGATE:
        a. Perform investigation actions
        b. Update epistemic vectors
        c. Return to step 1
    3. If PROCEED:
        a. Enter praxic phase
        b. Execute action
```

### 6.3.3 Loop Termination

The loop terminates when:
- **PROCEED**: Knowledge threshold reached
- **STOP**: Engagement too low (communication failure)
- **Max iterations**: Safety limit prevents infinite loops (configurable, default 5)
- **User override**: Human can force proceed or stop

## 6.4 Calibration Feedback

### 6.4.1 Learning from Outcomes

Each CASCADE cycle (PREFLIGHT → CHECK → POSTFLIGHT) provides calibration evidence:

```
calibration_delta[vector] = POSTFLIGHT[vector] - PREFLIGHT[vector]
```

Positive delta indicates the AI underestimated at PREFLIGHT; negative indicates overestimation. These deltas accumulate in the Bayesian belief system.

### 6.4.2 Correction Evolution

As evidence accumulates, corrections become more precise:

| Evidence Count | Correction Confidence |
|----------------|----------------------|
| < 3 | No correction (too uncertain) |
| 3-10 | Partial correction (weighted by evidence) |
| > 10 | Full correction (stable estimate) |

### 6.4.3 Per-Vector Calibration

Each vector has independent calibration. From our data (Section 5):

| Vector | Learned Correction |
|--------|-------------------|
| know | +0.141 |
| uncertainty | -0.154 |
| completion | +0.397 |
| engagement | +0.004 (near-calibrated) |

The COMPLETION vector shows the largest correction—AI systems dramatically underestimate task progress at PREFLIGHT.

## 6.5 Configuration

### 6.5.1 Threshold Tuning

Gate thresholds can be adjusted for different risk tolerances:

```yaml
sentinel:
  thresholds:
    know_minimum: 0.70      # Lower = more permissive
    uncertainty_maximum: 0.35  # Higher = more permissive
    engagement_minimum: 0.60   # Lower = accept worse communication

  max_investigation_rounds: 5
  apply_calibration: true
```

### 6.5.2 Domain-Specific Gates

Different task domains may warrant different thresholds:

| Domain | know_min | uncertainty_max | Rationale |
|--------|----------|-----------------|-----------|
| Code review | 0.65 | 0.40 | Lower stakes, can iterate |
| Production deploy | 0.85 | 0.20 | High stakes, need certainty |
| Exploration | 0.50 | 0.50 | Learning is the goal |
| Safety-critical | 0.90 | 0.15 | Cannot afford errors |

### 6.5.3 Override Mechanisms

For flexibility, Sentinel supports overrides:

```bash
# Force proceed despite gate
empirica check-submit --force-proceed ...

# Force investigate despite passing gate
empirica check-submit --force-investigate ...

# Disable calibration corrections
empirica check-submit --raw-vectors ...
```

Overrides are logged for audit purposes.

## 6.6 Integration with CASCADE

Sentinel is the bridge between noetic and praxic phases within CASCADE:

```
CASCADE Cycle:

    PREFLIGHT ──────────────────────────────────────┐
        │                                           │
        │  Initial epistemic assessment             │
        │                                           │
        ▼                                           │
    ┌─────────┐                                     │
    │ Noetic  │◄────────────────────┐               │
    │  Phase  │                     │               │
    └────┬────┘                     │               │
         │                          │               │
         │  Investigation           │               │
         │                          │               │
         ▼                          │               │
    ┌─────────┐                     │               │
    │  CHECK  │──── INVESTIGATE ────┘               │
    │(Sentinel)                                     │
    └────┬────┘                                     │
         │                                          │
         │  PROCEED                                 │
         │                                          │
         ▼                                          │
    ┌─────────┐                                     │
    │ Praxic  │                                     │
    │  Phase  │                                     │
    └────┬────┘                                     │
         │                                          │
         │  Execution                               │
         │                                          │
         ▼                                          │
    POSTFLIGHT ◄────────────────────────────────────┘
        │
        │  Learning delta → Calibration update
        │
        ▼
    [Next CASCADE or Session End]
```

## 6.7 Empirical Performance

From production deployment (849 sessions):

### 6.7.1 Gate Statistics

| Metric | Value |
|--------|-------|
| Total CHECK submissions | 694 |
| Total cascades | 217 |
| Clean learning pairs | 308 |
| Knowledge improvement rate | 91.3% |
| Uncertainty reduction rate | 95.1% |

### 6.7.2 Calibration Impact

Comparing outcomes with and without calibration correction:

| Condition | False PROCEED rate | False INVESTIGATE rate |
|-----------|-------------------|----------------------|
| Raw vectors | 18% | 34% |
| Calibrated vectors | 8% | 12% |

Calibration correction reduces both error types—fewer premature actions and fewer unnecessary investigations.

## 6.8 Summary

The Sentinel protocol implements epistemic gating:

1. **Gate, don't filter**: Prevent action when knowledge is insufficient, rather than filtering bad outputs after generation.

2. **Calibration-aware**: Apply learned corrections to compensate for systematic self-assessment biases.

3. **Investigation loop**: When knowledge is insufficient, enforce exploration until threshold is reached.

4. **Configurable**: Thresholds adjustable for different domains and risk tolerances.

The empirical result: calibrated gating reduces error rates by more than 50% compared to raw self-assessment. The learning delta (Section 5) shows that investigation produces genuine capability growth—the gate doesn't just prevent bad outputs; it enables good ones.
