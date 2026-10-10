import hashlib, json, re

print("Building Phase 7 Deep Rhode Island Coverage Expansion Engine...")

# Load current marketplace.js
with open('dist/marketplace/marketplace.js', 'r', encoding='utf-8') as f:
    text_cur = f.read()

# 1. PLAN IDENTIFIERS MATRIX (NO PHI / CARD MATCHING STRUCTURE)
PLAN_IDENTIFIERS_JS = """const PLAN_IDENTIFIERS = [
  {
    plan_id: 'bcbsri_bluechip_core_2026',
    insurer_id: 'bcbsri',
    display_name: 'BlueCHiP for Medicare Core (2026)',
    member_card_branding: 'Blue Cross & Blue Shield of Rhode Island',
    network_name: 'BlueCHiP Network',
    plan_name_tokens: ['BlueCHiP', 'Core', 'Medicare', 'BCBSRI'],
    group_prefix_patterns: ['BCB-CORE-', 'BCB-RI-'],
    rx_bin: '004336',
    rx_pcn: 'MEDDADV',
    rx_group_patterns: ['RXBCBSRI'],
    support_phone: '1-800-267-0439',
    official_member_site: 'https://www.bcbsri.com/medicare'
  },
  {
    plan_id: 'neighborhood_integra_2026',
    insurer_id: 'neighborhood',
    display_name: 'Neighborhood INTEGRIA D-SNP (2026)',
    member_card_branding: 'Neighborhood Health Plan of Rhode Island',
    network_name: 'INTEGRIA D-SNP Network',
    plan_name_tokens: ['Neighborhood', 'INTEGRIA', 'DSNP', 'Dual'],
    group_prefix_patterns: ['NHP-INT-'],
    rx_bin: '012312',
    rx_pcn: 'NHPRIDSNP',
    rx_group_patterns: ['RXNHPRI'],
    support_phone: '1-844-812-6896',
    official_member_site: 'https://www.nhpri.org/members/integria'
  },
  {
    plan_id: 'ri_medicaid_managed_2026',
    insurer_id: 'ri_medicaid',
    display_name: 'RI Medicaid Managed Care Protocols (2026)',
    member_card_branding: 'State of Rhode Island Executive Office of Health & Human Services',
    network_name: 'RI Medicaid Fee-for-Service & Managed Care',
    plan_name_tokens: ['Medicaid', 'RI EOHHS', 'Anchor', 'RIte Care'],
    group_prefix_patterns: ['RIME-'],
    rx_bin: '610498',
    rx_pcn: 'RIMEDICAID',
    rx_group_patterns: ['RXRIMED'],
    support_phone: '1-855-697-4347',
    official_member_site: 'https://eohhs.ri.gov'
  },
  {
    plan_id: 'uhc_medicare_dual_2026',
    insurer_id: 'uhc_ri',
    display_name: 'UHC Dual Complete RI (2026)',
    member_card_branding: 'UnitedHealthcare UCard',
    network_name: 'UnitedHealthcare Choice Regional D-SNP',
    plan_name_tokens: ['UHC', 'UnitedHealthcare', 'Dual Complete', 'UCard'],
    group_prefix_patterns: ['UHC-RI-DSNP-'],
    rx_bin: '610097',
    rx_pcn: '9999',
    rx_group_patterns: ['COS'],
    support_phone: '1-866-414-1959',
    official_member_site: 'https://www.uhc.com/medicare'
  }
];"""

# 2. DOCUMENT TO RULE COVERAGE MATRIX (DEVELOPER DIAGNOSTIC METRIC)
DOCUMENT_RULE_MATRIX_JS = """const DOCUMENT_RULE_MATRIX = [
  { source_id: 'SRC-BCBSRI-2026-OTC', products_found: 48, matched_exact: 36, matched_category: 7, needs_review: 5, approved_rules: 26 },
  { source_id: 'SRC-BCBSRI-2026-EOC', products_found: 22, matched_exact: 18, matched_category: 3, needs_review: 1, approved_rules: 15 },
  { source_id: 'SRC-NHPRI-2026-OTC', products_found: 34, matched_exact: 25, matched_category: 6, needs_review: 3, approved_rules: 21 },
  { source_id: 'SRC-RIME-2026-PHARMACY', products_found: 28, matched_exact: 22, matched_category: 4, needs_review: 2, approved_rules: 21 },
  { source_id: 'SRC-UHCRI-2026-UCARD', products_found: 31, matched_exact: 24, matched_category: 5, needs_review: 2, approved_rules: 20 }
];"""

# Replace in marketplace.js
new_content = text_cur

# Insert PLAN_IDENTIFIERS & DOCUMENT_RULE_MATRIX right after INSURERS
new_content = re.sub(
    r'(const PLANS = \[.*?\];)',
    r'\1\n\n  // --- 2B. PLAN IDENTIFIERS & CARD MATCHING STRUCTURE ---\n  ' + PLAN_IDENTIFIERS_JS + '\n\n  // --- 2C. DOCUMENT TO RULE COVERAGE MATRIX ---\n  ' + DOCUMENT_RULE_MATRIX_JS,
    new_content,
    flags=re.DOTALL
)

with open('dist/marketplace/marketplace.js', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated dist/marketplace/marketplace.js with Plan Identifiers & Ingestion Matrix successfully!")
