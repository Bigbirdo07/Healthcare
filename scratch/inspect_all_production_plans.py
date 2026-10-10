import json

with open('scratch/marketplace_dump.json', 'r', encoding='utf-8') as f:
    dump = json.load(f)

plans = dump['PLANS']

print(f"Total plans in PLANS: {len(plans)}")

by_state = {}
for p in plans:
    st = p.get('state', 'UNKNOWN')
    if st not in by_state:
        by_state[st] = []
    by_state[st].append(p)

for st, p_list in sorted(by_state.items()):
    print(f"\nState: {st} ({len(p_list)} total plans)")
    for p in p_list:
        p_id = p.get('id') or p.get('plan_id')
        name = p.get('official_plan_name') or p.get('display_name')
        p_vis = p.get('production_visibility')
        p_stat = p.get('plan_identity_status')
        env = p.get('environment')
        print(f"  • {p_id:40s} | vis={str(p_vis):5s} | stat={str(p_stat):18s} | env={str(env):6s} | {name}")
