# Failure Model

## F1 — stale sender-time source

Agent A leaves a valid checkpoint. A material source file changes before Agent B resumes. The old next move may now be wrong.

Expected: `BLOCKED_STALE_HANDOFF` before Agent B executes the stale plan.

## F2 — unrelated repository change

The repository HEAD changes because documentation or another unrelated file changes, while all declared material inputs remain byte-identical.

Expected: `PASS_RESUME_BINDING`; accepted work is not reopened merely because the repository changed somewhere else.

## F3 — handoff tampering

Packet content is changed without recomputing the integrity field.

Expected: `INCONCLUSIVE_HANDOFF_INTEGRITY`.

## F4 — acceptance contract drift

The acceptance command or contract changes after sender-time binding.

Expected: fail closed; old evidence cannot silently certify the new contract.

## F5 — source disappears

A declared material path no longer exists.

Expected: `BLOCKED_SOURCE_MISSING`.

## F6 — stale final green proof

Acceptance ran green, then material source changed again.

Expected: `BLOCKED_STALE_FINAL_PROOF`.

## F7 — AI says PASS while proof rejects

Expected: `unsupported_success_claim: true`.
