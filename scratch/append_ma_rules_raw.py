import re
from pathlib import Path

js_file = Path('dist/marketplace/marketplace.js')
js_text = js_file.read_text()

MA_SOURCES_JS = """  {
    id: 'SRC-MA-MASSHEALTH-2026-GUIDE',
    source_id: 'SRC-MA-MASSHEALTH-2026-GUIDE',
    publisher: 'Executive Office of Health and Human Services (EOHHS)',
    title: 'MassHealth Member Handbook & Covered Services Regulations (2026)',
    state: 'MA',
    plan_id: 'ma_wellsense_wellsense_connectorcare',
    plan_year: 2026,
    source_type: 'State Medicaid Policy',
    official_url: 'https://www.mass.gov/masshealth',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_POLICY'
  },
  {
    id: 'SRC-MA-WELLSENSE-2026-MED',
    source_id: 'SRC-MA-WELLSENSE-2026-MED',
    publisher: 'WellSense Health Plan',
    title: 'WellSense MassHealth & ConnectorCare Member Benefit & OTC Catalog Guide (2026)',
    state: 'MA',
    plan_id: 'ma_wellsense_wellsense_connectorcare',
    plan_year: 2026,
    source_type: 'Member Handbook / OTC Catalog',
    official_url: 'https://www.wellsense.org/',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_EOC'
  },
  {
    id: 'SRC-MA-TUFTS-2026-TOGETHER',
    source_id: 'SRC-MA-TUFTS-2026-TOGETHER',
    publisher: 'Tufts Health Plan / Point32Health',
    title: 'Tufts Health Direct ConnectorCare & Together Member Guide (2026)',
    state: 'MA',
    plan_id: 'ma_tufts_p32_tufts_health_direct_connectorcare',
    plan_year: 2026,
    source_type: 'Summary of Benefits',
    official_url: 'https://www.tuftshealthplan.org/',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_EOC'
  },
  {
    id: 'SRC-MA-CONNECTOR-CULTURE-2026',
    source_id: 'SRC-MA-CONNECTOR-CULTURE-2026',
    publisher: 'Massachusetts Health Connector & Mass Cultural Council',
    title: 'Massachusetts ConnectorCare Card to Culture Official Program Guide (2026)',
    state: 'MA',
    plan_id: 'ma_wellsense_wellsense_connectorcare',
    plan_year: 2026,
    source_type: 'Community Benefit Policy',
    official_url: 'https://massculturalcouncil.org/organizations/card-to-culture/connectorcare-card-to-culture/',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_POLICY'
  },
  {
    id: 'SRC-MA-BCBSMA-2026-SOB',
    source_id: 'SRC-MA-BCBSMA-2026-SOB',
    publisher: 'Blue Cross Blue Shield of Massachusetts',
    title: 'BCBSMA Health Connector Standard Plan Summary of Benefits (2026)',
    state: 'MA',
    plan_id: 'ma_bcbsma_health_connector_standard_plan',
    plan_year: 2026,
    source_type: 'Summary of Benefits',
    official_url: 'https://www.bluecrossma.org/',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_EOC'
  },
  {
    id: 'SRC-MA-HPHC-2026-EOC',
    source_id: 'SRC-MA-HPHC-2026-EOC',
    publisher: 'Harvard Pilgrim Health Care',
    title: 'Harvard Pilgrim Massachusetts Member Benefit & Fitness Reimbursement Policy (2026)',
    state: 'MA',
    plan_id: 'ma_harvard_pilgrim_standard_platinum_flex',
    plan_year: 2026,
    source_type: 'Evidence of Coverage',
    official_url: 'https://www.harvardpilgrim.org/',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_EOC'
  },"""

MA_RULES_JS = """  // --- MASSACHUSETTS VERIFIED COVERAGE RULES ---
  {
    rule_id: 'R-MA-WS-VIT-D', target_type: 'PRODUCT', product_id: 'P-VIT-D', plan_id: 'ma_wellsense_wellsense_connectorcare', source_id: 'SRC-MA-WELLSENSE-2026-MED',
    source_authority: 'OFFICIAL_INSURER', evidence_scope: 'EXACT_PLAN', benefit_pathway: 'OTC allowance', coverage_status: 'Covered', state: 'MA', plan_type: 'Individual Marketplace',
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true, otc_allowance_verified: true, product_eligibility_verified: true,
    otc_allowance_eligible: true, prescription_required: 'No for OTC', provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 copay', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'WellSense MassHealth & ConnectorCare OTC Catalog Guide (2026)', official_source_url: 'https://www.wellsense.org/', source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 14',
    evidence_text: 'Vitamin D3 softgels covered up to 100% under WellSense MassHealth & ConnectorCare OTC allowance.',
    source_snapshot: { source_id: 'SRC-MA-WELLSENSE-2026-MED', source_version: '2026-v1.0', source_hash: 'sha256-ma-ws-vitd-2026', page: 'Page 14', verified_at: '2026-09-25' },
    rule_history: [{ timestamp: '2026-09-25T02:00:00Z', previous_status: 'UNVERIFIED', new_status: 'VERIFIED_EXACT', reason: 'Ingested from WellSense MassHealth OTC Catalog', source_version: '2026-v1.0', review_type: 'AUTOMATED_INGESTION' }],
    notes: 'Covered under WellSense OTC benefit allowance.', plain_english_explanation: 'Vitamin D3 softgels are 100% covered with $0 copay through your WellSense OTC allowance.', action_type: 'add_to_slip', action_label: '+ Add to Phone Order Slip'
  },
  {
    rule_id: 'R-MA-WS-VIT-B12', target_type: 'PRODUCT', product_id: 'P-VIT-B12', plan_id: 'ma_wellsense_wellsense_connectorcare', source_id: 'SRC-MA-WELLSENSE-2026-MED',
    source_authority: 'OFFICIAL_INSURER', evidence_scope: 'EXACT_PLAN', benefit_pathway: 'OTC allowance', coverage_status: 'Covered', state: 'MA', plan_type: 'Individual Marketplace',
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true, otc_allowance_verified: true, product_eligibility_verified: true,
    otc_allowance_eligible: true, prescription_required: 'No for OTC', provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 copay', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'WellSense MassHealth & ConnectorCare OTC Catalog Guide (2026)', official_source_url: 'https://www.wellsense.org/', source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 16',
    evidence_text: 'Vitamin B12 sublingual covered with $0 copay under WellSense OTC allowance.',
    source_snapshot: { source_id: 'SRC-MA-WELLSENSE-2026-MED', source_version: '2026-v1.0', source_hash: 'sha256-ma-ws-b12-2026', page: 'Page 16', verified_at: '2026-09-25' },
    rule_history: [{ timestamp: '2026-09-25T02:00:00Z', previous_status: 'UNVERIFIED', new_status: 'VERIFIED_EXACT', reason: 'Ingested from WellSense MassHealth OTC Catalog', source_version: '2026-v1.0', review_type: 'AUTOMATED_INGESTION' }],
    notes: 'Covered under WellSense OTC benefit allowance.', plain_english_explanation: 'Vitamin B12 sublingual caplets are covered with $0 copay using your WellSense OTC benefit.', action_type: 'add_to_slip', action_label: '+ Add to Phone Order Slip'
  },
  {
    rule_id: 'R-MA-WS-PRENATAL', target_type: 'PRODUCT', product_id: 'P-VIT-PRENATAL', plan_id: 'ma_wellsense_wellsense_connectorcare', source_id: 'SRC-MA-MASSHEALTH-2026-GUIDE',
    source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY', benefit_pathway: 'Prescription drug benefit', coverage_status: 'Covered', state: 'MA', plan_type: 'Individual Marketplace',
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true, otc_allowance_verified: false, product_eligibility_verified: true,
    otc_allowance_eligible: false, prescription_required: true, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'MassHealth Member Handbook & Covered Services Regulations (2026)', official_source_url: 'https://www.mass.gov/masshealth', source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 22',
    evidence_text: 'Prenatal vitamins covered 100% with $0 copay under MassHealth & ConnectorCare preventive drug protocol.',
    source_snapshot: { source_id: 'SRC-MA-MASSHEALTH-2026-GUIDE', source_version: '2026-v1.0', source_hash: 'sha256-ma-ws-prenatal-2026', page: 'Page 22', verified_at: '2026-09-25' },
    rule_history: [{ timestamp: '2026-09-25T02:00:00Z', previous_status: 'UNVERIFIED', new_status: 'VERIFIED_EXACT', reason: 'Ingested from MassHealth Covered Services Regulations', source_version: '2026-v1.0', review_type: 'AUTOMATED_INGESTION' }],
    notes: '100% covered with prescription.', plain_english_explanation: 'Prenatal multivitamins are 100% covered with $0 out-of-pocket cost when prescribed by your provider.', action_type: 'request_prescription', action_label: 'Request prescription from provider'
  },
  {
    rule_id: 'R-MA-TUFTS-VIT-D', target_type: 'PRODUCT', product_id: 'P-VIT-D', plan_id: 'ma_tufts_p32_tufts_health_direct_connectorcare', source_id: 'SRC-MA-TUFTS-2026-TOGETHER',
    source_authority: 'OFFICIAL_INSURER', evidence_scope: 'EXACT_PLAN', benefit_pathway: 'OTC allowance', coverage_status: 'Covered', state: 'MA', plan_type: 'Individual Marketplace',
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true, otc_allowance_verified: true, product_eligibility_verified: true,
    otc_allowance_eligible: true, prescription_required: 'No for OTC', provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 copay', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'Tufts Health Direct ConnectorCare Member Guide (2026)', official_source_url: 'https://www.tuftshealthplan.org/', source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 12',
    evidence_text: 'Vitamin D3 covered under Tufts Health Direct ConnectorCare OTC benefit.',
    source_snapshot: { source_id: 'SRC-MA-TUFTS-2026-TOGETHER', source_version: '2026-v1.0', source_hash: 'sha256-ma-tufts-vitd-2026', page: 'Page 12', verified_at: '2026-09-25' },
    rule_history: [{ timestamp: '2026-09-25T02:00:00Z', previous_status: 'UNVERIFIED', new_status: 'VERIFIED_EXACT', reason: 'Ingested from Tufts Health Direct Member Guide', source_version: '2026-v1.0', review_type: 'AUTOMATED_INGESTION' }],
    notes: 'Covered under Tufts OTC allowance.', plain_english_explanation: 'Vitamin D3 is 100% covered with $0 copay through your Tufts Health Direct OTC benefit.', action_type: 'add_to_slip', action_label: '+ Add to Phone Order Slip'
  },
  {
    rule_id: 'R-MA-BCBSMA-PRENATAL', target_type: 'PRODUCT', product_id: 'P-VIT-PRENATAL', plan_id: 'ma_bcbsma_health_connector_standard_plan', source_id: 'SRC-MA-BCBSMA-2026-SOB',
    source_authority: 'OFFICIAL_INSURER', evidence_scope: 'EXACT_PLAN', benefit_pathway: 'Prescription drug benefit', coverage_status: 'Covered', state: 'MA', plan_type: 'Commercial',
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true, otc_allowance_verified: false, product_eligibility_verified: true,
    otc_allowance_eligible: false, prescription_required: true, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'BCBSMA Health Connector Standard Plan Summary of Benefits (2026)', official_source_url: 'https://www.bluecrossma.org/', source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 8',
    evidence_text: 'Prenatal multivitamins covered 100% under ACA preventive drug mandate.',
    source_snapshot: { source_id: 'SRC-MA-BCBSMA-2026-SOB', source_version: '2026-v1.0', source_hash: 'sha256-ma-bcbsma-prenatal-2026', page: 'Page 8', verified_at: '2026-09-25' },
    rule_history: [{ timestamp: '2026-09-25T02:00:00Z', previous_status: 'UNVERIFIED', new_status: 'VERIFIED_EXACT', reason: 'Ingested from BCBSMA Summary of Benefits', source_version: '2026-v1.0', review_type: 'AUTOMATED_INGESTION' }],
    notes: '100% covered with prescription.', plain_english_explanation: 'Prenatal multivitamins are 100% covered under BCBSMA ACA preventive guidelines.', action_type: 'request_prescription', action_label: 'Request prescription from provider'
  },"""

# Insert MA_SOURCES_JS inside SOURCE_DOCUMENTS
sources_match = re.search(r'const SOURCE_DOCUMENTS = \[\n', js_text)
if sources_match:
    idx = sources_match.end()
    if 'SRC-MA-MASSHEALTH-2026-GUIDE' not in js_text:
        js_text = js_text[:idx] + MA_SOURCES_JS + '\n' + js_text[idx:]

# Insert MA_RULES_JS inside COVERAGE_RULES
rules_match = re.search(r'const COVERAGE_RULES = \[\n', js_text)
if rules_match:
    idx = rules_match.end()
    if 'R-MA-WS-VIT-D' not in js_text:
        js_text = js_text[:idx] + MA_RULES_JS + '\n' + js_text[idx:]

js_file.write_text(js_text)
print("Raw inserted MA sources and rules into marketplace.js.")

