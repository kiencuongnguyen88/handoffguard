# HandoffGuard

**Resume AI coding work only from a verified repository state.**

HandoffGuard is a small fail-closed developer workflow for AI coding sessions that cross a chat/session/agent boundary.

A good checkpoint should preserve accepted work. But it should not freeze mutable repository facts forever. HandoffGuard separates those two things:

```text
accepted decisions survive the handoff
+
material source facts are verified again before resume
```

If an unrelated file changed, the next agent can continue. If a declared material input changed, HandoffGuard blocks stale execution, identifies the changed path, requires fresh-read + bounded re-plan, preserves accepted state, and then lets the successor continue from the repaired current reality.

## Why this matters

The dangerous failure is not only "an agent forgot context." It is:

1. Agent A plans against repository state A.
2. Agent A leaves a useful checkpoint.
3. The repo changes to A'.
4. Agent B receives the checkpoint and blindly runs the old next move.

Restarting everything wastes accepted work. Trusting everything risks stale execution.

HandoffGuard selects the middle path: **preserve accepted state, re-verify mutable facts.**

## 90-second local demo

Requires Python 3; Git is optional.

```bash
python demo.py
```

Expected sequence:

```text
PASS_RESUME_BINDING
→ PASS_RESUME_BINDING          # unrelated repository change: continue
→ BLOCKED_STALE_HANDOFF        # material source drift: stop before stale execution
→ PASS_RESUME_BINDING          # fresh-read/re-plan/rebind
→ FAIL_EXECUTABLE_PROOF        # unchanged acceptance exposes current regression
→ PASS_EXECUTABLE_PROOF        # bounded repair + unchanged rerun
→ PASS_CONTINUATION            # final current bytes still match green proof
```

This sequence is written to `evidence/demo_timeline.json`.

## CLI workflow

### 1. Create sender handoff

```bash
python handoffguard.py create \
  --contract contracts/demo.json \
  --output evidence/handoff.json
```

### 2. Verify before another agent resumes

```bash
python handoffguard.py verify \
  --contract contracts/demo.json \
  --handoff evidence/handoff.json \
  --output evidence/resume_verification.json
```

If material source changed, the result is `BLOCKED_STALE_HANDOFF` with exact changed paths.

### 3. After fresh-read + bounded re-plan, create a successor handoff

```bash
python handoffguard.py rebind \
  --contract contracts/demo.json \
  --handoff evidence/handoff.json \
  --verification evidence/resume_verification.json \
  --replan replan.md \
  --output evidence/handoff_successor.json
```

The successor preserves accepted scope/decisions/authority boundary and records parent lineage + the replan-note hash.

### 4. Run unchanged acceptance after a verified resume start

```bash
python handoffguard.py run \
  --contract contracts/demo.json \
  --handoff evidence/handoff_successor.json \
  --verification evidence/resume_successor.json \
  --receipt evidence/acceptance.json
```

### 5. Adjudicate the final claim

```bash
python handoffguard.py adjudicate \
  --contract contracts/demo.json \
  --handoff evidence/handoff_successor.json \
  --verification evidence/resume_successor.json \
  --receipt evidence/acceptance.json \
  --claim fixtures/agent_claim.json \
  --output evidence/final_adjudication.json
```

Only a consistent verified start + green executable acceptance + current final material bytes returns `PASS_CONTINUATION`.

## Full baseline, not a reduced probe

The hackathon build uses `FULL_BASELINE_SCOPE_R003.md` as its root. A reduced variant is not allowed to replace it merely because it is faster or shorter. `REDUCED_VARIANT_ADMISSION_GATE_R001.md` requires material net advantage and no material regression first.

## IBM Bob 2.0 role

IBM Bob is intended to perform the material development workflow, not generic research:

1. **Plan/repository understanding** — understand sender handoff, current source and the continuation boundary.
2. **Agent execution** — run stale-handoff verification, fresh-read changed source, produce bounded replan/rebind, expose the unchanged failing acceptance, repair the current code and rerun proof.
3. **Review** — inspect the final diff, lineage and executable evidence; check that README claims stay inside proof.

`bob_workbench/` is already staged in a real stale-handoff + failing-code state. See `BOB_TASKS.md`.

After each material Bob task, save the Bob task-session-summary screenshot into `bob_sessions/`.

Bob session screenshots prove Bob usage; they do not replace executable evidence.

## Tests

```bash
python -m unittest discover -s tests -v
```

Coverage includes fresh handoff, unrelated repo change, material drift, missing source, tampering, contract drift, rebind lineage, acceptance gating, failed execution, final stale proof and unsupported AI success claims.

## Privacy

All data/code in this repository is synthetic and public-safe. No P1/private CRM, credentials, client data or private Diamond OS database is included.

## What HandoffGuard is not

It is not a generic multi-agent orchestration platform, release system, code-review product, CI replacement or security guarantee. It proves a bounded continuation property across AI coding handoffs.
