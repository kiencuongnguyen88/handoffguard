# IBM Bob 2.0 — Material Task Plan

Keep the tasks separate and capture a task-session-summary screenshot immediately after each material Bob task.

## Task 01 — Plan / understand the handoff boundary

**Mode:** Plan

```text
You are working on the HandoffGuard IBM Bob 2.0 hackathon repository.

Read README.md, ARCHITECTURE.md, PROOF_CONTRACT.md, handoffguard.py, bob_workbench/contract.json, bob_workbench/evidence/handoff_A_sender.json, bob_workbench/evidence/handoff_A_current_stale_verify.json, bob_workbench/src/calc.py and bob_workbench/tests/test_calc.py.

Do not redesign the product and do not weaken the test.

Explain the exact continuation problem:
- which accepted decisions from Agent A should survive;
- which mutable source fact drifted after the handoff;
- why an unrelated repository change would not be enough to restart the task;
- why the current sender handoff is blocked before execution.

Return a bounded execution plan that preserves accepted state, fresh-reads only the changed material source, creates a successor handoff after re-plan, runs the unchanged acceptance command, repairs only the proven regression, reruns acceptance and finishes with adjudication.
```

Save summary screenshot:

`bob_sessions/handoffguard_task01_plan_summary.png`

## Task 02 — Agent / resume, re-plan, repair, prove

**Mode:** Agent

```text
Execute the prepared HandoffGuard Bob workbench exactly inside the bounded synthetic scope.

1. Verify the sender handoff:
python handoffguard.py verify --contract bob_workbench/contract.json --handoff bob_workbench/evidence/handoff_A_sender.json --output bob_workbench/evidence/bob_verify_sender.json

Expected: BLOCKED_STALE_HANDOFF. Do not proceed from the stale next move if verification returns another non-PASS state; diagnose honestly.

2. Fresh-read only the changed material path reported by verification plus the unchanged acceptance test. Write a concise replan note to:
bob_workbench/evidence/bob_replan.md

The note must preserve accepted scope/decisions and identify the smallest current repair.

3. Create the successor handoff from the stale verification:
python handoffguard.py rebind --contract bob_workbench/contract.json --handoff bob_workbench/evidence/handoff_A_sender.json --verification bob_workbench/evidence/bob_verify_sender.json --replan bob_workbench/evidence/bob_replan.md --output bob_workbench/evidence/handoff_B_bob.json --next-move "Repair only the current arithmetic regression, then rerun unchanged acceptance."

4. Verify the successor handoff:
python handoffguard.py verify --contract bob_workbench/contract.json --handoff bob_workbench/evidence/handoff_B_bob.json --output bob_workbench/evidence/bob_verify_successor.json

Expected: PASS_RESUME_BINDING.

5. Before repair, run the unchanged acceptance command through HandoffGuard:
python handoffguard.py run --contract bob_workbench/contract.json --handoff bob_workbench/evidence/handoff_B_bob.json --verification bob_workbench/evidence/bob_verify_successor.json --receipt bob_workbench/evidence/bob_pre_repair_acceptance.json

Expected: FAIL_EXECUTABLE_PROOF.

6. Repair only bob_workbench/src/calc.py. Do not edit or weaken bob_workbench/tests/test_calc.py or bob_workbench/contract.json.

7. Rerun the exact same acceptance command via HandoffGuard:
python handoffguard.py run --contract bob_workbench/contract.json --handoff bob_workbench/evidence/handoff_B_bob.json --verification bob_workbench/evidence/bob_verify_successor.json --receipt bob_workbench/evidence/bob_post_repair_acceptance.json

Expected: PASS_EXECUTABLE_PROOF.

8. Final adjudication:
python handoffguard.py adjudicate --contract bob_workbench/contract.json --handoff bob_workbench/evidence/handoff_B_bob.json --verification bob_workbench/evidence/bob_verify_successor.json --receipt bob_workbench/evidence/bob_post_repair_acceptance.json --claim fixtures/agent_claim.json --output bob_workbench/evidence/bob_final_adjudication.json

Expected: PASS_CONTINUATION.

9. Run product verification:
python -m unittest discover -s tests -v
python demo.py

Report exact statuses and changed files. Do not convert your own prose into PASS evidence.
```

Save summary screenshot:

`bob_sessions/handoffguard_task02_agent_summary.png`

## Task 03 — Review / submission evidence audit

**Mode:** review-capable mode

```text
Review the HandoffGuard repository as a hackathon submission artifact.

Check:
- material drift blocks before stale execution;
- unrelated repository change does not reopen accepted work;
- rebind preserves accepted scope/decisions/authority and records parent lineage;
- acceptance cannot run without PASS_RESUME_BINDING;
- final PASS expires if material bytes change after green acceptance;
- Bob evidence screenshots are present for every material task;
- README/submission claims stay inside executable proof;
- no credential, personal data, client data or private Diamond OS source is present.

Do not add features. If a material defect exists, identify the exact file and smallest repair. Otherwise report no material defect found.
```

Save summary screenshot:

`bob_sessions/handoffguard_task03_review_summary.png`

## Evidence rule

Bob task summaries prove Bob was used. HandoffGuard behavior is accepted only through executable receipts/readback.
