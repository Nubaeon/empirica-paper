# 3. Theoretical Framework

## 3.1 Epistemic Vectors: A Computational Theory of Knowing

We propose that AI cognitive state can be represented as a vector in a 13-dimensional epistemic space. Each dimension corresponds to a measurable aspect of the system's knowledge state, collectively capturing what the AI knows, what it can do, and how confident it should be in proceeding.

### 3.1.1 The Vector Taxonomy

The 13 epistemic vectors are organized into four tiers:

**Tier 0: Meta-Cognition**
- **ENGAGEMENT** - Quality of collaborative intelligence between human and AI. Functions as the primary gate: if engagement is below threshold, other assessments are unreliable.

**Tier 1: Foundation Knowledge** (35% weight in confidence calculation)
- **KNOW** - Domain knowledge and conceptual understanding
- **DO** - Technical execution capability and tool access
- **CONTEXT** - Environmental and systemic awareness

**Tier 2: Comprehension** (25% weight)
- **CLARITY** - Request specificity and goal definition
- **COHERENCE** - Logical consistency of approach
- **SIGNAL** - Useful information vs noise ratio
- **DENSITY** - Information packing efficiency (inverted: lower is better)

**Tier 3: Execution Readiness** (25% weight)
- **STATE** - Current state understanding
- **CHANGE** - Progress monitoring and regression detection
- **COMPLETION** - Path visibility to success
- **IMPACT** - Consequence and risk prediction

**Meta-Layer** (not in confidence calculation)
- **UNCERTAINTY** - Awareness of limitations and unknowns

### 3.1.2 Functional Self-Assessment

A critical design principle: these vectors implement *functional* self-assessment, not reportive self-assessment.

**Reportive**: AI tells a human "I am 80% confident." The human must trust the report; the AI has no stake in accuracy.

**Functional**: AI assesses itself to decide whether to proceed with a task. Bad assessment leads to bad outcomes, creating a feedback loop that enables calibration.

The epistemic vectors are routing signals for the AI's own decision-making. When an AI assesses KNOW = 0.4 and decides to investigate rather than proceed, the assessment directly affects behavior and outcomes. This requires no claim about consciousness or introspection—only that assessments correlate with task-relevant states.

### 3.1.3 Confidence Calculation

Overall epistemic confidence aggregates the vectors:

```
confidence = (
    ENGAGEMENT * 0.15 +
    mean(KNOW, DO, CONTEXT) * 0.35 +
    mean(CLARITY, COHERENCE, SIGNAL, 1-DENSITY) * 0.25 +
    mean(STATE, CHANGE, COMPLETION, IMPACT) * 0.25
)
```

The gate condition:
```
if ENGAGEMENT < 0.6:
    decision = STOP  # Insufficient collaborative intelligence
else:
    decision = PROCEED if confidence > threshold else INVESTIGATE
```

## 3.2 Noetic and Praxic Phases

We distinguish two fundamental phases of AI cognition:

### 3.2.1 Noetic Phase (Investigation)

The noetic phase encompasses exploration, hypothesis formation, and knowledge acquisition. During this phase, the AI:

- Explores the problem space
- Reads relevant context (files, documentation, conversation history)
- Identifies unknowns and knowledge gaps
- Forms hypotheses about solutions
- Builds genuine understanding of the task

The noetic phase is characterized by *increasing* epistemic vectors—particularly KNOW, CONTEXT, and CLARITY. The AI is learning.

### 3.2.2 Praxic Phase (Execution)

The praxic phase encompasses implementation, action, and output generation. During this phase, the AI:

- Applies acquired knowledge
- Executes planned actions
- Produces deliverables
- Modifies external state (code, files, systems)

The praxic phase is characterized by *stable* epistemic vectors (knowledge already acquired) and increasing COMPLETION and CHANGE vectors (progress toward goal).

### 3.2.3 The Ordering Principle

The central theoretical claim: **noetic must precede praxic**.

An AI that acts without first investigating is an AI that acts on incomplete knowledge. The execution-layer model—give task, receive output—skips the noetic phase entirely, assuming the AI either possesses sufficient knowledge or doesn't. This assumption fails for any task requiring exploration.

The evidence for this principle is the learning delta: systematic capability growth during task execution (Section 5). If noetic precedes praxic, we expect POSTFLIGHT assessments to exceed PREFLIGHT assessments—and they do, across all 13 vectors.

## 3.3 Computational Epistemology

The epistemic vector framework constitutes a *computational epistemology*: a formal theory of how any information-processing system can assess and manage its own knowledge state.

### 3.3.1 Grounding in Transformer Architecture (Speculative)

We hypothesize—but do not prove—that the 13 epistemic vectors correspond to measurable properties of transformer attention mechanisms:

| Vector | Hypothesized Attention Correlate |
|--------|----------------------------------|
| KNOW | Value vector richness in relevant attention heads |
| UNCERTAINTY | Attention entropy / calibration gap |
| CONTEXT | Cross-attention to context tokens |
| ENGAGEMENT | Attention coherence across layers |
| CLARITY | Query-key alignment sharpness |

This mapping remains speculative. We invite mechanistic interpretability researchers to test these correlations. If the mapping holds, it would provide architectural grounding for what currently relies on self-report.

### 3.3.2 Architecture Independence

Regardless of the attention-mechanism hypothesis, the epistemic vector framework applies to any system that must:

1. Assess its own knowledge state
2. Decide whether to act or investigate
3. Learn from the outcomes of its decisions

This includes biological agents. Humans experience epistemic states—the feeling of knowing, the sense of uncertainty, the quality of engagement—that map recognizably to the vector taxonomy. The framework does not anthropomorphize AI; it *mechanizes* human epistemology, formalizing what philosophers call "epistemic feelings" into computable quantities.

### 3.3.3 Falsifiable Predictions

The theoretical framework generates testable predictions:

1. **Learning delta exists**: POSTFLIGHT vectors should exceed PREFLIGHT vectors (Section 5 confirms)
2. **Gating improves outcomes**: Enforcing investigation when KNOW is low should increase task success
3. **Calibration is learnable**: Systematic bias in self-assessment should be correctable through feedback
4. **Attention correlates exist**: Vectors should correlate with extractable attention properties (testable via interpretability)

If these predictions fail, the framework is wrong. We publish data for replication.

## 3.4 The Overconfidence Trap

The theoretical framework explains a common failure mode: the **overconfidence trap**.

```
Conditions:
  UNCERTAINTY: LOW  (AI thinks it knows)
  KNOW: LOW        (AI doesn't actually know)

Without epistemic gating:
  → AI proceeds immediately (no investigation)
  → AI produces confident, wrong output
  → User loses trust

With epistemic gating:
  → Gate detects KNOW < threshold
  → AI forced to investigate (noetic phase)
  → Investigation produces learning
  → KNOW increases to threshold
  → AI proceeds with actual capability
  → Output quality improves
```

The gate doesn't just prevent bad outputs—it produces good outputs by forcing the learning that creates capability.

## 3.5 Summary

The theoretical framework rests on three claims:

1. **Epistemic vectors**: AI cognitive state can be represented in 13 dimensions that capture what the system knows and how ready it is to act.

2. **Noetic-before-praxic**: Investigation must precede execution. Skipping the noetic phase produces the overconfidence trap.

3. **Learning is measurable**: The delta between PREFLIGHT and POSTFLIGHT assessments captures genuine knowledge acquisition during task execution.

These claims are empirically testable. Section 5 presents evidence from 82,380 observations across 849 sessions.
