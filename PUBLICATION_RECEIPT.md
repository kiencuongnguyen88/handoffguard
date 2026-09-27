# Public Publication Receipt

## Repository and GitHub Pages

```yaml
repository: https://github.com/kiencuongnguyen88/handoffguard
public_repo: true
github_pages: true
live_demo_url: https://kiencuongnguyen88.github.io/handoffguard/
LabLab_submission: false
```

## Full Verified Evidence Explorer deployment

```yaml
page_baseline: FULL_VERIFIED_EVIDENCE_EXPLORER
source_file: docs/index.html
source_commit: a8e19242585da78bd9e6a047515d9e7942a5f5b2
source_blob: a674f127f030e618981b5177da92cfde941eb284
evidence_pin: 00f6778fca34dca5d8e6bcafa209ea4dde6adb53
pages_workflow_run_id: 36318548687
pages_artifact_id: 10931497680
pages_artifact_SHA256: 090c5692a1d96f187615cca93ec95ec2ea0180831defbd18790d4b12354cef71
built_index_SHA256: bedcf2cc32bfad6826f100acfef96fa1631ae3b5828869522e11b04af490c6e8
pages_build: PASS
pages_deploy: PASS
environment_url: https://kiencuongnguyen88.github.io/handoffguard/
```

The page implements the full judge-facing evidence surface: problem framing, preserve-vs-reverify invariant, pinned seven-state verified replay, accepted-state and material-hash inspectors, three IBM Bob session screenshots, raw evidence drill-down, fail-closed evidence loading, and 1920x1080-oriented presentation mode.

Static readback after the repository mutation passed JavaScript syntax compilation, all referenced DOM IDs were present, the exact evidence commit was pinned, no external framework was introduced, and GitHub Pages built and deployed the exact source commit successfully.

The current tool surface could not independently execute the final public page in a normal external browser. Human browser visual/runtime readback therefore remains a capability proof step; deployment success is not promoted into a claim that every client-side interaction has been visually exercised.
