# HandoffGuard — 2–3 minute demo

## 0:00–0:20 — Problem

"AI coding work often crosses sessions. A checkpoint can preserve accepted decisions, while the repository facts inside that checkpoint become stale. Restarting wastes work; blindly resuming can execute the wrong plan."

## 0:20–0:40 — Sender handoff

Show `bob_workbench/evidence/handoff_A_sender.json` and explain that accepted scope/decisions + material path hashes are bound at handoff time.

## 0:40–1:00 — Selective continuation

Run `python demo.py` and point to the first two statuses:

- initial `PASS_RESUME_BINDING`;
- unrelated repo HEAD change still `PASS_RESUME_BINDING`.

Key line: **repo change does not automatically mean project-state reset.**

## 1:00–1:25 — Material drift

Show `BLOCKED_STALE_HANDOFF` and exact changed path `src/calc.py`.

Key line: **the agent stops before executing sender-time instructions against changed material source.**

## 1:25–1:50 — Bob fresh-read + re-plan

Show Bob Task 01/02 screenshot and successor handoff lineage. Accepted scope stays intact; only current next move/source binding changes after fresh-read.

## 1:50–2:15 — Executable honesty

Show unchanged acceptance first returning `FAIL_EXECUTABLE_PROOF`, Bob's bounded repair, then unchanged rerun returning `PASS_EXECUTABLE_PROOF`.

## 2:15–2:35 — Final adjudication

Show `PASS_CONTINUATION` and explain it requires verified resume start + green acceptance + final-current-byte match.

## 2:35–2:50 — Value

"HandoffGuard lets long-running AI coding work continue without restarting accepted work and without trusting stale repository facts."
