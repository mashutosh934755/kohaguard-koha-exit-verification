# KohaGuard Evaluation Protocol

This protocol is intended to move the project from a technical prototype to a publishable empirical systems study.

## Research questions
1. Can KohaGuard correctly distinguish currently issued from non-issued physical items?
2. What is the system and end-to-end verification latency?
3. How do camera and manual verification compare?
4. How usable is the guard-facing system in a real library environment?

## Phase 1 — Controlled classification study
Use at least 500–1,000 genuine verification events across known ground-truth states. Include issued, non-issued, unknown, lost, withdrawn, not-for-loan and repeated items.

Record:
- ground-truth state
- KohaGuard decision
- input mode
- backend response time
- end-to-end task time
- device/browser
- scan success/failure

Report confusion matrix, accuracy, sensitivity, specificity, false-positive rate, false-negative rate and 95% confidence intervals.

A security-critical false negative is a non-issued item that is incorrectly authorized.

## Phase 2 — Comparative timing study
Compare:
- manual lookup in the Koha staff interface
- KohaGuard Type Mode
- KohaGuard Camera Mode

Measure time from presentation of the item to final decision. Choose statistical tests based on design and distribution; document assumptions rather than selecting tests post hoc for significance.

## Phase 3 — Field pilot
Deploy at a real library exit for a defined period. Record traffic volume, verification attempts, non-issued items intercepted, unknown identifiers, technical failures, overrides and peak-time throughput.

Do not label a blocked test event as a theft attempt unless independent evidence supports that classification.

## Phase 4 — Usability
Use a validated usability instrument (e.g., SUS where appropriate) plus task completion and short interviews with library/security staff.

## Research integrity
- Do not fabricate scan events to increase sample size.
- Separate demo/test records from field data.
- Predefine outcome labels.
- Report exclusions and failed scans.
- Do not claim theft reduction without before/after or otherwise valid theft/loss outcome data.
- Obtain institutional/ethics approval where required.
