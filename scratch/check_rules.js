
const fs = require('fs');
let code = fs.readFileSync('dist/marketplace/marketplace.js', 'utf8');
const dummyElem = { addEventListener: () => {}, querySelector: () => dummyElem, querySelectorAll: () => [], innerHTML: '', style: {}, textContent: '', value: '' };
const mockWindow = { addEventListener: () => {} };
const mockDoc = { getElementById: () => dummyElem, querySelector: () => dummyElem, querySelectorAll: () => [dummyElem], addEventListener: () => {} };

const lastIdx = code.lastIndexOf('})();');
code = code.slice(0, lastIdx) + ' window.PLANS = PLANS; window.PRODUCTS = PRODUCTS; window.COVERAGE_RULES = COVERAGE_RULES; window.BENEFITS = BENEFITS; window.INSURERS = INSURERS; })();';

eval('(function(window, document) { ' + code + ' })(mockWindow, mockDoc);');

const rules = mockWindow.COVERAGE_RULES;
console.log('Total COVERAGE_RULES count:', rules.length);

const rulesByPlan = {};
rules.forEach(r => {
  const pId = r.plan_id;
  if (!rulesByPlan[pId]) rulesByPlan[pId] = [];
  rulesByPlan[pId].push(r);
  if (r.applicable_plan_ids && Array.isArray(r.applicable_plan_ids)) {
    r.applicable_plan_ids.forEach(apId => {
      if (apId !== pId) {
        if (!rulesByPlan[apId]) rulesByPlan[apId] = [];
        rulesByPlan[apId].push(r);
      }
    });
  }
});

console.log('Plans with explicit rules count:', Object.keys(rulesByPlan).length);
for (const pId in rulesByPlan) {
  const pRules = rulesByPlan[pId];
  const prods = pRules.filter(r => r.target_type === 'PRODUCT' || r.product_id).length;
  const servs = pRules.filter(r => r.target_type === 'SERVICE' || r.service_id).length;
  const bens = pRules.filter(r => r.target_type === 'BENEFIT' || r.benefit_id).length;
  console.log('Plan [' + pId + ']: ' + pRules.length + ' rules (products: ' + prods + ', services: ' + servs + ', benefits: ' + bens + ')');
}
