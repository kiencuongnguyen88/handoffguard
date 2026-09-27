# HandoffGuard Architecture

## Developer failure

AI coding work often crosses a chat, session, agent, laptop or time boundary. A checkpoint can correctly preserve accepted decisions while repository facts named by that checkpoint later become stale.

Two bad defaults are common:

- restart from zero and waste accepted work; or
- trust sender-time repository facts and execute a stale plan.

HandoffGuard separates these concerns.

```text
accepted continuation state         mutable repository facts
(scope/decisions/authority)         (material source bytes)
            |                                 |
            +------------ handoff ------------+
                              |
                         new agent/session
                              |
                       resume verification
                       /                 \
         material unchanged          material drift
         PASS_RESUME_BINDING         BLOCKED_STALE_HANDOFF
                 |                         |
            continue                fresh-read changed paths
                                         |
                                   bounded re-plan + rebind
                                         |
                                   PASS_RESUME_BINDING
                                         |
                                      execution
                                         |
                              unchanged acceptance command
                                         |
                                executable receipt
                                         |
                                   adjudication
                                         |
                                  PASS_CONTINUATION
```

## Data objects

### Handoff packet

Carries accepted state plus sender-time material bindings:

- workflow ID;
- accepted scope;
- accepted decisions;
- authority boundary;
- exact next move;
- material paths + SHA256;
- acceptance command + SHA256;
- optional Git state;
- transition nonce;
- parent handoff lineage;
- optional replan note hash;
- packet integrity SHA256.

### Resume verification receipt

Records whether the successor is allowed to begin:

- `PASS_RESUME_BINDING`;
- `BLOCKED_STALE_HANDOFF`;
- `BLOCKED_SOURCE_MISSING`;
- integrity/contract/command failures.

It explicitly reports changed material paths while preserving the accepted state copied from the handoff.

### Acceptance receipt

Can only be created after a passing resume verification. It records:

- exact acceptance command;
- exit code/stdout/stderr;
- material hashes before/after execution of the acceptance command;
- mutation-during-test detection;
- binding to handoff + verification receipt.

### Final adjudication

`PASS_CONTINUATION` requires:

1. handoff integrity;
2. PASS resume verification;
3. matching handoff/verification lineage;
4. unchanged contract/acceptance command;
5. green executable acceptance;
6. current material bytes still matching the final receipt.

## Non-goals

HandoffGuard does not choose what a developer should build, authorize public actions, replace CI, coordinate all parallel agents, or prove general correctness/security.
