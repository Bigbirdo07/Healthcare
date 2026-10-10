import re
import json

with open('dist/marketplace/marketplace.js', 'r') as f:
    text = f.read()

# find PLANS block
start_idx = text.find('const PLANS = [')
end_idx = text.find('];', start_idx)
plans_str = text[start_idx + len('const PLANS = '):end_idx + 1]

# parse JS array using JS engine or basic eval in python via node
import subprocess
result = subprocess.run(
    ["node", "-e", f"const plans = {plans_str}; console.log(JSON.stringify(plans));"],
    capture_output=True, text=True
)

plans = json.loads(result.stdout)
print(f"Loaded {len(plans)} plans from repository.")

with open('scratch/repo_plans.json', 'w') as f:
    json.dump(plans, f, indent=2)

print("Saved to scratch/repo_plans.json")
