with open('dist/marketplace/marketplace.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Find the end of window.getMarketplaceForPlan = getMarketplaceForPlan;
anchor = 'window.getMarketplaceForPlan = getMarketplaceForPlan;\n'
idx = text.find(anchor)
if idx != -1:
    text = text[:idx + len(anchor)]

clean_cascading_js = '''
  // --- AUTHORITATIVE CASCADING DROPDOWN ENGINE ---
  var selectedCategory = 'MEDICARE_ADVANTAGE';
  var selectedInsurerId = 'bcbsri';

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
    activeState = newState;
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
      if (!planObj || (planObj.state !== activeState && planObj.state !== 'All Areas')) {
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

    const statePlans = getProductionPlans().filter(p => p.state === activeState || p.state === 'All Areas');
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
      (p.state === activeState || p.state === 'All Areas') && 
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
      (p.state === activeState || p.state === 'All Areas') && 
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
      statusPill.textContent = `✓ ${activeState} Active Plan`;
      statusPill.style.background = 'var(--terracotta)';
      statusPill.style.color = '#fff';
    } else {
      statusPill.style.display = 'none';
    }
  }

  function init() {
    renderDepartmentPills();

    const stateSelect = $('#stateSelect');
    const planTypeSelect = $('#planTypeSelect');
    const insurerSelect = $('#insurerSelect');
    const planSelect = $('#planSelect');

    if (stateSelect) stateSelect.value = activeState;
    updateCategoryDropdown();
    updateInsurerDropdown();
    updatePlanDropdown();
    updatePlanStatusBadge();

    if (stateSelect) {
      stateSelect.addEventListener('change', (e) => onStateChange(e.target.value));
    }

    if (planTypeSelect) {
      planTypeSelect.addEventListener('change', (e) => onCategoryChange(e.target.value));
    }

    if (insurerSelect) {
      insurerSelect.addEventListener('change', (e) => onInsurerChange(e.target.value));
    }

    if (planSelect) {
      planSelect.addEventListener('change', (e) => onPlanChange(e.target.value));
    }

    const searchInput = $('#marketSearchInput');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value;
        renderGrid();
      });
    }

    $('#chkVerifiedOnly')?.addEventListener('change', (e) => { chkVerifiedOnly = e.target.checked; renderGrid(); });
    $('#chkZeroCost')?.addEventListener('change', (e) => { chkZeroCostOnly = e.target.checked; renderGrid(); });
    $('#chkOtcOnly')?.addEventListener('change', (e) => { chkOtcOnly = e.target.checked; renderGrid(); });
    $('#chkRxOnly')?.addEventListener('change', (e) => { chkRxOnly = e.target.checked; renderGrid(); });
    $('#chkOrderOnly')?.addEventListener('change', (e) => { chkOrderOnly = e.target.checked; renderGrid(); });

    $$('input[name="sideStatus"]').forEach((radio) => {
      radio.addEventListener('change', () => {
        activeStatusFilter = radio.value;
        renderGrid();
      });
    });

    $$('input[name="sidePathway"]').forEach((radio) => {
      radio.addEventListener('change', () => {
        activePathwayFilter = radio.value;
        renderGrid();
      });
    });

    $('#heroViewFormBtn')?.addEventListener('click', openPrintableOrderForm);

    renderGrid();
    renderCallSlip();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
'''

text += clean_cascading_js

with open('dist/marketplace/marketplace.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("marketplace.js cleaned up cleanly.")
