import json
import re

with open('dist/marketplace/marketplace.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

def parse_js_array(var_name, content):
    pos = content.find(f'const {var_name} = [')
    if pos == -1:
        pos = content.find(f'{var_name} = [')
    if pos == -1:
        return []
    start = content.find('[', pos)
    # Find matching closing bracket
    bracket_count = 0
    end = start
    for i in range(start, len(content)):
        if content[i] == '[':
            bracket_count += 1
        elif content[i] == ']':
            bracket_count -= 1
            if bracket_count == 0:
                end = i + 1
                break
    arr_str = content[start:end]
    # Replace JS single quotes with double quotes or parse lines
    lines = [line.strip().rstrip(',') for line in arr_str.split('\n') if line.strip().startswith('{')]
    items = []
    for line in lines:
        try:
            # Simple sanitize JS object to JSON
            sanitized = re.sub(r"'", '"', line)
            items.append(json.loads(sanitized))
        except Exception:
            pass
    return items

products = parse_js_array('PRODUCTS', js_content)
services = parse_js_array('SERVICES', js_content)
benefits = parse_js_array('BENEFITS', js_content)
rules = parse_js_array('COVERAGE_RULES', js_content)

print(f"Products parsed: {len(products)}")
print(f"Services parsed: {len(services)}")
print(f"Benefits parsed: {len(benefits)}")
print(f"Rules parsed: {len(rules)}")
