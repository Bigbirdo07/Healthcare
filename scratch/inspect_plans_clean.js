
const fs = require('fs');
let code = fs.readFileSync('dist/marketplace/marketplace.js', 'utf8');
const dummyElem = { addEventListener: () => {}, querySelector: () => dummyElem, querySelectorAll: () => [], innerHTML: '', style: {}, textContent: '', value: '' };
const mockWindow = { addEventListener: () => {} };
const mockDoc = { getElementById: () => dummyElem, querySelector: () => dummyElem, querySelectorAll: () => [dummyElem], addEventListener: () => {} };

const lastIdx = code.lastIndexOf('})();');
code = code.slice(0, lastIdx) + ' window.PLANS = PLANS; window.PRODUCTS = PRODUCTS; window.COVERAGE_RULES = COVERAGE_RULES; window.BENEFITS = BENEFITS; window.INSURERS = INSURERS; })();';

eval('(function(window, document) { ' + code + ' })(mockWindow, mockDoc);');

console.log('Total PLANS in array:', mockWindow.PLANS.length);
const plans = mockWindow.PLANS;
const prod = plans.filter(p => p.production_visibility !== false && !p.is_test_fixture && p.environment !== 'TEST');
console.log('Production visibility != false count:', prod.length);

const bySt = {};
plans.forEach(p => {
  const vis = p.production_visibility !== false && !p.is_test_fixture && p.environment !== 'TEST';
  const idSt = p.plan_identity_status || 'UNSPECIFIED';
  if (!bySt[p.state]) bySt[p.state] = [];
  bySt[p.state].push({ id: p.id, name: p.official_plan_name || p.display_name, vis: vis, idSt: idSt, covSt: p.coverage_verification_status });
});

for (const st in bySt) {
  console.log('State:', st, 'Total plans:', bySt[st].length, 'Prod visible:', bySt[st].filter(x => x.vis).length);
  bySt[st].forEach(x => {
    console.log('  [' + x.st + '] id:' + x.id + ' | vis:' + x.vis + ' | idSt:' + x.idSt + ' | covSt:' + x.covSt + ' | name:' + x.name);
  });
}
