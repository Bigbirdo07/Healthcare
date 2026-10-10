const fs = require('fs');
const path = require('path');
const vm = require('vm');

const htmlContent = fs.readFileSync(path.join(__dirname, '../dist/marketplace/index.html'), 'utf8');
const jsContent = fs.readFileSync(path.join(__dirname, '../dist/marketplace/marketplace.js'), 'utf8');

class MockElement {
  constructor(tagName, id = '') {
    this.tagName = tagName;
    this.id = id;
    this.options = [];
    this.value = '';
    this.disabled = false;
    this.style = {};
    this.innerHTML = '';
    this.textContent = '';
    this.listeners = {};
    this.attributes = {};
  }

  addEventListener(event, fn) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(fn);
  }

  dispatchEvent(event) {
    const ev = typeof event === 'string' ? { type: event, target: this } : { ...event, target: this };
    (this.listeners[ev.type] || []).forEach(fn => fn(ev));
  }

  setAttribute(k, v) { this.attributes[k] = v; }
  getAttribute(k) { return this.attributes[k]; }
}

const elements = {};
function getOrCreate(id, tag = 'div') {
  if (!elements[id]) elements[id] = new MockElement(tag, id);
  return elements[id];
}

const mockDocument = {
  getElementById: (id) => getOrCreate(id),
  querySelector: (sel) => {
    if (sel.startsWith('#')) return getOrCreate(sel.slice(1));
    return new MockElement('div');
  },
  querySelectorAll: () => [],
  addEventListener: () => {},
  body: new MockElement('body'),
  readyState: 'complete'
};

const mockWindow = {
  addEventListener: () => {},
  document: mockDocument,
  Event: class Event { constructor(type) { this.type = type; } }
};

const context = {
  window: mockWindow,
  document: mockDocument,
  console: console,
  setTimeout: setTimeout,
  clearTimeout: clearTimeout
};

vm.createContext(context);
vm.runInContext(jsContent, context);

let passed = 0;
let failed = 0;

function assert(cond, msg) {
  if (cond) {
    passed++;
  } else {
    failed++;
    console.error('FAIL:', msg);
  }
}

const stateSel = mockDocument.getElementById('stateSelect');
const catSel = mockDocument.getElementById('planTypeSelect');
const insSel = mockDocument.getElementById('insurerSelect');
const planSel = mockDocument.getElementById('planSelect');
const statusPill = mockDocument.getElementById('planStatusPill');

// 1. Verify Initial RI State Setup
assert(mockWindow.getActiveState() === 'RI', 'Initial state should be RI');

// 2. Test RI -> MA State Transition
stateSel.value = 'MA';
stateSel.dispatchEvent('change');

assert(mockWindow.getActiveState() === 'MA', 'activeState should be MA');
assert(mockWindow.getActivePlanId() === null, 'activePlanId MUST be reset to null on state change');
assert(insSel.disabled === true, 'Insurer dropdown MUST be disabled on state change');
assert(planSel.disabled === true, 'Plan dropdown MUST be disabled on state change');
assert(catSel.innerHTML.includes('COMMERCIAL'), 'MA category options should include COMMERCIAL');

// 3. Test MA Category Selection (COMMERCIAL)
catSel.value = 'COMMERCIAL';
catSel.dispatchEvent('change');

assert(mockWindow.getSelectedCategory() === 'COMMERCIAL', 'selectedCategory should be COMMERCIAL');
assert(mockWindow.getActivePlanId() === null, 'activePlanId MUST be null after category change');
assert(insSel.disabled === false, 'Insurer dropdown MUST be enabled after category selection');
assert(insSel.innerHTML.includes('bcbsma'), 'MA Commercial insurers should include bcbsma');
assert(!insSel.innerHTML.includes('bcbsri'), 'MA Commercial insurers MUST NOT include bcbsri');
assert(planSel.disabled === true, 'Plan dropdown MUST remain disabled until insurer is selected');

// 4. Test MA Insurer Selection (bcbsma)
insSel.value = 'bcbsma';
insSel.dispatchEvent('change');

assert(mockWindow.getSelectedInsurerId() === 'bcbsma', 'selectedInsurerId should be bcbsma');
assert(mockWindow.getActivePlanId() === null, 'activePlanId MUST be null after insurer change');
assert(planSel.disabled === false, 'Plan dropdown MUST be enabled after insurer selection');
assert(planSel.innerHTML.includes('ma_bcbsma_health_connector_standard_plan'), 'Plan dropdown should include MA BCBSMA plan');
assert(!planSel.innerHTML.includes('bcbsri_bluechip_core_2026'), 'Plan dropdown MUST NOT include RI plans');

// 5. Test MA Plan Selection
planSel.value = 'ma_bcbsma_health_connector_standard_plan';
planSel.dispatchEvent('change');

assert(mockWindow.getActivePlanId() === 'ma_bcbsma_health_connector_standard_plan', 'activePlanId should be set after plan selection');

// 6. Test All 6 New England State Cascading Transitions (RI, MA, CT, NH, ME, VT)
const stateTransitions = [
  { state: 'CT', category: 'MEDICAID', insurer: 'husky_health', plan: 'ct_husky_health_husky_a' },
  { state: 'NH', category: 'MEDICAID', insurer: 'wellsense', plan: 'nh_wellsense_medicaid_mco' },
  { state: 'ME', category: 'MEDICAID', insurer: 'mainecare', plan: 'me_mainecare_medicaid' },
  { state: 'VT', category: 'MEDICAID', insurer: 'vermont_dvha', plan: 'vt_vermont_medicaid' },
  { state: 'RI', category: 'MEDICARE_ADVANTAGE', insurer: 'bcbsri', plan: 'bcbsri_bluechip_core_2026' }
];

stateTransitions.forEach(trans => {
  // Step 1: Change State
  stateSel.value = trans.state;
  stateSel.dispatchEvent('change');

  assert(mockWindow.getActiveState() === trans.state, `activeState should be ${trans.state}`);
  assert(mockWindow.getActivePlanId() === null, `activePlanId MUST be null on switching to ${trans.state}`);
  assert(insSel.disabled === true, `Insurer dropdown MUST be disabled after selecting ${trans.state}`);
  assert(planSel.disabled === true, `Plan dropdown MUST be disabled after selecting ${trans.state}`);

  // Step 2: Select Category
  catSel.value = trans.category;
  catSel.dispatchEvent('change');

  assert(mockWindow.getSelectedCategory() === trans.category, `selectedCategory should be ${trans.category}`);
  assert(insSel.disabled === false, `Insurer dropdown should be enabled for ${trans.state} ${trans.category}`);
  assert(planSel.disabled === true, `Plan dropdown should remain disabled`);

  // Step 3: Select Insurer
  insSel.value = trans.insurer;
  insSel.dispatchEvent('change');

  assert(mockWindow.getSelectedInsurerId() === trans.insurer, `selectedInsurerId should be ${trans.insurer}`);
  assert(planSel.disabled === false, `Plan dropdown should be enabled for ${trans.insurer}`);

  // Step 4: Select Plan
  planSel.value = trans.plan;
  planSel.dispatchEvent('change');

  assert(mockWindow.getActivePlanId() === trans.plan, `activePlanId should be set to ${trans.plan}`);
});

console.log(`\nTrue Cascading Dropdown Engine DOM Test Results: ${passed} / ${passed + failed} PASSED (${failed} FAILED)`);
if (failed > 0) process.exit(1);
