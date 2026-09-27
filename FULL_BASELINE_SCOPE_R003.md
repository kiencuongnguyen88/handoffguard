# HandoffGuard — Full Baseline Scope R003

State: FULL_BASELINE_SELECTED / REDUCED_VARIANTS_ARE_CHALLENGERS

## Purpose

Build the full bounded HandoffGuard capability first. A reduced/partial/fast-path variant may replace it only after a BBR demonstrates material net advantage with no material regression across the whole current hackathon TaskBox.

## Full baseline capabilities

1. Durable handoff packet preserving accepted scope, accepted decisions, authority boundary, exact next move, material path hashes, acceptance command hash, optional Git HEAD, transition nonce and lineage.
2. Resume verification before execution.
3. Selective continuation: unrelated repository change does not force restart; material-path drift blocks resume.
4. Fail-closed states for handoff tampering, contract drift, acceptance-command drift and missing material source.
5. Explicit stale path report for targeted fresh-read.
6. Rebind after fresh-read/re-plan, preserving accepted state and parent lineage while allowing the bounded next move to update.
7. Executable acceptance only after PASS_RESUME_BINDING.
8. Acceptance receipts bound to exact handoff, verification receipt, contract, command and final material bytes.
9. Final adjudication returns PASS_CONTINUATION only when verified start + executable proof + current final bytes all agree.
10. Unsupported AI success claims are flagged when proof is absent/stale/failing.
11. Synthetic deterministic demo covering unrelated change, material drift, replan/rebind, failure, repair and final PASS.
12. Real IBM Bob workbench prepared in an intentionally stale/failing state so Bob performs material repository understanding, re-plan and repair rather than prose-only participation.
13. Bob task-session screenshot contract and public-safe evidence folder.
14. README, architecture, proof contract, failure model, demo script, submission draft and reproducibility scripts.
15. Package manifest, checksums and fresh-package readback before handoff/publication.

## Full baseline is not maximal product scope

This baseline intentionally excludes unrelated platform expansion:

- generic multi-agent orchestration;
- production deployment service;
- CI vendor integration;
- database/backend/authentication;
- private Diamond OS data;
- automatic public publishing;
- automatic Human authority decisions.

The baseline is "full" relative to the selected HandoffGuard hackathon problem, not relative to all possible future product features.

## Replacement rule

A reduced challenger must show all of:

- material net advantage in runway, reliability, judge legibility or Bob evidence;
- no loss of the selective-continuation mechanism;
- no loss of stale material-path fail-closed behavior;
- no loss of accepted-state preservation across handoff;
- no loss of executable acceptance and final-current-byte binding;
- no weaker Bob-as-core-component story;
- no weaker reproducibility or submission evidence.

If proof is incomplete or a material tradeoff remains, keep this full baseline.
