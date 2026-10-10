import json
import re
from pathlib import Path

d_data = json.loads(Path('dist/data.json').read_text())

INSURERS = [
    { 'id': 'bcbsri', 'name': 'Blue Cross & Blue Shield of Rhode Island', 'code': 'BCBSRI', 'states': ['RI'] },
    { 'id': 'neighborhood', 'name': 'Neighborhood Health Plan of Rhode Island', 'code': 'NHPRI', 'states': ['RI'] },
    { 'id': 'ri_medicaid', 'name': 'Rhode Island Medicaid (EOHHS)', 'code': 'RIME', 'states': ['RI'] },
    { 'id': 'uhc_ri', 'name': 'UnitedHealthcare Rhode Island', 'code': 'UHCRI', 'states': ['RI'] },
    { 'id': 'tufts_p32', 'name': 'Tufts / Point32Health', 'code': 'TUFTS', 'states': ['RI', 'MA'] },
    { 'id': 'bcbsma', 'name': 'Blue Cross Blue Shield of Massachusetts', 'code': 'BCBSMA', 'states': ['MA'] },
    { 'id': 'harvard_pilgrim', 'name': 'Harvard Pilgrim Health Care', 'code': 'HPHC', 'states': ['MA', 'ME', 'NH'] },
    { 'id': 'health_new_england', 'name': 'Health New England', 'code': 'HNE', 'states': ['MA'] },
    { 'id': 'mgb_health', 'name': 'Mass General Brigham Health Plan', 'code': 'MGBHP', 'states': ['MA'] },
    { 'id': 'wellsense', 'name': 'WellSense Health Plan', 'code': 'WELLSENSE', 'states': ['MA', 'NH'] },
    { 'id': 'masshealth', 'name': 'MassHealth (Massachusetts EOHHS)', 'code': 'MASSHEALTH', 'states': ['MA'] },
    { 'id': 'anthem_bcbs', 'name': 'Anthem Blue Cross and Blue Shield', 'code': 'ANTHEM', 'states': ['CT', 'ME', 'NH'] },
    { 'id': 'connecticare', 'name': 'ConnectiCare', 'code': 'CONNECTICARE', 'states': ['CT'] },
    { 'id': 'husky_health', 'name': 'HUSKY Health Connecticut', 'code': 'HUSKY', 'states': ['CT'] },
    { 'id': 'community_health_options', 'name': 'Community Health Options', 'code': 'CHO', 'states': ['ME'] },
    { 'id': 'mending', 'name': 'Mending', 'code': 'MENDING', 'states': ['ME'] },
    { 'id': 'mainecare', 'name': 'MaineCare (Maine DHHS)', 'code': 'MAINECARE', 'states': ['ME'] },
    { 'id': 'ambetter_nh', 'name': 'Ambetter from NH Healthy Families', 'code': 'AMBETTER', 'states': ['NH'] },
    { 'id': 'amerihealth_nh', 'name': 'AmeriHealth Caritas New Hampshire', 'code': 'AMERIHEALTH', 'states': ['NH'] },
    { 'id': 'nh_dhhs', 'name': 'New Hampshire Medicaid (DHHS)', 'code': 'NHDHHS', 'states': ['NH'] },
    { 'id': 'bcbsvt', 'name': 'Blue Cross and Blue Shield of Vermont', 'code': 'BCBSVT', 'states': ['VT'] },
    { 'id': 'mvp_health', 'name': 'MVP Health Care', 'code': 'MVP', 'states': ['VT'] },
    { 'id': 'green_mountain_care', 'name': 'Green Mountain Care Vermont', 'code': 'GMC', 'states': ['VT'] },
    { 'id': 'medicare', 'name': 'Original Medicare (CMS)', 'code': 'CMS', 'states': ['RI', 'MA', 'CT', 'NH', 'VT', 'ME'] },
    { 'id': 'unselected', 'name': 'Generic / Unselected Insurer', 'code': 'GENERIC', 'states': ['RI', 'MA', 'CT', 'NH', 'VT', 'ME'] }
]

ISSUER_MAP = {
    'Blue Cross & Blue Shield of Rhode Island': 'bcbsri',
    'Neighborhood Health Plan of Rhode Island': 'neighborhood',
    'Neighborhood Health Plan of RI': 'neighborhood',
    'Rhode Island Medicaid (EOHHS)': 'ri_medicaid',
    'UnitedHealthcare Rhode Island': 'uhc_ri',
    'UnitedHealthcare RI': 'uhc_ri',
    'Tufts / Point32Health': 'tufts_p32',
    'Tufts Health Plan': 'tufts_p32',
    'Blue Cross Blue Shield of Massachusetts': 'bcbsma',
    'Harvard Pilgrim Health Care': 'harvard_pilgrim',
    'Health New England': 'health_new_england',
    'Mass General Brigham Health Plan': 'mgb_health',
    'WellSense Health Plan': 'wellsense',
    'MassHealth': 'masshealth',
    'Anthem Blue Cross and Blue Shield': 'anthem_bcbs',
    'ConnectiCare': 'connecticare',
    'HUSKY Health': 'husky_health',
    'Community Health Options': 'community_health_options',
    'Mending': 'mending',
    'MaineCare': 'mainecare',
    'Ambetter from NH Healthy Families': 'ambetter_nh',
    'AmeriHealth Caritas New Hampshire': 'amerihealth_nh',
    'NH Healthy Families': 'ambetter_nh',
    'WellSense New Hampshire Medicaid': 'wellsense',
    'Blue Cross and Blue Shield of Vermont': 'bcbsvt',
    'MVP Health Care': 'mvp_health',
    'Green Mountain Care': 'green_mountain_care'
}

CORE_RI_PLANS = [
    {
        'id': 'bcbsri_bluechip_core_2026', 'insurer_id': 'bcbsri', 'insurer_name': 'Blue Cross & Blue Shield of Rhode Island',
        'official_plan_name': 'BlueCHiP for Medicare Core (2026)', 'display_name': 'BlueCHiP Core 2026', 'plan_year': 2026,
        'state': 'RI', 'plan_type': 'Medicare Advantage', 'insurance_category': 'MEDICARE_ADVANTAGE', 'network_type': 'HMO-POS',
        'market_segment': 'Individual Medicare', 'service_area': 'Statewide RI', 'source_status': 'ACTIVE',
        'aliases': ['BlueCHiP Core', 'BCBSRI Medicare']
    },
    {
        'id': 'neighborhood_integra_2026', 'insurer_id': 'neighborhood', 'insurer_name': 'Neighborhood Health Plan of RI',
        'official_plan_name': 'Neighborhood INTEGRIA D-SNP (2026)', 'display_name': 'Neighborhood INTEGRIA 2026', 'plan_year': 2026,
        'state': 'RI', 'plan_type': 'D_SNP', 'insurance_category': 'D_SNP', 'network_type': 'HMO D-SNP',
        'market_segment': 'Dual Eligible Medicare/Medicaid', 'service_area': 'Statewide RI', 'source_status': 'ACTIVE',
        'aliases': ['INTEGRIA', 'NHPRI D-SNP']
    },
    {
        'id': 'ri_medicaid_managed_2026', 'insurer_id': 'ri_medicaid', 'insurer_name': 'Rhode Island Medicaid (EOHHS)',
        'official_plan_name': 'RI Medicaid Managed Care Protocols (2026)', 'display_name': 'RI Medicaid State Protocols 2026', 'plan_year': 2026,
        'state': 'RI', 'plan_type': 'Medicaid', 'insurance_category': 'MEDICAID', 'network_type': 'Statewide Medicaid Network',
        'market_segment': 'Medicaid State Program', 'service_area': 'Statewide RI', 'source_status': 'ACTIVE',
        'aliases': ['RIte Care', 'Rhody Health']
    },
    {
        'id': 'uhc_medicare_dual_2026', 'insurer_id': 'uhc_ri', 'insurer_name': 'UnitedHealthcare RI',
        'official_plan_name': 'UHC Dual Complete RI (2026)', 'display_name': 'UHC Dual Complete RI 2026', 'plan_year': 2026,
        'state': 'RI', 'plan_type': 'D_SNP', 'insurance_category': 'D_SNP', 'network_type': 'HMO D-SNP',
        'market_segment': 'Dual Eligible Medicare/Medicaid', 'service_area': 'Statewide RI', 'source_status': 'ACTIVE',
        'aliases': ['UHC Dual Complete', 'UnitedHealthcare Dual']
    }
]

raw_plans = d_data.get('plans', [])
all_plans = list(CORE_RI_PLANS)

all_plans.append({
    'id': 'generic_unselected_plan', 'insurer_id': 'unselected', 'insurer_name': 'Generic Insurer',
    'official_plan_name': 'Unselected Plan (Needs Verification)', 'display_name': 'Unselected Generic Plan', 'plan_year': 2026,
    'state': 'RI', 'plan_type': 'Medicare Advantage', 'insurance_category': 'OTHER', 'network_type': 'General',
    'market_segment': 'Unselected', 'service_area': 'All Areas', 'source_status': 'UNVERIFIED', 'aliases': []
})

seen_plan_keys = set((p['state'], p['insurer_id'], p['official_plan_name']) for p in all_plans)

def classify_category(name, ptype=''):
    n = name.upper()
    pt = ptype.upper()
    if 'D-SNP' in n or 'DSNP' in n or 'DUAL' in n:
        return 'D_SNP', 'D_SNP'
    if 'MEDICARE' in n or 'BLUECHIP' in n or 'MEDICARE' in pt:
        return 'MEDICARE_ADVANTAGE', 'Medicare Advantage'
    if 'MEDICAID' in n or 'HUSKY' in n or 'MASSHEALTH' in n or 'MAINECARE' in n or 'DR. DYNASAUR' in n or 'RITE CARE' in n:
        return 'MEDICAID', 'Medicaid'
    if 'CONNECTORCARE' in n or 'ACCESS HEALTH' in n or 'COVERME' in n:
        return 'INDIVIDUAL_MARKETPLACE', 'Individual Marketplace'
    return 'COMMERCIAL', 'Commercial'

for rp in raw_plans:
    st = rp.get('state', 'RI')
    issuer = rp.get('issuer', 'Generic Insurer')
    name = rp.get('name', '')
    ins_id = ISSUER_MAP.get(issuer, 'unselected')
    
    key = (st, ins_id, name)
    if key in seen_plan_keys:
        continue
    seen_plan_keys.add(key)
    
    cat_code, type_label = classify_category(name, rp.get('type', ''))
    
    slug = re.sub(r'[^a-z0-9]+', '_', f"{st}_{ins_id}_{name}".lower()).strip('_')
    
    all_plans.append({
        'id': slug,
        'insurer_id': ins_id,
        'insurer_name': issuer,
        'official_plan_name': name,
        'display_name': name,
        'plan_year': 2026,
        'state': st,
        'plan_type': type_label,
        'insurance_category': cat_code,
        'network_type': rp.get('network', 'State Network'),
        'market_segment': rp.get('market', 'Individual'),
        'service_area': f"Statewide {st}",
        'source_status': 'UNVERIFIED',
        'aliases': [name]
    })

print(f"Generated {len(all_plans)} normalized plans.")

# Update dist/marketplace/marketplace.js using string replacement
js_file = Path('dist/marketplace/marketplace.js')
js_text = js_file.read_text()

insurers_js_str = "  const INSURERS = " + json.dumps(INSURERS, indent=4) + ";"
plans_js_str = "  const PLANS = " + json.dumps(all_plans, indent=4) + ";"

def replace_const(text, var_name, new_code):
    pattern = rf'  const {var_name} = \[.*?\];'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        start, end = match.span()
        return text[:start] + new_code + text[end:]
    return text

js_text = replace_const(js_text, 'INSURERS', insurers_js_str)
js_text = replace_const(js_text, 'PLANS', plans_js_str)

js_file.write_text(js_text)
print("Successfully updated INSURERS and PLANS in dist/marketplace/marketplace.js.")

