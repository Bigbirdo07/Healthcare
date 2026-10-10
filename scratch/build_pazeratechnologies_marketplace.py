import re, json, os

print("Building Pazeratechnologies Production Insurance Marketplace Architecture...")

# --- 1. HTML INDEX TEMPLATE ---
html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pazeratechnologies Health Benefit Marketplace · Benefit Card Navigator</title>
  <meta name="description" content="Searchable, plan-specific healthcare benefits marketplace. Connect your health insurance card, plan, and state to official coverage sources across 33 departments.">
  <link rel="stylesheet" href="/marketplace/marketplace.css">
</head>
<body class="marketplace-page">
  <!-- Topbar Navigation -->
  <header class="topbar">
    <a href="/" class="brand">
      <span class="brandmark">B</span>
      <span class="brand-copy">
        <strong>Benefit Card Navigator</strong>
        <small>Pazeratechnologies Insurance Marketplace</small>
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
            Rhode Island &amp; New England Insurance Coverage Catalog
          </span>
          <h1>Amazon for Things Your Health Plan May Pay For</h1>
          <p>
            Select your exact health plan and state to search over 33 health departments. Discover whether products or services are covered under your OTC allowance, pharmacy benefit, or medical/DME benefit. Every verified coverage determination links directly to official plan documents.
          </p>
          <div class="hero-action-buttons">
            <button type="button" class="hero-form-btn" id="heroViewFormBtn">
              📄 View &amp; Print Order Sheet
            </button>
            <a href="#catalogAnchor" class="hero-form-btn" style="background:rgba(255,255,255,0.18);color:#fff;text-decoration:none">
              🔍 Search Marketplace Catalog
            </a>
          </div>
        </div>

        <div class="market-callout-card">
          <h3><span>💳</span> Plan-Specific Coverage Verification</h3>
          <p style="font-size:13px;line-height:1.5;margin:6px 0 10px;color:#e1eee9">
            Coverage rules depend on your exact health plan. Unverified coverage displays <strong style="color:var(--gold)">Unknown / needs verification</strong> until confirmed by official plan sources.
          </p>
          <small style="color:#d5e5df;font-size:11px;display:block">
            ✓ Rhode Island First (BCBSRI, Neighborhood Health, RI Medicaid, UHC, Tufts) · Scalable to MA, CT, NH, VT, ME
          </small>
        </div>
      </div>
    </div>
  </section>

  <!-- Multi-Filter Plan & Geography Control Bar -->
  <section class="plan-selector-strip">
    <div class="market-shell" style="padding:0">
      <div class="plan-selector-grid">
        <div class="filter-select-group">
          <label for="insurerSelect"><strong>Insurer / Card:</strong></label>
          <select id="insurerSelect" class="plan-dropdown">
            <option value="bcbsri">Blue Cross &amp; Blue Shield of Rhode Island</option>
            <option value="neighborhood">Neighborhood Health Plan of Rhode Island</option>
            <option value="ri_medicaid">Rhode Island Medicaid (EOHHS)</option>
            <option value="uhc_ri">UnitedHealthcare (Rhode Island)</option>
            <option value="tufts_p32">Tufts / Point32Health</option>
            <option value="medicare">Original Medicare (CMS)</option>
            <option value="unselected">Generic / Unselected Insurer</option>
          </select>
        </div>

        <div class="filter-select-group">
          <label for="planSelect"><strong>Exact Plan:</strong></label>
          <select id="planSelect" class="plan-dropdown">
            <option value="bcbsri_bluechip_core_2026">BlueCHiP for Medicare Core (2026)</option>
            <option value="neighborhood_integra_2026">Neighborhood INTEGRIA D-SNP (2026)</option>
            <option value="ri_medicaid_managed_2026">RI Medicaid Managed Care Protocols (2026)</option>
            <option value="uhc_medicare_dual_2026">UHC Dual Complete RI (2026)</option>
            <option value="generic_unselected_plan">Unselected Plan (Needs Verification)</option>
          </select>
        </div>

        <div class="filter-select-group">
          <label for="stateSelect"><strong>State:</strong></label>
          <select id="stateSelect" class="plan-dropdown" style="min-width:90px">
            <option value="RI" selected>RI (Rhode Island)</option>
            <option value="MA">MA (Massachusetts)</option>
            <option value="CT">CT (Connecticut)</option>
            <option value="NH">NH (New Hampshire)</option>
            <option value="VT">VT (Vermont)</option>
            <option value="ME">ME (Maine)</option>
          </select>
        </div>

        <div class="filter-select-group">
          <label for="planTypeSelect"><strong>Plan Type:</strong></label>
          <select id="planTypeSelect" class="plan-dropdown" style="min-width:140px">
            <option value="all">All Plan Types</option>
            <option value="Medicare Advantage" selected>Medicare Advantage</option>
            <option value="Medicaid">Medicaid</option>
            <option value="Medicare">Medicare</option>
            <option value="Commercial">Commercial</option>
          </select>
        </div>

        <div class="plan-status-indicator" id="planStatusIndicator">
          <span class="plan-status-pill" id="planStatusPill">✓ Plan Active</span>
        </div>
      </div>
    </div>
  </section>

  <!-- Search Strip & Category Bar -->
  <div class="search-strip-wrap" id="catalogAnchor">
    <div class="market-shell" style="padding:0">
      
      <div class="search-strip">
        <div class="market-search-box">
          <input
            type="search"
            id="marketSearchInput"
            class="market-search-input"
            placeholder="Search catalog (e.g. 'vitamin d', 'Tylenol', 'knee brace', 'BP monitor', 'sugar meter', 'toothpaste', 'walker')..."
            aria-label="Search marketplace products"
          >
          <button type="button" class="search-icon-btn" aria-label="Submit search">🔍</button>
        </div>

        <button type="button" class="cart-summary-trigger" onclick="document.querySelector('.order-slip-panel')?.scrollIntoView({behavior:'smooth'})">
          <span>📞 Phone Slip</span>
          <span id="slipCountBadge" class="cart-badge-count">0</span>
        </button>
      </div>

      <!-- Quick Department Category Pills (All 33 Departments) -->
      <div class="category-pills-bar" id="categoryPillsBar" role="tablist" aria-label="Product departments">
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
              <input type="radio" name="sideStatus" value="Covered">
              <span style="color:#0d6b63;font-weight:700">✓ Covered</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="sideStatus" value="Conditional">
              <span style="color:#8a5d00;font-weight:700">⚠️ Conditional</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="sideStatus" value="Unknown / needs verification">
              <span style="color:#b25900;font-weight:700">❓ Unknown / Needs Verification</span>
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
              <input type="radio" name="sidePathway" value="OTC allowance">
              <span style="color:#133e33;font-weight:700">💳 OTC Allowance</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="sidePathway" value="Prescription/pharmacy benefit">
              <span style="color:#1e4b85;font-weight:700">💊 Prescription / Pharmacy</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="sidePathway" value="Durable Medical Equipment (DME)">
              <span style="color:#5b2382;font-weight:700">🩺 Medical / DME Benefit</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="sidePathway" value="Preventive-care benefit">
              <span style="color:#0d6b63;font-weight:700">🌸 Preventive Care</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="sidePathway" value="Chronic-condition supplemental benefit">
              <span style="color:#8a5d00;font-weight:700">🍎 Chronic / SSBCI</span>
            </label>
          </div>
        </div>

        <div class="filter-group">
          <h4>Requirement Filters</h4>
          <div class="filter-checkbox-list">
            <label class="filter-checkbox-label">
              <input type="checkbox" id="chkZeroCost">
              <span>$0 Member Cost Only</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="checkbox" id="chkOtcEligible">
              <span>OTC Allowance Eligible</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="checkbox" id="chkRxRequired">
              <span>Prescription Required</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="checkbox" id="chkOrderRequired">
              <span>Provider Order Required</span>
            </label>
          </div>
        </div>

        <div class="filter-group">
          <h4>All 33 Departments</h4>
          <div class="filter-checkbox-list" id="sidebarCategoryList" style="max-height:360px;overflow-y:auto;padding-right:4px">
            <!-- JS injects department choices -->
          </div>
        </div>

        <div class="filter-group">
          <h4>Plan Sourcing Standard</h4>
          <div style="font-size:12px;line-height:1.55;color:var(--text-muted);display:grid;gap:8px">
            <div>
              <strong style="color:var(--green-dark)">✓ Source-Backed Rules:</strong>
              Coverage details link to official Evidence of Coverage, Formularies, or State Medicaid Protocols.
            </div>
            <div>
              <strong style="color:var(--green-dark)">✓ Verification Standard:</strong>
              Unverified items display <em>"Unknown / needs verification"</em>.
            </div>
          </div>
        </div>
      </aside>

      <!-- Center Product Grid -->
      <section class="market-catalog-area">
        <div class="product-grid-header">
          <div id="productCountLabel" class="product-count-label">
            Loading products...
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

  <!-- Marketplace Footer & Mandatory Legal Disclaimer -->
  <footer style="background:#fff;border-top:1px solid var(--line);padding:32px 0;margin-top:40px;color:var(--text-muted);font-size:12px">
    <div class="market-shell" style="padding:0">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:18px">
        <div style="max-width:760px">
          <strong style="color:var(--green-dark);font-size:14px">Benefit Card Navigator · Pazeratechnologies Marketplace</strong>
          <p style="margin:6px 0 0;line-height:1.6;color:var(--text-muted)">
            Coverage information is based on publicly available plan documents and may change. Eligibility, medical necessity, network requirements, and benefit limits may apply. Always confirm final coverage with your health plan or provider.
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
