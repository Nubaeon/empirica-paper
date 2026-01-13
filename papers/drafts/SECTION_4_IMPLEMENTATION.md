# 4. Implementation: The Empirica Framework

Empirica is an open-source framework implementing the epistemic vector theory. It provides infrastructure for AI self-assessment, epistemic gating, and calibration feedback loops.

## 4.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Empirica Framework                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Sessions   │  │  Cascades   │  │  Epistemic Snapshots│  │
│  │  Database   │──│  (Loops)    │──│  (Vector States)    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│         │                │                    │              │
│         ▼                ▼                    ▼              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              Bayesian Belief Manager                    ││
│  │         (Calibration & Correction Learning)             ││
│  └─────────────────────────────────────────────────────────┘│
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                  Sentinel Protocol                       ││
│  │            (Epistemic Gating Decisions)                  ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## 4.2 The CASCADE Workflow

CASCADE (Calibrated Assessment of State, Context, and Domain Epistemics) is the core epistemic loop:

```
PREFLIGHT ────► CHECK ────► POSTFLIGHT
    │            │              │
    │            │              │
Baseline     Sentinel        Learning
Assessment   Gate            Delta
    │            │              │
    │            ▼              │
    │     ┌──────────┐         │
    │     │ PROCEED? │         │
    │     └────┬─────┘         │
    │          │               │
    │    ┌─────┴─────┐         │
    │    ▼           ▼         │
    │  [YES]       [NO]        │
    │    │           │         │
    │    ▼           ▼         │
    │  PRAXIC    NOETIC        │
    │  (act)   (investigate)   │
    │    │           │         │
    │    │     ┌─────┘         │
    │    │     ▼               │
    │    │   RE-CHECK          │
    │    │     │               │
    │    ▼     ▼               │
    └────────► POSTFLIGHT ─────┘
                   │
                   ▼
            Bayesian Update
          (calibration learning)
```

### 4.2.1 PREFLIGHT Phase

At task onset, the AI assesses its epistemic state across all 13 vectors:

```bash
empirica preflight-submit - << EOF
{
  "session_id": "...",
  "vectors": {
    "know": 0.55,
    "uncertainty": 0.40,
    "context": 0.70,
    "engagement": 0.85,
    ...
  },
  "reasoning": "Initial assessment: familiar domain but specific codebase unknown"
}
EOF
```

This establishes the baseline against which learning will be measured.

### 4.2.2 CHECK Phase (Sentinel Gate)

The Sentinel protocol evaluates whether the AI has sufficient knowledge to proceed:

```bash
empirica check-submit - << EOF
{
  "session_id": "...",
  "action_description": "Implement authentication fix",
  "vectors": {
    "know": 0.65,
    "uncertainty": 0.35,
    ...
  }
}
EOF
```

The gate applies bias corrections (learned from historical calibration) and returns:
- **PROCEED**: Knowledge sufficient, enter praxic phase
- **INVESTIGATE**: Knowledge insufficient, remain in noetic phase

### 4.2.3 POSTFLIGHT Phase

After task completion (or significant progress), the AI reassesses:

```bash
empirica postflight-submit - << EOF
{
  "session_id": "...",
  "vectors": {
    "know": 0.82,
    "uncertainty": 0.20,
    "completion": 0.90,
    ...
  },
  "learnings": ["Auth flow uses JWT not sessions", "Rate limiting in middleware"],
  "delta_summary": "Significant learning about codebase architecture"
}
EOF
```

The delta between PREFLIGHT and POSTFLIGHT vectors measures learning.

## 4.3 The Sentinel Protocol

Sentinel is the epistemic gate that enforces noetic-before-praxic:

### 4.3.1 Gate Logic

```python
def sentinel_decision(vectors, calibration_adjustments):
    # Apply learned bias corrections
    corrected_know = vectors['know'] + calibration_adjustments.get('know', 0)
    corrected_uncertainty = vectors['uncertainty'] + calibration_adjustments.get('uncertainty', 0)

    # Readiness gate
    if corrected_know >= 0.70 and corrected_uncertainty <= 0.35:
        return "PROCEED"
    else:
        return "INVESTIGATE"
```

### 4.3.2 Calibration Integration

The Sentinel applies corrections learned from historical Bayesian updates. If the AI systematically underestimates KNOW by 0.15, the gate adjusts:

- Raw KNOW: 0.55
- Correction: +0.15
- Effective KNOW: 0.70
- Decision: PROCEED (would have been INVESTIGATE without correction)

This allows the system to compensate for learned biases while maintaining conservative defaults for uncalibrated vectors.

## 4.4 Bayesian Belief Management

The framework maintains Bayesian beliefs about each vector's calibration:

### 4.4.1 Update Rule

For each vector, we track a belief distribution updated via conjugate normal inference:

```
posterior_mean = (prior_var * observation + obs_var * prior_mean) / (prior_var + obs_var)
posterior_var = 1 / (1/prior_var + 1/obs_var)
```

Where:
- **prior**: Current belief about the AI's typical assessment
- **observation**: POSTFLIGHT assessment (the "ground truth" after learning)
- **posterior**: Updated belief incorporating new evidence

### 4.4.2 Calibration Delta

The key measurement is the learning delta:

```
delta = POSTFLIGHT_value - PREFLIGHT_value
```

Positive delta indicates the AI learned during the task (capability grew). The mean delta across sessions becomes the calibration correction.

## 4.5 Data Model

### 4.5.1 Sessions

```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    ai_id TEXT NOT NULL,
    created_at TIMESTAMP,
    status TEXT,  -- active, completed, abandoned
    metadata TEXT  -- JSON
);
```

### 4.5.2 Cascades

```sql
CREATE TABLE cascades (
    cascade_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    outcome TEXT,  -- completed, abandoned, error
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

### 4.5.3 Epistemic Snapshots

```sql
CREATE TABLE epistemic_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    cascade_phase TEXT,  -- PREFLIGHT, CHECK, POSTFLIGHT
    vectors TEXT,  -- JSON: {know: 0.7, uncertainty: 0.3, ...}
    delta TEXT,  -- JSON: changes from previous snapshot
    created_at TIMESTAMP
);
```

### 4.5.4 Bayesian Beliefs

```sql
CREATE TABLE bayesian_beliefs (
    belief_id TEXT PRIMARY KEY,
    cascade_id TEXT NOT NULL,
    vector_name TEXT NOT NULL,
    mean REAL,
    variance REAL,
    evidence_count INTEGER,
    prior_mean REAL,  -- PREFLIGHT value for this cycle
    prior_variance REAL,
    last_updated TIMESTAMP
);
```

## 4.6 CLI Interface

Empirica provides a command-line interface for integration:

```bash
# Session management
empirica session-create --ai-id claude-code --output json
empirica session-list --status active

# CASCADE workflow
empirica preflight-submit -    # Stdin JSON
empirica check-submit -        # Returns PROCEED or INVESTIGATE
empirica postflight-submit -   # Captures learning delta

# Knowledge management
empirica finding-log --session-id ... --finding "..." --impact 0.8
empirica unknown-log --session-id ... --unknown "..."

# Calibration
empirica calibration-report --ai-id claude-code
```

## 4.7 Integration Patterns

### 4.7.1 IDE Integration

Empirica integrates with development environments via hooks:

```javascript
// .claude/hooks/session-start.js
module.exports = async (context) => {
    await empirica.sessionCreate({ aiId: context.aiId });
    await empirica.preflightSubmit({ ... });
};
```

### 4.7.2 Agent Framework Integration

For autonomous agents, Empirica provides epistemic checkpoints:

```python
class EpistemicAgent:
    def run_task(self, task):
        # PREFLIGHT
        self.preflight_assess()

        while not self.task_complete():
            # CHECK gate
            if self.sentinel.should_investigate():
                self.investigate()  # Noetic phase
            else:
                self.act()  # Praxic phase

        # POSTFLIGHT
        self.postflight_assess()
        self.update_calibration()
```

## 4.8 Production Deployment

The framework has been deployed in production for 6+ months:

- **Sessions**: 849 completed
- **Evidence observations**: 82,380
- **Cascades**: 217 full PREFLIGHT→POSTFLIGHT cycles
- **Clean learning pairs**: 308 (filtered for data quality)
- **Findings logged**: 1,900+
- **Primary AI**: Claude (Anthropic), with cross-validation on GPT, Gemini, Qwen

The data presented in Section 5 derives from this production deployment.
