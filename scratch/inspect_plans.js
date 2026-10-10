
const fs = require('fs');
let code = fs.readFileSync('dist/marketplace/marketplace.js', 'utf8');

const dummyElem = { addEventListener: () => {}, querySelector: () => dummyElem, querySelectorAll: () => [], innerHTML: '', style: {}, textContent: '', value: '' };
const mockWindow = { addEventListener: () => {} };
const mockDoc = { getElementById: () => dummyElem, querySelector: () => dummyElem, querySelectorAll: () => [dummyElem], addEventListener: () => {} };

const lastIndex = code.lastIndexOf('})();');
code = code.substring(0, lastIndex) + '
 window.PLANS = PLANS; window.PRODUCTS = PRODUCTS; window.COVERAGE_RULES = COVERAGE_RULES; window.BENEFITS = BENEFITS; window.INSURERS = INSURERS;
})();';

eval('(function(window, document) { ' + code + ' })(mockWindow, mockDoc);');

const plans = mockWindow.PLANS;
console.log('Total plans in PLANS array:', plans.length);

const prodPlans = plans.filter(p => p.production_visibility !== false && !p.is_test_fixture && p.environment !== 'TEST');
console.log('Plans where production_visibility !== false:', prodPlans.length);

const byStateProd = {};
prodPlans.forEach(p => {
  byStateProd[p.state] = (byStateProd[p.state] || []).concat(p);
});

for (const st in byStateProd) {
  console.log('
=== State:', st, 'Count:', byStateProd[st].length, '===');
  byStateProd[st].forEach(p => {
    console.log(' - ID:', p.id, '| status:', p.plan_identity_status, '| vis:', p.production_visibility, '| name:', p.official_plan_name || p.display_name);
  });
}
