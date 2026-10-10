import json
import re

with open('dist/marketplace/marketplace.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

match = re.search(r'const COVERAGE_RULES = \[\s*(.*?)\s*\];', js_content, re.DOTALL)
rule_lines = [line.strip().rstrip(',') for line in match.group(1).split('\n') if line.strip().startswith('{')]

core_rules = []
for line in rule_lines:
    try:
        rule = json.loads(line)
        if rule.get('plan_id') == 'bcbsri_bluechip_core_2026':
            core_rules.append(rule)
    except Exception as e:
        pass

# Group by target
targets = {}
for r in core_rules:
    t_id = r.get('product_id') or r.get('service_id') or r.get('benefit_id') or r.get('target_id')
    if t_id not in targets:
        targets[t_id] = []
    targets[t_id].append(r)

print(f"Total unique target entities mapped for bcbsri_bluechip_core_2026: {len(targets)}")
for t_id, r_list in sorted(targets.items()):
    statuses = [r.get('coverage_status') for r in r_list]
    print(f"Target: {t_id:20s} | Rule Count: {len(r_list)} | Statuses: {statuses}")
