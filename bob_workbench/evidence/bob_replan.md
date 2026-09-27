# Bounded Re-Plan Note — HandoffGuard Bob Workbench Continuation

## Observed Drift

`src/calc.py` currently contains:

```python
def add(a, b):
    # Deliberate out-of-band regression after Agent A created the handoff.
    return a - b
```

This does not match the sender-time hash (`ba1a531f…`) recorded in
`handoff_A_sender.json`. The acceptance test expects `add(7,5)==12` and
`add(-2,2)==0`, but with `return a - b` those calls return `2` and `-4`
respectively. The hash mismatch triggered `BLOCKED_STALE_HANDOFF`.

`tests/test_calc.py` is unchanged — its on-disk SHA-256 still matches the
sender-recorded hash `f7251404…`.

## Required Repair

Change the body of `add` from `return a - b` to `return a + b`.

This is the smallest valid repair: a single arithmetic operator change that
restores the function's contract without altering any other line, file, or
test.

## Accepted Decisions (preserved verbatim)

1. `add(a, b) must perform arithmetic addition.`
2. `tests/test_calc.py remains an unchanged acceptance condition.`
3. `A new Bob session must verify mutable source before continuing the prior handoff.`

## Accepted Scope (preserved verbatim)

> Repair the bounded calculator regression without reopening the accepted
> addition behavior or weakening its test.

## Authority Boundary (re-stated)

- Do not weaken or delete the acceptance test.
- Do not broaden beyond this synthetic workbench.
- Do not claim PASS without executable acceptance evidence.
