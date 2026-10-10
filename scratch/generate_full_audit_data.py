import json, re

# Read marketplace.js
with open('dist/marketplace/marketplace.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# Read old script to get previous 92 products
with open('scratch/generate_marketplace_js.py', 'r', encoding='utf-8') as f:
    old_script = f.read()

old_skus = re.findall(r'sku:\s*\'([^\']+)\',\s*name:\s*\'([^\']+)\'', old_script)

# Extract counts from current marketplace.js
dept_matches = re.findall(r'id:\s*\'DEPT-[^\']+\',\s*name:\s*\'([^\']+)\'', js_content)
print(f"Total Departments: {len(dept_matches)}")

prod_matches = re.findall(r'id:\s*\'P-[^\']+\'', js_content)
print(f"Total Normalized Products: {len(prod_matches)}")

serv_matches = re.findall(r'id:\s*\'S-[^\']+\'', js_content)
print(f"Total Services: {len(serv_matches)}")

doc_matches = re.findall(r'id:\s*\'SRC-[^\']+\'', js_content)
print(f"Total Source Documents: {len(doc_matches)}")

variant_matches = re.findall(r'sku:\s*\'SKU-[^\']+\'', js_content)
print(f"Total Variants: {len(variant_matches)}")

alias_matches = re.findall(r'aliases:\s*\[(.*?)\]', js_content)
total_aliases = 0
for a in alias_matches:
    total_aliases += len([x for x in a.split(',') if x.strip()])
print(f"Total Aliases: {total_aliases}")

verified_rules = len(re.findall(r'verification_status:\s*\'VERIFIED\'', js_content))
partially_verified_rules = len(re.findall(r'verification_status:\s*\'PARTIALLY_SUPPORTED\'', js_content))
needs_verification_rules = len(re.findall(r'verification_status:\s*\'NEEDS_VERIFICATION\'', js_content))
unsupported_rules = len(re.findall(r'verification_status:\s*\'UNSUPPORTED\'', js_content))
stale_rules = len(re.findall(r'verification_status:\s*\'STALE\'', js_content))

total_rules = verified_rules + partially_verified_rules + needs_verification_rules + unsupported_rules + stale_rules
print(f"Total Coverage Rules: {total_rules}")
print(f"Verified Rules: {verified_rules}")
print(f"Partially Supported Rules: {partially_verified_rules}")
print(f"Needs Verification Rules: {needs_verification_rules}")
print(f"Unsupported Rules: {unsupported_rules}")
print(f"Stale Rules: {stale_rules}")
