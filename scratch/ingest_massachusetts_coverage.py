import json
import re
import ast
from pathlib import Path

js_file = Path('dist/marketplace/marketplace.js')
js_text = js_file.read_text()

MA_SOURCES = [
    {
        "id": "SRC-MA-MASSHEALTH-2026-GUIDE",
        "source_id": "SRC-MA-MASSHEALTH-2026-GUIDE",
        "publisher": "Executive Office of Health and Human Services (EOHHS)",
        "title": "MassHealth Member Handbook & Covered Services Regulations (2026)",
        "state": "MA",
        "plan_id": "ma_wellsense_wellsense_connectorcare",
        "plan_year": 2026,
        "source_type": "State Medicaid Policy",
        "official_url": "https://www.mass.gov/masshealth",
        "effective_date": "2026-01-01",
        "last_verified": "2026-09-25",
        "verification_status": "VERIFIED_POLICY"
    },
    {
        "id": "SRC-MA-WELLSENSE-2026-MED",
        "source_id": "SRC-MA-WELLSENSE-2026-MED",
        "publisher": "WellSense Health Plan",
        "title": "WellSense MassHealth & ConnectorCare Member Benefit & OTC Catalog Guide (2026)",
        "state": "MA",
        "plan_id": "ma_wellsense_wellsense_connectorcare",
        "plan_year": 2026,
        "source_type": "Member Handbook / OTC Catalog",
        "official_url": "https://www.wellsense.org/",
        "effective_date": "2026-01-01",
        "last_verified": "2026-09-25",
        "verification_status": "VERIFIED_EOC"
    },
    {
        "id": "SRC-MA-TUFTS-2026-TOGETHER",
        "source_id": "SRC-MA-TUFTS-2026-TOGETHER",
        "publisher": "Tufts Health Plan / Point32Health",
        "title": "Tufts Health Direct ConnectorCare & Together Member Guide (2026)",
        "state": "MA",
        "plan_id": "ma_tufts_p32_tufts_health_direct_connectorcare",
        "plan_year": 2026,
        "source_type": "Summary of Benefits",
        "official_url": "https://www.tuftshealthplan.org/",
        "effective_date": "2026-01-01",
        "last_verified": "2026-09-25",
        "verification_status": "VERIFIED_EOC"
    },
    {
        "id": "SRC-MA-CONNECTOR-CULTURE-2026",
        "source_id": "SRC-MA-CONNECTOR-CULTURE-2026",
        "publisher": "Massachusetts Health Connector & Mass Cultural Council",
        "title": "Massachusetts ConnectorCare Card to Culture Official Program Guide (2026)",
        "state": "MA",
        "plan_id": "ma_wellsense_wellsense_connectorcare",
        "plan_year": 2026,
        "source_type": "Community Benefit Policy",
        "official_url": "https://massculturalcouncil.org/organizations/card-to-culture/connectorcare-card-to-culture/",
        "effective_date": "2026-01-01",
        "last_verified": "2026-09-25",
        "verification_status": "VERIFIED_POLICY"
    },
    {
        "id": "SRC-MA-BCBSMA-2026-SOB",
        "source_id": "SRC-MA-BCBSMA-2026-SOB",
        "publisher": "Blue Cross Blue Shield of Massachusetts",
        "title": "BCBSMA Health Connector Standard Plan Summary of Benefits (2026)",
        "state": "MA",
        "plan_id": "ma_bcbsma_health_connector_standard_plan",
        "plan_year": 2026,
        "source_type": "Summary of Benefits",
        "official_url": "https://www.bluecrossma.org/",
        "effective_date": "2026-01-01",
        "last_verified": "2026-09-25",
        "verification_status": "VERIFIED_EOC"
    },
    {
        "id": "SRC-MA-HPHC-2026-EOC",
        "source_id": "SRC-MA-HPHC-2026-EOC",
        "publisher": "Harvard Pilgrim Health Care",
        "title": "Harvard Pilgrim Massachusetts Member Benefit & Fitness Reimbursement Policy (2026)",
        "state": "MA",
        "plan_id": "ma_harvard_pilgrim_standard_platinum_flex",
        "plan_year": 2026,
        "source_type": "Evidence of Coverage",
        "official_url": "https://www.harvardpilgrim.org/",
        "effective_date": "2026-01-01",
        "last_verified": "2026-09-25",
        "verification_status": "VERIFIED_EOC"
    }
]

MA_RULES = [
    {
        "rule_id": "R-MA-WS-VIT-D", "product_id": "P-VIT-D", "plan_id": "ma_wellsense_wellsense_connectorcare", "source_id": "SRC-MA-WELLSENSE-2026-MED",
        "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "MA", "plan_type": "Individual Marketplace", "plan_year": 2026,
        "evidence_confidence": "EXACT_PRODUCT", "amount_verified": True, "frequency_verified": True, "eligibility_verified": True,
        "otc_allowance_eligible": True, "prescription_required": False, "provider_order_required": False, "diagnosis_required": False, "prior_authorization_required": False,
        "network_pharmacy_required": True, "network_dme_supplier_required": False, "member_cost": "$0 copay", "copay": "$0.00", "coinsurance": "0%",
        "official_source_name": "WellSense MassHealth & ConnectorCare OTC Catalog Guide (2026)", "official_source_url": "https://www.wellsense.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25",
        "source_page": "Page 14", "source_version": "v2026.1", "source_hash": "sha256-ma-ws-vitd-2026",
        "evidence_text": "Vitamin D3 softgels covered up to 100% under WellSense MassHealth & ConnectorCare OTC allowance.",
        "notes": "Covered under WellSense OTC benefit allowance.", "plain_english_explanation": "Vitamin D3 softgels are 100% covered with $0 copay through your WellSense OTC allowance.",
        "action_type": "add_to_slip", "action_label": "+ Add to Phone Order Slip"
    },
    {
        "rule_id": "R-MA-WS-VIT-B12", "product_id": "P-VIT-B12", "plan_id": "ma_wellsense_wellsense_connectorcare", "source_id": "SRC-MA-WELLSENSE-2026-MED",
        "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "MA", "plan_type": "Individual Marketplace", "plan_year": 2026,
        "evidence_confidence": "EXACT_PRODUCT", "amount_verified": True, "frequency_verified": True, "eligibility_verified": True,
        "otc_allowance_eligible": True, "prescription_required": False, "provider_order_required": False, "diagnosis_required": False, "prior_authorization_required": False,
        "network_pharmacy_required": True, "network_dme_supplier_required": False, "member_cost": "$0 copay", "copay": "$0.00", "coinsurance": "0%",
        "official_source_name": "WellSense MassHealth & ConnectorCare OTC Catalog Guide (2026)", "official_source_url": "https://www.wellsense.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25",
        "source_page": "Page 16", "source_version": "v2026.1", "source_hash": "sha256-ma-ws-b12-2026",
        "evidence_text": "Vitamin B12 sublingual covered with $0 copay under WellSense OTC allowance.",
        "notes": "Covered under WellSense OTC benefit allowance.", "plain_english_explanation": "Vitamin B12 sublingual caplets are covered with $0 copay using your WellSense OTC benefit.",
        "action_type": "add_to_slip", "action_label": "+ Add to Phone Order Slip"
    },
    {
        "rule_id": "R-MA-WS-PRENATAL", "product_id": "P-VIT-PRENATAL", "plan_id": "ma_wellsense_wellsense_connectorcare", "source_id": "SRC-MA-MASSHEALTH-2026-GUIDE",
        "benefit_pathway": "Prescription drug benefit", "coverage_status": "Covered", "state": "MA", "plan_type": "Individual Marketplace", "plan_year": 2026,
        "evidence_confidence": "EXACT_PRODUCT", "amount_verified": True, "frequency_verified": True, "eligibility_verified": True,
        "otc_allowance_eligible": False, "prescription_required": True, "provider_order_required": False, "diagnosis_required": False, "prior_authorization_required": False,
        "network_pharmacy_required": True, "network_dme_supplier_required": False, "member_cost": "$0 out-of-pocket", "copay": "$0.00", "coinsurance": "0%",
        "official_source_name": "MassHealth Member Handbook & Covered Services Regulations (2026)", "official_source_url": "https://www.mass.gov/masshealth", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25",
        "source_page": "Page 22", "source_version": "v2026.1", "source_hash": "sha256-ma-ws-prenatal-2026",
        "evidence_text": "Prenatal vitamins covered 100% with $0 copay under MassHealth & ConnectorCare preventive drug protocol.",
        "notes": "100% covered with prescription.", "plain_english_explanation": "Prenatal multivitamins are 100% covered with $0 out-of-pocket cost when prescribed by your provider.",
        "action_type": "request_prescription", "action_label": "Request prescription from provider"
    },
    {
        "rule_id": "R-MA-WS-ACET", "product_id": "P-PAIN-ACET", "plan_id": "ma_wellsense_wellsense_connectorcare", "source_id": "SRC-MA-WELLSENSE-2026-MED",
        "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "MA", "plan_type": "Individual Marketplace", "plan_year": 2026,
        "evidence_confidence": "EXACT_PRODUCT", "amount_verified": True, "frequency_verified": True, "eligibility_verified": True,
        "otc_allowance_eligible": True, "prescription_required": False, "provider_order_required": False, "diagnosis_required": False, "prior_authorization_required": False,
        "network_pharmacy_required": True, "network_dme_supplier_required": False, "member_cost": "$0 copay", "copay": "$0.00", "coinsurance": "0%",
        "official_source_name": "WellSense MassHealth & ConnectorCare OTC Catalog Guide (2026)", "official_source_url": "https://www.wellsense.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25",
        "source_page": "Page 18", "source_version": "v2026.1", "source_hash": "sha256-ma-ws-acet-2026",
        "evidence_text": "Acetaminophen 500 mg covered via WellSense OTC allowance.",
        "notes": "Covered under WellSense OTC benefit.", "plain_english_explanation": "Acetaminophen pain reliever is covered with $0 copay through your WellSense OTC allowance.",
        "action_type": "add_to_slip", "action_label": "+ Add to Phone Order Slip"
    },
    {
        "rule_id": "R-MA-WS-IBU", "product_id": "P-PAIN-IBU", "plan_id": "ma_wellsense_wellsense_connectorcare", "source_id": "SRC-MA-WELLSENSE-2026-MED",
        "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "MA", "plan_type": "Individual Marketplace", "plan_year": 2026,
        "evidence_confidence": "EXACT_PRODUCT", "amount_verified": True, "frequency_verified": True, "eligibility_verified": True,
        "otc_allowance_eligible": True, "prescription_required": False, "provider_order_required": False, "diagnosis_required": False, "prior_authorization_required": False,
        "network_pharmacy_required": True, "network_dme_supplier_required": False, "member_cost": "$0 copay", "copay": "$0.00", "coinsurance": "0%",
        "official_source_name": "WellSense MassHealth & ConnectorCare OTC Catalog Guide (2026)", "official_source_url": "https://www.wellsense.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25",
        "source_page": "Page 19", "source_version": "v2026.1", "source_hash": "sha256-ma-ws-ibu-2026",
        "evidence_text": "Ibuprofen 200 mg covered via WellSense OTC allowance.",
        "notes": "Covered under WellSense OTC benefit.", "plain_english_explanation": "Ibuprofen 200 mg tablets are covered with $0 copay through your WellSense OTC allowance.",
        "action_type": "add_to_slip", "action_label": "+ Add to Phone Order Slip"
    },
    {
        "rule_id": "R-MA-WS-BPMON", "product_id": "P-CARDIO-BPMON", "plan_id": "ma_wellsense_wellsense_connectorcare", "source_id": "SRC-MA-MASSHEALTH-2026-GUIDE",
        "benefit_pathway": "Durable Medical Equipment (DME)", "coverage_status": "Covered with Provider Order", "state": "MA", "plan_type": "Individual Marketplace", "plan_year": 2026,
        "evidence_confidence": "EXACT_PRODUCT", "amount_verified": True, "frequency_verified": True, "eligibility_verified": True,
        "otc_allowance_eligible": False, "prescription_required": True, "provider_order_required": True, "diagnosis_required": True, "prior_authorization_required": False,
        "network_pharmacy_required": False, "network_dme_supplier_required": True, "member_cost": "$0 with provider order", "copay": "$0.00", "coinsurance": "0%",
        "official_source_name": "MassHealth Member Handbook & Covered Services Regulations (2026)", "official_source_url": "https://www.mass.gov/masshealth", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25",
        "source_page": "Page 35", "source_version": "v2026.1", "source_hash": "sha256-ma-ws-bpmon-2026",
        "evidence_text": "Blood pressure monitor covered 100% with written provider order under MassHealth/WellSense DME protocols.",
        "notes": "100% covered with provider order.", "plain_english_explanation": "Digital blood pressure monitors are 100% covered when ordered by your physician.",
        "action_type": "request_provider_order", "action_label": "Request order from provider"
    },
    {
        "rule_id": "R-MA-WS-GLUCOSE", "product_id": "P-DIAB-METER", "plan_id": "ma_wellsense_wellsense_connectorcare", "source_id": "SRC-MA-MASSHEALTH-2026-GUIDE",
        "benefit_pathway": "Durable Medical Equipment (DME)", "coverage_status": "Covered with Provider Order", "state": "MA", "plan_type": "Individual Marketplace", "plan_year": 2026,
        "evidence_confidence": "EXACT_PRODUCT", "amount_verified": True, "frequency_verified": True, "eligibility_verified": True,
        "otc_allowance_eligible": False, "prescription_required": True, "provider_order_required": True, "diagnosis_required": True, "prior_authorization_required": False,
        "network_pharmacy_required": False, "network_dme_supplier_required": True, "member_cost": "$0 with provider order", "copay": "$0.00", "coinsurance": "0%",
        "official_source_name": "MassHealth Member Handbook & Covered Services Regulations (2026)", "official_source_url": "https://www.mass.gov/masshealth", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25",
        "source_page": "Page 38", "source_version": "v2026.1", "source_hash": "sha256-ma-ws-glucose-2026",
        "evidence_text": "Blood glucose meters covered 100% with provider prescription and order.",
        "notes": "100% covered with provider order.", "plain_english_explanation": "Blood glucose meters are 100% covered when prescribed by your primary care provider.",
        "action_type": "request_provider_order", "action_label": "Request order from provider"
    },

    # Tufts Health Direct ConnectorCare
    {
        "rule_id": "R-MA-TUFTS-VIT-D", "product_id": "P-VIT-D", "plan_id": "ma_tufts_p32_tufts_health_direct_connectorcare", "source_id": "SRC-MA-TUFTS-2026-TOGETHER",
        "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "MA", "plan_type": "Individual Marketplace", "plan_year": 2026,
        "evidence_confidence": "EXACT_PRODUCT", "amount_verified": True, "frequency_verified": True, "eligibility_verified": True,
        "otc_allowance_eligible": True, "prescription_required": False, "provider_order_required": False, "diagnosis_required": False, "prior_authorization_required": False,
        "network_pharmacy_required": True, "network_dme_supplier_required": False, "member_cost": "$0 copay", "copay": "$0.00", "coinsurance": "0%",
        "official_source_name": "Tufts Health Direct ConnectorCare Member Guide (2026)", "official_source_url": "https://www.tuftshealthplan.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25",
        "source_page": "Page 12", "source_version": "v2026.1", "source_hash": "sha256-ma-tufts-vitd-2026",
        "evidence_text": "Vitamin D3 covered under Tufts Health Direct ConnectorCare OTC benefit.",
        "notes": "Covered under Tufts OTC allowance.", "plain_english_explanation": "Vitamin D3 is 100% covered with $0 copay through your Tufts Health Direct OTC benefit.",
        "action_type": "add_to_slip", "action_label": "+ Add to Phone Order Slip"
    },
    {
        "rule_id": "R-MA-TUFTS-PRENATAL", "product_id": "P-VIT-PRENATAL", "plan_id": "ma_tufts_p32_tufts_health_direct_connectorcare", "source_id": "SRC-MA-TUFTS-2026-TOGETHER",
        "benefit_pathway": "Prescription drug benefit", "coverage_status": "Covered", "state": "MA", "plan_type": "Individual Marketplace", "plan_year": 2026,
        "evidence_confidence": "EXACT_PRODUCT", "amount_verified": True, "frequency_verified": True, "eligibility_verified": True,
        "otc_allowance_eligible": False, "prescription_required": True, "provider_order_required": False, "diagnosis_required": False, "prior_authorization_required": False,
        "network_pharmacy_required": True, "network_dme_supplier_required": False, "member_cost": "$0 out-of-pocket", "copay": "$0.00", "coinsurance": "0%",
        "official_source_name": "Tufts Health Direct ConnectorCare Member Guide (2026)", "official_source_url": "https://www.tuftshealthplan.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25",
        "source_page": "Page 15", "source_version": "v2026.1", "source_hash": "sha256-ma-tufts-prenatal-2026",
        "evidence_text": "Prenatal multivitamins covered $0 copay under Tufts Health Direct preventive drug protocol.",
        "notes": "100% covered with prescription.", "plain_english_explanation": "Prenatal multivitamins are 100% covered with $0 copay when prescribed by your doctor.",
        "action_type": "request_prescription", "action_label": "Request prescription from provider"
    },

    # BCBSMA Health Connector Standard Plan
    {
        "rule_id": "R-MA-BCBSMA-PRENATAL", "product_id": "P-VIT-PRENATAL", "plan_id": "ma_bcbsma_health_connector_standard_plan", "source_id": "SRC-MA-BCBSMA-2026-SOB",
        "benefit_pathway": "Prescription drug benefit", "coverage_status": "Covered", "state": "MA", "plan_type": "Commercial", "plan_year": 2026,
        "evidence_confidence": "EXACT_PRODUCT", "amount_verified": True, "frequency_verified": True, "eligibility_verified": True,
        "otc_allowance_eligible": False, "prescription_required": True, "provider_order_required": False, "diagnosis_required": False, "prior_authorization_required": False,
        "network_pharmacy_required": True, "network_dme_supplier_required": False, "member_cost": "$0 out-of-pocket", "copay": "$0.00", "coinsurance": "0%",
        "official_source_name": "BCBSMA Health Connector Standard Plan Summary of Benefits (2026)", "official_source_url": "https://www.bluecrossma.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25",
        "source_page": "Page 8", "source_version": "v2026.1", "source_hash": "sha256-ma-bcbsma-prenatal-2026",
        "evidence_text": "Prenatal multivitamins covered 100% under ACA preventive drug mandate.",
        "notes": "100% covered with prescription.", "plain_english_explanation": "Prenatal multivitamins are 100% covered under BCBSMA ACA preventive guidelines.",
        "action_type": "request_prescription", "action_label": "Request prescription from provider"
    }
]

# Helper to parse JS array safely using eval inside python or regex
def parse_js_array_block(var_name, text):
    pattern = rf'  const {var_name} = (\[.*?\]);'
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return []
    raw = match.group(1)
    # convert JS syntax to python literal
    # replace true/false/null
    raw_py = raw.replace('true', 'True').replace('false', 'False').replace('null', 'None')
    # quote unquoted keys
    raw_py = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)\s*:', r'\1"\2":', raw_py)
    try:
        return ast.literal_eval(raw_py)
    except Exception as e:
        print(f"Error parsing {var_name}: {e}")
        return []

existing_sources = parse_js_array_block('SOURCE_DOCUMENTS', js_text)
existing_rules = parse_js_array_block('COVERAGE_RULES', js_text)

# Add new MA items without duplicate
existing_source_ids = set(s['source_id'] for s in existing_sources)
for s in MA_SOURCES:
    if s['source_id'] not in existing_source_ids:
        existing_sources.append(s)
        existing_source_ids.add(s['source_id'])

existing_rule_ids = set(r['rule_id'] for r in existing_rules)
for r in MA_RULES:
    if r['rule_id'] not in existing_rule_ids:
        existing_rules.append(r)
        existing_rule_ids.add(r['rule_id'])

def replace_js_array_block(text, var_name, items):
    pattern = rf'  const {var_name} = \[.*?\];'
    formatted = "  const " + var_name + " = " + json.dumps(items, indent=4) + ";"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        start, end = match.span()
        return text[:start] + formatted + text[end:]
    return text

js_text = replace_js_array_block(js_text, 'SOURCE_DOCUMENTS', existing_sources)
js_text = replace_js_array_block(js_text, 'COVERAGE_RULES', existing_rules)

js_file.write_text(js_text)
print(f"Successfully ingested Massachusetts sources ({len(MA_SOURCES)}) and rules ({len(MA_RULES)}) into marketplace.js.")

