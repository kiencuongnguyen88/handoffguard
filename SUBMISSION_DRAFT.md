# Submission Draft — HandoffGuard

## Submission Title

HandoffGuard

## Short Description

HandoffGuard verifies repository state before one AI coding agent resumes another agent's checkpoint, blocking stale handoffs while preserving accepted work and requiring fresh executable evidence before continuation.

## Long Description

AI coding work increasingly spans multiple sessions and agents. A checkpoint may still contain valid accepted decisions even after files in the repository change. Continuing blindly can execute a once-correct plan against stale source, while restarting everything throws away useful accepted work.

HandoffGuard separates those two concerns. A sender handoff records accepted scope, accepted decisions, authority boundaries, the exact next move, declared material file hashes, acceptance-command binding, and lineage. When a later agent or session resumes, HandoffGuard verifies the current repository before execution. Unrelated repository changes do not force a restart. If a declared material input changed, HandoffGuard fails closed with `BLOCKED_STALE_HANDOFF`, reports the exact changed path, requires a targeted fresh read and bounded re-plan, and creates a successor handoff that preserves accepted state while rebinding current facts.

The successor must then pass `PASS_RESUME_BINDING` before the unchanged acceptance command can run. A failing acceptance stays a real failure; an agent cannot turn it into success by prose. After repair, HandoffGuard reruns the same acceptance and binds the result to current material hashes. Final adjudication returns `PASS_CONTINUATION` only when the verified handoff, executable receipt, and live final source bytes are consistent.

The target users are developers and teams using AI coding agents across interrupted sessions, handoffs, or multiple agents. The prototype is intentionally bounded: it demonstrates safe continuation without claiming general correctness, production security, or autonomous authority.

## IBM Bob Usage Statement

IBM Bob IDE was used as the material coding environment for HandoffGuard in three separate tasks. In Task 01, Bob Plan mode read the sender handoff, proof contract, implementation, stale verification evidence, current source, and unchanged acceptance test. It identified `src/calc.py` as the material drift, preserved Agent A's accepted decisions, explained why unrelated repository changes should not restart accepted work, and produced a bounded continuation plan.

In Task 02, Bob Agent mode executed that plan. It verified the original sender handoff and obtained `BLOCKED_STALE_HANDOFF`, fresh-read the changed material source, wrote `bob_replan.md`, created a successor handoff with parent lineage, and verified `PASS_RESUME_BINDING`. Bob then ran the unchanged acceptance before repair and obtained `FAIL_EXECUTABLE_PROOF`. It made the smallest proven implementation repair in `bob_workbench/src/calc.py`, changing `return a - b` to `return a + b`, without modifying `bob_workbench/tests/test_calc.py` or `bob_workbench/contract.json`. The same acceptance command then returned `PASS_EXECUTABLE_PROOF`, and final adjudication returned `PASS_CONTINUATION`. Bob also ran the full repository suite: 14 tests passed, and the deterministic demo sequence matched exactly.

In Task 03, a separate Bob review task independently checked the handoff lineage, unchanged test and contract hashes, pre/post acceptance receipts, current final source bytes, unsupported-success handling, screenshot evidence, and privacy boundary. It returned `PASS_REVIEW`. Task-session-summary screenshots for all three Bob tasks are stored in `bob_sessions/`, while the executable evidence chain is stored in `bob_workbench/evidence/`.

## Public links

- Repository: https://github.com/kiencuongnguyen88/handoffguard
- Live demo: https://kiencuongnguyen88.github.io/handoffguard/

## Categories

- Developer Tools
- Coding excellence (if multiple categories are allowed)
- Coding (if multiple categories are allowed)

## Technologies Used

- IBM
- GitHub

## Demonstrated States

```text
BLOCKED_STALE_HANDOFF
→ PASS_RESUME_BINDING
→ FAIL_EXECUTABLE_PROOF
→ PASS_EXECUTABLE_PROOF
→ PASS_CONTINUATION
```

The broader deterministic demo also proves that unrelated repository changes do not invalidate accepted work.

## Privacy

The project uses only synthetic public-safe code and fixtures. It contains no client data, credentials, personal information, private CRM data or private Diamond OS databases.

## Claim Boundary

HandoffGuard does not claim general correctness, production security or autonomous authority. It proves a bounded continuation property from verified handoff start to current executable evidence.
