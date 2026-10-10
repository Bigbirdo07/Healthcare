import json

with open('scratch/marketplace_dump.json', 'r', encoding='utf-8') as f:
    dump = json.load(f)

plans = dump['PLANS']
rules = dump['COVERAGE_RULES']

def is_production(p):
    if p.get('is_test_fixture') is True or p.get('id') == 'zero_rule_test_plan' or p.get('id') == 'generic_unselected_plan':
        return False
    if p.get('production_visibility') is False:
        return False
    stat = p.get('plan_identity_status') or p.get('source_status')
    if stat in ['SOURCE_CONFIRMED', 'ACTIVE']:
        return True
    return False

prod_plans = [p for p in plans if is_production(p)]

print(f"Total Confirmed Production Plans across New England: {len(prod_plans)}")

by_state = {}
for p in prod_plans:
    st = p.get('state', 'UNKNOWN')
    if st not in by_state:
        by_state[st] = []
    by_state[st].append(p)

for st, p_list in sorted(by_state.items()):
    print(f"\n==================== State: {st} ({len(p_list)} plans) ====================")
    for p in p_list:
        p_id = p.get('id')
        name = p.get('official_plan_name') or p.get('display_name')
        r_count = len([r for r in rules if r.get('plan_id') == p_id])
        print(f"  [{p_id:36s}] Rules: {r_count:3d} | {name}")
