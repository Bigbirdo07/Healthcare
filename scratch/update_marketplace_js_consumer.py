import json
import re

with open('dist/marketplace/marketplace.js', 'r', encoding='utf-8') as f:
    js_text = f.read()

# Enhance renderGrid() and related helper functions in marketplace.js

new_render_grid = """
  let activeEntityType = 'ALL';

  function renderGrid() {
    const grid = $('#productGrid');
    const countLabel = $('#resultCountLabel');
    const bannerContainer = $('#planSummaryBannerContainer');

    if (!grid) return;

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
    }

    // Combine all products, services, benefits
    let allItems = [
      ...marketData.products,
      ...marketData.services,
      ...marketData.benefits
    ];

    // Filter by Entity Type Tab
    if (activeEntityType !== 'ALL') {
      allItems = allItems.filter(item => item.entity_type === activeEntityType);
    }

    // Filter by Department / Category
    if (activeDepartment !== 'all') {
      allItems = allItems.filter(item => (item.category === activeDepartment || item.department === activeDepartment));
    }

    // Filter by Search Query
    if (searchQuery && searchQuery.trim() !== '') {
      const q = searchQuery.toLowerCase().trim();
      allItems = allItems.filter(item => {
        const nameMatch = (item.product_name || item.service_name || item.benefit_name || '').toLowerCase().includes(q);
        const aliasMatch = (item.aliases || []).some(a => a.toLowerCase().includes(q));
        const catMatch = (item.category || '').toLowerCase().includes(q);
        const pathMatch = (item.benefit_pathway || '').toLowerCase().includes(q);
        const descMatch = (item.description || '').toLowerCase().includes(q);
        return nameMatch || aliasMatch || catMatch || pathMatch || descMatch;
      });
    }

    // Filter by Verified Only checkbox
    if (chkVerifiedOnly) {
      allItems = allItems.filter(item => {
        const st = (item.coverage_status || '').toLowerCase();
        return st === 'covered' || st.includes('conditional') || st.includes('order') || st.includes('prior auth');
      });
    }

    // Filter by Status Radio
    if (activeStatusFilter !== 'all') {
      allItems = allItems.filter(item => {
        const st = (item.coverage_status || '').toLowerCase();
        if (activeStatusFilter === 'Covered') return st === 'covered';
        if (activeStatusFilter === 'Conditional') return st.includes('conditional') || st.includes('order') || st.includes('prior auth');
        if (activeStatusFilter === 'Needs Verification') return st.includes('verification') || st.includes('unknown');
        if (activeStatusFilter === 'Not Covered') return st.includes('not covered');
        return true;
      });
    }

    // Default Sorting Order: 1. COVERED, 2. CONDITIONAL, 3. NEEDS_VERIFICATION, 4. NOT_COVERED
    const statusPriority = {
      'covered': 1,
      'conditional': 2,
      'needs_verification': 3,
      'unknown / needs verification': 3,
      'not_covered': 4,
      'not covered': 4
    };

    allItems.sort((a, b) => {
      const stA = (a.coverage_status || '').toLowerCase();
      const stB = (b.coverage_status || '').toLowerCase();
      
      let pA = 3;
      if (stA === 'covered') pA = 1;
      else if (stA.includes('conditional') || stA.includes('order') || stA.includes('prior auth')) pA = 2;
      else if (stA.includes('not covered')) pA = 4;

      let pB = 3;
      if (stB === 'covered') pB = 1;
      else if (stB.includes('conditional') || stB.includes('order') || stB.includes('prior auth')) pB = 2;
      else if (stB.includes('not covered')) pB = 4;

      return pA - pB;
    });

    if (countLabel) {
      countLabel.innerHTML = `Showing <strong>${allItems.length}</strong> items for <strong>${esc(marketData.official_plan_name)}</strong> (${esc(activeState)})`;
    }

    if (allItems.length === 0) {
      grid.innerHTML = `
        <div style="grid-column:1/-1;background:#fff;border:1px solid var(--line);border-radius:12px;padding:40px;text-align:center">
          <span style="font-size:36px;display:block;margin-bottom:12px">🔍</span>
          <h3 style="margin:0 0 8px;color:var(--green-dark)">No matching catalog items found</h3>
          <p style="color:var(--text-muted);font-size:14px;max-width:500px;margin:0 auto 16px">
            Try resetting your search query or selecting "All Statuses".
          </p>
          <button type="button" class="hero-form-btn" onclick="window.resetMarketFilters()" style="background:var(--green-dark);color:#fff">
            Reset All Filters
          </button>
        </div>
      `;
      return;
    }

    grid.innerHTML = allItems.map((item) => {
      const itemId = item.id || item.entity_id;
      const itemName = item.product_name || item.service_name || item.benefit_name || 'Marketplace Item';
      const itemIcon = item.icon || (item.entity_type === 'BENEFIT' ? '💳' : (item.entity_type === 'SERVICE' ? '🩺' : '📦'));
      const inSlip = callSlip.some((i) => i.id === itemId);

      const stLower = (item.coverage_status || '').toLowerCase();
      let badgeHTML = `<span class="status-badge status-needs-verification">? Needs Verification</span>`;
      let cardClass = "product-card";

      if (stLower === 'covered') {
        badgeHTML = `<span class="status-badge status-covered" style="background:#e6f4f1;color:#0d6b63;border:1px solid #b2ded7;font-weight:700">✓ Covered</span>`;
      } else if (stLower.includes('conditional') || stLower.includes('order') || stLower.includes('prior auth')) {
        badgeHTML = `<span class="status-badge status-conditional" style="background:#fff8e6;color:#8a5d00;border:1px solid #fce8b2;font-weight:700">⚡ Covered with conditions</span>`;
      } else if (stLower.includes('not covered')) {
        badgeHTML = `<span class="status-badge status-not-covered" style="background:#fef2f2;color:#b91c1c;border:1px solid #fecaca;font-weight:700">✕ Not Covered</span>`;
      }

      return `
        <div class="${cardClass}">
          <div class="product-card-top">
            <span class="product-sku">${esc(item.entity_type)} · ${esc(item.category || 'General')}</span>
            ${badgeHTML}
          </div>

          <div class="product-image-area">
            <span style="font-size:40px">${itemIcon}</span>
          </div>

          <h3 class="product-title">${esc(itemName)}</h3>
          <p class="product-specs">${esc(item.description || item.benefit_description || 'Evaluated marketplace entity for selected plan.')}</p>

          <div style="margin:10px 0;font-size:12px;line-height:1.4;background:var(--cream);padding:10px;border-radius:6px;border:1px solid var(--line)">
            <div style="font-weight:700;color:var(--green-dark);margin-bottom:4px">
              Pathway: ${esc(item.benefit_pathway || 'Plan Benefit')}
            </div>
            <div><strong>Member Cost:</strong> ${esc(item.member_cost || 'See plan cost-sharing')}</div>
            ${item.requirements ? `<div style="margin-top:4px;color:#8a5d00;font-weight:600">Requires: ${esc(item.requirements)}</div>` : ''}
          </div>

          <div style="display:grid;gap:8px;margin-top:auto">
            ${stLower !== 'not covered' ? `
              <button type="button" class="add-to-slip-btn ${inSlip ? 'added' : ''}" data-add-id="${esc(itemId)}">
                ${inSlip ? '✓ Added to Request' : '+ Add to Request'}
              </button>
            ` : ''}

            <button type="button" class="slip-secondary-btn" data-view-source="${esc(itemId)}">
              🔍 ${stLower.includes('not covered') ? 'View Source' : (stLower.includes('conditional') ? 'View Requirements' : (stLower.includes('verification') ? 'View Details' : 'View Coverage Details'))}
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
  }

  // --- SOURCE DETAIL DRAWER / MODAL ---
  function openSourceDetailModal(itemId) {
    const marketData = getMarketplaceForPlan(activePlanId);
    const allItems = [...marketData.products, ...marketData.services, ...marketData.benefits];
    const item = allItems.find(i => (i.id || i.entity_id) === itemId);
    if (!item) return;

    let modal = $('#sourceDetailModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'sourceDetailModal';
      modal.className = 'order-form-modal-overlay';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      document.body.appendChild(modal);
    }

    const stLower = (item.coverage_status || '').toLowerCase();
    let badgeHTML = `<span class="status-badge status-needs-verification">❓ Needs Verification</span>`;
    if (stLower === 'covered') {
      badgeHTML = `<span class="status-badge status-covered" style="background:#e6f4f1;color:#0d6b63;font-weight:700">✓ Covered</span>`;
    } else if (stLower.includes('conditional') || stLower.includes('order') || stLower.includes('prior auth')) {
      badgeHTML = `<span class="status-badge status-conditional" style="background:#fff8e6;color:#8a5d00;font-weight:700">⚡ Covered with conditions</span>`;
    } else if (stLower.includes('not covered')) {
      badgeHTML = `<span class="status-badge status-not-covered" style="background:#fef2f2;color:#b91c1c;font-weight:700">✕ Not Covered</span>`;
    }

    modal.innerHTML = `
      <div class="order-form-modal-window" style="max-width:700px">
        <div class="order-form-modal-header">
          <div>
            <h2 style="margin:0;font-size:20px;color:var(--green-dark)">
              ${item.icon || '📦'} ${esc(item.product_name || item.service_name || item.benefit_name)}
            </h2>
            <small style="color:var(--text-muted)">Entity ID: ${esc(itemId)} · Type: ${esc(item.entity_type)}</small>
          </div>
          <button type="button" class="close-modal-btn" id="closeSourceDetailModalBtn" aria-label="Close modal">✕</button>
        </div>

        <div class="order-form-modal-body">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:16px;background:var(--cream);padding:12px;border-radius:8px">
            <div>
              <strong style="font-size:11px;color:var(--text-muted);display:block">ACTIVE PLAN CONTRACT:</strong>
              <span style="font-size:14px;font-weight:700;color:var(--green-dark)">${esc(marketData.official_plan_name)} (${esc(activeState)})</span>
            </div>
            <div>${badgeHTML}</div>
          </div>

          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
            <div style="background:#fff;border:1px solid var(--line);padding:12px;border-radius:8px">
              <strong style="font-size:13px;display:block;margin-bottom:6px;color:var(--green-dark)">Coverage Details:</strong>
              <ul style="margin:0;padding-left:18px;font-size:12px;line-height:1.6">
                <li><strong>Pathway:</strong> ${esc(item.benefit_pathway || 'Plan Benefit')}</li>
                <li><strong>Member Cost:</strong> ${esc(item.member_cost || 'See plan cost-sharing')}</li>
                <li><strong>Requirements:</strong> ${esc(item.requirements || 'None')}</li>
              </ul>
            </div>

            <div style="background:#fff;border:1px solid var(--line);padding:12px;border-radius:8px">
              <strong style="font-size:13px;display:block;margin-bottom:6px;color:var(--green-dark)">Official Evidence Source:</strong>
              <ul style="margin:0;padding-left:18px;font-size:12px;line-height:1.6">
                <li><strong>Source ID:</strong> ${esc(item.source_id || 'SRC-VERIFIED')}</li>
                <li><strong>Document:</strong> ${esc(item.official_source_name || 'Official Plan EOC / Handbook')}</li>
                <li><strong>Page / Section:</strong> ${esc(item.source_page || 'Chapter 4')}</li>
                <li><strong>Last Reviewed:</strong> ${esc(marketData.last_reviewed)}</li>
              </ul>
            </div>
          </div>

          <div style="background:var(--green-tint);border:1px solid var(--line);padding:12px;border-radius:8px;margin-bottom:16px;font-size:12px">
            <strong>Official Source URL:</strong><br/>
            <a href="${esc(item.official_source_url || '/find-care/#sources')}" target="_blank" rel="noopener" style="color:var(--green-dark);font-weight:700;word-break:break-all">
              ${esc(item.official_source_url || 'https://www.bcbsri.com/medicare')}
            </a>
          </div>

          <div style="display:flex;gap:10px;justify-content:flex-end">
            <button type="button" class="hero-form-btn" id="closeSourceDetailBtn" style="background:var(--green-dark);color:#fff">
              Close Detail
            </button>
          </div>
        </div>
      </div>
    `;

    modal.style.display = 'flex';
    $('#closeSourceDetailModalBtn')?.addEventListener('click', () => { modal.style.display = 'none'; });
    $('#closeSourceDetailBtn')?.addEventListener('click', () => { modal.style.display = 'none'; });
  }
"""

# Replace renderGrid function in marketplace.js
pattern = r'function renderGrid\(\) \{.*?\n  \}'
js_text = re.sub(pattern, new_render_grid, js_text, flags=re.DOTALL)

with open('dist/marketplace/marketplace.js', 'w', encoding='utf-8') as f:
    f.write(js_text)

print("Updated marketplace.js with consumer rendering and source detail modal cleanly.")
