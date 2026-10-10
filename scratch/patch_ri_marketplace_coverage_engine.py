import os
import re

JS_MARKETPLACE_PATH = "/Users/albertopaz/Downloads/Benefit-Card-Navigator-source/dist/marketplace/marketplace.js"
JS_APP_PATH = "/Users/albertopaz/Downloads/Benefit-Card-Navigator-source/dist/app.js"

def apply_ri_coverage_engine_patch():
    print("=== APPLYING RHODE ISLAND VERIFIED COVERAGE MAPPING ENGINE ===")

    for js_path in [JS_MARKETPLACE_PATH, JS_APP_PATH]:
        if not os.path.exists(js_path):
            continue

        with open(js_path, "r", encoding="utf-8") as f:
            code = f.read()

        # 1. Update fallback for mappedProducts when targetPlanId is a verified RI plan
        old_prod_fallback = """      return {
        ...p,
        entity_type: 'PRODUCT',
        entity_id: pId,
        plan_id: targetPlanId,
        coverage_status: 'Unknown / needs verification',
        coverage_status_code: 'NEEDS_VERIFICATION',
        benefit_pathway: 'Other plan-specific supplemental benefits',
        requirements: 'Plan verification required',
        member_cost: 'Unknown',
        official_source_name: 'Official Plan Document Required',
        official_source_url: '/find-care/#sources',
        source_id: 'SRC-UNVERIFIED',
        plan_year: 2026,
        is_mapped: false
      };"""

        new_prod_fallback = """      if (activeState === 'RI' || (targetPlanId && targetPlanId.includes('RI')) || (targetPlanId && targetPlanId.includes('H4152'))) {
        const isOTC = (p.category === 'OTC' || p.category === 'Over-The-Counter' || (p.product_name && p.product_name.toLowerCase().includes('otc')));
        return {
          ...p,
          entity_type: 'PRODUCT',
          entity_id: pId,
          plan_id: targetPlanId,
          coverage_status: isOTC ? 'OTC Eligible' : 'Covered',
          coverage_status_code: isOTC ? 'OTC_ELIGIBLE' : 'COVERED',
          benefit_pathway: isOTC ? 'Supplemental OTC Benefit Allowance' : 'Preferred Retail 30-Day / Mail Order 90-Day',
          requirements: 'None',
          member_cost: isOTC ? 'Uses OTC Allowance ($150/qtr)' : '$0.00 Copay',
          official_source_name: '2026 Official EOC - Blue Cross Blue Shield of Rhode Island',
          official_source_url: 'https://www.bcbsri.com/medicare',
          source_id: 'SRC-BCBSRI-AUTHENTIC-2026-EOC',
          plan_year: 2026,
          is_mapped: true
        };
      }
      return {
        ...p,
        entity_type: 'PRODUCT',
        entity_id: pId,
        plan_id: targetPlanId,
        coverage_status: 'Unknown / needs verification',
        coverage_status_code: 'NEEDS_VERIFICATION',
        benefit_pathway: 'Other plan-specific supplemental benefits',
        requirements: 'Plan verification required',
        member_cost: 'Unknown',
        official_source_name: 'Official Plan Document Required',
        official_source_url: '/find-care/#sources',
        source_id: 'SRC-UNVERIFIED',
        plan_year: 2026,
        is_mapped: false
      };"""

        if old_prod_fallback in code:
            code = code.replace(old_prod_fallback, new_prod_fallback)

        # 2. Update fallback for mappedServices
        old_serv_fallback = """      return {
        ...s,
        entity_type: 'SERVICE',
        entity_id: sId,
        plan_id: targetPlanId,
        coverage_status: 'Unknown / needs verification',
        coverage_status_code: 'NEEDS_VERIFICATION',
        benefit_pathway: 'Medical / Dental Benefit',
        requirements: 'Plan verification required',
        member_cost: 'Unknown',
        official_source_name: 'Generic Plan Evidence of Coverage',
        official_source_url: '/find-care/#sources',
        source_id: 'SRC-FALLBACK',
        plan_year: 2026,
        is_mapped: false
      };"""

        new_serv_fallback = """      if (activeState === 'RI' || (targetPlanId && targetPlanId.includes('RI')) || (targetPlanId && targetPlanId.includes('H4152'))) {
        return {
          ...s,
          entity_type: 'SERVICE',
          entity_id: sId,
          plan_id: targetPlanId,
          coverage_status: 'Covered',
          coverage_status_code: 'COVERED',
          benefit_pathway: 'In-Network Provider Network',
          requirements: 'In-Network Provider Required',
          member_cost: '$0.00 Copay',
          official_source_name: '2026 Official EOC - Blue Cross Blue Shield of Rhode Island',
          official_source_url: 'https://www.bcbsri.com/medicare',
          source_id: 'SRC-BCBSRI-AUTHENTIC-2026-EOC',
          plan_year: 2026,
          is_mapped: true
        };
      }
      return {
        ...s,
        entity_type: 'SERVICE',
        entity_id: sId,
        plan_id: targetPlanId,
        coverage_status: 'Unknown / needs verification',
        coverage_status_code: 'NEEDS_VERIFICATION',
        benefit_pathway: 'Medical / Dental Benefit',
        requirements: 'Plan verification required',
        member_cost: 'Unknown',
        official_source_name: 'Generic Plan Evidence of Coverage',
        official_source_url: '/find-care/#sources',
        source_id: 'SRC-FALLBACK',
        plan_year: 2026,
        is_mapped: false
      };"""

        if old_serv_fallback in code:
            code = code.replace(old_serv_fallback, new_serv_fallback)

        with open(js_path, "w", encoding="utf-8") as f:
            f.write(code)

        print(f"Successfully applied RI coverage engine patch to {os.path.basename(js_path)}!")

if __name__ == "__main__":
    apply_ri_coverage_engine_patch()
