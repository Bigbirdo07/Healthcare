import json

with open('scratch/marketplace_dump.json', 'r', encoding='utf-8') as f:
    dump = json.load(f)

PLANS = dump['PLANS']

def get_insurance_selector_options(state=None, card_type=None, insurer_id=None):
    prod_plans = [p for p in PLANS if p.get('production_visibility', True) and p.get('source_status') != 'HIDDEN' and p.get('id') not in ('zero_rule_test_plan', 'generic_unselected_plan')]
    
    states = ['RI', 'MA', 'CT', 'NH', 'ME', 'VT']
    if not state:
        return {'states': states, 'card_types': [], 'insurers': [], 'plans': []}
    
    state_plans = [p for p in prod_plans if p.get('state') == state or p.get('state') == 'All Areas']
    
    def is_medicaid(p):
        cat = (p.get('insurance_category') or p.get('plan_type') or '').upper()
        seg = (p.get('market_segment') or '').upper()
        snp = (p.get('snp_type') or '').upper()
        name = (p.get('official_plan_name') or p.get('display_name') or '').upper()
        return 'MEDICAID' in cat or 'CHIP' in cat or 'D_SNP' in cat or 'DUAL' in cat or 'MEDICAID' in seg or 'CHIP' in seg or 'DUAL' in snp or 'D-SNP' in snp or 'D-SNP' in name or 'DUAL' in name
    
    has_medicaid = any(is_medicaid(p) for p in state_plans)
    has_insurance = any(not is_medicaid(p) for p in state_plans)
    
    card_types = []
    if has_insurance: card_types.append({'id': 'INSURANCE_CARD', 'label': 'Insurance card'})
    if has_medicaid: card_types.append({'id': 'MEDICAID_CARD', 'label': 'Medicaid card'})
    
    if not card_type:
        return {'states': states, 'card_types': card_types, 'insurers': [], 'plans': []}
    
    type_plans = [p for p in state_plans if (is_medicaid(p) if card_type == 'MEDICAID_CARD' else not is_medicaid(p))]
    
    insurer_map = {}
    for p in type_plans:
        ins_id = p.get('insurer_id') or p.get('insurer') or 'unknown'
        ins_name = p.get('insurer_name') or p.get('insurer') or ins_id
        if ins_id not in insurer_map:
            insurer_map[ins_id] = {'id': ins_id, 'name': ins_name}
    
    insurers = sorted(list(insurer_map.values()), key=lambda x: x['name'])
    
    if not insurer_id:
        return {'states': states, 'card_types': card_types, 'insurers': insurers, 'plans': []}
    
    plans = sorted([
        {
            'id': p['id'],
            'name': p.get('official_plan_name') or p.get('display_name') or p['id'],
            'insurer_id': p.get('insurer_id'),
            'state': p.get('state')
        }
        for p in type_plans if p.get('insurer_id') == insurer_id or p.get('insurer') == insurer_id
    ], key=lambda x: x['name'])
    
    return {'states': states, 'card_types': card_types, 'insurers': insurers, 'plans': plans}

passed = 0
failed = 0

def assert_check(cond, msg):
    global passed, failed
    if cond:
        passed += 1
    else:
        failed += 1
        print(f"FAILED: {msg}")

# CASE A: Massachusetts -> Insurance card -> Harvard Pilgrim Health Care
case_a = get_insurance_selector_options('MA', 'INSURANCE_CARD', 'harvard_pilgrim')
assert_check(len(case_a['plans']) > 0, "Case A should return valid MA Harvard Pilgrim plans")
assert_check(all(p['state'] == 'MA' for p in case_a['plans']), "Case A plans must all belong to MA")
assert_check(all(p['insurer_id'] == 'harvard_pilgrim' for p in case_a['plans']), "Case A plans must all be Harvard Pilgrim")

# CASE B: Rhode Island -> Insurance card -> Blue Cross & Blue Shield of RI
case_b = get_insurance_selector_options('RI', 'INSURANCE_CARD', 'blue_cross_blue_shield_of_rhode_island')
assert_check(len(case_b['plans']) > 0, "Case B should return valid RI BCBSRI plans")
assert_check(all(p['state'] == 'RI' for p in case_b['plans']), "Case B plans must all belong to RI")
assert_check(all(p['insurer_id'] == 'blue_cross_blue_shield_of_rhode_island' for p in case_b['plans']), "Case B plans must all be BCBSRI")

# CASE C: Rhode Island -> Medicaid card -> Neighborhood Health Plan of RI
case_c = get_insurance_selector_options('RI', 'MEDICAID_CARD', 'neighborhood')
assert_check(len(case_c['plans']) >= 1, "Case C should return valid Neighborhood Medicaid/D-SNP plans")
assert_check(any(p['id'] == 'ri_neighborhood_integria' for p in case_c['plans']), "Case C should include ri_neighborhood_integria")

# Verify NO commercial BCBSRI plans leak into Case C!
bcbsri_leaks = [p for p in case_c['plans'] if 'bcbs' in p['id'].lower() or 'basicblue' in p['name'].lower()]
assert_check(len(bcbsri_leaks) == 0, "Case C MUST NOT contain any BCBSRI commercial plans")

# CASE D: Rhode Island -> Medicaid card -> UnitedHealthcare
case_d = get_insurance_selector_options('RI', 'MEDICAID_CARD', 'unitedhealthcare')
assert_check(len(case_d['plans']) >= 1, "Case D should return UHC Medicaid/Dual plan")
assert_check(any(p['id'] == 'ri_uhc_dual_complete' for p in case_d['plans']), "Case D should include ri_uhc_dual_complete")

# CASE E: Switch Card Type (Insurance card -> Medicaid card)
res_ins = get_insurance_selector_options('RI', 'INSURANCE_CARD')
res_med = get_insurance_selector_options('RI', 'MEDICAID_CARD')
ins_ids_ins = [i['id'] for i in res_ins['insurers']]
ins_ids_med = [i['id'] for i in res_med['insurers']]
assert_check(ins_ids_ins != ins_ids_med, "Card type switch MUST regenerate insurer list")

print(f"\nUnified Selector Engine Test Results: {passed} / {passed + failed} PASSED ({failed} FAILED)")
if failed > 0:
    exit(1)
