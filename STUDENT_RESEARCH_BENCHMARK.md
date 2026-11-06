# Lessons from recognized high-school research

**This is a comparison of research practices, not a claim that AI-NIDS is an ISEF finalist.** The projects below are named based on award records; we do not infer unreported methods or metric values.

## Recognized student projects

1. **Ayushi Mehrotra — AdvMed: Detecting Adversarial Attacks in Medical Deep Learning Systems**. First Place Special Award Cybersecurity, Regeneron ISEF 2024. Transferable idea: research reliability under adverse conditions (our defensive offline dataset robustness protocol).
2. **Eric Ruike Song — Improving the Ransomware Detection/Mitigation Proof-of-Concept With Machine Learning**. Second Place Special Award Cybersecurity, Regeneron ISEF 2024. Transferable idea: articulate a bounded defensive problem and demonstrate tested practical impact.
3. **Sebastian Rae Alexis — Unmasking Cybersecurity Vulnerabilities in Direct and Transitive OSS Dependencies**. Third Place Special Award Cybersecurity, Regeneron ISEF 2024. Transferable idea: investigate a narrowly formulated failure mode rather than merely maximize one metric.

Verified award listing: https://www.societyforscience.org/press-release/regeneron-isef-2024-special-awards-winners/

## ISEF criteria translated to our work

| Criterion | ISEF points | Evidence AI-NIDS must produce |
|---|---:|---|
| Research question | 10 | Explicit RQs, controls, falsifiable hypotheses and defined scope |
| Methodology | 15 | Frozen splits, leakage review, transparent model comparisons |
| Execution and analysis | 20 | Raw input hashes, real model outputs, uncertainty and ablations |
| Creativity and impact | 20 | Novel *finding* on efficiency/robustness with evidence, not a claim based on model choice |
| Presentation and interview | 35 | Figure captions, scientific poster, reproducibility demonstration and student explanation |

Source: https://www.societyforscience.org/isef/grand-award/criteria/

## Academic literature relevant to originality

- Bouke & Abdullah (2023), *An empirical study of pattern leakage impact during data preprocessing on machine learning-based intrusion detection models reliability*. https://doi.org/10.1016/j.eswa.2023.120715
- Berhili, Chaieb & Benabdellah (2026), *How evaluation protocol choices inflate intrusion detection accuracy: A three-dataset systematic study*. https://doi.org/10.1016/j.cose.2026.105218

Because protocol sensitivity and cross-dataset generalization are already studied, we **cannot call leakage control or distribution-shift evaluation inherently novel**. A contribution requires a bounded, previously unreported result and credible comparison to this literature.

## What not to copy

Do not reuse another student's abstract, diagrams or conclusions as our own. Avoid presenting AI-written text or unavailable experimental results as original verified measurements. Scientific honesty takes priority over an award-oriented title.
