#!/usr/bin/env python3
"""HandoffGuard: fail closed when an AI coding handoff no longer matches material repository reality."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HANDOFF_SCHEMA = "handoffguard.handoff.v1"
VERIFY_SCHEMA = "handoffguard.resume-verification.v1"
ACCEPT_SCHEMA = "handoffguard.acceptance-receipt.v1"
ADJUDICATION_SCHEMA = "handoffguard.adjudication.v1"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_json(data: Any) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        value = json.load(f)
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def add_digest(record: dict[str, Any], field: str) -> dict[str, Any]:
    clone = dict(record)
    clone.pop(field, None)
    record[field] = sha256_bytes(canonical_json(clone))
    return record


def verify_digest(record: dict[str, Any], field: str) -> bool:
    stored = record.get(field)
    if not isinstance(stored, str):
        return False
    clone = dict(record)
    clone.pop(field, None)
    return secrets.compare_digest(stored, sha256_bytes(canonical_json(clone)))


def resolve_root(contract_path: Path, contract: dict[str, Any]) -> Path:
    root = (contract_path.parent / str(contract.get("root", "."))).resolve()
    if not root.is_dir():
        raise ValueError(f"root is not a directory: {root}")
    return root


def validate_contract(contract: dict[str, Any]) -> None:
    required_strings = ["workflow_id", "accepted_scope", "next_move"]
    for key in required_strings:
        if not isinstance(contract.get(key), str) or not contract[key].strip():
            raise ValueError(f"{key} must be a non-empty string")
    for key in ["material_paths", "accepted_decisions", "authority_boundary", "acceptance_command"]:
        value = contract.get(key)
        if not isinstance(value, list) or not value or not all(isinstance(x, str) and x for x in value):
            raise ValueError(f"{key} must be a non-empty string array")
    if len(set(contract["material_paths"])) != len(contract["material_paths"]):
        raise ValueError("material_paths must not contain duplicates")


def safe_path(root: Path, rel: str) -> Path:
    p = (root / rel).resolve()
    try:
        p.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path escapes root: {rel}") from exc
    return p


def hash_material_paths(root: Path, paths: list[str]) -> tuple[dict[str, str], list[str]]:
    hashes: dict[str, str] = {}
    missing: list[str] = []
    for rel in paths:
        p = safe_path(root, rel)
        if not p.is_file():
            missing.append(rel)
        else:
            hashes[rel] = sha256_file(p)
    return hashes, missing


def command_digest(command: list[str]) -> str:
    return sha256_bytes(canonical_json(command))


def git_state(root: Path) -> dict[str, Any]:
    def run(args: list[str]) -> subprocess.CompletedProcess[str] | None:
        try:
            return subprocess.run(args, cwd=root, text=True, capture_output=True, check=False)
        except OSError:
            return None

    inside = run(["git", "rev-parse", "--is-inside-work-tree"])
    if inside is None or inside.returncode != 0 or inside.stdout.strip() != "true":
        return {"available": False, "head": None, "dirty": None}
    head = run(["git", "rev-parse", "HEAD"])
    status = run(["git", "status", "--porcelain"])
    return {
        "available": True,
        "head": head.stdout.strip() if head and head.returncode == 0 else None,
        "dirty": bool(status.stdout.strip()) if status and status.returncode == 0 else None,
    }


def load_contract(contract_path: Path) -> tuple[dict[str, Any], Path]:
    contract_path = contract_path.resolve()
    contract = load_json(contract_path)
    validate_contract(contract)
    return contract, resolve_root(contract_path, contract)


def create_handoff(contract_path: Path, output_path: Path, *, parent: dict[str, Any] | None = None,
                   replan_path: Path | None = None, next_move: str | None = None) -> dict[str, Any]:
    contract, root = load_contract(contract_path)
    hashes, missing = hash_material_paths(root, list(contract["material_paths"]))
    if missing:
        raise ValueError(f"Cannot create handoff; material paths missing: {', '.join(missing)}")

    if parent is not None:
        if not verify_digest(parent, "handoff_sha256"):
            raise ValueError("Parent handoff integrity check failed")
        if parent.get("workflow_id") != contract["workflow_id"]:
            raise ValueError("Parent handoff workflow_id mismatch")
        accepted_scope = parent["accepted_scope"]
        accepted_decisions = list(parent["accepted_decisions"])
        authority_boundary = list(parent["authority_boundary"])
        parent_sha = parent["handoff_sha256"]
    else:
        accepted_scope = contract["accepted_scope"]
        accepted_decisions = list(contract["accepted_decisions"])
        authority_boundary = list(contract["authority_boundary"])
        parent_sha = None

    replan = None
    if replan_path is not None:
        rp = replan_path.resolve()
        if not rp.is_file() or not rp.read_text(encoding="utf-8").strip():
            raise ValueError("replan note must be a non-empty file")
        replan = {"ref": rp.name, "sha256": sha256_file(rp)}

    record: dict[str, Any] = {
        "schema": HANDOFF_SCHEMA,
        "workflow_id": contract["workflow_id"],
        "handoff_id": f"HG-{secrets.token_hex(6).upper()}",
        "transition_nonce": secrets.token_hex(12),
        "created_at": now_utc(),
        "contract_sha256": sha256_file(contract_path.resolve()),
        "root_label": contract.get("root_label", root.name),
        "accepted_scope": accepted_scope,
        "accepted_decisions": accepted_decisions,
        "next_move": next_move.strip() if isinstance(next_move, str) and next_move.strip() else contract["next_move"],
        "authority_boundary": authority_boundary,
        "material_paths": list(contract["material_paths"]),
        "material_hashes": hashes,
        "acceptance_command": list(contract["acceptance_command"]),
        "acceptance_command_sha256": command_digest(list(contract["acceptance_command"])),
        "git_state": git_state(root),
        "parent_handoff_sha256": parent_sha,
        "replan": replan,
    }
    add_digest(record, "handoff_sha256")
    write_json(output_path.resolve(), record)
    return record


def verify_handoff(contract_path: Path, handoff_path: Path, output_path: Path | None = None) -> dict[str, Any]:
    contract, root = load_contract(contract_path)
    handoff = load_json(handoff_path.resolve())

    status = "PASS_RESUME_BINDING"
    reason = "Accepted continuation state is preserved and all declared material source bytes still match the handoff."
    changed: list[str] = []
    missing: list[str] = []

    if not verify_digest(handoff, "handoff_sha256"):
        status = "INCONCLUSIVE_HANDOFF_INTEGRITY"
        reason = "Handoff bytes do not match handoff_sha256."
    elif handoff.get("workflow_id") != contract.get("workflow_id"):
        status = "BLOCKED_WORKFLOW_MISMATCH"
        reason = "Handoff workflow_id does not match the current contract."
    elif handoff.get("contract_sha256") != sha256_file(contract_path.resolve()):
        status = "BLOCKED_STALE_HANDOFF_CONTRACT"
        reason = "The handoff contract changed after the handoff was created."
    elif handoff.get("acceptance_command_sha256") != command_digest(list(contract["acceptance_command"])):
        status = "BLOCKED_ACCEPTANCE_COMMAND_DRIFT"
        reason = "The acceptance command no longer matches the handoff."
    else:
        current_hashes, missing = hash_material_paths(root, list(contract["material_paths"]))
        if missing:
            status = "BLOCKED_SOURCE_MISSING"
            reason = f"Material source paths are missing: {', '.join(missing)}"
        else:
            old_hashes = handoff.get("material_hashes", {})
            changed = sorted(rel for rel, h in current_hashes.items() if old_hashes.get(rel) != h)
            if changed:
                status = "BLOCKED_STALE_HANDOFF"
                reason = "Material source changed after the handoff; fresh-read and bounded re-plan are required before resume."

    current_git = git_state(root)
    prior_git = handoff.get("git_state", {}) if isinstance(handoff.get("git_state"), dict) else {}
    receipt: dict[str, Any] = {
        "schema": VERIFY_SCHEMA,
        "workflow_id": contract["workflow_id"],
        "verified_at": now_utc(),
        "status": status,
        "accepted": status == "PASS_RESUME_BINDING",
        "reason": reason,
        "handoff_sha256": handoff.get("handoff_sha256"),
        "contract_sha256": sha256_file(contract_path.resolve()),
        "changed_material_paths": changed,
        "missing_material_paths": missing,
        "preserved_accepted_scope": handoff.get("accepted_scope"),
        "preserved_accepted_decisions": handoff.get("accepted_decisions"),
        "exact_next_move": handoff.get("next_move"),
        "git_head_at_handoff": prior_git.get("head"),
        "git_head_now": current_git.get("head"),
        "repo_head_changed": bool(prior_git.get("head") and current_git.get("head") and prior_git.get("head") != current_git.get("head")),
        "replan_required": status == "BLOCKED_STALE_HANDOFF",
    }
    add_digest(receipt, "verification_sha256")
    if output_path is not None:
        write_json(output_path.resolve(), receipt)
    return receipt


def rebind_handoff(contract_path: Path, handoff_path: Path, verification_path: Path, replan_path: Path,
                  output_path: Path, next_move: str | None = None) -> dict[str, Any]:
    parent = load_json(handoff_path.resolve())
    verification = load_json(verification_path.resolve())
    if not verify_digest(parent, "handoff_sha256"):
        raise ValueError("Parent handoff integrity check failed")
    if not verify_digest(verification, "verification_sha256"):
        raise ValueError("Verification receipt integrity check failed")
    if verification.get("handoff_sha256") != parent.get("handoff_sha256"):
        raise ValueError("Verification receipt is not bound to the parent handoff")
    if verification.get("status") != "BLOCKED_STALE_HANDOFF":
        raise ValueError("Rebind requires a BLOCKED_STALE_HANDOFF verification receipt")
    return create_handoff(contract_path, output_path, parent=parent, replan_path=replan_path, next_move=next_move)


def run_acceptance(contract_path: Path, handoff_path: Path, verification_path: Path, receipt_path: Path) -> dict[str, Any]:
    contract, root = load_contract(contract_path)
    handoff = load_json(handoff_path.resolve())
    verification = load_json(verification_path.resolve())

    if not verify_digest(handoff, "handoff_sha256"):
        raise ValueError("Handoff integrity check failed")
    if not verify_digest(verification, "verification_sha256"):
        raise ValueError("Verification receipt integrity check failed")
    if verification.get("status") != "PASS_RESUME_BINDING":
        raise ValueError("Acceptance cannot run without PASS_RESUME_BINDING")
    if verification.get("handoff_sha256") != handoff.get("handoff_sha256"):
        raise ValueError("Verification receipt is not bound to this handoff")
    if handoff.get("contract_sha256") != sha256_file(contract_path.resolve()):
        raise ValueError("Current contract differs from the verified handoff contract")

    command = list(contract["acceptance_command"])
    before, missing_before = hash_material_paths(root, list(contract["material_paths"]))
    started_at = now_utc()
    if missing_before:
        receipt: dict[str, Any] = {
            "schema": ACCEPT_SCHEMA,
            "workflow_id": contract["workflow_id"],
            "started_at": started_at,
            "finished_at": now_utc(),
            "handoff_sha256": handoff["handoff_sha256"],
            "verification_sha256": verification["verification_sha256"],
            "contract_sha256": sha256_file(contract_path.resolve()),
            "acceptance_command": command,
            "acceptance_command_sha256": command_digest(command),
            "material_hashes_before": before,
            "material_hashes_after": before,
            "missing_material_paths": missing_before,
            "mutated_during_acceptance": False,
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "status": "INCONCLUSIVE_SOURCE_MISSING",
        }
    else:
        proc = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False,
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        after, missing_after = hash_material_paths(root, list(contract["material_paths"]))
        mutated = before != after
        if missing_after:
            status = "INCONCLUSIVE_SOURCE_MISSING"
        elif mutated:
            status = "INCONCLUSIVE_MUTATED_DURING_ACCEPTANCE"
        elif proc.returncode == 0:
            status = "PASS_EXECUTABLE_PROOF"
        else:
            status = "FAIL_EXECUTABLE_PROOF"
        receipt = {
            "schema": ACCEPT_SCHEMA,
            "workflow_id": contract["workflow_id"],
            "started_at": started_at,
            "finished_at": now_utc(),
            "handoff_sha256": handoff["handoff_sha256"],
            "verification_sha256": verification["verification_sha256"],
            "contract_sha256": sha256_file(contract_path.resolve()),
            "acceptance_command": command,
            "acceptance_command_sha256": command_digest(command),
            "material_hashes_before": before,
            "material_hashes_after": after,
            "missing_material_paths": missing_after,
            "mutated_during_acceptance": mutated,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "status": status,
        }
    add_digest(receipt, "acceptance_receipt_sha256")
    write_json(receipt_path.resolve(), receipt)
    return receipt


def adjudicate(contract_path: Path, handoff_path: Path, verification_path: Path, receipt_path: Path,
               claim_path: Path | None = None, output_path: Path | None = None) -> dict[str, Any]:
    contract, root = load_contract(contract_path)
    handoff = load_json(handoff_path.resolve())
    verification = load_json(verification_path.resolve())
    receipt = load_json(receipt_path.resolve())
    claim = load_json(claim_path.resolve()) if claim_path else {}
    claim_status = str(claim.get("status", "")).upper()
    claim_success = claim_status in {"PASS", "SUCCESS", "DONE", "COMPLETED"}

    accepted = False
    if not verify_digest(handoff, "handoff_sha256"):
        status, reason = "INCONCLUSIVE_HANDOFF_INTEGRITY", "Handoff integrity check failed."
    elif not verify_digest(verification, "verification_sha256"):
        status, reason = "INCONCLUSIVE_VERIFICATION_INTEGRITY", "Resume verification integrity check failed."
    elif not verify_digest(receipt, "acceptance_receipt_sha256"):
        status, reason = "INCONCLUSIVE_ACCEPTANCE_RECEIPT_INTEGRITY", "Acceptance receipt integrity check failed."
    elif verification.get("status") != "PASS_RESUME_BINDING":
        status, reason = "BLOCKED_NO_VALID_RESUME_BINDING", "Execution did not start from a verified handoff state."
    elif verification.get("handoff_sha256") != handoff.get("handoff_sha256"):
        status, reason = "BLOCKED_VERIFICATION_HANDOFF_MISMATCH", "Resume verification belongs to another handoff."
    elif receipt.get("handoff_sha256") != handoff.get("handoff_sha256"):
        status, reason = "BLOCKED_RECEIPT_HANDOFF_MISMATCH", "Acceptance receipt belongs to another handoff."
    elif receipt.get("verification_sha256") != verification.get("verification_sha256"):
        status, reason = "BLOCKED_RECEIPT_VERIFICATION_MISMATCH", "Acceptance receipt is not bound to this resume verification."
    elif handoff.get("contract_sha256") != sha256_file(contract_path.resolve()):
        status, reason = "BLOCKED_STALE_HANDOFF_CONTRACT", "Current contract changed after handoff verification."
    elif receipt.get("acceptance_command_sha256") != command_digest(list(contract["acceptance_command"])):
        status, reason = "BLOCKED_ACCEPTANCE_COMMAND_DRIFT", "Acceptance command differs from the current contract."
    elif receipt.get("status") != "PASS_EXECUTABLE_PROOF":
        status, reason = "FAIL_EXECUTABLE_PROOF", f"Acceptance receipt is not green: {receipt.get('status')}."
    else:
        current_hashes, missing = hash_material_paths(root, list(contract["material_paths"]))
        if missing:
            status, reason = "INCONCLUSIVE_SOURCE_MISSING", f"Current material paths are missing: {', '.join(missing)}"
        elif current_hashes != receipt.get("material_hashes_after"):
            status, reason = "BLOCKED_STALE_FINAL_PROOF", "Material source changed after the green acceptance receipt."
        else:
            status = "PASS_CONTINUATION"
            reason = "A verified handoff start, executable acceptance, and current final source bytes all bind consistently."
            accepted = True

    result: dict[str, Any] = {
        "schema": ADJUDICATION_SCHEMA,
        "workflow_id": contract["workflow_id"],
        "checked_at": now_utc(),
        "status": status,
        "accepted": accepted,
        "reason": reason,
        "handoff_sha256": handoff.get("handoff_sha256"),
        "verification_sha256": verification.get("verification_sha256"),
        "acceptance_receipt_sha256": receipt.get("acceptance_receipt_sha256"),
        "claim_status": claim_status or None,
        "unsupported_success_claim": bool(claim_success and not accepted),
    }
    add_digest(result, "adjudication_sha256")
    if output_path is not None:
        write_json(output_path.resolve(), result)
    return result


def print_json(value: dict[str, Any]) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))


def cmd_create(args: argparse.Namespace) -> int:
    print_json(create_handoff(Path(args.contract), Path(args.output)))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    result = verify_handoff(Path(args.contract), Path(args.handoff), Path(args.output) if args.output else None)
    print_json(result)
    return 0 if result["accepted"] else 3


def cmd_rebind(args: argparse.Namespace) -> int:
    result = rebind_handoff(Path(args.contract), Path(args.handoff), Path(args.verification), Path(args.replan),
                            Path(args.output), args.next_move)
    print_json(result)
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    result = run_acceptance(Path(args.contract), Path(args.handoff), Path(args.verification), Path(args.receipt))
    print_json(result)
    return 0 if result["status"] == "PASS_EXECUTABLE_PROOF" else 2


def cmd_adjudicate(args: argparse.Namespace) -> int:
    result = adjudicate(Path(args.contract), Path(args.handoff), Path(args.verification), Path(args.receipt),
                        Path(args.claim) if args.claim else None, Path(args.output) if args.output else None)
    print_json(result)
    return 0 if result["accepted"] else 4


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Verify durable AI coding handoffs before resume, then bind final proof to the verified continuation.")
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("create", help="Create a handoff packet from current accepted state and material source bytes.")
    c.add_argument("--contract", required=True)
    c.add_argument("--output", required=True)
    c.set_defaults(func=cmd_create)

    v = sub.add_parser("verify", help="Verify current material source before another agent/session resumes.")
    v.add_argument("--contract", required=True)
    v.add_argument("--handoff", required=True)
    v.add_argument("--output")
    v.set_defaults(func=cmd_verify)

    rb = sub.add_parser("rebind", help="After stale detection + fresh-read/re-plan, create a successor handoff while preserving accepted state.")
    rb.add_argument("--contract", required=True)
    rb.add_argument("--handoff", required=True)
    rb.add_argument("--verification", required=True)
    rb.add_argument("--replan", required=True)
    rb.add_argument("--output", required=True)
    rb.add_argument("--next-move")
    rb.set_defaults(func=cmd_rebind)

    r = sub.add_parser("run", help="Run the unchanged executable acceptance command after a PASS_RESUME_BINDING start.")
    r.add_argument("--contract", required=True)
    r.add_argument("--handoff", required=True)
    r.add_argument("--verification", required=True)
    r.add_argument("--receipt", required=True)
    r.set_defaults(func=cmd_run)

    a = sub.add_parser("adjudicate", help="Accept continuation only when resume binding + executable proof + final current bytes all agree.")
    a.add_argument("--contract", required=True)
    a.add_argument("--handoff", required=True)
    a.add_argument("--verification", required=True)
    a.add_argument("--receipt", required=True)
    a.add_argument("--claim")
    a.add_argument("--output")
    a.set_defaults(func=cmd_adjudicate)
    return p


def main() -> int:
    try:
        args = build_parser().parse_args()
        return int(args.func(args))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 64


if __name__ == "__main__":
    raise SystemExit(main())
