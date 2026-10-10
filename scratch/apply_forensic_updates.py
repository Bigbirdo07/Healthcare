import json
import re

with open('scratch/marketplace_dump.json', 'r', encoding='utf-8') as f:
    dump = json.load(f)

rules = dump['COVERAGE_RULES']

# Filter out old bcbsri_bluechip_core_2026 rules that were downgraded (P-VIT-PRENATAL and P-WMN-PUMP)
# and ensure clean, accurate rules for all validated items.

with open('scratch/forensic_matrix.json', 'r', encoding='utf-8') as f:
    matrix = json.load(f)

# Load current marketplace.js text
with open('dist/marketplace/marketplace.js', 'r', encoding='utf-8') as f:
    js_text = f.read()

# Build new COVERAGE_RULES array for bcbsri_bluechip_core_2026
updated_core_rules = []
for item in matrix:
    if item['coverage_status'] == 'NEEDS_VERIFICATION':
        continue # Will default to NEEDS_VERIFICATION in getMarketplaceForPlan
    
    # Map status label
    status_label = item['coverage_status']
    if item['coverage_status'] == 'COVERED':
        status_label = 'Covered'
    elif item['coverage_status'] == 'CONDITIONAL':
        if 'Authorization' in item['requirement_claim']:
            status_label = 'Covered with Prior Authorization'
        elif 'Allowance' in item['cost_claim']:
            status_label = 'Covered with Allowance'
        elif 'Network' in item['requirement_claim']:
            status_label = 'Covered with Network Provider'
        elif 'Prescription' in item['requirement_claim']:
            status_label = 'Covered with Prescription & Diagnosis'
        else:
            status_label = 'Covered with Provider Order'
    elif item['coverage_status'] == 'NOT_COVERED':
        status_label = 'Not Covered'

    target_type = item['entity_type']
    rule = {
        "rule_id": f"R-GS-BCBS-{item['entity_id'].replace('-', '')}",
        "target_type": target_type,
        "plan_id": "bcbsri_bluechip_core_2026",
        "applicable_plan_ids": ["bcbsri_bluechip_core_2026"],
        "source_id": item['source_id'],
        "source_authority": "OFFICIAL_INSURER",
        "benefit_pathway": item['benefit_pathway'],
        "coverage_status": status_label,
        "state": "RI",
        "plan_type": "Medicare Advantage",
        "plan_year": 2026,
        "verification_status": "VERIFIED_EXACT",
        "member_cost": item['cost_claim'],
        "official_source_name": item['official_source_name'],
        "official_source_url": item['official_url'],
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": item['page_number']
    }
    if target_type == 'PRODUCT':
        rule['product_id'] = item['entity_id']
    elif target_type == 'SERVICE':
        rule['service_id'] = item['entity_id']
    elif target_type == 'BENEFIT':
        rule['benefit_id'] = item['entity_id']
    
    updated_core_rules.append(rule)

print(f"Generated {len(updated_core_rules)} active coverage rules for bcbsri_bluechip_core_2026.")

# Replace rules in marketplace.js
# First find all non-core rules
non_core_rules = [r for r in rules if r.get('plan_id') != 'bcbsri_bluechip_core_2026']
all_rules = non_core_rules + updated_core_rules

rules_js = "  const COVERAGE_RULES = [\n" + ",\n".join(["  " + json.dumps(r) for r in all_rules]) + "\n  ];"

# Replace COVERAGE_RULES in js_text
pattern = r'const COVERAGE_RULES = \[\s*(.*?)\s*\];'
new_js_text = re.sub(pattern, rules_js, js_text, flags=re.DOTALL)

with open('dist/marketplace/marketplace.js', 'w', encoding='utf-8') as f:
    f.write(new_js_text)

print("Updated dist/marketplace/marketplace.js successfully.")
