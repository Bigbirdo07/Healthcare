import re

with open('dist/marketplace/marketplace.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update renderGrid to handle activePlanId === null cleanly
grid_old = '''    // Get marketplace data contract for active plan
    const marketData = getMarketplaceForPlan(activePlanId);
    const summary = marketData.summary;

    // Render Selected Plan Summary Banner
    if (bannerContainer) {
      bannerContainer.innerHTML = `
        <div style="background:linear-gradient(135deg, #133e33 0%, #1e4b85 100%);color:#fff;padding:16px 20px;border-radius:12px;margin-bottom:20px;box-shadow:0 4px 12px rgba(0,0,0,0.08);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
          <div>
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">
              <span style="font-size:20px">🛡️</span>
              <h2 style="margin:0;font-size:18px;font-weight:700;color:#fff">${esc(marketData.official_plan_name)} (${esc(activeState)})</h2>
              <span style="background:rgba(255,255,255,0.2);color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700">Catalog reviewed: 100%</span>
            </div>
            <div style="font-size:12px;color:#d0e6df">Last reviewed: ${esc(marketData.last_reviewed)} · Active Plan Marketplace Contract</div>
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            <span style="background:#0d6b63;color:#fff;padding:6px 12px;border-radius:20px;font-size:12px;font-weight:700">✓ ${summary.covered_count} Covered</span>
            <span style="background:#8a5d00;color:#fff;padding:6px 12px;border-radius:20px;font-size:12px;font-weight:700">⚡ ${summary.conditional_count} Conditional</span>
            <span style="background:#b91c1c;color:#fff;padding:6px 12px;border-radius:20px;font-size:12px;font-weight:700">✕ ${summary.not_covered_count} Not Covered</span>
            <span style="background:#2b5797;color:#fff;padding:6px 12px;border-radius:20px;font-size:12px;font-weight:700">❓ ${summary.needs_verification_count} Need Verification</span>
          </div>
        </div>
      `;
    }'''

grid_new = '''    // Cross-state safeguard
    if (activePlanId) {
      const planObj = PLANS.find(p => p.id === activePlanId);
      if (!planObj || (planObj.state !== activeState && planObj.state !== 'All Areas')) {
        activePlanId = null;
      }
    }

    // Handle Unselected Plan State (activePlanId === null)
    if (!activePlanId) {
      if (bannerContainer) bannerContainer.innerHTML = '';
      if (countLabel) {
        countLabel.innerHTML = `<strong>Select your insurance card to see your benefits.</strong>`;
      }

      let genericItems = [...PRODUCTS, ...SERVICES, ...BENEFITS].map(item => ({
        ...item,
        entity_type: item.product_name ? 'PRODUCT' : (item.service_name ? 'SERVICE' : 'BENEFIT'),
        entity_id: item.id || item.product_id || item.service_id || item.benefit_id,
        coverage_status: 'Unknown / needs verification',
        benefit_pathway: item.benefit_pathway || 'Marketplace Item',
        member_cost: 'Select plan to calculate cost',
        requirements: 'Plan verification required'
      }));

      if (activeEntityType !== 'ALL') {
        genericItems = genericItems.filter(item => item.entity_type === activeEntityType);
      }

      if (searchQuery && searchQuery.trim() !== '') {
        const q = searchQuery.toLowerCase().trim();
        genericItems = genericItems.filter(item => {
          const nameMatch = (item.product_name || item.service_name || item.benefit_name || '').toLowerCase().includes(q);
          const catMatch = (item.category || '').toLowerCase().includes(q);
          return nameMatch || catMatch;
        });
      }

      grid.innerHTML = `
        <div style="grid-column:1/-1;background:#fff;border:1px solid var(--line);border-radius:12px;padding:32px;text-align:center;margin-bottom:12px;box-shadow:0 2px 8px rgba(0,0,0,0.04)">
          <span style="font-size:36px;display:block;margin-bottom:8px">🎴</span>
          <h3 style="margin:0 0 6px;color:var(--green-dark)">Select your insurance card to see your benefits.</h3>
          <p style="color:var(--text-muted);font-size:14px;max-width:550px;margin:0 auto">
            Please select your <strong>Insurance Category</strong>, <strong>Insurer</strong>, and <strong>Exact Insurance Card</strong> above to calculate your plan-specific coverage.
          </p>
        </div>
      ` + genericItems.map(item => {
        const itemId = item.id || item.entity_id;
        const itemName = item.product_name || item.service_name || item.benefit_name || 'Marketplace Item';
        const itemIcon = item.icon || (item.entity_type === 'BENEFIT' ? '💳' : (item.entity_type === 'SERVICE' ? '🩺' : '📦'));
        const inSlip = callSlip.some((i) => i.id === itemId);

        return `
          <div class="product-card">
            <div class="product-card-top">
              <span class="product-sku">${esc(item.entity_type)} · ${esc(item.category || 'General')}</span>
              <span class="status-badge status-needs-verification">? Needs Verification</span>
            </div>
            <div class="product-image-area">
              <span style="font-size:40px">${itemIcon}</span>
            </div>
            <h3 class="product-title">${esc(itemName)}</h3>
            <p class="product-specs">${esc(item.description || 'Select your insurance card to see plan-specific coverage.')}</p>
            <div style="margin:10px 0;font-size:12px;line-height:1.4;background:var(--cream);padding:10px;border-radius:6px;border:1px solid var(--line)">
              <div style="font-weight:700;color:var(--green-dark);margin-bottom:4px">
                Pathway: ${esc(item.benefit_pathway || 'Plan Benefit')}
              </div>
              <div><strong>Member Cost:</strong> Select plan</div>
            </div>
            <div style="display:grid;gap:8px;margin-top:auto">
              <button type="button" class="add-to-slip-btn ${inSlip ? 'added' : ''}" data-add-id="${esc(itemId)}">
                ${inSlip ? '✓ Added to Request' : '+ Add to Request'}
              </button>
              <button type="button" class="slip-secondary-btn" data-view-source="${esc(itemId)}">
                🔍 View Details
              </button>
            </div>
          </div>
        `;
      }).join('');

      $$('[data-add-id]').forEach((btn) => {
        btn.addEventListener('click', () => addToCallSlip(btn.dataset.addId));
      });
      $$('[data-view-source]').forEach((btn) => {
        btn.addEventListener('click', () => openSourceDetailModal(btn.dataset.viewSource));
      });

      return;
    }

    // Get marketplace data contract for active plan
    const marketData = getMarketplaceForPlan(activePlanId);
    const summary = marketData.summary;

    // Render Selected Plan Summary Banner
    if (bannerContainer) {
      bannerContainer.innerHTML = `
        <div style="background:linear-gradient(135deg, #133e33 0%, #1e4b85 100%);color:#fff;padding:16px 20px;border-radius:12px;margin-bottom:20px;box-shadow:0 4px 12px rgba(0,0,0,0.08);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
          <div>
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">
              <span style="font-size:20px">🛡️</span>
              <h2 style="margin:0;font-size:18px;font-weight:700;color:#fff">${esc(marketData.official_plan_name)} (${esc(activeState)})</h2>
              <span style="background:rgba(255,255,255,0.2);color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700">Catalog reviewed: 100%</span>
            </div>
            <div style="font-size:12px;color:#d0e6df">Last reviewed: ${esc(marketData.last_reviewed)} · Active Plan Marketplace Contract</div>
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            <span style="background:#0d6b63;color:#fff;padding:6px 12px;border-radius:20px;font-size:12px;font-weight:700">✓ ${summary.covered_count} Covered</span>
            <span style="background:#8a5d00;color:#fff;padding:6px 12px;border-radius:20px;font-size:12px;font-weight:700">⚡ ${summary.conditional_count} Conditional</span>
            <span style="background:#b91c1c;color:#fff;padding:6px 12px;border-radius:20px;font-size:12px;font-weight:700">✕ ${summary.not_covered_count} Not Covered</span>
            <span style="background:#2b5797;color:#fff;padding:6px 12px;border-radius:20px;font-size:12px;font-weight:700">❓ ${summary.needs_verification_count} Need Verification</span>
          </div>
        </div>
      `;
    }'''

if grid_old in text:
  text = text.replace(grid_old, grid_new)

# Replace cascading JS block cleanly
init_start = text.find('function init() {')
if init_start != -1:
  text = text[:init_start]

cascading_js = '''  // --- AUTHORITATIVE CASCADING DROPDOWN ENGINE ---
  let selectedCategory = 'MEDICARE_ADVANTAGE';
  let selectedInsurerId = 'bcbsri';

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

text += "\n" + cascading_js

with open('dist/marketplace/marketplace.js', 'w', encoding='utf-8') as f:
  f.write(text)

print("Clean cascading JS applied successfully!")
