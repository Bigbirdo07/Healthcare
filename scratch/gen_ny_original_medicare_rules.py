"""Copy the Original Medicare rules from the Rhode Island spec into the New York
spec. They quote CMS's national "Your Medicare Benefits" booklet, so the same
excerpts (and the same hashed PDF) apply in every state; the builder re-checks
each quote against the PDF for NY too.

Usage: python3 scratch/gen_ny_original_medicare_rules.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RI = json.load(open(os.path.join(ROOT, "data/ri_verified_coverage_2026/evidence_spec.json"), encoding="utf-8"))
NY_PATH = os.path.join(ROOT, "data/ny_verified_coverage_2026/evidence_spec.json")
NY = json.load(open(NY_PATH, encoding="utf-8"))

rules = [r for r in RI["rules"] if r["plans"] == "ORIGINAL_MEDICARE"]
for r in rules:
    for ex in r["excerpts"]:
        if isinstance(ex, dict) and ex.get("source"):
            NY["sources"][ex["source"]] = RI["sources"][ex["source"]]
    NY["sources"][r["source"]] = RI["sources"][r["source"]]
    if r.get("template"):
        NY["templates"][r["template"]] = RI["templates"][r["template"]]
    if r["targets"] in RI["groups"]:
        NY["groups"][r["targets"]] = RI["groups"][r["targets"]]
NY["plans"]["ORIGINAL_MEDICARE"] = ["CMS:NY:ORIGINAL_MEDICARE:2026"]
NY["rules"] = [r for r in NY["rules"] if r["plans"] != "ORIGINAL_MEDICARE"] + rules
json.dump(NY, open(NY_PATH, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"{len(rules)} Original Medicare evidence entries copied to the NY spec")
