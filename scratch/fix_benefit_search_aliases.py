import re

with open('dist/marketplace/marketplace.js', 'r', encoding='utf-8') as f:
    js_text = f.read()

# Update B-FIT-REIMB in BENEFITS array to include aliases and keywords
old_b_fit = r"id: 'B-FIT-REIMB', benefit_name: 'Fitness Program Benefit'.*?\}"
new_b_fit = "id: 'B-FIT-REIMB', benefit_name: 'Fitness Program Benefit', category: 'fitness', benefit_type: 'Fitness & Wellness', description: 'SilverSneakers network fitness membership & gym access.', aliases: ['gym', 'fitness', 'gym membership', 'silversneakers', 'workout']}"

js_text = re.sub(old_b_fit, new_b_fit, js_text, flags=re.DOTALL)

with open('dist/marketplace/marketplace.js', 'w', encoding='utf-8') as f:
    f.write(js_text)

print("Updated B-FIT-REIMB search aliases in marketplace.js cleanly.")
