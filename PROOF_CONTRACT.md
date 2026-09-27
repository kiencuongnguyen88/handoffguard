# Proof Contract

## Claim ceiling

HandoffGuard proves one bounded property:

> A successor coding session began from a verified handoff state, material drift was handled explicitly when present, and the final claimed continuation is backed by executable acceptance whose covered material bytes are still current.

It does **not** prove general software correctness, production safety, security or fitness for every workflow.

## Required states

### Resume

- `PASS_RESUME_BINDING`
- `BLOCKED_STALE_HANDOFF`
- `BLOCKED_SOURCE_MISSING`
- `BLOCKED_STALE_HANDOFF_CONTRACT`
- `BLOCKED_ACCEPTANCE_COMMAND_DRIFT`
- `INCONCLUSIVE_HANDOFF_INTEGRITY`

### Acceptance

- `PASS_EXECUTABLE_PROOF`
- `FAIL_EXECUTABLE_PROOF`
- `INCONCLUSIVE_SOURCE_MISSING`
- `INCONCLUSIVE_MUTATED_DURING_ACCEPTANCE`

### Final

- `PASS_CONTINUATION`
- `BLOCKED_NO_VALID_RESUME_BINDING`
- `BLOCKED_STALE_FINAL_PROOF`
- lineage/integrity mismatch states
- `FAIL_EXECUTABLE_PROOF`

## Fail-closed rules

- AI prose never creates PASS.
- A stale material path blocks resume before execution.
- An unrelated file change alone does not invalidate accepted state.
- Rebind requires an earlier `BLOCKED_STALE_HANDOFF` plus a non-empty replan note.
- Acceptance cannot run without a `PASS_RESUME_BINDING` receipt.
- Final PASS expires if material bytes change after the green acceptance receipt.
