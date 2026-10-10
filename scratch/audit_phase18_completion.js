const fs = require('fs');
let code = fs.readFileSync('dist/marketplace/marketplace.js', 'utf8');
const dummyElem = { addEventListener: () => {}, querySelector: () => dummyElem, querySelectorAll: () => [], innerHTML: '', style: {}, textContent: '', value: '' };
const mockWindow = { addEventListener: () => {} };
const mockDoc = { getElementById: () => dummyElem, querySelector: () => dummyElem, querySelectorAll: () => [dummyElem], addEventListener: () => {} };

const lastIdx = code.lastIndexOf('})();');
code = code.slice(0, lastIdx) + ' window.PLANS = PLANS; window.PRODUCTS = PRODUCTS; window.COVERAGE_RULES = COVERAGE_RULES; window.BENEFITS = BENEFITS; window.SERVICES = typeof SERVICES !== "undefined" ? SERVICES : []; window.INSURERS = INSURERS; window.getMarketplaceForPlan = getMarketplaceForPlan; })();';

eval('(function(window, document) { ' + code + ' })(mockWindow, mockDoc);');

const target32 = [
  'bcbsri_bluechip_core_2026', 'neighborhood_integra_2026', 'uhc_medicare_dual_2026', 'ri_medicaid_managed_2026', 'tufts_ri_medicare_2026', 'bcbsri_access_2026', 'neighborhood_access_2026',
  'ma_wellsense_wellsense_connectorcare', 'ma_tufts_p32_tufts_health_direct_connectorcare', 'ma_bcbsma_health_connector_standard_plan', 'ma_harvard_pilgrim_standard_silver_ii', 'ma_mgb_health_connectorcare', 'ma_health_new_england_connectorcare',
  'ct_husky_health_husky_a', 'ct_husky_health_husky_b', 'ct_husky_health_husky_c', 'ct_husky_health_husky_d', 'ct_connecticare_connecticare_choice_silver', 'ct_connecticare_connecticare_covered_ct', 'ct_anthem_bcbs_anthem_pathway_standard_silver',
  'nh_wellsense_medicaid_mco', 'nh_amerihealth_caritas_medicaid', 'nh_nh_healthy_families_medicaid', 'nh_harvard_pilgrim_nh_local_hmo_silver_6000_standard_0_rx_list_0_virtual_urgent_care',
  'me_mainecare_medicaid', 'me_community_health_options_community_health_options_clear_choice', 'me_harvard_pilgrim_clear_choice_hmo_silver_4000', 'me_anthem_bcbs_anthem_clear_choice_ppo',
  'vt_vermont_medicaid', 'vt_dr_dynasaur_medicaid', 'vt_mvp_health_mvp_vt_plus_silver', 'vt_bcbsvt_bcbsvt_silver'
];

console.log('--- PHASE 18 DEEP CATALOG AUDIT REPORT ---');
const totalMasterCatalogItems = mockWindow.PRODUCTS.length + mockWindow.SERVICES.length + mockWindow.BENEFITS.length;
console.log('Total Master Catalog Items:', totalMasterCatalogItems);

const planAuditResults = [];

target32.forEach(planId => {
  const plan = mockWindow.PLANS.find(p => p.id === planId) || {};
  const cat = mockWindow.getMarketplaceForPlan(planId);
  
  const pCov = cat.products.filter(p => p.is_mapped && p.coverage_status_code === 'COVERED').length;
  const pCond = cat.products.filter(p => p.is_mapped && (p.coverage_status_code === 'CONDITIONAL' || p.coverage_status_code === 'OTC_ELIGIBLE')).length;
  const pNot = cat.products.filter(p => p.is_mapped && p.coverage_status_code === 'NOT_COVERED').length;
  const pNeeds = cat.products.filter(p => !p.is_mapped || p.coverage_status_code === 'NEEDS_VERIFICATION').length;

  const sCov = cat.services.filter(s => s.is_mapped && s.coverage_status_code === 'COVERED').length;
  const sCond = cat.services.filter(s => s.is_mapped && s.coverage_status_code === 'CONDITIONAL').length;
  const sNot = cat.services.filter(s => s.is_mapped && s.coverage_status_code === 'NOT_COVERED').length;
  const sNeeds = cat.services.filter(s => !s.is_mapped || s.coverage_status_code === 'NEEDS_VERIFICATION').length;

  const bCov = cat.benefits.filter(b => b.is_mapped && b.coverage_status_code === 'COVERED').length;
  const bCond = cat.benefits.filter(b => b.is_mapped && b.coverage_status_code === 'CONDITIONAL').length;
  const bNeeds = cat.benefits.filter(b => !b.is_mapped || b.coverage_status_code === 'NEEDS_VERIFICATION').length;

  const verifiedDepth = pCov + pCond + sCov + sCond + bCov + bCond;
  const reviewCompleteness = Math.round((verifiedDepth / totalMasterCatalogItems) * 100);

  let completionStatus = 'INITIAL';
  if (verifiedDepth >= 8) {
    completionStatus = 'SUBSTANTIAL';
  } else if (verifiedDepth >= 5) {
    completionStatus = 'PARTIAL';
  }

  planAuditResults.push({
    state: plan.state || '??',
    insurer: plan.insurer_name || plan.insurer_id || '??',
    plan_name: plan.official_plan_name || plan.display_name || planId,
    plan_id: planId,
    products: { covered: pCov, conditional: pCond, not_covered: pNot, needs_verification: pNeeds },
    services: { covered: sCov, conditional: sCond, not_covered: sNot, needs_verification: sNeeds },
    benefits: { covered: bCov, conditional: bCond, needs_verification: bNeeds },
    verified_catalog_depth: verifiedDepth,
    review_completeness_pct: reviewCompleteness,
    completion_status: completionStatus
  });
});

console.log(JSON.stringify(planAuditResults, null, 2));
