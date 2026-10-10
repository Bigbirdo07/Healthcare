import json
import re
from pathlib import Path

print("Building Phase 15 Plan Filtering & Card Isolation Engine...")

js_file = Path('dist/marketplace/marketplace.js')
js_text = js_file.read_text()

# 1. ADD ZERO-RULE TEST PLAN FOR ZERO-RULE SELECTABILITY VALIDATION
ZERO_RULE_PLAN_JS = """  {
    id: 'zero_rule_test_plan', insurer_id: 'bcbsri', insurer_name: 'Blue Cross & Blue Shield of Rhode Island',
    official_plan_name: 'BCBSRI Zero-Rule Validation Plan (2026)', display_name: 'BCBSRI Zero-Rule Validation Plan', plan_year: 2026,
    state: 'RI', plan_type: 'Medicare Advantage', insurance_category: 'MEDICARE_ADVANTAGE', network_type: 'Statewide Network',
    market_segment: 'Individual Medicare', service_area: 'Statewide RI', source_status: 'ACTIVE',
    plan_identity_status: 'SOURCE_CONFIRMED', coverage_verification_status: 'UNVERIFIED', is_verified: false,
    production_visibility: true, aliases: ['Zero-Rule Validation Plan', 'BCBSRI Zero Rule']
  },"""

if 'zero_rule_test_plan' not in js_text:
    idx = js_text.find('const PLANS = [')
    if idx != -1:
        js_text = js_text[:idx + len('const PLANS = [')] + '\n' + ZERO_RULE_PLAN_JS + js_text[idx + len('const PLANS = ['):]

# 2. UPDATE EVALUATE COVERAGE RULE TO CHECK APPLICABLE_PLAN_IDS PROPERLY
OLD_EVAL_FUNC = """    const found = COVERAGE_RULES.find((r) => r.product_id === productId && r.plan_id === planId);
    if (found) return found;"""

NEW_EVAL_FUNC = """    const found = COVERAGE_RULES.find((r) => 
      (r.product_id === productId || r.service_id === productId || r.target_id === productId) && 
      (r.plan_id === planId || (r.applicable_plan_ids && Array.isArray(r.applicable_plan_ids) && r.applicable_plan_ids.includes(planId)))
    );
    if (found) return found;"""

if OLD_EVAL_FUNC in js_text:
    js_text = js_text.replace(OLD_EVAL_FUNC, NEW_EVAL_FUNC)

# 3. ADD PLAN REVALIDATION LOGIC ON ACTIVE PLAN CHANGE
REVAL_JS = """        // Revalidate request workflow items if active plan changes
        if (typeof revalidateProviderRequests === 'function') {
          revalidateProviderRequests(activePlanId);
        }"""

if 'activePlanId = e.target.value;' in js_text and 'revalidateProviderRequests' not in js_text:
    js_text = js_text.replace(
      "activePlanId = e.target.value;",
      "activePlanId = e.target.value;\n" + REVAL_JS
    )

js_file.write_text(js_text)
print("Successfully built Phase 15 Plan Filtering & Card Isolation into marketplace.js.")
