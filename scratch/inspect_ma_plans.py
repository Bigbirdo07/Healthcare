import json

with open('scratch/marketplace_dump.json', 'r', encoding='utf-8') as f:
    dump = json.load(f)

plans = dump['PLANS']
rules = dump['COVERAGE_RULES']

ma_plans = [p for p in plans if p.get('state') == 'MA']
print(f"Total MA plans in PLANS: {len(ma_plans)}")
for p in ma_plans:
    p_id = p.get('id')
    name = p.get('official_plan_name') or p.get('display_name')
    r_count = len([r for r in rules if r.get('plan_id') == p_id])
    stat = p.get('plan_identity_status') or p.get('source_status')
    vis = p.get('production_visibility')
    print(f"  [{p_id:45s}] Rules: {r_count:2d} | stat={str(stat):16s} | vis={str(vis):5s} | {name}")
