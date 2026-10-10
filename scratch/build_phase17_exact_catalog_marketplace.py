import json
import re
from pathlib import Path

print("Building Phase 17 Exact Plan Catalog Query Engine & Marketplace Integration...")

js_path = Path('dist/marketplace/marketplace.js')
code = js_path.read_text(encoding='utf-8')

# Ensure SERVICES array exists
SERVICES_BLOCK = """  const SERVICES = [
    {
      id: 'S-DEN-EXAM',
      service_id: 'S-DEN-EXAM',
      target_type: 'SERVICE',
      service_name: 'Routine Dental Cleanings & Preventive Exam',
      category: 'dental',
      description: 'Preventive dental cleaning, comprehensive oral evaluation, and diagnostic bitewing x-rays.',
      icon: '🦷'
    },
    {
      id: 'S-VIS-EXAM',
      service_id: 'S-VIS-EXAM',
      target_type: 'SERVICE',
      service_name: 'Annual Routine Vision Examination',
      category: 'eyecare',
      description: 'Comprehensive eye health examination and vision refraction testing by network optometrist/ophthalmologist.',
      icon: '👓'
    },
    {
      id: 'S-TRN-RIDE',
      service_id: 'S-TRN-RIDE',
      target_type: 'SERVICE',
      service_name: 'Non-Emergency Medical Transportation Ride',
      category: 'ssbci',
      description: 'Covered roundtrip transportation to medical appointments, dialysis, and pharmacy pickups.',
      icon: '🚐'
    },
    {
      id: 'S-PREV-WELLNESS',
      service_id: 'S-PREV-WELLNESS',
      target_type: 'SERVICE',
      service_name: 'Annual Physical & Preventive Wellness Visit',
      category: 'diagnostics',
      description: 'Comprehensive annual wellness checkup, preventive screening, and personalized health plan.',
      icon: '🩺'
    }
  ];
"""

if 'const SERVICES = [' not in code:
    # Insert SERVICES right after BENEFITS definition
    b_idx = code.find('const BENEFITS = [')
    if b_idx != -1:
        end_b = code.find('];', b_idx)
        if end_b != -1:
            code = code[:end_b+2] + '\n\n' + SERVICES_BLOCK + code[end_b+2:]

# Ensure getMarketplaceForPlan function exists and is exported
GET_MARKETPLACE_FUNC = """  // --- 11. EXACT PLAN MARKETPLACE QUERY CONTRACT ---
  function getMarketplaceForPlan(planId) {
    const targetPlanId = planId || activePlanId || 'generic_unselected_plan';

    if (targetPlanId === 'generic_unselected_plan' || activeInsurerId === 'unselected') {
      return {
        plan_id: targetPlanId,
        products: PRODUCTS.map(p => ({
          ...p,
          entity_type: 'PRODUCT',
          entity_id: p.id || p.product_id,
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
        })),
        services: (typeof SERVICES !== 'undefined' ? SERVICES : []).map(s => ({
          ...s,
          entity_type: 'SERVICE',
          entity_id: s.id || s.service_id,
          plan_id: targetPlanId,
          coverage_status: 'Unknown / needs verification',
          coverage_status_code: 'NEEDS_VERIFICATION',
          benefit_pathway: 'Medical / Dental benefit',
          requirements: 'Plan verification required',
          member_cost: 'Unknown',
          official_source_name: 'Official Plan Document Required',
          official_source_url: '/find-care/#sources',
          source_id: 'SRC-UNVERIFIED',
          plan_year: 2026,
          is_mapped: false
        })),
        benefits: (typeof BENEFITS !== 'undefined' ? BENEFITS : []).map(b => ({
          ...b,
          entity_type: 'BENEFIT',
          entity_id: b.id || b.benefit_id,
          plan_id: targetPlanId,
          coverage_status: 'Unknown / needs verification',
          coverage_status_code: 'NEEDS_VERIFICATION',
          benefit_pathway: 'Supplemental Benefit Allowance',
          requirements: 'Plan verification required',
          member_cost: 'Unknown',
          official_source_name: 'Official Plan Document Required',
          official_source_url: '/find-care/#sources',
          source_id: 'SRC-UNVERIFIED',
          plan_year: 2026,
          is_mapped: false
        }))
      };
    }

    // Find rules that explicitly apply to targetPlanId
    const applicableRules = COVERAGE_RULES.filter(r => 
      r.plan_id === targetPlanId || (r.applicable_plan_ids && Array.isArray(r.applicable_plan_ids) && r.applicable_plan_ids.includes(targetPlanId))
    );

    // Map Products
    const mappedProducts = PRODUCTS.map(p => {
      const pId = p.id || p.product_id;
      const rule = applicableRules.find(r => 
        (r.target_type === 'PRODUCT' || !r.target_type) && 
        (r.product_id === pId || r.target_id === pId)
      );

      if (rule) {
        const statusStr = rule.coverage_status || 'Covered';
        let statusCode = 'COVERED';
        const sLower = statusStr.toLowerCase();
        if (sLower.includes('not')) {
          statusCode = 'NOT_COVERED';
        } else if (sLower.includes('otc') || sLower.includes('allowance')) {
          statusCode = 'OTC_ELIGIBLE';
        } else if (sLower.includes('conditional') || sLower.includes('order') || sLower.includes('rx')) {
          statusCode = 'CONDITIONAL';
        }

        return {
          ...p,
          entity_type: 'PRODUCT',
          entity_id: pId,
          plan_id: targetPlanId,
          coverage_status: statusStr,
          coverage_status_code: statusCode,
          benefit_pathway: rule.benefit_pathway || 'OTC allowance',
          requirements: rule.requirements || (rule.provider_order_required ? 'Provider Order Required' : (rule.prescription_required ? 'Prescription Required' : 'None')),
          member_cost: rule.member_cost || rule.copay || '$0.00',
          official_source_name: rule.official_source_name || 'Official Plan Document',
          official_source_url: rule.official_source_url || '/find-care/#sources',
          source_id: rule.source_id || 'SRC-VERIFIED',
          plan_year: rule.plan_year || 2026,
          rule_id: rule.rule_id,
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
        official_source_name: 'Generic Plan Evidence of Coverage',
        official_source_url: '/find-care/#sources',
        source_id: 'SRC-FALLBACK',
        plan_year: 2026,
        is_mapped: false
      };
    });

    // Map Services
    const serviceList = typeof SERVICES !== 'undefined' ? SERVICES : [];
    const mappedServices = serviceList.map(s => {
      const sId = s.id || s.service_id;
      const rule = applicableRules.find(r => 
        (r.target_type === 'SERVICE' || r.service_id) && 
        (r.service_id === sId || r.target_id === sId)
      );

      if (rule) {
        const statusStr = rule.coverage_status || 'Covered';
        const statusCode = statusStr.toLowerCase().includes('conditional') ? 'CONDITIONAL' : 'COVERED';

        return {
          ...s,
          entity_type: 'SERVICE',
          entity_id: sId,
          plan_id: targetPlanId,
          coverage_status: statusStr,
          coverage_status_code: statusCode,
          benefit_pathway: rule.benefit_pathway || 'Preventive care benefit',
          requirements: rule.requirements || (rule.prior_authorization_required ? 'Prior Authorization Required' : 'In-Network Provider'),
          member_cost: rule.member_cost || rule.copay || '$0.00',
          official_source_name: rule.official_source_name || 'Official Plan Document',
          official_source_url: rule.official_source_url || '/find-care/#sources',
          source_id: rule.source_id || 'SRC-VERIFIED',
          plan_year: rule.plan_year || 2026,
          rule_id: rule.rule_id,
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
      };
    });

    // Map Benefits
    const benefitList = typeof BENEFITS !== 'undefined' ? BENEFITS : [];
    const mappedBenefits = benefitList.map(b => {
      const bId = b.id || b.benefit_id;
      const rule = applicableRules.find(r => 
        (r.target_type === 'BENEFIT' || r.benefit_id) && 
        (r.benefit_id === bId || r.target_id === bId || b.plan_id === targetPlanId)
      );

      const isPlanSpecific = b.plan_id === targetPlanId;

      if (rule || isPlanSpecific) {
        const statusStr = (rule && rule.coverage_status) ? rule.coverage_status : 'Covered';
        return {
          ...b,
          entity_type: 'BENEFIT',
          entity_id: bId,
          plan_id: targetPlanId,
          coverage_status: statusStr,
          coverage_status_code: 'COVERED',
          benefit_pathway: (rule && rule.benefit_pathway) ? rule.benefit_pathway : (b.benefit_type || 'Supplemental Benefit Allowance'),
          requirements: 'Active plan membership',
          member_cost: b.allowance_amount ? `$${b.allowance_amount} ${b.allowance_period || 'allowance'}` : '$0.00 member cost',
          official_source_name: (rule && rule.official_source_name) ? rule.official_source_name : 'Plan Evidence of Coverage / OTC Catalog',
          official_source_url: '/find-care/#sources',
          source_id: (rule && rule.source_id) ? rule.source_id : 'SRC-VERIFIED',
          plan_year: 2026,
          is_mapped: true
        };
      }

      return {
        ...b,
        entity_type: 'BENEFIT',
        entity_id: bId,
        plan_id: targetPlanId,
        coverage_status: 'Unknown / needs verification',
        coverage_status_code: 'NEEDS_VERIFICATION',
        benefit_pathway: 'Supplemental Benefit Allowance',
        requirements: 'Plan verification required',
        member_cost: 'Unknown',
        official_source_name: 'Generic Plan Evidence of Coverage',
        official_source_url: '/find-care/#sources',
        source_id: 'SRC-FALLBACK',
        plan_year: 2026,
        is_mapped: false
      };
    });

    return {
      plan_id: targetPlanId,
      products: mappedProducts,
      services: mappedServices,
      benefits: mappedBenefits
    };
  }

  window.getMarketplaceForPlan = getMarketplaceForPlan;
"""

if 'function getMarketplaceForPlan' not in code:
    # Insert right before init or window exports
    init_idx = code.find('function init()')
    if init_idx != -1:
        code = code[:init_idx] + GET_MARKETPLACE_FUNC + '\n\n' + code[init_idx:]

js_path.write_text(code, encoding='utf-8')
print("Successfully built Phase 17 Exact Plan Catalog Query Contract into marketplace.js.")
