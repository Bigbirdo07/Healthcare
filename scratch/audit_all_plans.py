import json
import re
from pathlib import Path

js_content = Path('dist/marketplace/marketplace.js').read_text()

# Extract arrays from JS
def extract_array_block(var_name, text):
    pattern = rf'const {var_name}\s*=\s*(\[.*?\]);'
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return []
    block = match.group(1)
    # clean comments
    block = re.sub(r'//.*?\n', '\n', block)
    block = re.sub(r'/\*.*?\*/', '', block, flags=re.DOTALL)
    # convert JS object keys to json keys
    block = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)\s*:', r'\1"\2":', block)
    block = block.replace("'", '"')
    # fix trailing commas
    block = re.sub(r',\s*([\]}])', r'\1', block)
    try:
        return json.loads(block)
    except Exception as e:
        print(f"Error parsing {var_name}: {e}")
        return []

insurers_js = extract_array_block('INSURERS', js_content)
plans_js = extract_array_block('PLANS', js_content)
sources_js = extract_array_block('SOURCE_DOCUMENTS', js_content)
rules_js = extract_array_block('COVERAGE_RULES', js_content)

print(f"=== MARKETPLACE.JS AUDIT ===")
print(f"Insurers count: {len(insurers_js)}")
print(f"Plans count: {len(plans_js)}")
print(f"Source docs count: {len(sources_js)}")
print(f"Coverage rules count: {len(rules_js)}")

print("\n--- INSURERS ---")
for ins in insurers_js:
    print(f"  [{ins.get('id')}] {ins.get('name')} (Code: {ins.get('code')}, States: {ins.get('states')})")

print("\n--- PLANS IN MARKETPLACE.JS ---")
for p in plans_js:
    print(f"  [{p.get('state')}] {p.get('id')}: {p.get('insurer_name')} - {p.get('official_plan_name')} (Type: {p.get('plan_type')}, Year: {p.get('plan_year')})")

print("\n--- SOURCE DOCUMENTS IN MARKETPLACE.JS ---")
for s in sources_js:
    print(f"  [{s.get('state', 'RI')}] {s.get('id')}: {s.get('publisher')} - {s.get('title')} (Plan: {s.get('plan_id')}, Year: {s.get('plan_year')})")

# Also check dist/data.json
d = json.loads(Path('dist/data.json').read_text())

print(f"\n=== DIST/DATA.JSON AUDIT ===")
print(f"Plans in dist/data.json: {len(d.get('plans', []))}")
print(f"Extras in dist/data.json: {len(d.get('extras', []))}")

by_state_data_json = {}
for p in d.get('plans', []):
    st = p.get('state', 'UNKNOWN')
    by_state_data_json.setdefault(st, []).append(p)

for st, plist in sorted(by_state_data_json.items()):
    print(f"\nState: {st} ({len(plist)} plans)")
    issuers = {}
    for p in plist:
        iss = p.get('issuer', 'UNKNOWN')
        issuers.setdefault(iss, []).append(p.get('name'))
    for iss, pnames in issuers.items():
        print(f"  Insurer: {iss} ({len(pnames)} plans)")
        for name in pnames[:3]:
            print(f"    - {name}")
        if len(pnames) > 3:
            print(f"    ... +{len(pnames)-3} more")

