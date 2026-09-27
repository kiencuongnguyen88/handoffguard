# HandoffGuard — Post-Build BBR R004

State: FULL_BASELINE_PROVEN / REDUCED_CHALLENGERS_REVIEWED

## Baseline evidence before BBR

The full baseline is no longer an architecture hypothesis. Local evidence proves:

- 14 tests PASS;
- deterministic demo sequence matches all 7 expected states;
- unrelated repository change preserves `PASS_RESUME_BINDING`;
- material source change returns `BLOCKED_STALE_HANDOFF` before stale execution;
- successor handoff preserves accepted scope/decisions/authority and parent lineage;
- unchanged acceptance exposes the regression as `FAIL_EXECUTABLE_PROOF`;
- repaired rerun returns `PASS_EXECUTABLE_PROOF`;
- final current-byte adjudication returns `PASS_CONTINUATION`;
- public-safe privacy scan PASS;
- prepared Bob workbench is genuinely in `BLOCKED_STALE_HANDOFF` state awaiting real Bob execution.

## Candidate normalization

### A — FULL_BASELINE

Keep the complete capability defined in `FULL_BASELINE_SCOPE_R003.md`.

### B — HASH_ONLY_RESUME_GATE

Keep only material path hashes + stale detection. Remove accepted-state payload, rebind lineage, executable acceptance binding and final adjudication.

### C — RESUME_PLUS_TEST_NO_SUCCESSOR_LINEAGE

Keep resume verification and executable acceptance, but remove explicit fresh-read/replan rebind and parent handoff lineage.

### D — ONE_COMMAND_UX_WRAPPER

Expose one convenience command while internally preserving the full handoff, verification, rebind, acceptance and adjudication records.

D is not a semantic replacement. It is a possible UX adapter over A.

## BBR comparison

| Material force | A Full | B Hash-only | C No-lineage | D Wrapper over Full |
|---|---|---|---|---|
| Preserve accepted state across handoff | PASS | FAIL | PARTIAL | PASS |
| Unrelated change does not force restart | PASS | PASS | PASS | PASS |
| Material drift blocks before stale execution | PASS | PASS | PASS | PASS |
| Exact changed paths for targeted fresh-read | PASS | PASS | PASS | PASS |
| Explicit fresh-read/re-plan successor | PASS | FAIL | FAIL | PASS |
| Parent lineage / transition continuity | PASS | FAIL | FAIL | PASS |
| Acceptance cannot run without verified resume | PASS | FAIL | PASS | PASS |
| Executable failure honesty | PASS | FAIL | PASS | PASS |
| Final-current-byte freshness | PASS | FAIL | PASS | PASS |
| Unsupported success claim flagging | PASS | FAIL | PASS | PASS |
| Bob multi-step story | STRONG | WEAK | MEDIUM | STRONG |
| Current implementation proof | PROVEN | NOT_PROVEN_AS_REPLACEMENT | NOT_PROVEN_AS_REPLACEMENT | NOT_BUILT_YET |

## Verdict

```yaml
FULL_BASELINE:
  verdict: KEEP_INCUMBENT
  reason: proven whole-task capability; no challenger demonstrates material net advantage plus no material regression

HASH_ONLY_RESUME_GATE:
  verdict: REJECT_AS_REPLACEMENT
  reason: materially collapses the invention into a stale-hash detector and loses accepted-state continuity, replan lineage and end-to-end proof

RESUME_PLUS_TEST_NO_SUCCESSOR_LINEAGE:
  verdict: REJECT_AS_REPLACEMENT
  reason: loses the explicit causal bridge from stale detection through fresh-read/re-plan into a successor continuation state

ONE_COMMAND_UX_WRAPPER:
  verdict: MAY_ADD_AS_ADAPTER_NOT_REPLACEMENT
  reason: could reduce operator friction only if it preserves every underlying proof object and state transition; no need to replace the full baseline
```

## Decision

`KEEP_FULL_BASELINE`.

The next material move is not another reduction pass. It is real IBM Bob execution against the prepared full-baseline workbench, with task-session-summary screenshots captured immediately after each material task.
