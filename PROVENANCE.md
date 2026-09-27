# Provenance

## Public-safe derivation

HandoffGuard is a new hackathon prototype derived from operating patterns already exercised in the builder's public-safe AI workflow work:

- checkpoint continuation;
- accepted-state preservation;
- fresh readback of mutable facts;
- exact next move;
- fail-closed proof/adjudication;
- lineage and execution receipts.

It reuses the locally built ProofFresh hashing/receipt concepts as implementation lineage, but changes the primary problem from post-test proof freshness to durable cross-session coding handoff integrity.

No private Diamond OS databases, private CRM/person records, credentials, tokens or client data are copied into this repository.

## Competition distinction

The intended framing is not generic evidence gating, parallel-agent lease coordination, release verification, plan-scope enforcement or stale-test detection. The bounded problem is durable resume after an agent/session handoff: preserve accepted state while re-verifying mutable source before continuing.
