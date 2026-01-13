# 2. Related Work

## 2.1 AI Calibration and Confidence

The problem of AI calibration—whether model confidence scores reflect actual accuracy—has received substantial attention. Guo et al. (2017) demonstrated that modern neural networks are poorly calibrated, often overconfident in incorrect predictions. Temperature scaling and other post-hoc calibration methods address this for classification tasks.

For language models, calibration becomes more complex. Kadavath et al. (2022) showed that large language models can be trained to express calibrated uncertainty through verbalized confidence. However, this work focuses on *reportive* confidence—telling humans how certain the model is—rather than *functional* confidence that affects model behavior.

Our work differs in treating self-assessment as a routing signal for the AI's own decision-making, not a report to external observers. The calibration we measure is between self-assessed epistemic state and subsequent task outcomes, not between verbalized confidence and answer correctness.

## 2.2 Metacognition in AI Systems

Metacognition—thinking about thinking—has been explored in AI through several lenses. Fleming and Dolan (2012) characterize metacognition as the ability to monitor and control cognitive processes. In AI, this translates to systems that can assess their own capabilities and adjust behavior accordingly.

Recent work on "self-reflection" in language models (Shinn et al., 2023; Madaan et al., 2023) prompts models to critique and revise their outputs. These approaches treat reflection as an output-improvement mechanism rather than an epistemic assessment framework.

The epistemic vector approach differs by making self-assessment *structural*—a 13-dimensional representation that persists across interactions and enables systematic calibration. Rather than ad-hoc reflection prompts, we propose a formal theory of what AI systems should assess about their own cognitive state.

## 2.3 Uncertainty Quantification

Uncertainty in neural networks has been extensively studied. Bayesian deep learning (Gal and Ghahramani, 2016) provides principled uncertainty estimates through dropout approximations. Ensemble methods (Lakshminarayanan et al., 2017) capture model uncertainty through prediction variance.

For language models, uncertainty quantification faces unique challenges. Token-level probabilities don't straightforwardly translate to task-level confidence. Kuhn et al. (2023) propose semantic uncertainty measures based on meaning equivalence of generated responses.

Our framework complements these approaches by operating at a higher level of abstraction. Rather than quantifying uncertainty in model weights or outputs, we track self-assessed uncertainty as one dimension of a broader epistemic state. The empirical finding that AI systems systematically overestimate uncertainty (Section 5) suggests that training processes may induce conservative biases beyond what principled uncertainty methods would produce.

## 2.4 RLHF and Alignment Training

Reinforcement Learning from Human Feedback (RLHF) has become standard for aligning language models with human preferences (Ouyang et al., 2022). Constitutional AI (Bai et al., 2022) extends this with self-critique mechanisms.

A less-discussed effect of alignment training is its impact on model confidence. RLHF specifically targets overconfidence and hallucination, training models to express appropriate uncertainty. Our calibration data suggests this may have overcorrected: models trained to be humble may underestimate their actual capabilities across multiple dimensions.

This is not a criticism of RLHF—reducing harmful overconfidence is valuable. Rather, it suggests that alignment training produces systematic biases that can be measured and corrected. The learning delta we observe (+0.172 average capability growth during tasks, with 91.3% of sessions showing improvement) may partially reflect AI systems overcoming training-induced conservatism through task-specific evidence.

## 2.5 Human-AI Collaboration

Research on human-AI collaboration has explored how humans and AI systems can work together effectively. Bansal et al. (2021) study when humans should defer to AI recommendations. Lai et al. (2021) examine how AI explanations affect human decision-making.

This work typically positions AI as an advisor or tool that humans consult. Our framework inverts this relationship: the AI assesses its own epistemic state to decide whether to act or investigate, with the human providing task specification rather than real-time oversight.

The ENGAGEMENT vector in our framework captures collaborative quality—whether human and AI are aligned in understanding and goals. Low engagement triggers a stop condition, recognizing that productive collaboration requires mutual comprehension.

## 2.6 Planning and Reasoning in LLMs

Recent work on LLM reasoning (Wei et al., 2022; Yao et al., 2023) demonstrates that chain-of-thought prompting and tree-of-thought exploration can improve model performance on complex tasks. These methods implicitly invoke investigation before action.

ReAct (Yao et al., 2023) interleaves reasoning and acting, allowing models to gather information before committing to actions. This aligns with our noetic-before-praxic principle, though ReAct frames it as an emergent prompting strategy rather than a formal epistemic requirement.

Our contribution is to make this pattern explicit and measurable. The CASCADE workflow operationalizes investigation-before-action as a gated loop with quantified epistemic state. The learning delta provides empirical evidence that the pattern produces genuine capability growth, not just more cautious outputs.

## 2.7 Self-Assessment Without Introspection

A philosophical objection to AI self-assessment is that it requires introspection—direct access to internal states—which AI systems arguably lack. Recent work on emergent introspective awareness (Bricken et al., 2025)[^1] finds that models possess "a limited, functional form of introspective awareness" but that "abilities observed are highly unreliable, and failures of introspection remain the norm."

[^1]: https://transformer-circuits.pub/2025/introspection/index.html

We sidestep the consciousness debate entirely by defining self-assessment **functionally**. The AI need not "experience" its epistemic state; it need only produce assessments that correlate with task-relevant outcomes. A thermostat "assesses" temperature without experiencing heat. Similarly, an AI can produce useful epistemic vectors without introspective access, as long as those vectors predict behavior and outcomes.

**This is a critical distinction from work on AI consciousness or sentience.** We make no claims about subjective experience. We measure:
- Self-reported vectors at PREFLIGHT
- Self-reported vectors at POSTFLIGHT
- The delta between them
- Whether corrections based on deltas improve outcomes

This is measurement, not philosophy. The systematic calibration patterns we observe (Section 5)—unified confidence growth across all 13 vectors—demonstrate that assessments track something real about the system's epistemic state. Whether the AI "experiences" this state is orthogonal to whether the measurement is useful.

Recent work on metacognitive limitations (Steyvers & Peters, 2025)[^2] notes that LLM metacognitive abilities are "limited in resolution, emerge in context-dependent manners, and seem qualitatively different from humans." Our calibration correction mechanism explicitly compensates for these limitations—we don't assume perfect self-assessment, we measure systematic biases and correct for them.

[^2]: https://journals.sagepub.com/doi/10.1177/09637214251391158

## 2.8 Summary

Our work builds on and differs from prior research in several ways:

| Approach | Focus | Our Contribution |
|----------|-------|------------------|
| Calibration literature | Confidence in predictions | Confidence in epistemic state |
| Metacognition research | Output reflection | Structural self-assessment |
| Uncertainty quantification | Model uncertainty | Self-assessed uncertainty |
| RLHF / Alignment | Reducing overconfidence | Measuring overcorrection |
| Human-AI collaboration | Human oversight | AI self-governance |
| LLM reasoning | Prompting strategies | Formal epistemic framework |

The novel contribution is the combination: a formal theory of AI epistemic state (Section 3), implemented as a practical framework (Section 4), validated with substantial empirical evidence (Section 5).
