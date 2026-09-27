import json
import sys
import tempfile
import unittest
from pathlib import Path

from handoffguard import (
    adjudicate,
    create_handoff,
    load_json,
    rebind_handoff,
    run_acceptance,
    verify_handoff,
    write_json,
)


class HandoffGuardTests(unittest.TestCase):
    def make_repo(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        (root / "src").mkdir()
        (root / "tests").mkdir()
        (root / "contracts").mkdir()
        (root / "evidence").mkdir()
        (root / "src" / "__init__.py").write_text("", encoding="utf-8")
        (root / "src" / "calc.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
        (root / "tests" / "test_calc.py").write_text(
            "import unittest\nfrom src.calc import add\n\n"
            "class T(unittest.TestCase):\n"
            "    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n",
            encoding="utf-8",
        )
        contract = {
            "workflow_id": "t-workflow",
            "root": "..",
            "accepted_scope": "Continue bounded calculator maintenance.",
            "accepted_decisions": ["Keep add behavior.", "Do not weaken tests."],
            "next_move": "Continue exact maintenance task.",
            "authority_boundary": ["No publish.", "PASS requires executable evidence."],
            "material_paths": ["src/calc.py", "tests/test_calc.py"],
            "acceptance_command": [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        }
        cp = root / "contracts" / "demo.json"
        cp.write_text(json.dumps(contract, indent=2), encoding="utf-8")
        return td, root, cp

    def create_and_verify(self, root, cp):
        hp = root / "evidence" / "handoff.json"
        vp = root / "evidence" / "verify.json"
        handoff = create_handoff(cp, hp)
        verify = verify_handoff(cp, hp, vp)
        self.assertEqual(verify["status"], "PASS_RESUME_BINDING")
        return hp, vp, handoff, verify

    def test_fresh_handoff_passes(self):
        td, root, cp = self.make_repo(); self.addCleanup(td.cleanup)
        _, _, _, verify = self.create_and_verify(root, cp)
        self.assertTrue(verify["accepted"])

    def test_unrelated_file_change_does_not_restart_accepted_work(self):
        td, root, cp = self.make_repo(); self.addCleanup(td.cleanup)
        hp, _, _, _ = self.create_and_verify(root, cp)
        (root / "notes.md").write_text("unrelated change\n", encoding="utf-8")
        verify = verify_handoff(cp, hp)
        self.assertEqual(verify["status"], "PASS_RESUME_BINDING")

    def test_material_change_blocks_resume(self):
        td, root, cp = self.make_repo(); self.addCleanup(td.cleanup)
        hp, _, _, _ = self.create_and_verify(root, cp)
        (root / "src" / "calc.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
        verify = verify_handoff(cp, hp)
        self.assertEqual(verify["status"], "BLOCKED_STALE_HANDOFF")
        self.assertEqual(verify["changed_material_paths"], ["src/calc.py"])
        self.assertTrue(verify["replan_required"])

    def test_missing_material_path_blocks_resume(self):
        td, root, cp = self.make_repo(); self.addCleanup(td.cleanup)
        hp, _, _, _ = self.create_and_verify(root, cp)
        (root / "src" / "calc.py").unlink()
        verify = verify_handoff(cp, hp)
        self.assertEqual(verify["status"], "BLOCKED_SOURCE_MISSING")

    def test_tampered_handoff_is_inconclusive(self):
        td, root, cp = self.make_repo(); self.addCleanup(td.cleanup)
        hp, _, _, _ = self.create_and_verify(root, cp)
        data = load_json(hp)
        data["next_move"] = "tampered"
        write_json(hp, data)
        verify = verify_handoff(cp, hp)
        self.assertEqual(verify["status"], "INCONCLUSIVE_HANDOFF_INTEGRITY")

    def test_contract_change_blocks_old_handoff(self):
        td, root, cp = self.make_repo(); self.addCleanup(td.cleanup)
        hp, _, _, _ = self.create_and_verify(root, cp)
        contract = load_json(cp)
        contract["next_move"] = "different current contract"
        write_json(cp, contract)
        verify = verify_handoff(cp, hp)
        self.assertEqual(verify["status"], "BLOCKED_STALE_HANDOFF_CONTRACT")

    def test_rebind_requires_stale_verification(self):
        td, root, cp = self.make_repo(); self.addCleanup(td.cleanup)
        hp, vp, _, _ = self.create_and_verify(root, cp)
        rp = root / "replan.md"; rp.write_text("fresh-read complete\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            rebind_handoff(cp, hp, vp, rp, root / "evidence" / "successor.json")

    def test_rebind_preserves_accepted_state_and_lineage(self):
        td, root, cp = self.make_repo(); self.addCleanup(td.cleanup)
        hp, _, parent, _ = self.create_and_verify(root, cp)
        (root / "src" / "calc.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
        stale_vp = root / "evidence" / "stale_verify.json"
        stale = verify_handoff(cp, hp, stale_vp)
        self.assertEqual(stale["status"], "BLOCKED_STALE_HANDOFF")
        rp = root / "replan.md"; rp.write_text("Fresh-read src/calc.py; repair regression only.\n", encoding="utf-8")
        successor_path = root / "evidence" / "successor.json"
        successor = rebind_handoff(cp, hp, stale_vp, rp, successor_path, "Repair current regression, then rerun acceptance.")
        self.assertEqual(successor["accepted_scope"], parent["accepted_scope"])
        self.assertEqual(successor["accepted_decisions"], parent["accepted_decisions"])
        self.assertEqual(successor["authority_boundary"], parent["authority_boundary"])
        self.assertEqual(successor["parent_handoff_sha256"], parent["handoff_sha256"])
        self.assertIsNotNone(successor["replan"])

    def test_acceptance_cannot_run_without_pass_resume(self):
        td, root, cp = self.make_repo(); self.addCleanup(td.cleanup)
        hp, _, _, _ = self.create_and_verify(root, cp)
        (root / "src" / "calc.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
        vp = root / "evidence" / "verify_stale.json"
        verify_handoff(cp, hp, vp)
        with self.assertRaises(ValueError):
            run_acceptance(cp, hp, vp, root / "evidence" / "receipt.json")

    def test_failed_acceptance_stays_failed(self):
        td, root, cp = self.make_repo(); self.addCleanup(td.cleanup)
        hp, _, _, _ = self.create_and_verify(root, cp)
        (root / "src" / "calc.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
        stale_vp = root / "evidence" / "stale.json"; verify_handoff(cp, hp, stale_vp)
        rp = root / "replan.md"; rp.write_text("Fresh-read regression.\n", encoding="utf-8")
        hp2 = root / "evidence" / "h2.json"; rebind_handoff(cp, hp, stale_vp, rp, hp2)
        vp2 = root / "evidence" / "v2.json"; verify_handoff(cp, hp2, vp2)
        receipt = run_acceptance(cp, hp2, vp2, root / "evidence" / "fail_receipt.json")
        self.assertEqual(receipt["status"], "FAIL_EXECUTABLE_PROOF")
        result = adjudicate(cp, hp2, vp2, root / "evidence" / "fail_receipt.json")
        self.assertEqual(result["status"], "FAIL_EXECUTABLE_PROOF")
        self.assertFalse(result["accepted"])

    def test_successful_continuation_passes(self):
        td, root, cp = self.make_repo(); self.addCleanup(td.cleanup)
        hp, vp, _, _ = self.create_and_verify(root, cp)
        receipt_path = root / "evidence" / "receipt.json"
        receipt = run_acceptance(cp, hp, vp, receipt_path)
        self.assertEqual(receipt["status"], "PASS_EXECUTABLE_PROOF")
        result = adjudicate(cp, hp, vp, receipt_path)
        self.assertEqual(result["status"], "PASS_CONTINUATION")
        self.assertTrue(result["accepted"])

    def test_post_acceptance_edit_blocks_stale_final_claim(self):
        td, root, cp = self.make_repo(); self.addCleanup(td.cleanup)
        hp, vp, _, _ = self.create_and_verify(root, cp)
        receipt_path = root / "evidence" / "receipt.json"
        run_acceptance(cp, hp, vp, receipt_path)
        (root / "src" / "calc.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
        result = adjudicate(cp, hp, vp, receipt_path)
        self.assertEqual(result["status"], "BLOCKED_STALE_FINAL_PROOF")

    def test_success_claim_flagged_when_proof_not_accepted(self):
        td, root, cp = self.make_repo(); self.addCleanup(td.cleanup)
        hp, vp, _, _ = self.create_and_verify(root, cp)
        receipt_path = root / "evidence" / "receipt.json"
        run_acceptance(cp, hp, vp, receipt_path)
        (root / "src" / "calc.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
        claim = root / "claim.json"; claim.write_text('{"status":"PASS"}', encoding="utf-8")
        result = adjudicate(cp, hp, vp, receipt_path, claim)
        self.assertTrue(result["unsupported_success_claim"])


if __name__ == "__main__":
    unittest.main()
