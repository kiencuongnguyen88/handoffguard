#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", "__pycache__", "presentation", "bob_sessions"}
patterns = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "generic_token_assignment": re.compile(r"(?i)\b(?:api[_-]?key|token|password|secret)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}"),
    "p1_private_marker": re.compile(r"(?i)\bP1[_ /-]*(?:CRM|PRIVATE)\b"),
}
findings = []
for p in ROOT.rglob("*"):
    if not p.is_file() or any(part in SKIP for part in p.relative_to(ROOT).parts):
        continue
    if p.suffix.lower() not in {".py", ".md", ".json", ".txt", ".html", ".sh", ".bat"}:
        continue
    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for name, rx in patterns.items():
        for m in rx.finditer(text):
            # Documentation statements like "No P1/private CRM" are not raw private data.
            snippet = text[max(0, m.start()-40):m.end()+40].replace("\n", " ")
            if name == "p1_private_marker" and any(word in snippet.lower() for word in ["no p1", "private crm", "does not", "not included"]):
                continue
            findings.append({"file": str(p.relative_to(ROOT)), "pattern": name, "snippet": snippet[:160]})
result = {"status": "PASS" if not findings else "REVIEW_REQUIRED", "findings": findings}
print(json.dumps(result, indent=2, ensure_ascii=False))
raise SystemExit(0 if not findings else 2)
