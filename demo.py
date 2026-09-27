#!/usr/bin/env python3
"""Deterministic HandoffGuard demo: preserve accepted state, block stale material facts, recover, prove continuation."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from handoffguard import adjudicate, create_handoff, rebind_handoff, run_acceptance, verify_handoff


def emit(step, record):
    print(json.dumps({"step": step, **record}, sort_keys=True, ensure_ascii=False))


def git(root: Path, *args: str) -> None:
    if shutil.which("git") is None:
        return
    subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)


def main() -> int:
    out_root = Path(__file__).resolve().parent / "evidence"
    out_root.mkdir(exist_ok=True)
    timeline = []

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "src").mkdir(); (root / "tests").mkdir(); (root / "contracts").mkdir(); (root / "evidence").mkdir()
        (root / "src" / "__init__.py").write_text("", encoding="utf-8")
        (root / "src" / "calc.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
        (root / "tests" / "test_calc.py").write_text(
            "import unittest\nfrom src.calc import add\n\nclass T(unittest.TestCase):\n"
            "    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n\n"
            "if __name__ == '__main__':\n    unittest.main()\n", encoding="utf-8")
        contract = {
            "workflow_id": "handoffguard-live-demo-v1",
            "root": "..",
            "root_label": "synthetic-calculator",
            "accepted_scope": "Continue the bounded calculator maintenance task without reopening accepted behavior.",
            "accepted_decisions": [
                "add(a, b) must return arithmetic addition.",
                "The existing test remains unchanged.",
                "Accepted state may survive a handoff, but material source facts must be verified before resume."
            ],
            "next_move": "Continue the bounded maintenance task from current verified source.",
            "authority_boundary": ["No publish.", "No private data.", "PASS requires executable evidence."],
            "material_paths": ["src/calc.py", "tests/test_calc.py"],
            "acceptance_command": [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
        }
        cp = root / "contracts" / "demo.json"; cp.write_text(json.dumps(contract, indent=2), encoding="utf-8")

        git(root, "init", "-q"); git(root, "config", "user.email", "demo@example.invalid"); git(root, "config", "user.name", "HandoffGuard Demo")
        git(root, "add", "."); git(root, "commit", "-qm", "baseline")

        h1p = root / "evidence" / "handoff_A.json"
        create_handoff(cp, h1p)
        v1p = root / "evidence" / "verify_A.json"
        v1 = verify_handoff(cp, h1p, v1p); emit("01_initial_resume", v1); timeline.append(v1["status"])

        (root / "notes.md").write_text("unrelated documentation change\n", encoding="utf-8")
        git(root, "add", "notes.md"); git(root, "commit", "-qm", "unrelated docs")
        v2 = verify_handoff(cp, h1p); emit("02_unrelated_repo_change", v2); timeline.append(v2["status"])

        (root / "src" / "calc.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
        git(root, "add", "src/calc.py"); git(root, "commit", "-qm", "out-of-band regression")
        stale_vp = root / "evidence" / "verify_stale.json"
        stale = verify_handoff(cp, h1p, stale_vp); emit("03_material_drift", stale); timeline.append(stale["status"])

        replan = root / "replan.md"
        replan.write_text(
            "Fresh-read changed path: src/calc.py.\n"
            "Preserve accepted scope and tests.\n"
            "Updated next move: repair the arithmetic regression only, then rerun unchanged acceptance.\n",
            encoding="utf-8")
        h2p = root / "evidence" / "handoff_B.json"
        create2 = rebind_handoff(cp, h1p, stale_vp, replan, h2p,
                                 "Repair the current arithmetic regression only, then rerun unchanged acceptance.")
        emit("04_successor_handoff", {"status": "SUCCESSOR_HANDOFF_CREATED", "handoff_sha256": create2["handoff_sha256"],
                                      "parent_handoff_sha256": create2["parent_handoff_sha256"]})
        v2p = root / "evidence" / "verify_B.json"
        v3 = verify_handoff(cp, h2p, v2p); emit("05_rebound_resume", v3); timeline.append(v3["status"])

        fail_rp = root / "evidence" / "acceptance_before_repair.json"
        fail = run_acceptance(cp, h2p, v2p, fail_rp); emit("06_unchanged_acceptance_exposes_regression", fail); timeline.append(fail["status"])

        (root / "src" / "calc.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
        pass_rp = root / "evidence" / "acceptance_after_repair.json"
        passed = run_acceptance(cp, h2p, v2p, pass_rp); emit("07_repair_and_rerun", passed); timeline.append(passed["status"])

        claim = root / "claim.json"; claim.write_text('{"status":"PASS","claim":"continuation complete"}', encoding="utf-8")
        final = adjudicate(cp, h2p, v2p, pass_rp, claim, root / "evidence" / "final_adjudication.json")
        emit("08_final_adjudication", final); timeline.append(final["status"])

        export = {
            "expected_sequence": [
                "PASS_RESUME_BINDING", "PASS_RESUME_BINDING", "BLOCKED_STALE_HANDOFF",
                "PASS_RESUME_BINDING", "FAIL_EXECUTABLE_PROOF", "PASS_EXECUTABLE_PROOF", "PASS_CONTINUATION"
            ],
            "observed_sequence": timeline,
            "sequence_match": timeline == [
                "PASS_RESUME_BINDING", "PASS_RESUME_BINDING", "BLOCKED_STALE_HANDOFF",
                "PASS_RESUME_BINDING", "FAIL_EXECUTABLE_PROOF", "PASS_EXECUTABLE_PROOF", "PASS_CONTINUATION"
            ],
            "selective_continuation_proven": v2["status"] == "PASS_RESUME_BINDING" and stale["status"] == "BLOCKED_STALE_HANDOFF",
            "final_status": final["status"],
        }
        (out_root / "demo_timeline.json").write_text(json.dumps(export, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(export, indent=2))
        return 0 if export["sequence_match"] and final["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
