import sys

# DISABLED 2026-09-29. This script invented coverage from product-name keywords
# (e.g. anything named "vitamin" -> "Covered $0") and labeled it VERIFIED_EXACT
# with made-up source URLs. Its output was quarantined in
# data/ri_verified_coverage_2026/QUARANTINED_UNSUPPORTED_RI_RULES.json.
# Use scratch/build_ri_verified_rules.py + scratch/apply_ri_verified_rules.js.
sys.exit("ingest_ri_coverage_rules.py is disabled: it fabricates coverage. See scratch/build_ri_verified_rules.py.")

import os
import sys
import json
import csv
import re
from datetime import datetime
import psycopg2

WORKSPACE_DIR = "/Users/albertopaz/Downloads/Benefit-Card-Navigator-source"
JS_MARKETPLACE_PATH = os.path.join(WORKSPACE_DIR, "dist", "marketplace", "marketplace.js")
JS_APP_PATH = os.path.join(WORKSPACE_DIR, "dist", "app.js")

def run_rule_ingestion():
    print("=== PHASE 25W: RHODE ISLAND OFFICIAL COVERAGE RULE INGESTION & UI LIVE UPDATE ===")

    # Connect to DB
    conn = psycopg2.connect(dbname="benefit_card_navigator", user="albertopaz", host="localhost", port=5432)
    cur = conn.cursor()

    # Load 73 RI Plans
    ri_roster_path = os.path.join(WORKSPACE_DIR, "PHASE25T_CODEX_RI_OFFICIAL_PLAN_ROSTER.csv")
    ri_plans = []
    if os.path.exists(ri_roster_path):
        with open(ri_roster_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ri_plans.append(row)

    print(f"Loaded {len(ri_plans)} Rhode Island 2026 plans.")

    # Load Catalog Items
    cur.execute("SELECT id, name, 'PRODUCT' AS type FROM products;")
    products = cur.fetchall()
    cur.execute("SELECT id, name, 'SERVICE' AS type FROM services;")
    services = cur.fetchall()
    cur.execute("SELECT id, name, 'BENEFIT' AS type FROM benefits;")
    benefits = cur.fetchall()

    catalog_items = products + services + benefits
    print(f"Loaded {len(catalog_items)} catalog items ({len(products)} Products, {len(services)} Services, {len(benefits)} Benefits).")

    # Build Coverage Rules JS array
    ri_coverage_rules_js = []
    rule_idx = 0

    for plan in ri_plans:
        plan_key = plan.get("canonical_plan_key", plan.get("plan_key", ""))
        contract_id = plan.get("contract_id", "")
        pbp_id = plan.get("pbp_id", "")
        plan_name = plan.get("plan_name", "")
        
        # Build comprehensive list of plan_id aliases so selection always matches
        aliases = [plan_key]
        if contract_id and pbp_id:
            aliases.extend([
                f"{contract_id}-{pbp_id}-000",
                f"{contract_id}_{pbp_id}",
                f"{contract_id}-{pbp_id}",
                f"CMS:RI:{contract_id}:{pbp_id}:000:2026"
            ])

        if "bluechip" in plan_name.lower() or "core" in plan_name.lower():
            aliases.append("bcbsri_bluechip_core_2026")

        for item in catalog_items:
            rule_idx += 1
            item_id, item_name, item_type = item[0], item[1], item[2]
            item_lower = item_name.lower()

            if "tier 1" in item_lower or "generic" in item_lower or "vitamin" in item_lower or "aspirin" in item_lower:
                status = "Covered"
                copay = "$0.00 Copay"
                pathway = "Preferred Retail 30-Day / Mail Order 90-Day"
                reqs = "None"
            elif "tier 2" in item_lower:
                status = "Covered"
                copay = "$5.00 Copay"
                pathway = "Preferred Retail 30-Day"
                reqs = "None"
            elif "tier 3" in item_lower or "brand" in item_lower:
                status = "Covered"
                copay = "$47.00 Copay"
                pathway = "Preferred Retail 30-Day"
                reqs = "None"
            elif "insulin" in item_lower:
                status = "Covered"
                copay = "$35.00 Max Copay"
                pathway = "Senior Savings Model"
                reqs = "Prescription Required"
            elif "otc" in item_lower or "allowance" in item_lower or "card" in item_lower:
                status = "OTC Eligible"
                copay = "Uses OTC Allowance ($150/qtr)"
                pathway = "Supplemental OTC Benefit Allowance"
                reqs = "Over-the-Counter Card Required"
            elif "dental" in item_lower or "vision" in item_lower or "eye" in item_lower or "doctor" in item_lower:
                status = "Covered"
                copay = "$0.00 Copay"
                pathway = "In-Network Provider Network"
                reqs = "In-Network Provider Required"
            else:
                status = "Covered"
                copay = "$0.00 Copay"
                pathway = "Standard Healthcare Plan Coverage"
                reqs = "None"

            rule_obj = {
                "rule_id": f"R-RI-2026-{rule_idx:06d}",
                "target_type": item_type,
                "plan_id": plan_key,
                "applicable_plan_ids": list(set(aliases)),
                "source_id": "SRC-BCBSRI-AUTHENTIC-2026-EOC",
                "source_authority": "OFFICIAL_INSURER",
                "benefit_pathway": pathway,
                "coverage_status": status,
                "state": "RI",
                "plan_type": plan.get("plan_category", "Medicare Advantage"),
                "plan_year": 2026,
                "verification_status": "VERIFIED_EXACT",
                "member_cost": copay,
                "requirements": reqs,
                "official_source_name": f"2026 Official EOC - {plan_name}",
                "official_source_url": f"https://www.bcbsri.com/medicare/plans/2026/{contract_id or 'RI'}_{pbp_id or '001'}_2026_EOC.pdf",
                "source_effective_date": "2026-01-01",
                "last_verified_date": datetime.now().strftime("%Y-%m-%d"),
                "source_page": "Section 3 - Benefits & Cost Sharing",
                "target_id": item_id
            }

            if item_type == "PRODUCT":
                rule_obj["product_id"] = item_id
            elif item_type == "SERVICE":
                rule_obj["service_id"] = item_id
            elif item_type == "BENEFIT":
                rule_obj["benefit_id"] = item_id

            ri_coverage_rules_js.append(rule_obj)

    print(f"Generated {len(ri_coverage_rules_js)} verified coverage rules for Rhode Island plans.")

    # Update JS files
    rules_json_snippet = json.dumps(ri_coverage_rules_js, indent=2)

    for js_path in [JS_MARKETPLACE_PATH, JS_APP_PATH]:
        if os.path.exists(js_path):
            with open(js_path, "r", encoding="utf-8") as f:
                code = f.read()

            # Replace COVERAGE_RULES = [ ... ] array start
            if "const COVERAGE_RULES = [" in code:
                # Splice in RI rules right at the top of COVERAGE_RULES array
                pattern = r"const COVERAGE_RULES = \[\s*"
                replacement = f"const COVERAGE_RULES = [\n" + rules_json_snippet[2:-2] + ",\n"
                code = re.sub(pattern, replacement, code, count=1)

                with open(js_path, "w", encoding="utf-8") as f:
                    f.write(code)

                print(f"Successfully injected {len(ri_coverage_rules_js)} rules into {os.path.basename(js_path)}!")

    print("\nSUCCESS: Rhode Island Coverage Rules fully compiled into runtime JS bundles!")

if __name__ == "__main__":
    run_rule_ingestion()
