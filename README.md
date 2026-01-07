# Empirica Research Papers

Research papers on AI epistemic cognition and the Empirica framework.

## Repository Structure

```
empirica-paper/
├── papers/
│   ├── drafts/          # Working paper drafts
│   └── published/       # Final published versions
├── data/
│   ├── calibration/     # Bayesian calibration observations
│   ├── sessions/        # Session metrics and vectors
│   ├── findings/        # Logged findings and dead ends
│   └── unknowns/        # Tracked unknowns
├── scripts/             # Data processing scripts
└── analysis/            # Analysis notebooks and outputs
```

## Data Summary

Extracted from Empirica production database (2024-2026):

| Dataset | Records | Description |
|---------|---------|-------------|
| `bayesian_beliefs.csv` | 1,184 | Calibration observations showing AI bias patterns |
| `sessions.csv` | 685 | AI sessions with metadata |
| `epistemic_snapshots.csv` | 51 | Epistemic vector snapshots with deltas |
| `cascades.csv` | 149 | CASCADE workflow executions |
| `goals.csv` | 179 | Tracked goals |
| `project_findings.csv` | 1,255 | High-impact learnings |
| `session_findings.csv` | 445 | Session-specific findings |
| `project_unknowns.csv` | 161 | Unresolved questions |
| `session_unknowns.csv` | 76 | Session-specific unknowns |
| `dead_ends.csv` | 9 | Documented failed approaches |
| `mistakes.csv` | 5 | Logged mistakes |
| `lessons.csv` | 9 | Procedural knowledge lessons |

## Paper Drafts

1. **UNIFIED_EPISTEMIC_THEORY.md** - Core theoretical framework
2. **UNIFIED_EPISTEMIC_VECTORS.md** - Vector space model for epistemic states
3. **EPISTEMIC_GROUNDING_PAPER.md** - Grounding AI cognition in observable behaviors
4. **HUMAN_AI_SYMBIOSIS.md** - Human-AI collaborative cognition
5. **AIs_Epistemic_Blueprint.pdf** - Visual blueprint (14MB)

## Key Research Questions

1. **Bayesian Calibration**: How do AI systems develop systematic biases in self-assessment?
   - Evidence: 1,184 calibration observations showing consistent patterns
   - Key finding: AIs underestimate completion (+0.54), overestimate uncertainty (-0.19)

2. **Epistemic Vectors**: Can we quantify AI knowledge states in real-time?
   - 13 tracked vectors: know, uncertainty, context, engagement, completion, etc.
   - Delta tracking shows learning progression

3. **Knowledge Persistence**: How should AI learning persist across sessions?
   - Eidetic memory (facts with confidence) vs episodic memory (narratives with decay)
   - Qdrant vector store for semantic retrieval

## License

Proprietary - Internal research use only.
