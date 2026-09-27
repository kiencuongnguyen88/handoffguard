# HandoffGuard Bob Workbench — Bounded Continuation Plan

## Top-Level Overview

**Goal:** Resume a stale-blocked AI coding handoff inside the synthetic
`bob_workbench/` scope, repair exactly one arithmetic regression, and end
with a `PASS_CONTINUATION` adjudication whose every claim is backed by
executable evidence.

**Scope:** Only `bob_workbench/src/calc.py` may be edited.
`bob_workbench/tests/test_calc.py` and `bob_workbench/contract.json` must
remain unchanged throughout.

**Approach:** Follow the HandoffGuard fail-closed workflow precisely:
verify → rebind → verify successor → run acceptance (expect FAIL) → repair
→ re-run acceptance (expect PASS) → adjudicate.

---

## Exact Continuation Problem (diagnosis)

### 1 — Accepted decisions that must survive

All three `accepted_decisions` from `handoff_A_sender.json` must pass
unchanged into the successor handoff via `rebind`:

- `"add(a, b) must perform arithmetic addition."`
- `"tests/test_calc.py remains an unchanged acceptance condition."`
- `"A new Bob session must verify mutable source before continuing the
  prior handoff."`

`rebind` copies `accepted_scope`, `accepted_decisions`, and
`authority_boundary` from the parent handoff, not from the contract,
so they are preserved automatically — but only if the parent handoff
passes its integrity check first.

### 2 — Which mutable source fact drifted

`handoff_A_current_stale_verify.json` records:

```
"changed_material_paths": ["src/calc.py"]
```

The sender-time SHA-256 for `src/calc.py` stored in `handoff_A_sender.json`
is `ba1a531f…`. The current on-disk file contains `return a - b` (a
subtraction) rather than the expected addition. The hash no longer matches,
which is the sole cause of `BLOCKED_STALE_HANDOFF`.

`tests/test_calc.py` is unchanged (`f7251404…` still matches).

### 3 — Why an unrelated repository change is not enough to restart

`verify_handoff` (handoffguard.py line 218–226) only checks the paths
listed in `contract["material_paths"]` — currently `src/calc.py` and
`tests/test_calc.py`. A change to any file outside that list produces no
`changed` entries, leaves `status = "PASS_RESUME_BINDING"`, and lets the
successor continue from the preserved accepted state without any re-plan.
HandoffGuard explicitly separates mutable repository facts (material paths)
from the rest of the working tree. An unrelated change is noise, not a
blocker.

### 4 — Why the sender handoff is blocked before execution

`run_acceptance` (handoffguard.py line 280) raises immediately if
`verification.get("status") != "PASS_RESUME_BINDING"`.
`handoff_A_current_stale_verify.json` has `"status": "BLOCKED_STALE_HANDOFF"`,
so attempting to run the acceptance command against the original sender
handoff is a hard error before any subprocess is spawned. The guard is
fail-closed: stale material input → no execution.

---

## Sub-Tasks

---

### Sub-Task 1 — Verify the sender handoff (confirm BLOCKED_STALE_HANDOFF)

**Status:** `[ ] pending`

**Intent**
Prove to the current session's audit trail that the sender handoff is
genuinely stale with respect to the current `src/calc.py`. The output
receipt is required as the `--verification` argument to `rebind`.
(The pre-staged `handoff_A_current_stale_verify.json` already records
this result, but the task workflow requires running the command fresh so
the receipt is produced by this Bob session.)

**Expected Outcomes**
- `bob_workbench/evidence/bob_verify_sender.json` is written.
- `status` = `BLOCKED_STALE_HANDOFF`.
- `changed_material_paths` = `["src/calc.py"]`.
- `preserved_accepted_decisions` and `preserved_accepted_scope` copied
  from the sender handoff.

**Todo List**
1. Run:
   ```
   python handoffguard.py verify \
     --contract bob_workbench/contract.json \
     --handoff   bob_workbench/evidence/handoff_A_sender.json \
     --output    bob_workbench/evidence/bob_verify_sender.json
   ```
2. Confirm exit code is 3 (non-zero = not accepted).
3. Confirm `changed_material_paths` contains exactly `src/calc.py`.

**Relevant Context**
- `verify_handoff` in `handoffguard.py:196`
- `handoff_A_sender.json` → `material_hashes.src/calc.py` =
  `ba1a531f…` (sender-time hash)
- Current `src/calc.py` body: `return a - b`

---

### Sub-Task 2 — Fresh-read changed material and write bounded replan note

**Status:** `[ ] pending`

**Intent**
Read the current `src/calc.py` (the changed material path) and the
unchanged `tests/test_calc.py`. Produce a concise replan note that
identifies the regression and the minimum repair, while explicitly
preserving the accepted scope and all three accepted decisions.
This note is a mandatory input to `rebind` (a non-empty file is enforced
by `create_handoff` at line 167).

**Expected Outcomes**
- `bob_workbench/evidence/bob_replan.md` is written, non-empty.
- Note records: observed regression (`return a - b`), required repair
  (`return a + b`), that `tests/test_calc.py` is unchanged and remains
  the acceptance condition, and that accepted decisions are preserved.

**Todo List**
1. Read `bob_workbench/src/calc.py` — confirm `return a - b`.
2. Read `bob_workbench/tests/test_calc.py` — confirm unchanged test
   (`add(7,5)==12`, `add(-2,2)==0`).
3. Write `bob_workbench/evidence/bob_replan.md` with:
   - Observed drift: `src/calc.py` now contains `return a - b`.
   - Required repair: change body to `return a + b`.
   - Accepted decisions and scope preserved verbatim.
   - Authority boundary re-stated (no test weakening, no scope broadening).

**Relevant Context**
- `bob_workbench/src/calc.py` (current: subtraction regression)
- `bob_workbench/tests/test_calc.py` (unchanged acceptance test)
- `contract.json` accepted_decisions and accepted_scope

---

### Sub-Task 3 — Create the successor handoff (rebind)

**Status:** `[ ] pending`

**Intent**
Produce a new handoff packet (`handoff_B_bob.json`) that (a) carries the
parent's accepted state, (b) records the replan note hash, (c) re-hashes
the current material paths, and (d) stamps lineage to the sender handoff.
This is the gating step: `rebind` refuses to run unless the verification
receipt status is exactly `BLOCKED_STALE_HANDOFF`.

**Expected Outcomes**
- `bob_workbench/evidence/handoff_B_bob.json` is written.
- `parent_handoff_sha256` = `655ab893…` (sender handoff SHA).
- `accepted_decisions` and `accepted_scope` are identical to the parent.
- `material_hashes.src/calc.py` reflects the current (drifted) hash.
- `replan` field is non-null and references `bob_replan.md`.

**Todo List**
1. Run:
   ```
   python handoffguard.py rebind \
     --contract     bob_workbench/contract.json \
     --handoff      bob_workbench/evidence/handoff_A_sender.json \
     --verification bob_workbench/evidence/bob_verify_sender.json \
     --replan       bob_workbench/evidence/bob_replan.md \
     --output       bob_workbench/evidence/handoff_B_bob.json \
     --next-move    "Repair only the current arithmetic regression, then rerun unchanged acceptance."
   ```
2. Confirm `parent_handoff_sha256` links to sender.
3. Confirm accepted state fields are preserved.

**Relevant Context**
- `rebind_handoff` in `handoffguard.py:256`
- `create_handoff` in `handoffguard.py:142` (called internally by rebind)
- Verification receipt must carry `"status": "BLOCKED_STALE_HANDOFF"` — enforced at line 267

---

### Sub-Task 4 — Verify the successor handoff (confirm PASS_RESUME_BINDING)

**Status:** `[ ] pending`

**Intent**
The successor handoff was created against the current (drifted) bytes of
`src/calc.py`, so its stored `material_hashes` now match the on-disk file.
Verifying it must return `PASS_RESUME_BINDING`, which is the mandatory
gate before `run_acceptance` can proceed.

**Expected Outcomes**
- `bob_workbench/evidence/bob_verify_successor.json` is written.
- `status` = `PASS_RESUME_BINDING`.
- `accepted` = `true`.
- Exit code 0.

**Todo List**
1. Run:
   ```
   python handoffguard.py verify \
     --contract bob_workbench/contract.json \
     --handoff   bob_workbench/evidence/handoff_B_bob.json \
     --output    bob_workbench/evidence/bob_verify_successor.json
   ```
2. Confirm `status` = `PASS_RESUME_BINDING`.
3. Confirm `changed_material_paths` = `[]`.

**Relevant Context**
- `verify_handoff` in `handoffguard.py:196`
- `run_acceptance` line 280: hard-raises if status ≠ `PASS_RESUME_BINDING`

---

### Sub-Task 5 — Run unchanged acceptance BEFORE repair (expect FAIL_EXECUTABLE_PROOF)

**Status:** `[ ] pending`

**Intent**
Run the acceptance command against the unrepaired `src/calc.py` to
produce a `FAIL_EXECUTABLE_PROOF` receipt. This is the "expose the
regression" step: it proves the regression is real and current, not
hypothetical. The receipt is not used in final adjudication (the
post-repair receipt is), but it is required evidence that HandoffGuard
exposes existing failures honestly.

**Expected Outcomes**
- `bob_workbench/evidence/bob_pre_repair_acceptance.json` is written.
- `status` = `FAIL_EXECUTABLE_PROOF`.
- `exit_code` ≠ 0 (unittest fails because `add(7,5)` returns 2, not 12).
- `stdout` / `stderr` contain the AssertionError trace.

**Todo List**
1. Run:
   ```
   python handoffguard.py run \
     --contract     bob_workbench/contract.json \
     --handoff      bob_workbench/evidence/handoff_B_bob.json \
     --verification bob_workbench/evidence/bob_verify_successor.json \
     --receipt      bob_workbench/evidence/bob_pre_repair_acceptance.json
   ```
2. Confirm `status` = `FAIL_EXECUTABLE_PROOF`.
3. Record that `tests/test_calc.py` was not modified.

**Relevant Context**
- `run_acceptance` in `handoffguard.py:271`
- `add(7,5)` with `return a - b` returns `2`; test expects `12`

---

### Sub-Task 6 — Repair only src/calc.py (bounded single-line fix)

**Status:** `[ ] pending`

**Intent**
Change the body of `add` from `return a - b` to `return a + b`.
This is the only edit permitted by the authority boundary and the only
change required by the acceptance test.

**Expected Outcomes**
- `bob_workbench/src/calc.py` contains `return a + b`.
- No other file is modified.

**Todo List**
1. Edit `bob_workbench/src/calc.py`: change `return a - b` → `return a + b`.
2. Verify no other file was touched.
3. Do not edit `tests/test_calc.py` or `contract.json`.

**Relevant Context**
- `bob_workbench/src/calc.py` line 3 (current: `return a - b`)
- Authority boundary: "Do not weaken or delete the acceptance test."

---

### Sub-Task 7 — Rerun unchanged acceptance AFTER repair (expect PASS_EXECUTABLE_PROOF)

**Status:** `[ ] pending`

**Intent**
Run the same unchanged acceptance command against the repaired source.
The resulting receipt is the executable proof that the adjudicator requires.
Same `--handoff` and `--verification` arguments as Sub-Task 5; only the
`--receipt` output path differs.

**Expected Outcomes**
- `bob_workbench/evidence/bob_post_repair_acceptance.json` is written.
- `status` = `PASS_EXECUTABLE_PROOF`.
- `exit_code` = 0.
- `material_hashes_before` = `material_hashes_after` (source unchanged
  during the test run).

**Todo List**
1. Run:
   ```
   python handoffguard.py run \
     --contract     bob_workbench/contract.json \
     --handoff      bob_workbench/evidence/handoff_B_bob.json \
     --verification bob_workbench/evidence/bob_verify_successor.json \
     --receipt      bob_workbench/evidence/bob_post_repair_acceptance.json
   ```
2. Confirm `status` = `PASS_EXECUTABLE_PROOF`.
3. Confirm `exit_code` = 0.

**Relevant Context**
- `run_acceptance` in `handoffguard.py:271`
- `adjudicate` at line 376 requires `receipt.status == "PASS_EXECUTABLE_PROOF"`

---

### Sub-Task 8 — Final adjudication (expect PASS_CONTINUATION)

**Status:** `[ ] pending`

**Intent**
Adjudicate the full chain: handoff integrity → PASS resume verification →
lineage consistency → unchanged contract/command → green executable
acceptance → current final bytes still match the post-repair receipt.
All six conditions must hold simultaneously for `PASS_CONTINUATION`.

**Expected Outcomes**
- `bob_workbench/evidence/bob_final_adjudication.json` is written.
- `status` = `PASS_CONTINUATION`.
- `accepted` = `true`.
- `unsupported_success_claim` = `false` (if claim file is present).

**Todo List**
1. Run:
   ```
   python handoffguard.py adjudicate \
     --contract     bob_workbench/contract.json \
     --handoff      bob_workbench/evidence/handoff_B_bob.json \
     --verification bob_workbench/evidence/bob_verify_successor.json \
     --receipt      bob_workbench/evidence/bob_post_repair_acceptance.json \
     --claim        fixtures/agent_claim.json \
     --output       bob_workbench/evidence/bob_final_adjudication.json
   ```
2. Confirm `status` = `PASS_CONTINUATION`.
3. Confirm `accepted` = `true`.
4. Run product tests to confirm no regression introduced in HandoffGuard itself:
   ```
   python -m unittest discover -s tests -v
   python demo.py
   ```

**Relevant Context**
- `adjudicate` in `handoffguard.py:347`
- Six checks applied in sequence at lines 358–386
- Final check: `current_hashes == receipt.material_hashes_after` — so
  `src/calc.py` must not be touched after Sub-Task 7

---

## File Inventory

| File | Role | Permitted change? |
|---|---|---|
| `bob_workbench/contract.json` | contract | No |
| `bob_workbench/src/calc.py` | material source — regression lives here | Yes (Sub-Task 6 only) |
| `bob_workbench/tests/test_calc.py` | material source — acceptance test | No |
| `bob_workbench/evidence/handoff_A_sender.json` | sender handoff (read-only input) | No |
| `bob_workbench/evidence/handoff_A_current_stale_verify.json` | pre-staged stale verification (reference) | No |
| `bob_workbench/evidence/bob_verify_sender.json` | NEW — stale verification receipt | Created in Sub-Task 1 |
| `bob_workbench/evidence/bob_replan.md` | NEW — replan note | Created in Sub-Task 2 |
| `bob_workbench/evidence/handoff_B_bob.json` | NEW — successor handoff | Created in Sub-Task 3 |
| `bob_workbench/evidence/bob_verify_successor.json` | NEW — PASS verification receipt | Created in Sub-Task 4 |
| `bob_workbench/evidence/bob_pre_repair_acceptance.json` | NEW — FAIL proof receipt | Created in Sub-Task 5 |
| `bob_workbench/evidence/bob_post_repair_acceptance.json` | NEW — PASS proof receipt | Created in Sub-Task 7 |
| `bob_workbench/evidence/bob_final_adjudication.json` | NEW — final PASS_CONTINUATION | Created in Sub-Task 8 |
