import re
from pathlib import Path

print("Updating marketplace UI rendering to seamlessly integrate Products, Services, and Benefits via getMarketplaceForPlan...")

js_path = Path('dist/marketplace/marketplace.js')
code = js_path.read_text(encoding='utf-8')

OLD_RENDER_GRID = """function renderGrid() {
    const grid = $('#productGrid');
    const countLabel = $('#productCountLabel');
    if (!grid) return;

    const results = filterProducts();

    if (countLabel) {
      countLabel.innerHTML = `Showing <strong>${results.length}</strong> products for <strong>${esc(getPlanName(activePlanId))}</strong> (${esc(activeState)})`;
    }"""

NEW_RENDER_GRID = """function renderGrid() {
    const grid = $('#productGrid');
    const countLabel = $('#productCountLabel');
    if (!grid) return;

    const catalog = getMarketplaceForPlan(activePlanId);
    let results = filterProducts();

    // Map evaluateCoverageRule onto results
    let displayItems = results.map(p => {
      const rule = evaluateCoverageRule(p.id, activePlanId);
      return {
        type: 'PRODUCT',
        id: p.id,
        name: p.product_name,
        category: p.category,
        subcategory: p.subcategory,
        icon: p.icon,
        generic: p.generic_name,
        brand: p.brand_name,
        description: p.description,
        rule: rule,
        is_mapped: rule.rule_id && !rule.rule_id.startsWith('R-FALLBACK-') && rule.rule_id !== 'R-UNVERIFIED'
      };
    });

    // Add Services if matching category or all
    if (activeDepartment === 'all' || activeDepartment === 'dental' || activeDepartment === 'eyecare' || activeDepartment === 'ssbci' || activeDepartment === 'diagnostics') {
      const filteredServices = catalog.services.filter(s => activeDepartment === 'all' || s.category === activeDepartment);
      filteredServices.forEach(s => {
        displayItems.push({
          type: 'SERVICE',
          id: s.id || s.service_id,
          name: s.service_name,
          category: s.category || 'service',
          subcategory: 'Healthcare Service',
          icon: s.icon || '🩺',
          generic: 'Medical / Dental Service',
          brand: '',
          description: s.description,
          rule: {
            coverage_status: s.coverage_status,
            benefit_pathway: s.benefit_pathway,
            member_cost: s.member_cost,
            official_source_name: s.official_source_name,
            plain_english_explanation: s.description + ' Covered under your plan.'
          },
          is_mapped: s.is_mapped
        });
      });
    }

    // Add Benefits if matching category or all
    if (activeDepartment === 'all' || activeDepartment === 'ssbci' || activeDepartment === 'vitamins') {
      const filteredBenefits = catalog.benefits.filter(b => activeDepartment === 'all' || b.plan_id === activePlanId || b.is_mapped);
      filteredBenefits.forEach(b => {
        displayItems.push({
          type: 'BENEFIT',
          id: b.id || b.benefit_id,
          name: b.benefit_name,
          category: b.benefit_type ? b.benefit_type.toLowerCase() : 'benefit',
          subcategory: 'Supplemental Allowance',
          icon: b.icon || '💳',
          generic: 'Supplemental Plan Benefit',
          brand: '',
          description: b.description,
          rule: {
            coverage_status: b.coverage_status,
            benefit_pathway: b.benefit_pathway,
            member_cost: b.member_cost,
            official_source_name: b.official_source_name,
            plain_english_explanation: b.description
          },
          is_mapped: b.is_mapped
        });
      });
    }

    if (countLabel) {
      countLabel.innerHTML = `Showing <strong>${displayItems.length}</strong> items (Products, Services & Benefits) for <strong>${esc(getPlanName(activePlanId))}</strong> (${esc(activeState)})`;
    }"""

if OLD_RENDER_GRID in code:
    code = code.replace(OLD_RENDER_GRID, NEW_RENDER_GRID)
    js_path.write_text(code, encoding='utf-8')
    print("Successfully updated renderGrid in marketplace.js.")
else:
    print("OLD_RENDER_GRID snippet not found exactly. Code unchanged.")
