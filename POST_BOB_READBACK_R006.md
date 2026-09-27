# HandoffGuard Post-Bob Fresh Readback — R006

## Verdict

`PASS_POST_BOB_PUBLICATION_CANDIDATE`

## Independent readback

The uploaded post-Bob ZIP was fresh-unzipped and checked independently of Bob's prose report.

Observed Bob evidence chain:

```text
BLOCKED_STALE_HANDOFF
→ PASS_RESUME_BINDING
→ FAIL_EXECUTABLE_PROOF
→ PASS_EXECUTABLE_PROOF
→ PASS_CONTINUATION
```

Current `bob_workbench/src/calc.py` SHA256 matches the post-repair receipt. The unchanged workbench test SHA256 also matches the receipt. The current repair is exactly `return a + b`.

Independent rerun:

- 14/14 repository tests PASS.
- deterministic demo sequence matches exactly.
- selective continuation is proven.
- final demo state is `PASS_CONTINUATION`.
- privacy scan PASS with zero findings.

## Bob session evidence

Present:

- `bob_sessions/handoffguard_task01_plan_summary.png`
- `bob_sessions/handoffguard_task02_agent_summary.png`
- `bob_sessions/handoffguard_task03_review_summary.png`

Task 02's screenshot preserves the observed Bob Todo UI discrepancy (`10/11` with final report already present). Task 03 independently reviewed the executable receipts and current bytes and classified that as UI bookkeeping, not an execution failure.

## Repair applied to publication candidate

The uploaded ZIP still contained pre-Bob integrity ledgers and state text. Those ledgers incorrectly stated `real_Bob_execution: false` and did not include the new Bob artifacts. The publication candidate repairs only packaging/state metadata:

- updates current state to post-Bob reality;
- updates README Bob section from planned usage to observed usage;
- updates submission draft with evidence-backed Bob usage;
- includes this readback;
- removes Python cache files;
- regenerates `MANIFEST.json` and `SHA256SUMS.txt` from current bytes.

No product capability was reduced.

## Claim boundary at this readback checkpoint

```yaml
real_Bob_execution: true
Bob_session_screenshots: true
public_repo: false
publish: false
LabLab_submission: false
source_apply: false
DB_write: false
RLDB_writeback: false
```

The public-repository publication occurred later and is tracked by `CURRENT_STATE.md`.
