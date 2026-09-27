#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m unittest discover -s tests -v
python demo.py
printf '%s\n' HANDOFFGUARD_REPRODUCE_PASS
