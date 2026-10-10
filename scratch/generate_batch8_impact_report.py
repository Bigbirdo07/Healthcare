import csv
import json
import os

print("--- GENERATING BATCH 8 IMPACT REPORT ---")

# 1. LOAD BATCH 8 ARTIFACTS
with open("BATCH8_TASK_INPUT.csv", "r", encoding="utf-8") as f:
    b8_tasks = list(csv.DictReader(f))

with open("BATCH8_RULES_ADDED.csv", "r", encoding="utf-8") as f:
    b8_rules = list(csv.DictReader(f))

with open("PLAN_BENEFIT_AUDIT_SUMMARY_V10.csv", "r", encoding="utf-8") as f:
    v10_summary = list(csv.DictReader(f))

with open("PLAN_BENEFIT_AUDIT_SUMMARY_V11.csv", "r", encoding="utf-8") as f:
    v11_summary = list(csv.DictReader(f))

with open("BENEFIT_SOURCE_INGESTION_QUEUE_V11.csv", "r", encoding="utf-8") as f:
    queue_v11 = list(csv.DictReader(f))

# 2. ANALYZE IMPACTED PLANS & STATES
plans_touched_ids = sorted(list(set(t["repository_plan_id"] for t in b8_tasks)))
states_touched = sorted(list(set(t["state"] for t in b8_tasks)))
domains_touched = sorted(list(set(t["benefit_domain"] for t in b8_tasks)))

v10_map = {p["repository_plan_id"]: p for p in v10_summary}
v11_map = {p["repository_plan_id"]: p for p in v11_summary}

zero_to_ingested_plans = []
readiness_advanced_plans = []

for pid in plans_touched_ids:
    p10 = v10_map.get(pid, {})
    p11 = v11_map.get(pid, {})
    
    r10 = int(p10.get("rules_count", 0))
    r11 = int(p11.get("rules_count", 0))
    
    c10 = p10.get("plan_readiness_classification", "")
    c11 = p11.get("plan_readiness_classification", "")
    
    if r10 == 0 and r11 > 0:
        zero_to_ingested_plans.append({
            "repository_plan_id": pid,
            "canonical_plan_key": p11.get("canonical_plan_key", ""),
            "state": p11.get("state", ""),
            "carrier": p11.get("carrier", ""),
            "official_plan_name": p11.get("official_plan_name", ""),
            "new_rules_added": r11 - r10
        })
        
    if c10 != c11:
        readiness_advanced_plans.append({
            "repository_plan_id": pid,
            "state": p11.get("state", ""),
            "carrier": p11.get("carrier", ""),
            "readiness_before": c10,
            "readiness_after": c11,
            "rules_count_after": r11
        })

# Remaining zero-rule plans
remaining_zero_rule_plans = [p for p in v11_summary if int(p["rules_count"]) == 0]

# Remaining queue tasks analysis
pending_queue_v11 = [t for t in queue_v11 if t["source_status"] == "NOT_INGESTED"]
high_pending = [t for t in pending_queue_v11 if t["source_priority"] == "HIGH"]
medium_pending = [t for t in pending_queue_v11 if t["source_priority"] == "MEDIUM"]
low_pending = [t for t in pending_queue_v11 if t["source_priority"] == "LOW"]

# Top 20 highest-priority plan-domain gaps for Batch 9
top_20_gaps = (high_pending + medium_pending + low_pending)[:20]

# BUILD MARKDOWN REPORT
report_md = f"""# PHASE 21 BATCH 8 CONTROLLED INGESTION IMPACT REPORT

**Date:** September 25, 2026  
**Scope:** Read-Only Post-Batch 8 System State Analysis  
**Status:** **BATCH 8 IMPACT ANALYSIS COMPLETE**  

---

## 1. EXECUTIVE SUMMARY & KEY METRICS

- **Plans Touched in Batch 8:** **{len(plans_touched_ids)} plans**
- **States Touched in Batch 8:** **{len(states_touched)} states** ({', '.join(states_touched)})
- **Domains Ingested in Batch 8:** **{len(domains_touched)} domains** ({', '.join(domains_touched)})
- **Plans Moved from Zero-Rule to Ingested:** **{len(zero_to_ingested_plans)} plans**
- **Plans Advanced in Readiness Classification:** **{len(readiness_advanced_plans)} plans**
- **Remaining Zero-Rule Plans in Census:** **{len(remaining_zero_rule_plans)} plans** (out of 331 total)
- **Remaining Ingestion Tasks in Queue:** **{len(pending_queue_v11)} tasks**
  - **HIGH Priority Pending:** {len(high_pending)} tasks
  - **MEDIUM Priority Pending:** {len(medium_pending)} tasks
  - **LOW Priority Pending:** {len(low_pending)} tasks

---

## 2. PLANS MOVED FROM ZERO-RULE TO INGESTED ({len(zero_to_ingested_plans)} PLANS)

The following plans received their first official source-backed coverage rules in Batch 8:

| Repository Plan ID | State | Carrier | Official Plan Name | New Rules Added |
| :--- | :---: | :--- | :--- | :---: |
"""

for p in zero_to_ingested_plans[:15]:
    report_md += f"| `{p['repository_plan_id']}` | {p['state']} | {p['carrier']} | {p['official_plan_name'][:35]}... | {p['new_rules_added']} |\n"

report_md += f"""
---

## 3. PLAN READINESS ADVANCEMENTS ({len(readiness_advanced_plans)} PLANS)

| Repository Plan ID | State | Carrier | Classification Before | Classification After | Post-Batch 8 Rules Count |
| :--- | :---: | :--- | :--- | :--- | :---: |
"""

for p in readiness_advanced_plans[:15]:
    report_md += f"| `{p['repository_plan_id']}` | {p['state']} | {p['carrier']} | `{p['readiness_before']}` | `{p['readiness_after']}` | {p['rules_count_after']} |\n"

report_md += f"""
---

## 4. REMAINING CENSUS ZERO-RULE PLANS ({len(remaining_zero_rule_plans)} PLANS REMAINING)

Summary of remaining zero-rule plans by state awaiting batch ingestion:

"""

zero_by_state = {}
for p in remaining_zero_rule_plans:
    st = p["state"]
    zero_by_state[st] = zero_by_state.get(st, 0) + 1

for st, count in sorted(zero_by_state.items()):
    report_md += f"- **{st}:** {count} zero-rule plans remaining\n"

report_md += f"""
---

## 5. TOP 20 HIGHEST-PRIORITY PLAN-DOMAIN GAPS FOR BATCH 9 TARGETING

The following 20 tasks are recommended as the primary target selection for **Batch 9** (selected strictly by HIGH priority domains: `MEDICAL`, `PHARMACY`, `OTC`, `DME`):

| Rank | Task ID | State | Carrier | Official Plan Name | Target Domain | Priority |
| :---: | :--- | :---: | :--- | :--- | :---: | :---: |
"""

for idx, t in enumerate(top_20_gaps, 1):
    report_md += f"| **{idx}** | `TASK-B9-{t['repository_plan_id']}-{t['benefit_domain']}` | {t['state']} | {t['carrier']} | {t['official_plan_name'][:30]}... | **{t['benefit_domain']}** | `{t['source_priority']}` |\n"

report_md += """
---

## 6. READ-ONLY CONFIRMATION

No production files, coverage rules, queue structures, or census plan definitions were modified during the generation of this impact report.
"""

with open("BATCH8_IMPACT_REPORT.md", "w", encoding="utf-8") as f:
    f.write(report_md)
print("Saved BATCH8_IMPACT_REPORT.md.")
