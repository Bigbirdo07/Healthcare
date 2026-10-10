import json

with open('scratch/marketplace_dump.json', 'r', encoding='utf-8') as f:
    dump = json.load(f)

rules = dump['COVERAGE_RULES']
core_rules = [r for r in rules if r.get('plan_id') == 'bcbsri_bluechip_core_2026']

fit_rule = next((r for r in core_rules if r.get('benefit_id') == 'B-FIT-REIMB' or r.get('target_id') == 'B-FIT-REIMB'), None)
print("Fit rule found:", fit_rule)
