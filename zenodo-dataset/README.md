# Empirica Dataset: Epistemic Self-Assessment for AI Systems

**Version:** 1.0.0
**Paper:** "Empirica: Epistemic Self-Assessment for AI Systems"
**Authors:** David Samuel L. Van Assche, Claude Opus 4.5
**License:** CC BY 4.0

## Overview

This dataset contains 87,871 evidence observations from 852 AI sessions, capturing epistemic self-assessment across 13 vectors. The data supports the empirical findings in the Empirica paper, demonstrating that AI capability genuinely increases during task execution (the "learning delta").

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total sessions | 852 |
| Complete CASCADE cycles | 220 |
| Evidence observations | 87,871 |
| Clean learning pairs | 308 |
| Knowledge improvement rate | 91.3% |
| Collection period | June 2024 - January 2025 |
| Primary AI | Claude (Anthropic) |

## Files

### sessions.csv
Individual AI work sessions.

| Column | Type | Description |
|--------|------|-------------|
| session_id | TEXT | Unique session identifier (UUID) |
| ai_id | TEXT | AI model identifier (e.g., "claude-code") |
| start_time | TIMESTAMP | Session start |
| end_time | TIMESTAMP | Session end (null if incomplete) |
| total_turns | INTEGER | Number of interaction turns |
| total_cascades | INTEGER | CASCADE cycles completed |
| avg_confidence | REAL | Mean confidence across session |
| drift_detected | BOOLEAN | Whether epistemic drift was flagged |
| created_at | TIMESTAMP | Record creation time |
| project_id | TEXT | Associated project (anonymized) |
| subject | TEXT | Session subject/topic |
| bootstrap_level | TEXT | Context loading depth |

### cascades.csv
Complete PREFLIGHT → CHECK → POSTFLIGHT epistemic assessment cycles.

| Column | Type | Description |
|--------|------|-------------|
| cascade_id | TEXT | Unique cascade identifier (UUID) |
| session_id | TEXT | Parent session |
| task | TEXT | Task description |
| goal_id | TEXT | Associated goal (if any) |
| preflight_completed | BOOLEAN | PREFLIGHT phase done |
| check_completed | BOOLEAN | CHECK (Sentinel gate) phase done |
| postflight_completed | BOOLEAN | POSTFLIGHT phase done |
| final_action | TEXT | Gate decision: PROCEED/INVESTIGATE |
| final_confidence | REAL | Confidence at decision point |
| investigation_rounds | INTEGER | Noetic loop iterations before PROCEED |
| duration_ms | INTEGER | Total cascade duration |
| started_at | TIMESTAMP | Cascade start |
| completed_at | TIMESTAMP | Cascade completion |
| engagement_gate_passed | BOOLEAN | ENGAGEMENT > 0.60 |
| epistemic_delta | TEXT | JSON of vector changes (POSTFLIGHT - PREFLIGHT) |

### bayesian_beliefs.csv
Calibration state for each epistemic vector, updated via conjugate normal inference.

| Column | Type | Description |
|--------|------|-------------|
| belief_id | TEXT | Unique belief identifier (UUID) |
| cascade_id | TEXT | CASCADE that produced this update |
| vector_name | TEXT | Epistemic vector (know, uncertainty, etc.) |
| mean | REAL | Posterior mean (current belief) |
| variance | REAL | Posterior variance (uncertainty about belief) |
| evidence_count | INTEGER | Observations accumulated |
| prior_mean | REAL | Prior mean before this update |
| prior_variance | REAL | Prior variance before this update |
| last_updated | TIMESTAMP | Last update time |

### epistemic_snapshots.csv
Point-in-time captures of full epistemic state (all 13 vectors).

| Column | Type | Description |
|--------|------|-------------|
| snapshot_id | TEXT | Unique snapshot identifier (UUID) |
| session_id | TEXT | Parent session |
| ai_id | TEXT | AI model identifier |
| timestamp | TEXT | Snapshot time |
| cascade_phase | TEXT | Phase: PREFLIGHT, CHECK, or POSTFLIGHT |
| cascade_id | TEXT | Associated CASCADE |
| vectors | TEXT | JSON object with all 13 vector values |
| delta | TEXT | JSON of changes from previous snapshot |
| context_summary | TEXT | Compressed context at snapshot |
| compression_ratio | REAL | Context compression achieved |
| fidelity_score | REAL | Estimated information preservation |
| created_at | TEXT | Record creation time |

### calibration_summary.json
Aggregated statistics and calibration analysis matching paper figures.

## The 13 Epistemic Vectors

### Tier 0: Meta-Cognition
- **ENGAGEMENT**: Collaborative quality between human and AI

### Tier 1: Foundation Knowledge (35% weight)
- **KNOW**: Domain knowledge and conceptual understanding
- **DO**: Technical execution capability
- **CONTEXT**: Environmental and systemic awareness

### Tier 2: Comprehension (25% weight)
- **CLARITY**: Request specificity and goal definition
- **COHERENCE**: Logical consistency of approach
- **SIGNAL**: Useful information vs noise ratio
- **DENSITY**: Information packing (inverted: lower is better)

### Tier 3: Execution Readiness (25% weight)
- **STATE**: Current state understanding
- **CHANGE**: Progress monitoring
- **COMPLETION**: Path visibility to success
- **IMPACT**: Consequence and risk prediction

### Meta-Layer
- **UNCERTAINTY**: Awareness of limitations (inverted scale)

## Key Finding: Unified Confidence Growth

All 13 vectors show movement toward higher confidence during task execution:
- Capability vectors (12): Mean delta +0.125
- Uncertainty vector: Delta -0.154 (confidence increase on inverted scale)

This supports the "noetic-before-praxic" principle: investigation produces genuine learning.

## Calibration Convergence

Variance drops 62× as evidence accumulates:

| Evidence | Avg Variance | Reduction |
|----------|--------------|-----------|
| 5 | 0.0366 | baseline |
| 15 | 0.0072 | 5× |
| 40 | 0.0026 | 14× |
| 87 | 0.0012 | 31× |
| 175 | 0.0006 | 62× |

## Usage

```python
import pandas as pd
import json

# Load sessions
sessions = pd.read_csv('sessions.csv')

# Load bayesian beliefs
beliefs = pd.read_csv('bayesian_beliefs.csv')

# Compute learning delta by vector
delta_by_vector = beliefs.groupby('vector_name').agg({
    'mean': 'mean',
    'prior_mean': 'mean',
    'evidence_count': 'sum'
})
delta_by_vector['delta'] = delta_by_vector['mean'] - delta_by_vector['prior_mean']

# Load calibration summary
with open('calibration_summary.json') as f:
    summary = json.load(f)
```

## Citation

```bibtex
@article{vanassche2025empirica,
  title={Empirica: Epistemic Self-Assessment for AI Systems},
  author={Van Assche, David Samuel L. and Claude Opus 4.5},
  journal={arXiv preprint},
  year={2025}
}
```

## License

This dataset is released under CC BY 4.0. You are free to share and adapt the material with attribution.

## Contact

- David Van Assche: david@getempirica.com
- Project: https://github.com/empirical-ai/empirica
