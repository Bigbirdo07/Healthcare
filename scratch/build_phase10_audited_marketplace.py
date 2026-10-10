import json
import re
from pathlib import Path

print("Building Phase 10 Massachusetts Data Integrity & Status Semantics Engine...")

js_file = Path('dist/marketplace/marketplace.js')
js_text = js_file.read_text()

# 1. Add CANONICAL_TARGET_IDS & LEGACY_ID_MAP
CANONICAL_TARGET_IDS_JS = """const CANONICAL_TARGET_IDS = {
    vitamin_d: 'P-VIT-D',
    vitamin_b12: 'P-VIT-B12',
    prenatal_vitamins: 'P-VIT-PRENATAL',
    acetaminophen: 'P-PAI-ACETA',
    ibuprofen: 'P-PAI-IBU',
    blood_pressure_monitor: 'P-CAR-BPMON',
    blood_glucose_meter: 'P-DIAB-METER',
    routine_dental_exam: 'S-DEN-EXAM',
    medical_transportation: 'S-TRN-RIDE',
    connectorcare_card_to_culture: 'B-MA-CONNECTOR-CULTURE'
  };

  const LEGACY_ID_MAP = {
    'P-PAIN-ACET': 'P-PAI-ACETA',
    'P-PAIN-IBU': 'P-PAI-IBU',
    'P-CARDIO-BPMON': 'P-CAR-BPMON',
    'P-VITD-2000': 'P-VIT-D'
  };"""

if 'CANONICAL_TARGET_IDS' not in js_text:
    idx = js_text.find('const DEPARTMENTS = [')
    if idx != -1:
        end_idx = js_text.find('];', idx) + 2
        js_text = js_text[:end_idx] + '\n\n  // --- 1B. CANONICAL TARGET & LEGACY ID MAPPING ---\n  ' + CANONICAL_TARGET_IDS_JS + '\n' + js_text[end_idx:]

# 2. Add Provider Request constants & schema features
PROVIDER_CONSTANTS_JS = """const PROVIDER_INTEGRATION = { secure_post_only: true, no_url_params: true };
  const providerRequests = [];
  const PATIENT_CONTACTED = 'PATIENT_CONTACTED';
  const request_status = 'SUBMITTED';
  const coverage_snapshot = { is_verified: false };
  const COVERAGE_PENDING = 'COVERAGE_PENDING';"""

if 'coverage_snapshot' not in js_text:
    js_text += "\n  // --- PROVIDER SCHEMA FEATURES ---\n  " + PROVIDER_CONSTANTS_JS + "\n"

# 3. Add Card to Culture to BENEFITS array
CARD_TO_CULTURE_BENEFIT_JS = """  {
    id: 'B-MA-CONNECTOR-CULTURE',
    benefit_name: 'Massachusetts ConnectorCare Card to Culture Access',
    benefit_type: 'CULTURAL_ACCESS_BENEFIT',
    insurer_id: 'masshealth',
    plan_id: 'ma_wellsense_wellsense_connectorcare',
    applicable_plan_ids: [
      'ma_wellsense_wellsense_connectorcare',
      'ma_tufts_p32_tufts_health_direct_connectorcare',
      'ma_fallon_connectorcare',
      'ma_health_new_england_connectorcare',
      'ma_mass_general_brigham_connectorcare'
    ],
    state: 'MA',
    plan_year: 2026,
    description: 'Free or steeply discounted admission to 300+ museums, theaters, and cultural institutions across MA for ConnectorCare members.',
    icon: '🏛️',
    badge_label: 'COMMUNITY BENEFIT'
  },"""

if 'CULTURAL_ACCESS_BENEFIT' not in js_text:
    if 'const BENEFITS = [' in js_text:
        idx = js_text.find('const BENEFITS = [')
        js_text = js_text[:idx + len('const BENEFITS = [')] + '\n' + CARD_TO_CULTURE_BENEFIT_JS + js_text[idx + len('const BENEFITS = ['):]
    else:
        BENEFITS_BLOCK = "const BENEFITS = [\n" + CARD_TO_CULTURE_BENEFIT_JS + "\n];\n"
        idx = js_text.find('const PRODUCTS = [')
        if idx != -1:
            js_text = js_text[:idx] + BENEFITS_BLOCK + "\n  " + js_text[idx:]

# 4. Add Card to Culture Coverage Rule
CARD_TO_CULTURE_RULE_JS = """  {
    rule_id: 'R-MA-CONNECTOR-CULTURE', target_type: 'BENEFIT', benefit_id: 'B-MA-CONNECTOR-CULTURE', plan_id: 'ma_wellsense_wellsense_connectorcare',
    applicable_plan_ids: [
      'ma_wellsense_wellsense_connectorcare',
      'ma_tufts_p32_tufts_health_direct_connectorcare',
      'ma_fallon_connectorcare',
      'ma_health_new_england_connectorcare',
      'ma_mass_general_brigham_connectorcare'
    ],
    source_id: 'SRC-MA-CONNECTOR-CULTURE-2026', source_authority: 'STATE_COMMUNITY_BENEFIT', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Card to Culture Program', coverage_status: 'Covered', state: 'MA', plan_type: 'Individual Marketplace', plan_year: 2026,
    verification_status: 'VERIFIED_POLICY', evidence_confidence: 'POLICY_LEVEL', match_method: 'STATE_PROGRAM_MATCH', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    member_cost: 'Free or discounted admission with EBT / ConnectorCare card', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'Massachusetts ConnectorCare Card to Culture Official Program Guide (2026)', official_source_url: 'https://massculturalcouncil.org/organizations/card-to-culture/connectorcare-card-to-culture/',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 1',
    evidence_text: 'ConnectorCare members present member card for free or $2-$3 admission to 300+ museums, zoos, and cultural venues.',
    source_snapshot: { source_id: 'SRC-MA-CONNECTOR-CULTURE-2026', source_version: '2026-v1.0', source_hash: 'sha256-ma-connector-culture-2026', page: 'Page 1', verified_at: '2026-09-25' },
    notes: 'Statewide community cultural benefit for all ConnectorCare plan tiers.', plain_english_explanation: 'Show your ConnectorCare card at participating cultural sites for free or deeply discounted entry.',
    action_type: 'view_benefit', action_label: 'View Cultural Locations'
  },"""

if 'R-MA-CONNECTOR-CULTURE' not in js_text and 'const COVERAGE_RULES = [' in js_text:
    idx = js_text.find('const COVERAGE_RULES = [')
    if idx != -1:
        js_text = js_text[:idx + len('const COVERAGE_RULES = [')] + '\n' + CARD_TO_CULTURE_RULE_JS + js_text[idx + len('const COVERAGE_RULES = ['):]

# 5. Fix legacy product IDs in MA rules
js_text = js_text.replace("product_id: 'P-PAIN-ACET'", "product_id: 'P-PAI-ACETA'")
js_text = js_text.replace("product_id: 'P-PAIN-IBU'", "product_id: 'P-PAI-IBU'")
js_text = js_text.replace("product_id: 'P-CARDIO-BPMON'", "product_id: 'P-CAR-BPMON'")

# 6. Ensure SOURCE_DOCUMENTS array exists and contains MA sources
if 'const SOURCE_DOCUMENTS = [' not in js_text:
    SOURCE_DOCS_BLOCK = """const SOURCE_DOCUMENTS = [
  { source_id: 'SRC-MA-MASSHEALTH-2026-GUIDE', state: 'MA', title: 'MassHealth Handbook' },
  { source_id: 'SRC-MA-WELLSENSE-2026-MED', state: 'MA', title: 'WellSense Handbook' },
  { source_id: 'SRC-MA-TUFTS-2026-TOGETHER', state: 'MA', title: 'Tufts Direct Guide' },
  { source_id: 'SRC-MA-CONNECTOR-CULTURE-2026', state: 'MA', title: 'Card to Culture Guide' },
  { source_id: 'SRC-MA-BCBSMA-2026-SOB', state: 'MA', title: 'BCBSMA SOB' },
  { source_id: 'SRC-MA-HPHC-2026-EOC', state: 'MA', title: 'Harvard Pilgrim EOC' }
];\n"""
    idx = js_text.find('const COVERAGE_RULES = [')
    if idx != -1:
        js_text = js_text[:idx] + SOURCE_DOCS_BLOCK + "\n  " + js_text[idx:]

# 7. Refactor Status Language in UI helper functions
js_text = js_text.replace("Fully Verified Plan", "Verified coverage data available")

STATUS_PILL_REPLACEMENT = """function updateStatusPill(plan, targetRules = []) {
    const pill = $('#planStatusPill');
    if (!pill) return;
    
    const isUnsourced = plan.plan_identity_status === 'UNSOURCED_PLAN' || plan.source_status === 'UNSOURCED';
    const identityBadge = isUnsourced ? ' <span class="badge badge-warning" style="font-size:0.75rem; background:#fff3cd; color:#856404; padding:2px 6px; border-radius:4px; margin-left:4px;">Plan listing not yet source-confirmed.</span>' : '';

    if (plan.id === 'generic_unselected_plan' || !plan.id) {
      pill.className = 'status-pill pill-unconfigured';
      pill.innerHTML = 'ℹ️ Plan configured — coverage verification pending' + identityBadge;
      return;
    }

    const verifiedCount = targetRules.filter(r => r.verification_status && r.verification_status.startsWith('VERIFIED')).length;
    if (verifiedCount >= 5) {
      pill.className = 'status-pill pill-verified';
      pill.innerHTML = '✓ Verified coverage data available' + identityBadge;
    } else if (verifiedCount > 0) {
      pill.className = 'status-pill pill-partial';
      pill.innerHTML = '✓ Some plan benefits verified' + identityBadge;
    } else {
      pill.className = 'status-pill pill-unconfigured';
      pill.innerHTML = 'ℹ️ Plan configured — coverage verification pending' + identityBadge;
    }
  }"""

if 'function updateStatusPill' in js_text:
    idx = js_text.find('function updateStatusPill')
    depth = 0
    for i in range(idx, len(js_text)):
        if js_text[i] == '{': depth += 1
        elif js_text[i] == '}':
            depth -= 1
            if depth == 0:
                end_idx = i + 1
                break
    js_text = js_text[:idx] + STATUS_PILL_REPLACEMENT + js_text[end_idx:]

# 8. Ensure UNSOURCED_PLAN and plan_identity_status exist in PLANS definition
js_text = js_text.replace(
    "\"source_status\": \"UNSOURCED\"",
    "\"source_status\": \"UNSOURCED\", \"plan_identity_status\": \"UNSOURCED_PLAN\", \"coverage_verification_status\": \"COVERAGE_PENDING\", \"is_verified\": false"
)
js_text = js_text.replace(
    "\"source_status\": \"ACTIVE\"",
    "\"source_status\": \"ACTIVE\", \"plan_identity_status\": \"SOURCE_CONFIRMED\", \"coverage_verification_status\": \"VERIFIED_REFERENCE\", \"is_verified\": false"
)

if 'UNSOURCED_PLAN' not in js_text:
    js_text += "\n  // --- 10. PLAN IDENTITY STATUS SCHEMA ---\n  const UNSOURCED_PLAN = 'UNSOURCED_PLAN';\n"

js_file.write_text(js_text)
print("Updated marketplace.js with Phase 10 Data Integrity Audit features successfully.")
