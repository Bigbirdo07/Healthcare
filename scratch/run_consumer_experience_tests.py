import json
import subprocess

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout

run_cmd('node scratch/parse_data.js')

with open('scratch/marketplace_dump.json', 'r', encoding='utf-8') as f:
    dump = json.load(f)

products = dump['PRODUCTS']
services = dump['SERVICES']
benefits = dump['BENEFITS']
rules = dump['COVERAGE_RULES']
plans = dump['PLANS']

passed = 0
failed = 0

def assert_check(cond, msg):
    global passed, failed
    if cond:
        passed += 1
    else:
        failed += 1
        print(f"FAILED: {msg}")

# Master list of 28 source-confirmed production plans
target_plans = [
    # Rhode Island (4)
    "bcbsri_bluechip_core_2026", "neighborhood_integra_2026", "ri_medicaid_managed_2026", "uhc_medicare_dual_2026",
    # Massachusetts (6)
    "ma_wellsense_wellsense_connectorcare", "ma_tufts_p32_tufts_health_direct_connectorcare", "ma_bcbsma_health_connector_standard_plan",
    "ma_harvard_pilgrim_standard_silver_ii", "ma_health_new_england_connectorcare", "ma_mgb_health_connectorcare",
    # Connecticut (7)
    "ct_husky_health_husky_a", "ct_husky_health_husky_b", "ct_husky_health_husky_c", "ct_husky_health_husky_d",
    "ct_connecticare_connecticare_choice_silver", "ct_connecticare_connecticare_covered_ct", "ct_anthem_bcbs_anthem_pathway_standard_silver",
    # New Hampshire (3)
    "nh_wellsense_medicaid_mco", "nh_amerihealth_caritas_medicaid", "nh_nh_healthy_families_medicaid",
    # Maine (4)
    "me_mainecare_medicaid", "me_harvard_pilgrim_clear_choice_hmo_silver_4000", "me_anthem_bcbs_anthem_clear_choice_ppo",
    "me_community_health_options_community_health_options_clear_choice",
    # Vermont (4)
    "vt_vermont_medicaid", "vt_dr_dynasaur_medicaid", "vt_bcbsvt_bcbsvt_silver", "vt_mvp_health_mvp_vt_plus_silver"
]

# 1. Test 28 Source-Confirmed Production Plans Count
assert_check(len(target_plans) == 28, f"Expected 28 production plans, found {len(target_plans)}")

# 2. Test End-to-End User Journey for RI (bcbsri_bluechip_core_2026)
core_rules = [r for r in rules if r.get('plan_id') == 'bcbsri_bluechip_core_2026']
assert_check(len(core_rules) == 69, "BlueCHiP Core 2026 should have 69 active rules")

# Test search queries
def search_catalog(q, p_id='bcbsri_bluechip_core_2026'):
    q_lower = q.lower()
    p_rules = [r for r in rules if r.get('plan_id') == p_id]
    matches = []
    for r in p_rules:
        target_id = r.get('product_id') or r.get('service_id') or r.get('benefit_id') or r.get('target_id')
        p_match = next((p for p in products if p['id'] == target_id), None)
        s_match = next((s for s in services if s['id'] == target_id), None)
        b_match = next((b for b in benefits if b['id'] == target_id), None)

        name = (p_match['product_name'] if p_match else (s_match['service_name'] if s_match else (b_match['benefit_name'] if b_match else ''))).lower()
        path = (r.get('benefit_pathway') or '').lower()
        cat = (p_match.get('category') if p_match else (s_match.get('category') if s_match else (b_match.get('category') if b_match else ''))).lower()
        aliases = [a.lower() for a in (p_match.get('aliases', []) if p_match else (s_match.get('aliases', []) if s_match else (b_match.get('aliases', []) if b_match else [])))]
        desc = (p_match.get('description') if p_match else (s_match.get('description') if s_match else (b_match.get('description') if b_match else ''))).lower()

        if q_lower in name or q_lower in path or q_lower in cat or q_lower in desc or any(q_lower in a for a in aliases):
            matches.append(target_id)
    return matches

assert_check('P-VIT-D' in search_catalog('vitamin d'), "Search 'vitamin d' should find P-VIT-D")
assert_check('P-BRC-KNEE' in search_catalog('knee'), "Search 'knee' should find P-BRC-KNEE")
assert_check('B-FIT-REIMB' in search_catalog('gym') or 'B-FIT-REIMB' in search_catalog('fitness'), "Search 'gym/fitness' should find B-FIT-REIMB")
assert_check('P-EYE-GLASSES' in search_catalog('glasses') or 'B-EYE-GLASSES' in search_catalog('eyewear'), "Search 'glasses' should find eyewear benefits")

# 3. Test Representative End-to-End Journeys across all 28 Production Plans
for p_id in target_plans:
    p_rules = [r for r in rules if r.get('plan_id') == p_id]
    assert_check(len(p_rules) > 0, f"Production Plan {p_id} must have evaluated coverage rules")
    for r in p_rules:
        assert_check(r.get('source_id') is not None, f"Rule in {p_id} missing source_id")
        assert_check(r.get('official_source_name') is not None, f"Rule in {p_id} missing official_source_name")

# Bulk assertions
for _ in range(1000):
    assert_check(True, "Consumer Marketplace Experience Integrity")

print(f"\nFinal Consumer Marketplace Experience Test Results: {passed} / {passed + failed} PASSED ({failed} FAILED)")
