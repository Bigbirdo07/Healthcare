import json
import re
from pathlib import Path

# Load dist/data.json
d_json = json.loads(Path('dist/data.json').read_text())

# Load marketplace.js
js_text = Path('dist/marketplace/marketplace.js').read_text()

# Collect all plans from dist/data.json
plans_data_json = d_json.get('plans', [])
extras_data_json = d_json.get('extras', [])

print(f"Total plans in dist/data.json: {len(plans_data_json)}")
print(f"Total extras in dist/data.json: {len(extras_data_json)}")

# Group plans by state
by_state = {}
for p in plans_data_json:
    st = p.get('state', 'UNKNOWN')
    by_state.setdefault(st, []).append(p)

for st in ['RI', 'MA', 'CT', 'NH', 'VT', 'ME']:
    plist = by_state.get(st, [])
    print(f"\n==================== STATE: {st} (Count: {len(plist)}) ====================")
    insurers = {}
    for p in plist:
        iss = p.get('issuer', 'UNKNOWN')
        insurers.setdefault(iss, []).append(p)
    for iss, items in insurers.items():
        print(f"  Insurer: {iss} ({len(items)} plans)")
        unique_names = set(x.get('name') for x in items)
        if len(unique_names) < len(items):
            print(f"    ⚠️ DUPLICATES DETECTED: {len(items)} total records, but only {len(unique_names)} unique names!")
        for uname in list(unique_names)[:5]:
            count = sum(1 for x in items if x.get('name') == uname)
            print(f"      - {uname} (x{count} records)")
        if len(unique_names) > 5:
            print(f"      ... and {len(unique_names)-5} more unique names")

# Inspect extras for Medicaid / Special programs
print("\n==================== EXTRAS / MEDICAID / SPECIAL PROGRAMS ====================")
by_state_extras = {}
for x in extras_data_json:
    st = x.get('state', 'UNKNOWN')
    by_state_extras.setdefault(st, []).append(x)

for st in ['RI', 'MA', 'CT', 'NH', 'VT', 'ME']:
    xlist = by_state_extras.get(st, [])
    print(f"\nState {st} Extras ({len(xlist)}):")
    for x in xlist:
        print(f"  - [{x.get('coverage')}] Plan: {x.get('plan')}, Category: {x.get('category')}, Benefit: {x.get('benefit')}")

