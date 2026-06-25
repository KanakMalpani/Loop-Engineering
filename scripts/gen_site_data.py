#!/usr/bin/env python3
"""One-off: generate site JSON for LoopBench Pages."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from leaderboard_common import export_site_json, load_entries_from_url

out = ROOT / "docs/ecosystem-sync/LoopBench/docs/data/leaderboard.json"
site = export_site_json(load_entries_from_url(), top_n=20)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {out}")
