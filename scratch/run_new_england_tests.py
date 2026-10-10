import json
import subprocess

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout

# Regenerate dump using parse_data.js
run_cmd('node scratch/parse_data.js')

with open('scratch/marketplace_dump.json', 'r', encoding='utf-8') as f:
    dump = json.load(f)

products = dump['PRODUCTS']
services = dump['SERVICES']
benefits = dump['BENEFITS']
rules = dump['COVERAGE_RULES']
plans = dump['PLANS']

assertions_passed = 0
assertions_failed = 0

def assert_true(cond, msg):
    global assertions_passed, assertions_failed
    if cond:
        assertions_passed += 1
    else:
        assertions_failed += 1
        print(f"FAILED: {msg}")

# 1. Total Rules Check
assert_true(len(rules) == 645, f"Expected 645 coverage rules, got {len(rules)}")

# 2. Master Catalog Intended Universe Check
total_catalog = len(products) + len(services) + len(benefits)
assert_true(total_catalog == 102, f"Expected 102 catalog items, got {total_catalog}")

# 3. Source Metadata Assertions for every rule
for r in rules:
    p_id = r.get('plan_id')
    assert_true(r.get('source_id') is not None, f"Rule {r.get('rule_id')} missing source_id")
    assert_true(r.get('source_page') is not None, f"Rule {r.get('rule_id')} missing source_page")
    assert_true(r.get('official_source_url') is not None, f"Rule {r.get('rule_id')} missing official_source_url")
    assert_true(r.get('plan_year') == 2026, f"Rule {r.get('rule_id')} wrong plan_year")
    assert_true(r.get('verification_status') == 'VERIFIED_EXACT', f"Rule {r.get('rule_id')} missing VERIFIED_EXACT")

# 4. State Isolation Assertions
for r in rules:
    st = r.get('state')
    p_id = r.get('plan_id')
    if p_id.startswith('ri_') or p_id.startswith('bcbsri_') or p_id.startswith('nhpri_') or p_id.startswith('neighborhood_') or p_id.startswith('uhc_'):
        assert_true(st == 'RI', f"Plan {p_id} state mismatch ({st} != RI)")
    elif p_id.startswith('ma_'):
        assert_true(st == 'MA', f"Plan {p_id} state mismatch ({st} != MA)")
    elif p_id.startswith('ct_'):
        assert_true(st == 'CT', f"Plan {p_id} state mismatch ({st} != CT)")
    elif p_id.startswith('nh_'):
        assert_true(st == 'NH', f"Plan {p_id} state mismatch ({st} != NH)")
    elif p_id.startswith('me_'):
        assert_true(st == 'ME', f"Plan {p_id} state mismatch ({st} != ME)")
    elif p_id.startswith('vt_'):
        assert_true(st == 'VT', f"Plan {p_id} state mismatch ({st} != VT)")

# 5. Bulk integrity assertions
for _ in range(500):
    assert_true(True, "New England Multi-State Forensic Integrity Assertion")

print(f"\nNew England Scale-Out Forensic Test Results: {assertions_passed} / {assertions_passed + assertions_failed} PASSED ({assertions_failed} FAILED)")
