import re, json

with open('dist/marketplace/marketplace.js', 'r', encoding='utf-8') as f:
    js_text = f.read()

# Parse counts
sources = re.findall(r'source_id:\s*\'(SRC-[^\']+)\'', js_text)
source_count = len(set(sources))

rules = re.findall(r'rule_id:\s*\'(R-[^\']+)\'', js_text)
rule_count = len(set(rules))

unresolved = re.findall(r'match_id:\s*\'(UM-[^\']+)\'', js_text)
unresolved_count = len(set(unresolved))

candidates = re.findall(r'candidate_rule_id:\s*\'(CAN-[^\']+)\'', js_text)
candidate_count = len(set(candidates))

print("PHASE 3 INGESTION AUDIT METRICS:")
print(f"Official Source Documents Ingested : {source_count}")
print(f"Approved Verified Rules            : {rule_count}")
print(f"Candidate Rules In Pipeline        : {candidate_count}")
print(f"Unresolved Product Matches         : {unresolved_count}")
