import re, json

with open('dist/marketplace/marketplace.js', 'r', encoding='utf-8') as f:
    js_text = f.read()

# 1. DEPARTMENTS
dept_block = re.search(r'const DEPARTMENTS = (\[.*?\]);', js_text, re.DOTALL).group(1)
dept_count = len(re.findall(r'id:\s*\'([^\']+)\'', dept_block))
print(f"DEPARTMENTS COUNT: {dept_count - 1}") # subtract 'all'

# 2. PLANS
plans_block = re.search(r'const PLANS = (\[.*?\]);', js_text, re.DOTALL).group(1)
plan_ids = re.findall(r'id:\s*\'([^\']+)\'', plans_block)
print(f"PLANS COUNT: {len(plan_ids)}")

# 3. SOURCE_DOCUMENTS
sources_block = re.search(r'const SOURCE_DOCUMENTS = (\[.*?\]);', js_text, re.DOTALL).group(1)
source_ids = re.findall(r'source_id:\s*\'([^\']+)\'', sources_block)
print(f"SOURCE DOCUMENTS COUNT: {len(source_ids)}")

# 4. PRODUCTS
products_block = re.search(r'const PRODUCTS = (\[.*?\]);', js_text, re.DOTALL).group(1)
prod_ids = re.findall(r'id:\s*\'(P-[^\']+)\'', products_block)
print(f"PRODUCTS COUNT: {len(prod_ids)}")

# Variants count inside products
variants = re.findall(r'sku:\s*\'(SKU-[^\']+)\'', products_block)
print(f"VARIANTS COUNT: {len(variants)}")

# Aliases count inside products
aliases_matches = re.findall(r'aliases:\s*\[(.*?)\]', products_block)
total_aliases = 0
for a in aliases_matches:
    total_aliases += len([x for x in a.split(',') if x.strip()])
print(f"ALIASES COUNT: {total_aliases}")

# 5. SERVICES
services_block = re.search(r'const SERVICES = (\[.*?\]);', js_text, re.DOTALL).group(1)
serv_ids = re.findall(r'id:\s*\'(S-[^\']+)\'', services_block)
print(f"SERVICES COUNT: {len(serv_ids)}")

# Rules count
rules = re.findall(r'rule_id:\s*\'(R-[^\']+)\'', products_block + services_block)
print(f"TOTAL COVERAGE RULES: {len(rules)}")

v_status = re.findall(r'verification_status:\s*\'([^\']+)\'', products_block + services_block)
from collections import Counter
status_counts = Counter(v_status)
print("VERIFICATION STATUS COUNTS:", dict(status_counts))

conf_levels = re.findall(r'evidence_confidence:\s*\'([^\']+)\'', products_block + services_block)
conf_counts = Counter(conf_levels)
print("CONFIDENCE COUNTS:", dict(conf_counts))
