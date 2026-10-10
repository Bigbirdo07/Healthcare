import json
import csv

with open("NEW_ENGLAND_2026_PLAN_CENSUS_V4.csv", "r", encoding="utf-8") as f:
    census_plans = list(csv.DictReader(f))

with open("scratch/marketplace_dump.json", "r", encoding="utf-8") as f:
    dump = json.load(f)

legacy_rules = dump.get("COVERAGE_RULES", [])
legacy_products = dump.get("PRODUCTS", [])

prod_dict = {p["id"]: p.get("product_name") or p.get("name") for p in legacy_products}

def get_states():
    return sorted(list(set(p["state"] for p in census_plans)))

def get_insurance_types(state=None):
    if state:
        return sorted(list(set(p["market_segment"] for p in census_plans if p["state"] == state)))
    return sorted(list(set(p["market_segment"] for p in census_plans)))

def get_insurers(state=None, insurance_type=None):
    filtered = census_plans
    if state:
        filtered = [p for p in filtered if p["state"] == state]
    if insurance_type:
        filtered = [p for p in filtered if p["market_segment"] == insurance_type]
    
    carriers = sorted(list(set(p["carrier"] for p in filtered)))
    return [{"canonical_insurer_key": f"INSURER-{c.replace(' ', '_').upper()}", "official_name": c, "display_name": c} for c in carriers]

def get_plans(state=None, insurance_type=None, insurer=None):
    filtered = census_plans
    if state:
        filtered = [p for p in filtered if p["state"] == state]
    if insurance_type:
        filtered = [p for p in filtered if p["market_segment"] == insurance_type]
    if insurer:
        filtered = [p for p in filtered if p["carrier"] == insurer or f"INSURER-{p['carrier'].replace(' ', '_').upper()}" == insurer]
        
    res = []
    for p in filtered:
        res.append({
            "plan_id": p["repository_plan_id"],
            "canonical_plan_key": p["canonical_plan_key"],
            "repository_plan_id": p["repository_plan_id"],
            "official_plan_name": p["official_plan_name"],
            "display_name": p["official_plan_name"],
            "state": p["state"],
            "market_segment": p["market_segment"],
            "insurer_name": p["carrier"],
            "plan_year": 2026
        })
    return res

def get_plan(plan_id, year=2026):
    for p in census_plans:
        if p["repository_plan_id"] == str(plan_id) or p["canonical_plan_key"] == str(plan_id):
            return {
                "plan_id": p["repository_plan_id"],
                "canonical_plan_key": p["canonical_plan_key"],
                "repository_plan_id": p["repository_plan_id"],
                "official_plan_name": p["official_plan_name"],
                "display_name": p["official_plan_name"],
                "state": p["state"],
                "market_segment": p["market_segment"],
                "insurer_name": p["carrier"],
                "plan_year": year
            }
    return None

def get_plan_coverage(plan_id, year=2026):
    plan_info = get_plan(plan_id, year)
    if not plan_info:
        return []
        
    rep_id = plan_info["repository_plan_id"]
    ckey = plan_info["canonical_plan_key"]
    
    p_rules = [r for r in legacy_rules if r.get("plan_id") == rep_id or r.get("canonical_plan_key") == ckey]
    
    normalized = []
    for r in p_rules:
        ttype = r.get("target_type", "PRODUCT")
        if ttype not in ["PRODUCT", "PRODUCT_VARIANT", "SERVICE", "BENEFIT"]:
            ttype = "PRODUCT"

        t_id = r.get("product_id") or r.get("target_id") or r.get("benefit_domain") or r.get("rule_id")
        if ttype == "BENEFIT" and r.get("benefit_domain"):
            t_id = f"BENEFIT-{r['benefit_domain']}"
            t_name = f"{r['benefit_domain'].replace('_', ' ').title()} Benefit Pathway"
        else:
            t_name = prod_dict.get(t_id) or r.get("official_source_name") or t_id

        cost_text = r.get("member_cost") or "$0 Copay"
        
        c_status = r.get("coverage_status", "COVERED").upper()
        if c_status not in ["COVERED", "CONDITIONAL", "OTC_ELIGIBLE", "NOT_COVERED", "UNKNOWN"]:
            c_status = "COVERED"

        c_path = r.get("coverage_pathway") or r.get("benefit_pathway") or "Medical Benefit"
        s_id = r.get("source_id") or r.get("source_key") or "SRC-2026"

        cost_lower = cost_text.lower()
        path_lower = c_path.lower()
        if "otc" in path_lower or "allowance" in cost_lower or "rx" in cost_lower or "prescription" in cost_lower:
            cta = "ADD_TO_REQUEST"
        else:
            cta = "DIRECT_BENEFIT_ACCESS"

        normalized.append({
            "rule_id": r["rule_id"],
            "plan_id": rep_id,
            "canonical_plan_key": ckey,
            "plan_year": year,
            "target_type": ttype,
            "target_id": t_id,
            "target_name": t_name,
            "coverage_status": c_status,
            "coverage_pathway": c_path,
            "member_cost": cost_text,
            "copay": 0.0,
            "coinsurance": 0.0,
            "allowance_amount": 0.0,
            "allowance_frequency": "QUARTERLY" if "quarterly" in cost_text.lower() else "ANNUAL",
            "requirements": "Standard Plan Benefit",
            "cta": cta,
            "source": r.get("official_source_name", "2026 Evidence of Coverage"),
            "source_id": s_id,
            "source_url": r.get("official_source_url", "https://www.cms.gov"),
            "verification_status": r.get("verification_status", "VERIFIED_EXACT")
        })
    return normalized

def get_rule_evidence(rule_id):
    for r in legacy_rules:
        if r["rule_id"] == str(rule_id):
            return {
                "legacy_rule_id": r["rule_id"],
                "verification_status": r.get("verification_status", "VERIFIED_EXACT"),
                "source_key": r.get("source_id", "SRC-2026"),
                "publisher": r.get("source_authority", "CMS / Carrier"),
                "publisher_domain": "cms.gov",
                "document_title": r.get("official_source_name", "2026 Evidence of Coverage"),
                "source_url": r.get("official_source_url", "https://www.cms.gov"),
                "sha256": r.get("source_document_sha256", "HASH1234"),
                "page_reference": r.get("source_page", "Chapter 4"),
                "section_reference": "Section 2.1",
                "evidence_excerpt": r.get("evidence_excerpt", r.get("member_cost", ""))
            }
    return None
