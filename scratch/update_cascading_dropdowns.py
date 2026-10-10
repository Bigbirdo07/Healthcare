import re

with open('dist/marketplace/marketplace.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace dropdown event handlers and update cascading logic
# Search for dropdown setup in init() or DOMContentLoaded

cascading_js = '''
  // --- AUTHORITATIVE CASCADING DROPDOWN ENGINE ---
  let selectedState = 'RI';
  let selectedCategory = 'MEDICARE_ADVANTAGE';
  let selectedInsurerId = 'bcbsri';
  let activePlanId = 'bcbsri_bluechip_core_2026';

  function formatCategoryLabel(cat) {
    if (cat === 'MEDICARE_ADVANTAGE' || cat === 'Medicare Advantage') return 'Medicare (Medicare Advantage / D-SNP)';
    if (cat === 'MEDICAID' || cat === 'Medicaid') return 'Medicaid (State & Managed Care)';
    if (cat === 'COMMERCIAL' || cat === 'Commercial') return 'Regular Commercial Insurance';
    if (cat === 'D_SNP') return 'Medicare D-SNP Dual Eligible';
    if (cat === 'INDIVIDUAL_MARKETPLACE') return 'Individual ACA Marketplace';
    if (cat === 'CHIP') return 'CHIP (Children’s Health Insurance)';
    return cat;
  }

  function getProductionPlans() {
    return PLANS.filter(p => 
      p.production_visibility !== false && 
      !p.is_test_fixture && 
      p.environment !== 'TEST' && 
      p.source_status !== 'HIDDEN'
    );
  }

  function onStateChange(newState) {
    selectedState = newState;
    selectedCategory = '';
    selectedInsurerId = '';
    activePlanId = null;

    updateCategoryDropdown();
    updateInsurerDropdown();
    updatePlanDropdown();
    updatePlanStatusBadge();
    renderGrid();
  }

  function onCategoryChange(newCategory) {
    selectedCategory = newCategory;
    selectedInsurerId = '';
    activePlanId = null;

    updateInsurerDropdown();
    updatePlanDropdown();
    updatePlanStatusBadge();
    renderGrid();
  }

  function onInsurerChange(newInsurerId) {
    selectedInsurerId = newInsurerId;
    activePlanId = null;

    updatePlanDropdown();
    updatePlanStatusBadge();
    renderGrid();
  }

  function onPlanChange(newPlanId) {
    activePlanId = newPlanId;
    if (activePlanId) {
      const planObj = PLANS.find(p => p.id === activePlanId);
      if (!planObj || (planObj.state !== selectedState && planObj.state !== 'All Areas')) {
        activePlanId = null;
      }
    }

    if (typeof revalidateProviderRequests === 'function') {
      revalidateProviderRequests(activePlanId);
    }

    updatePlanStatusBadge();
    renderGrid();
  }

  function updateCategoryDropdown() {
    const catSel = $('#planTypeSelect');
    if (!catSel) return;

    const statePlans = getProductionPlans().filter(p => p.state === selectedState || p.state === 'All Areas');
    const categories = [];
    statePlans.forEach(p => {
      const cat = p.insurance_category || p.plan_type;
      if (cat && !categories.includes(cat)) {
        categories.push(cat);
      }
    });

    catSel.innerHTML = `
      <option value="" disabled ${!selectedCategory ? 'selected' : ''}>Select insurance type</option>
      ${categories.map(cat => `
        <option value="${esc(cat)}" ${selectedCategory === cat ? 'selected' : ''}>${esc(formatCategoryLabel(cat))}</option>
      `).join('')}
    `;
    catSel.disabled = false;
  }

  function updateInsurerDropdown() {
    const insSel = $('#insurerSelect');
    if (!insSel) return;

    if (!selectedCategory) {
      insSel.innerHTML = `<option value="" disabled selected>Select insurer</option>`;
      insSel.disabled = true;
      return;
    }

    const matchingPlans = getProductionPlans().filter(p => 
      (p.state === selectedState || p.state === 'All Areas') && 
      (p.insurance_category === selectedCategory || p.plan_type === selectedCategory)
    );

    const insurersMap = {};
    matchingPlans.forEach(p => {
      const insId = p.insurer_id || 'unknown';
      const insName = p.insurer_name || p.insurer_id || 'Insurer';
      insurersMap[insId] = insName;
    });

    const insIds = Object.keys(insurersMap);
    insSel.innerHTML = `
      <option value="" disabled ${!selectedInsurerId ? 'selected' : ''}>Select insurer</option>
      ${insIds.map(id => `
        <option value="${esc(id)}" ${selectedInsurerId === id ? 'selected' : ''}>${esc(insurersMap[id])}</option>
      `).join('')}
    `;
    insSel.disabled = false;
  }

  function updatePlanDropdown() {
    const planSel = $('#planSelect');
    if (!planSel) return;

    if (!selectedCategory || !selectedInsurerId) {
      planSel.innerHTML = `<option value="" disabled selected>Select insurance plan</option>`;
      planSel.disabled = true;
      return;
    }

    const matchingPlans = getProductionPlans().filter(p => 
      (p.state === selectedState || p.state === 'All Areas') && 
      (p.insurance_category === selectedCategory || p.plan_type === selectedCategory) &&
      p.insurer_id === selectedInsurerId
    );

    planSel.innerHTML = `
      <option value="" disabled ${!activePlanId ? 'selected' : ''}>Select insurance plan</option>
      ${matchingPlans.map(p => `
        <option value="${esc(p.id)}" ${activePlanId === p.id ? 'selected' : ''}>${esc(p.official_plan_name)}</option>
      `).join('')}
    `;
    planSel.disabled = false;
  }

  function updatePlanStatusBadge() {
    const statusPill = $('#planStatusPill');
    if (!statusPill) return;

    if (activePlanId) {
      const planObj = PLANS.find(p => p.id === activePlanId);
      statusPill.style.display = 'inline-block';
      statusPill.textContent = `✓ ${selectedState} Active Plan`;
      statusPill.style.background = 'var(--terracotta)';
      statusPill.style.color = '#fff';
    } else {
      statusPill.style.display = 'none';
    }
  }
'''

print("Cascading JS block ready for injection.")
