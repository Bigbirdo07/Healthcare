import json
import re
from pathlib import Path

print("Building Phase 16 Plan Inventory Reconciliation & Production Cleanup Engine...")

js_file = Path('dist/marketplace/marketplace.js')
js_text = js_file.read_text()

# 1. SET ZERO-RULE TEST PLAN PRODUCTION_VISIBILITY TO FALSE & MARK AS TEST FIXTURE
if 'id: \'zero_rule_test_plan\'' in js_text:
    js_text = js_text.replace(
        "id: 'zero_rule_test_plan', insurer_id: 'bcbsri', insurer_name: 'Blue Cross & Blue Shield of Rhode Island',\n    official_plan_name: 'BCBSRI Zero-Rule Validation Plan (2026)', display_name: 'BCBSRI Zero-Rule Validation Plan', plan_year: 2026,\n    state: 'RI', plan_type: 'Medicare Advantage', insurance_category: 'MEDICARE_ADVANTAGE', network_type: 'Statewide Network',\n    market_segment: 'Individual Medicare', service_area: 'Statewide RI', source_status: 'ACTIVE',\n    plan_identity_status: 'SOURCE_CONFIRMED', coverage_verification_status: 'UNVERIFIED', is_verified: false,\n    production_visibility: true, aliases: ['Zero-Rule Validation Plan', 'BCBSRI Zero Rule']",
        "id: 'zero_rule_test_plan', insurer_id: 'bcbsri', insurer_name: 'Blue Cross & Blue Shield of Rhode Island',\n    official_plan_name: 'BCBSRI Zero-Rule Validation Plan (2026)', display_name: 'BCBSRI Zero-Rule Validation Plan', plan_year: 2026,\n    state: 'RI', plan_type: 'Medicare Advantage', insurance_category: 'MEDICARE_ADVANTAGE', network_type: 'Statewide Network',\n    market_segment: 'Individual Medicare', service_area: 'Statewide RI', source_status: 'SOURCE_CONFIRMED',\n    plan_identity_status: 'SOURCE_CONFIRMED', coverage_verification_status: 'UNVERIFIED', is_verified: false,\n    production_visibility: false, is_test_fixture: true, environment: 'TEST', aliases: ['Zero-Rule Validation Plan', 'BCBSRI Zero Rule']"
    )

# 2. UPDATE PLAN DROPDOWN FILTERING TO STRICTLY HIDE TEST FIXTURES & UNAPPROVED PLANS
OLD_UPDATE_FUNC = """      const filteredPlans = PLANS.filter(p => {
        const stateOk = p.state === selectedState || p.state === 'All Areas' || selectedState === 'RI';
        const typeOk = selectedType === 'all' || p.plan_type === selectedType;
        return stateOk && typeOk;
      });"""

NEW_UPDATE_FUNC = """      const filteredPlans = PLANS.filter(p => {
        const stateOk = p.state === selectedState || p.state === 'All Areas' || selectedState === 'RI';
        const typeOk = selectedType === 'all' || p.plan_type === selectedType;
        const visOk = p.production_visibility !== false && !p.is_test_fixture && p.environment !== 'TEST';
        return stateOk && typeOk && visOk;
      });"""

if OLD_UPDATE_FUNC in js_text:
    js_text = js_text.replace(OLD_UPDATE_FUNC, NEW_UPDATE_FUNC)

js_file.write_text(js_text)
print("Successfully built Phase 16 Inventory Reconciliation into marketplace.js.")
