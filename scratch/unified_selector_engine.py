import json, re

# Read extracted_data.js or dump for PLANS
with open('scratch/marketplace_dump.json', 'r', encoding='utf-8') as f:
    dump = json.load(f)

plans_json = json.dumps(dump['PLANS'])

# Shared Selector JS Core
shared_selector_code = f"""
// --- SHARED INSURANCE SELECTOR ENGINE ---
window.PLANS = {plans_json};

window.getInsuranceSelectorOptions = function(opts) {{
  const state = opts ? opts.state : null;
  const cardType = opts ? opts.cardType : null;
  const insurerId = opts ? opts.insurerId : null;

  const prodPlans = window.PLANS.filter(p => 
    p.production_visibility !== false && 
    !p.is_test_fixture && 
    p.environment !== 'TEST' && 
    p.source_status !== 'HIDDEN' &&
    p.id !== 'zero_rule_test_plan' &&
    p.id !== 'generic_unselected_plan'
  );

  const states = ['RI', 'MA', 'CT', 'NH', 'ME', 'VT'];
  if (!state) return {{ states, cardTypes: [], insurers: [], plans: [] }};

  const statePlans = prodPlans.filter(p => p.state === state || p.state === 'All Areas');

  function isMedicaidPlan(p) {{
    const cat = (p.insurance_category || p.plan_type || '').toUpperCase();
    return cat.includes('MEDICAID') || cat.includes('CHIP') || cat.includes('D_SNP') || cat.includes('DUAL');
  }}

  const hasMedicaid = statePlans.some(p => isMedicaidPlan(p));
  const hasInsurance = statePlans.some(p => !isMedicaidPlan(p));

  const cardTypes = [];
  if (hasInsurance) cardTypes.push({{ id: 'INSURANCE_CARD', label: 'Insurance card' }});
  if (hasMedicaid) cardTypes.push({{ id: 'MEDICAID_CARD', label: 'Medicaid card' }});

  if (!cardType) return {{ states, cardTypes, insurers: [], plans: [] }};

  const typePlans = statePlans.filter(p => cardType === 'MEDICAID_CARD' ? isMedicaidPlan(p) : !isMedicaidPlan(p));

  const insurerMap = {{}};
  typePlans.forEach(p => {{
    const insId = p.insurer_id || p.insurer || 'unknown';
    let insName = p.insurer_name || p.insurer || insId;
    if (insName.includes('from NH Healthy Families')) insName = insName.replace(' from NH Healthy Families', '');
    if (!insurerMap[insId]) {{
      insurerMap[insId] = {{ id: insId, name: insName }};
    }}
  }});

  const insurers = Object.values(insurerMap).sort((a, b) => a.name.localeCompare(b.name));
  if (!insurerId) return {{ states, cardTypes, insurers, plans: [] }};

  const plans = typePlans
    .filter(p => p.insurer_id === insurerId || p.insurer === insurerId)
    .map(p => ({{
      id: p.id,
      name: p.official_plan_name || p.display_name || p.name || p.id,
      insurer_id: p.insurer_id,
      state: p.state
    }}))
    .sort((a, b) => a.name.localeCompare(b.name));

  return {{ states, cardTypes, insurers, plans }};
}};
"""

with open('scratch/shared_selector.js', 'w', encoding='utf-8') as f:
    f.write(shared_selector_code)

print("Shared selector code generated.")
