import re, json

with open('dist/marketplace/marketplace.js', 'r', encoding='utf-8') as f:
    js_text = f.read()

# Extract PRODUCTS block
prod_match = re.search(r'const PRODUCTS = (\[.*?\]);\s*\n\s*// --- 5\.', js_text, re.DOTALL)
if not prod_match:
    prod_match = re.search(r'const PRODUCTS = (\[.*?\]);', js_text, re.DOTALL)

products_js = prod_match.group(1)

# Extract COVERAGE_RULES block
rules_match = re.search(r'const COVERAGE_RULES = (\[.*?\]);\s*\n\s*// --- 6\.', js_text, re.DOTALL)
rules_js = rules_match.group(1)

# Parse products
products_id = re.findall(r'id:\s*\'([^\']+)\'', products_js)
print(f"Total Catalog Items: {len(products_id)}")

# Extract variants count
variants = re.findall(r'name:\s*\'([^\']+)\'', products_js)
print(f"Variants listed: {len(variants)}")

# Extract rules count
rule_ids = re.findall(r'rule_id:\s*\'([^\']+)\'', rules_js)
print(f"Total Rules listed: {len(rule_ids)}")
