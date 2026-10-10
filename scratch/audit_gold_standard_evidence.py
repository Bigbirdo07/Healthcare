import json

with open('scratch/marketplace_dump.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

products = data['PRODUCTS']
services = data['SERVICES']
benefits = data['BENEFITS']
rules = data['COVERAGE_RULES']

core_rules = [r for r in rules if r.get('plan_id') == 'bcbsri_bluechip_core_2026']

print("Loaded marketplace data successfully.")
print(f"Total Core Rules: {len(core_rules)}")
