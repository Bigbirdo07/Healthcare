import re, json, os

print("Building Pazeratechnologies Insurance Marketplace Architecture...")

# --- 1. HTML BUILD ---
html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Insurance Benefit & OTC Marketplace · Benefit Card Navigator</title>
  <meta name="description" content="Plan-specific insurance marketplace connecting health plan OTC allowances, pharmacy benefits, DME medical equipment, and supplemental services to official plan sources.">
  <link rel="stylesheet" href="/marketplace/marketplace.css">
</head>
<body class="marketplace-page">
  <!-- Topbar Navigation -->
  <header class="topbar">
    <a href="/" class="brand">
      <span class="brandmark">B</span>
      <span class="brand-copy">
        <strong>Benefit Card Navigator</strong>
        <small>Pazeratechnologies Benefit Marketplace</small>
      </span>
    </a>
    <nav class="header-utility" aria-label="Main Navigation">
      <a href="/find-care/doctors/">Find a Doctor</a>
      <a href="/find-care/dentists/">Find a Dentist</a>
      <a href="/find-care/eye-doctors/">Find a Eye doctor</a>
      <a href="/marketplace/" class="active">Marketplace</a>
      <a href="/find-care/#sources" class="nav-sources">About the data &amp; sources</a>
    </nav>
  </header>

  <!-- Marketplace Hero Banner -->
  <section class="market-hero-banner">
    <div class="market-shell" style="padding:0">
      <div class="market-hero-inner">
        <div class="market-hero-copy">
          <span class="hero-badge">
            Pazeratechnologies Multi-Pathway Insurance Marketplace
          </span>
          <h1>What Can Your Insurance Pay For?</h1>
          <p>
            Select your health plan below to view plan-specific coverage determinations for OTC health items, prescribed pharmacy supplies, durable medical equipment (DMEPOS), and supplemental benefits (dental, rides, meals, fitness). Every verified coverage determination links directly to official plan sources.
          </p>
          <div class="hero-action-buttons">
            <button type="button" class="hero-form-btn" id="heroViewFormBtn">
              📄 View &amp; Print Order Sheet
            </button>
            <a href="#catalogAnchor" class="hero-form-btn" style="background:rgba(255,255,255,0.18);color:#fff;text-decoration:none">
              🔍 Search Marketplace
            </a>
          </div>
        </div>

        <div class="market-callout-card">
          <h3><span>💳</span> Plan-Specific Coverage Verification</h3>
          <p style="font-size:13px;line-height:1.5;margin:6px 0 10px;color:#e1eee9">
            Coverage rules depend on your exact health plan. Unverified coverage defaults to <strong style="color:var(--gold)">Needs Verification</strong> until backed by official plan documents.
          </p>
          <small style="color:#d5e5df;font-size:11px;display:block">
            ✓ RI Medicaid 2026 EOHHS Protocols · BCBSRI BlueCHiP 2026 · CarePartners MA · Highmark D-SNP
          </small>
        </div>
      </div>
    </div>
  </section>

  <!-- Plan Selection Bar -->
  <section class="plan-selector-strip">
    <div class="market-shell" style="padding:0">
      <div class="plan-selector-box">
        <label for="planSelectorSelect" class="plan-selector-label">
          <strong>🏥 Selected Health Insurance Plan:</strong>
        </label>
        <select id="planSelectorSelect" class="plan-selector-dropdown">
          <option value="bcbsri_bluechip_2026_core">Blue Cross & Blue Shield of RI — BlueCHiP for Medicare Core (2026)</option>
          <option value="ri_medicaid_eohhs_2026">Rhode Island Medicaid — EOHHS Managed Care Pharmacy Protocol (2026)</option>
          <option value="carepartners_ma_2026">CarePartners of Connecticut — Medicare Advantage Flex Card (2026)</option>
          <option value="highmark_dsnp_2026">Highmark Wholecare — Medicare D-SNP SSBCI Allowance (2026)</option>
          <option value="unselected_generic">Generic / Unselected Plan (Needs Verification Mode)</option>
        </select>
        <span class="plan-status-pill" id="planStatusPill">✓ Plan Verified</span>
      </div>
    </div>
  </section>

  <!-- Sticky Search Strip & Primary View Tabs (Shop Products vs Your Benefits) -->
  <div class="search-strip-wrap" id="catalogAnchor">
    <div class="market-shell" style="padding:0">
      
      <!-- Primary View Mode Tabs -->
      <div class="primary-view-tabs" role="tablist">
        <button type="button" class="view-tab active" id="tabShopProducts" data-view="products">
          🛒 SHOP PRODUCTS <span class="tab-count-badge" id="productTabCount">33 Categories</span>
        </button>
        <button type="button" class="view-tab" id="tabYourBenefits" data-view="services">
          🏥 YOUR BENEFITS &amp; SUPPORTS <span class="tab-count-badge" id="serviceTabCount">Dental, Rides, Meals, Gym, SSBCI</span>
        </button>
      </div>

      <div class="search-strip">
        <div class="market-search-box">
          <input
            type="search"
            id="marketSearchInput"
            class="market-search-input"
            placeholder="Search products (Vitamin D, knee brace, BP cuff, test strips) or benefits (gym, rides to doctor, dental)..."
            aria-label="Search catalog items and benefits"
          >
          <button type="button" class="search-icon-btn" aria-label="Submit search">🔍</button>
        </div>

        <button type="button" class="cart-summary-trigger" onclick="document.querySelector('.order-slip-panel')?.scrollIntoView({behavior:'smooth'})">
          <span>📞 Phone Slip</span>
          <span id="slipCountBadge" class="cart-badge-count">0</span>
        </button>
      </div>

      <!-- Quick Category Pills (Dynamically rendered by JS based on View Mode) -->
      <div class="category-pills-bar" id="categoryPillsBar" role="tablist" aria-label="Catalog categories">
        <!-- JS injects pills -->
      </div>
    </div>
  </div>

  <!-- Main Marketplace Workspace -->
  <main class="market-shell">
    <div class="market-layout">
      <!-- Left Filter Sidebar -->
      <aside class="market-sidebar" aria-label="Catalog filters">
        <div class="filter-group">
          <h4>Filter by Coverage Status</h4>
          <div class="filter-checkbox-list">
            <label class="filter-checkbox-label">
              <input type="radio" name="sideStatus" value="all" checked>
              <span>All Coverage Statuses</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="sideStatus" value="COVERED">
              <span style="color:#0d6b63;font-weight:700">✓ Covered</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="sideStatus" value="OTC_ELIGIBLE">
              <span style="color:#133e33;font-weight:700">💳 OTC Allowance Eligible</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="sideStatus" value="CONDITIONAL">
              <span style="color:#8a5d00;font-weight:700">⚠️ Conditional / Needs Order</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="sideStatus" value="NEEDS_VERIFICATION">
              <span style="color:#b25900;font-weight:700">❓ Needs Verification</span>
            </label>
          </div>
        </div>

        <div class="filter-group">
          <h4>Filter by Benefit Pathway</h4>
          <div class="filter-checkbox-list">
            <label class="filter-checkbox-label">
              <input type="radio" name="sidePathway" value="all" checked>
              <span>All Benefit Pathways</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="sidePathway" value="OTC_ALLOWANCE">
              <span style="color:#133e33;font-weight:700">💳 OTC Card Allowance</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="sidePathway" value="PHARMACY">
              <span style="color:#1e4b85;font-weight:700">💊 Pharmacy Prescribed (Rx)</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="sidePathway" value="DMEPOS">
              <span style="color:#5b2382;font-weight:700">🩺 Medical / DME Benefit</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="sidePathway" value="PREVENTIVE">
              <span style="color:#0d6b63;font-weight:700">🌸 100% ACA Preventive</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="sidePathway" value="SSBCI">
              <span style="color:#8a5d00;font-weight:700">🍎 SSBCI / Supplemental</span>
            </label>
          </div>
        </div>

        <div class="filter-group">
          <h4>Filter by Category</h4>
          <div class="filter-checkbox-list" id="sidebarCategoryList" style="max-height:360px;overflow-y:auto;padding-right:4px">
            <!-- JS injects category choices -->
          </div>
        </div>

        <div class="filter-group">
          <h4>Plan Sourcing Standard</h4>
          <div style="font-size:12px;line-height:1.55;color:var(--text-muted);display:grid;gap:8px">
            <div>
              <strong style="color:var(--green-dark)">✓ Source-Backed Rules:</strong>
              Every verified status links to official Evidence of Coverage, Formularies, or State Medicaid Protocols.
            </div>
            <div>
              <strong style="color:var(--green-dark)">✓ Plan Specificity:</strong>
              Changing your selected plan dynamically recalculates costs, requirements, and suppliers.
            </div>
          </div>
        </div>
      </aside>

      <!-- Center Product/Service Grid -->
      <section class="market-catalog-area">
        <div class="product-grid-header">
          <div id="productCountLabel" class="product-count-label">
            Loading marketplace catalog...
          </div>
        </div>

        <div id="productGrid" class="product-grid" aria-live="polite">
          <!-- Populated dynamically by marketplace.js -->
        </div>
      </section>

      <!-- Right Sidebar: Phone Order Call Slip -->
      <aside class="order-slip-panel" aria-label="Phone order call slip">
        <div style="display:flex;align-items:center;justify-content:space-between">
          <h3 style="margin:0">Phone Order Slip</h3>
        </div>
        <p style="font-size:12px;color:#cbe0d9;margin:4px 0 14px">
          Read these catalog item numbers when you call your health plan:
        </p>

        <div id="callSlipContainer">
          <!-- Populated dynamically by marketplace.js -->
        </div>
      </aside>
    </div>
  </main>

  <!-- Marketplace Footer -->
  <footer style="background:#fff;border-top:1px solid var(--line);padding:32px 0;margin-top:40px;color:var(--text-muted);font-size:12px">
    <div class="market-shell" style="padding:0">
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px">
        <div>
          <strong style="color:var(--green-dark)">Benefit Card Navigator · Pazeratechnologies Marketplace</strong>
          <p style="margin:4px 0 0">
            Coverage rules and benefit estimates are plan-specific and source-backed. Official plan documentation governs final eligibility determinations.
          </p>
        </div>
        <div style="display:flex;gap:18px">
          <a href="/find-care/doctors/" style="color:var(--terracotta);text-decoration:none">Find a Doctor</a>
          <a href="/find-care/dentists/" style="color:var(--terracotta);text-decoration:none">Find a Dentist</a>
          <a href="/find-care/eye-doctors/" style="color:var(--terracotta);text-decoration:none">Find an Eye Doctor</a>
          <a href="/find-care/#sources" style="color:var(--green-dark);text-decoration:underline">Sources</a>
        </div>
      </div>
    </div>
  </footer>

  <!-- Marketplace Logic Script -->
  <script src="/marketplace/marketplace.js"></script>
</body>
</html>
"""

with open('dist/marketplace/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("HTML template written successfully.")
