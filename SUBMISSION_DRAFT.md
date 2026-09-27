# Submission Draft — HandoffGuard

## One-line description

Resume AI coding work only from a verified repository state.

## Short description

HandoffGuard preserves accepted decisions across AI coding sessions while re-verifying mutable source before resume. Unrelated repo changes do not force a restart; material drift blocks stale execution, triggers targeted fresh-read/re-plan, and requires executable proof before PASS.

## Problem

AI coding work increasingly spans multiple sessions and agents. A checkpoint may still contain valid accepted decisions even after files in the repository change. Existing approaches tend to either restart from zero or let the successor trust stale sender-time facts. Both create waste or risk.

## Solution

HandoffGuard binds a sender handoff to accepted scope/decisions, the exact next move, material source hashes, the acceptance command and lineage. A successor verifies the handoff before execution. Unrelated changes can continue; changed material paths fail closed and identify what must be fresh-read. After bounded re-plan/rebind, executable acceptance and final-current-byte adjudication determine whether the continuation can be called PASS.

## IBM Bob usage

IBM Bob is the material coding environment: Plan mode understands the sender handoff and current repo, Agent mode performs stale detection, targeted fresh-read/re-plan, the real repair and unchanged test rerun, and review checks the final diff/evidence. Task-session-summary screenshots are stored in `bob_sessions/`.

## Demonstrated states

```text
PASS_RESUME_BINDING
→ PASS_RESUME_BINDING (unrelated change)
→ BLOCKED_STALE_HANDOFF (material drift)
→ PASS_RESUME_BINDING (fresh-read/re-plan/rebind)
→ FAIL_EXECUTABLE_PROOF
→ PASS_EXECUTABLE_PROOF
→ PASS_CONTINUATION
```

## Privacy

The project uses only synthetic public-safe code and fixtures. It contains no client data, credentials, personal information, private CRM data or private Diamond OS databases.

## Claim boundary

HandoffGuard does not claim general correctness, production security or autonomous authority. It proves a bounded continuation property from verified handoff start to current executable evidence.
