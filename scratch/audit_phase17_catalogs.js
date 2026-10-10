const fs = require('fs');
let code = fs.readFileSync('dist/marketplace/marketplace.js', 'utf8');
const dummyElem = { addEventListener: () => {}, querySelector: () => dummyElem, querySelectorAll: () => [], innerHTML: '', style: {}, textContent: '', value: '' };
const mockWindow = { addEventListener: () => {} };
const mockDoc = { getElementById: () => dummyElem, querySelector: () => dummyElem, querySelectorAll: () => [dummyElem], addEventListener: () => {} };

const lastIdx = code.lastIndexOf('})();');
code = code.slice(0, lastIdx) + ' window.PLANS = PLANS; window.PRODUCTS = PRODUCTS; window.COVERAGE_RULES = COVERAGE_RULES; window.BENEFITS = BENEFITS; window.INSURERS = INSURERS; window.getMarketplaceForPlan = getMarketplaceForPlan; })();';

eval('(function(window, document) { ' + code + ' })(mockWindow, mockDoc);');

const target32 = [
  'bcbsri_bluechip_core_2026', 'neighborhood_integra_2026', 'uhc_medicare_dual_2026', 'ri_medicaid_managed_2026', 'tufts_ri_medicare_2026', 'bcbsri_access_2026', 'neighborhood_access_2026',
  'ma_wellsense_wellsense_connectorcare', 'ma_tufts_p32_tufts_health_direct_connectorcare', 'ma_bcbsma_health_connector_standard_plan', 'ma_harvard_pilgrim_standard_silver_ii', 'ma_mgb_health_connectorcare', 'ma_health_new_england_connectorcare',
  'ct_husky_health_husky_a', 'ct_husky_health_husky_b', 'ct_husky_health_husky_c', 'ct_husky_health_husky_d', 'ct_connecticare_connecticare_choice_silver', 'ct_connecticare_connecticare_covered_ct', 'ct_anthem_bcbs_anthem_pathway_standard_silver',
  'nh_wellsense_medicaid_mco', 'nh_amerihealth_caritas_medicaid', 'nh_nh_healthy_families_medicaid', 'nh_harvard_pilgrim_nh_local_hmo_silver_6000_standard_0_rx_list_0_virtual_urgent_care',
  'me_mainecare_medicaid', 'me_community_health_options_community_health_options_clear_choice', 'me_harvard_pilgrim_clear_choice_hmo_silver_4000', 'me_anthem_bcbs_anthem_clear_choice_ppo',
  'vt_vermont_medicaid', 'vt_dr_dynasaur_medicaid', 'vt_mvp_health_mvp_vt_plus_silver', 'vt_bcbsvt_bcbsvt_silver'
];

console.log('--- PHASE 17 AUDIT FOR ALL PRODUCTION PLANS ---');
target32.forEach(planId => {
  const cat = mockWindow.getMarketplaceForPlan(planId);
  const pCount = cat.products.filter(p => p.is_mapped).length;
  const sCount = cat.services.filter(s => s.is_mapped).length;
  const bCount = cat.benefits.filter(b => b.is_mapped).length;
  const unmappedCount = cat.products.filter(p => !p.is_mapped).length + cat.services.filter(s => !s.is_mapped).length + cat.benefits.filter(b => !b.is_mapped).length;
  console.log(`Plan [${planId}]: Products=${pCount}, Services=${sCount}, Benefits=${bCount}, Unmapped/NeedsVerification=${unmappedCount}`);
});
