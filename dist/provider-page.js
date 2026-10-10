/**
 * Benefit Card Navigator — Provider Marketplace & Care Inquiry System
 * Handles New England provider search, source-backed filters, Care List,
 * and synthetic demonstration inquiries while strictly respecting data boundaries.
 */

(function () {
  'use strict';

  // provider-page.js lives at the site root; resolve data and links from it so the
  // pages work at any depth and under a hosting subpath (e.g. GitHub Pages /Healthcare/).
  const SITE_ROOT = document.currentScript ? new URL('./', document.currentScript.src).href : '/';

  const $ = (selector, parent = document) => parent.querySelector(selector);
  const $$ = (selector, parent = document) => [...parent.querySelectorAll(selector)];
  const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  const phoneText = (s) => {
    const d = String(s || '').replace(/\D/g, '');
    return d.length === 10 ? `(${d.slice(0, 3)}) ${d.slice(3, 6)}-${d.slice(6)}` : String(s || '');
  };

  const stateNames = {
    CT: 'Connecticut',
    ME: 'Maine',
    MA: 'Massachusetts',
    NH: 'New Hampshire',
    RI: 'Rhode Island',
    VT: 'Vermont',
    NY: 'New York'
  };

  // Determine initial provider type based on route or attribute or URL param
  function detectProviderType() {
    const path = window.location.pathname.toLowerCase();
    if (path.includes('/dentist')) return 'dentist';
    if (path.includes('/eye-doctor') || path.includes('/eye')) return 'eye';
    if (path.includes('/doctor')) return 'doctor';
    const params = new URLSearchParams(window.location.search);
    const typeParam = params.get('type');
    if (['doctor', 'dentist', 'eye'].includes(typeParam)) return typeParam;
    return document.body.dataset.providerType || 'doctor';
  }

  let providerType = detectProviderType();
  let state = 'RI';
  let data = { meta: { status: 'loading' }, providers: [] };
  const cache = {};
  let displayedCount = 60;

  // Care list state (persisted in sessionStorage for user convenience across routes)
  let careListState = {
    selectedProvider: null,
    requestPcp: false,
    insuranceContext: 'Traditional Medicare (Part A/B)',
    services: []
  };

  function loadCareListState() {
    try {
      const stored = sessionStorage.getItem('bcnCareListState');
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed && typeof parsed === 'object') {
          careListState = { ...careListState, ...parsed };
        }
      } else {
        // Fallback check for older simple benefit list
        const old = sessionStorage.getItem('benefitCareList');
        if (old) {
          const oldList = JSON.parse(old);
          if (Array.isArray(oldList) && oldList.length) {
            careListState.services = oldList.map((item) => (typeof item === 'string' ? item : item.benefit || 'Covered Benefit'));
          }
        }
      }
    } catch (e) {
      console.warn('Could not read care list storage', e);
    }
  }

  function saveCareListState() {
    try {
      sessionStorage.setItem('bcnCareListState', JSON.stringify(careListState));
      // Keep backward compatibility with older key
      sessionStorage.setItem('benefitCareList', JSON.stringify(careListState.services.map((s) => ({ benefit: s }))));
    } catch (e) {
      console.warn('Could not save care list storage', e);
    }
  }

  function unpack(payload) {
    if (payload.provider_columns && payload.provider_rows) {
      const columns = payload.provider_columns;
      // Large states (NY) omit constant columns and send them once as row_defaults.
      const defaults = payload.row_defaults || {};
      const labels = (payload.meta && payload.meta.medicaid_status_labels) || {};
      payload.providers = payload.provider_rows.map((row) => {
        const p = { ...defaults, ...Object.fromEntries(columns.map((column, i) => [column, row[i]])) };
        if (!p.ri_medicaid_enrollment_label && labels[p.ri_medicaid_ffs_status]) p.ri_medicaid_enrollment_label = labels[p.ri_medicaid_ffs_status];
        return p;
      });
      delete payload.provider_columns;
      delete payload.provider_rows;
    }
    const rawList = payload.providers || [];
    
    // Deduplicate providers by NPI or primary clinician key and aggregate office locations
    const dedupedMap = new Map();
    rawList.forEach((p) => {
      const key = p.npi ? String(p.npi) : `${(p.first_name || '').toUpperCase()}_${(p.last_name || '').toUpperCase()}_${(p.specialty || '').toUpperCase()}`;
      const locStr = [p.address_line_1, p.address_line_2, p.city, p.state, p.zip].filter(Boolean).join(', ');
      
      if (!dedupedMap.has(key)) {
        const item = { ...p, locations: [] };
        if (locStr) {
          item.locations.push({ address: locStr, city: p.city || '', state: p.state || '', phone: p.public_phone || '' });
        }
        dedupedMap.set(key, item);
      } else {
        const existing = dedupedMap.get(key);
        if (locStr && !existing.locations.some((l) => l.address === locStr)) {
          existing.locations.push({ address: locStr, city: p.city || '', state: p.state || '', phone: p.public_phone || '' });
        }
        // Retain best available coverage & enrollment metadata from duplicate rows
        if (p.ri_medicaid_ffs_status === 'historical_active') {
          existing.ri_medicaid_ffs_status = 'historical_active';
          if (p.ri_medicaid_enrollment_label) existing.ri_medicaid_enrollment_label = p.ri_medicaid_enrollment_label;
        }
        if (p.medicare_assignment_status === 'yes') {
          existing.medicare_assignment_status = 'yes';
        }
        if (!existing.public_phone && p.public_phone) {
          existing.public_phone = p.public_phone;
        }
      }
    });

    const uniqueProviders = [...dedupedMap.values()];
    uniqueProviders.sort((a, b) =>
      `${a.last_name || ''} ${a.first_name || ''} ${a.city || ''}`.localeCompare(
        `${b.last_name || ''} ${b.first_name || ''} ${b.city || ''}`
      )
    );
    payload.providers = uniqueProviders;
    return payload;
  }

  // Coverage filter wording depends on the state's Medicaid source: NY has a
  // current enrollment listing, the other states a 2018-2024 extract.
  function labelCoverageFilter() {
    const ny = state === 'NY';
    const text = {
      medicare_assignment: `Accepts Medicare Assignment (${ny ? 'NY' : 'RI'} data)`,
      medicaid_active: ny ? 'NY Medicaid enrolled now (can bill)' : 'Historical Medicaid Active (through 2024)',
      medicaid_all: ny ? 'Any current NY Medicaid enrollment' : 'Any Medicaid Segment Record'
    };
    Object.entries(text).forEach(([value, label]) => {
      const option = document.querySelector(`#providerCoverage option[value="${value}"]`);
      if (option) option.textContent = label;
    });
  }

  function loadState(nextState) {
    state = Object.hasOwn(stateNames, nextState) ? nextState : 'RI';
    labelCoverageFilter();
    if ($('#providerState')) $('#providerState').value = state;

    data = { meta: { status: 'loading' }, providers: [] };
    displayedCount = 60;
    render();

    if (cache[state]) {
      data = cache[state];
      populateSpecialtyFilter();
      render();
      return;
    }

    const url = state === 'RI' ? `${SITE_ROOT}providers.json` : `${SITE_ROOT}providers/${state.toLowerCase()}.json`;

    fetch(url)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`Failed to load ${url}`))))
      .then((payload) => {
        cache[state] = unpack(payload);
        if (state === nextState) {
          data = cache[state];
          populateSpecialtyFilter();
          render();
        }
      })
      .catch((err) => {
        console.error(err);
        if (state === nextState) {
          data = { meta: { status: 'unavailable' }, providers: [] };
          render();
        }
      });
  }

  function matchesType(p) {
    const cat = (p.provider_category || '').toLowerCase();
    const text = [
      cat,
      p.taxonomy_description,
      p.specialty,
      p.subspecialty
    ].join(' ').toLowerCase();

    if (providerType === 'dentist') {
      return cat === 'dentist' || /dentist|dental|oral surgery|dmd|dds/.test(text);
    }
    if (providerType === 'eye') {
      return cat === 'optometrist' || cat === 'ophthalmologist' || /optometr|ophthalm|eye care|optician|vision/.test(text);
    }
    // Default: Doctor (excludes dentists and vision specialists)
    return cat === 'doctor_or_other_clinician' || (!/dentist|dental|oral surgery|dmd|dds|optometr|ophthalm|optician/.test(text));
  }

  function setProviderType(next, updateUrl = true) {
    providerType = ['doctor', 'dentist', 'eye'].includes(next) ? next : 'doctor';
    document.body.dataset.providerType = providerType;

    const copy = {
      doctor: {
        eyebrow: 'New England care directory',
        title: 'Find a doctor.',
        intro:
          'Search doctors, nurse practitioners, physician assistants, and clinical specialists across New England by name, specialty, city, ZIP, and source-labeled coverage data. Confirm current licensure, exact network participation, and appointment availability before scheduling.',
        placeholder: 'Search by doctor name, specialty, practice, city, or ZIP'
      },
      dentist: {
        eyebrow: 'New England dental directory',
        title: 'Find a dentist.',
        intro:
          'Search dental practitioners present in the federal Medicare/Medicaid baseline. This source is not a comprehensive census of all licensed dentists. Always confirm dental plan network participation directly with the practice.',
        placeholder: 'Search by dentist name, dental specialty, city, or ZIP'
      },
      eye: {
        eyebrow: 'New England vision directory',
        title: 'Find an eye doctor.',
        intro:
          'Search optometrists and ophthalmologists identified by primary specialty. Confirm whether medical or routine vision coverage applies, exact network participation, and office availability directly with the practice.',
        placeholder: 'Search by eye doctor name, ophthalmology, optometry, city, or ZIP'
      }
    }[providerType];

    if ($('#providerEyebrow')) $('#providerEyebrow').textContent = copy.eyebrow;
    if ($('#providerFinderTitle')) $('#providerFinderTitle').textContent = copy.title;
    if ($('#providerIntro')) $('#providerIntro').textContent = copy.intro;
    if ($('#providerSearch')) $('#providerSearch').placeholder = copy.placeholder;

    $$('.provider-tab').forEach((tab) => {
      tab.classList.toggle('active', tab.dataset.providerType === providerType);
    });

    populateSpecialtyFilter();
    displayedCount = 60;
    render();
    renderCareList();
  }

  function populateSpecialtyFilter() {
    const specialtySelect = $('#providerSpecialty');
    if (!specialtySelect) return;

    const currentVal = specialtySelect.value;
    const specialties = new Set();
    (data.providers || []).filter(matchesType).forEach((p) => {
      if (p.specialty) specialties.add(p.specialty.trim().toUpperCase());
      else if (p.taxonomy_description) specialties.add(p.taxonomy_description.trim().toUpperCase());
    });

    const sorted = [...specialties].sort();
    specialtySelect.innerHTML = `<option value="all">All Specialties (${sorted.length})</option>` +
      sorted.map((s) => `<option value="${esc(s)}">${esc(s)}</option>`).join('');

    if (sorted.includes(currentVal)) {
      specialtySelect.value = currentVal;
    } else {
      specialtySelect.value = 'all';
    }
  }

  function matchesCoverage(p, value) {
    if (value === 'all') return true;
    if (value === 'medicare') return p.medicare_enrollment_status === 'yes' || state !== 'RI';
    if (value === 'medicare_assignment') return p.medicare_assignment_status === 'yes';
    if (value === 'medicaid_active') return ['historical_active', 'active_ffs', 'active_managed_care_only'].includes(p.ri_medicaid_ffs_status);
    if (value === 'medicaid_all') return p.ri_medicaid_ffs_status && !['no_record_in_extract', 'not_in_current_listing'].includes(p.ri_medicaid_ffs_status);
    return true;
  }

  function getMedicaidPill(p) {
    const label = p.ri_medicaid_enrollment_label || 'Unknown';
    const status = p.ri_medicaid_ffs_status;
    let kind = 'unknown';
    let icon = '?';

    // New York uses the state's current enrollment listing, not the 2018-2024 extract.
    if (/^active_|^not_in_current_listing$/.test(status || '')) {
      const asOf = (data.meta && data.meta.medicaid_status_as_of) || '';
      const title = `NY Medicaid Enrolled Provider Listing (NYS DOH), file date ${asOf}. Enrollment does NOT confirm a managed care plan network or new-patient acceptance.`;
      const look = status === 'active_ffs' || status === 'active_managed_care_only' ? ['verified', '✓']
        : status === 'active_opra_only' ? ['warning', '!'] : ['unknown', '?'];
      return `<span class="provider-pill ${look[0]}" title="${esc(title)}">${look[1]} ${state} Medicaid (${esc(asOf)}): ${esc(label)}</span>`;
    }

    if (status === 'historical_active') {
      kind = 'historical';
      icon = '◷';
    } else if (status === 'terminated' || status === 'denied') {
      kind = 'negative';
      icon = '×';
    } else if (status === 'active_do_not_pay' || status === 'source_conflict') {
      kind = 'warning';
      icon = '!';
    } else if (status === 'eligibility_verification_only') {
      kind = 'historical';
      icon = 'ℹ';
    }

    return `<span class="provider-pill ${kind}" title="Historical enrollment data through December 31, 2024. Does NOT confirm current 2026 participation, managed care plan network, or new-patient acceptance.">${icon} ${state} Medicaid (through 2024): ${esc(label)}</span>`;
  }

  function getMedicarePills(p) {
    const pills = [];
    // Care compare baseline
    pills.push('<span class="provider-pill verified" title="Included in CMS Medicare Care Compare downloadable baseline">✓ Medicare Care Compare</span>');

    if (state === 'RI' || state === 'NY') {
      if (p.medicare_assignment_status === 'yes') {
        pills.push('<span class="provider-pill verified" title="Clinician accepts Medicare assignment rates">✓ Accepts Medicare Assignment</span>');
      } else if (p.medicare_assignment_status === 'no') {
        pills.push('<span class="provider-pill negative" title="Does not accept Medicare assignment">× No Medicare Assignment</span>');
      } else {
        pills.push('<span class="provider-pill unknown" title="Assignment status not verified in baseline">? Medicare Assignment: Unverified</span>');
      }
    }
    return pills.join('');
  }

  function render() {
    const searchInput = $('#providerSearch');
    const query = searchInput ? searchInput.value.trim().toLowerCase() : '';
    const coverageSelect = $('#providerCoverage');
    const coverage = coverageSelect ? coverageSelect.value : 'all';
    const specialtySelect = $('#providerSpecialty');
    const specialtyFilter = specialtySelect ? specialtySelect.value : 'all';
    const telehealthOnly = $('#telehealthFilter') ? $('#telehealthFilter').checked : false;

    let filtered = (data.providers || []).filter(matchesType).filter((p) => matchesCoverage(p, coverage));

    if (specialtyFilter !== 'all') {
      filtered = filtered.filter((p) => {
        const spec = (p.specialty || p.taxonomy_description || '').toUpperCase();
        return spec === specialtyFilter;
      });
    }

    if (query) {
      filtered = filtered.filter((p) => {
        const haystack = [
          p.first_name,
          p.middle_name,
          p.last_name,
          p.credentials,
          p.practice_name,
          p.specialty,
          p.taxonomy_description,
          p.city,
          p.zip,
          p.public_phone,
          p.npi
        ].join(' ').toLowerCase();
        return haystack.includes(query);
      });
    }

    if (telehealthOnly) {
      filtered = filtered.filter((p) => p.telehealth_status === 'yes');
    }

    const totalMatching = filtered.length;
    const rows = filtered.slice(0, displayedCount);
    const status = data.meta?.status;

    // Render Data Notice with clear statutory and factual boundaries
    const noticeEl = $('#providerDataNotice');
    if (noticeEl) {
      if (status === 'loading') {
        noticeEl.innerHTML = `<div class="data-notice-header"><strong class="data-notice-count">Loading ${esc(stateNames[state])} provider records…</strong></div><p>Fetching public baseline dataset from local index. Please wait.</p>`;
      } else if (status === 'unavailable') {
        noticeEl.innerHTML = `<div class="data-notice-header"><strong class="data-notice-count" style="color:var(--status-red)">Provider data currently unavailable</strong></div><p>The ${esc(stateNames[state])} dataset could not be loaded. Please check your connection or choose another state.</p>`;
      } else {
        noticeEl.innerHTML = `
          <div class="data-notice-header">
            <span class="data-notice-count">${totalMatching.toLocaleString()} matching ${esc(stateNames[state])} ${totalMatching === 1 ? 'record' : 'records'}</span>
            <small style="color:var(--text-muted)">Showing ${Math.min(rows.length, totalMatching)} of ${totalMatching.toLocaleString()}</small>
          </div>
          <ul>
            <li><strong>Medicaid Data Scope:</strong> Medicaid enrollment records reflect CMS/T-MSIS historical data through <strong>December 31, 2024</strong> only. They do <em>not</em> prove current 2026 participation, enrollment in a specific managed-care plan network, or acceptance of new patients.</li>
            <li><strong>Medicare Data Scope:</strong> Sourced from CMS Medicare Care Compare national downloadable baseline (September 2026 release). Medicare assignment is verified where indicated.</li>
            <li><strong>No Language Inference:</strong> Clinician and staff languages are <strong>never inferred</strong> from names, photos, or perceived backgrounds. Verified provider-attested language data is currently pending.</li>
            <li><strong>Mandatory Confirmation:</strong> Licensure, commercial plan network tiers, and appointment availability remain unverified in public baselines. Always confirm directly with the practice and health plan before scheduling.</li>
          </ul>
        `;
      }
    }

    // Render Provider Grid
    const gridEl = $('#providerGrid');
    if (!gridEl) return;

    if (status === 'loading') {
      gridEl.innerHTML = `<div class="empty-directory"><strong>Loading provider records…</strong><p>Filtering ${esc(stateNames[state])} dataset.</p></div>`;
      return;
    }

    if (!rows.length) {
      gridEl.innerHTML = `
        <div class="empty-directory">
          <strong>No clinicians match your current search and filters.</strong>
          <p>Try searching for a different city, ZIP code, or specialty, or reset the coverage filter.</p>
        </div>
      `;
      return;
    }

    gridEl.innerHTML = rows
      .map((p) => {
        const fullName = [p.first_name, p.middle_name, p.last_name, p.suffix]
          .filter(Boolean)
          .join(' ');
        const creds = p.credentials ? esc(p.credentials) : '';
        const practice = p.practice_name ? esc(p.practice_name) : 'Independent Medical Practice';
        const specialty = p.specialty || p.taxonomy_description || 'Specialty not listed';
        const addressParts = [p.address_line_1, p.address_line_2, p.city, p.state, p.zip].filter(Boolean);
        const addressStr = addressParts.length ? addressParts.join(', ') : `${p.city || ''}, ${p.state || state} ${p.zip || ''}`.trim();
        const sourceUrl = p.profile_page_url || (p.npi ? `https://npiregistry.cms.hhs.gov/provider-view/${p.npi}` : null);
        const isSelected = careListState.selectedProvider && careListState.selectedProvider.npi === p.npi;
        const extraLocations = p.locations && p.locations.length > 1 ? p.locations.length : 1;

        return `
          <article class="provider-card ${isSelected ? 'selected-in-carelist' : ''}" data-npi="${esc(p.npi || '')}">
            <div class="provider-card-top">
              <span class="coverage-badge">${esc((p.provider_category || providerType).replace(/_/g, ' '))}</span>
              <small>${p.last_verified_at ? `Verified ${esc(p.last_verified_at.slice(0, 10))}` : 'Federal baseline · 2026'}</small>
            </div>
            <h3>${esc(fullName || 'Clinician')} ${creds ? `<span style="font-size:16px;font-family:sans-serif;color:var(--text-muted);font-weight:600">· ${creds}</span>` : ''}</h3>
            <p class="provider-practice">${practice}</p>
            <p class="provider-specialty">${esc(specialty)}</p>
            <address>📍 ${esc(addressStr)}</address>
            ${extraLocations > 1 ? `
              <div style="font-size:11px;font-weight:700;color:var(--green-dark);background:#edf4f1;padding:4px 8px;border-radius:4px;display:inline-block;margin-bottom:10px">
                🏢 ${extraLocations} Practice Locations in ${esc(state)}
              </div>
            ` : ''}
            ${p.public_phone ? `
              <div class="provider-phone" style="margin-bottom:10px">
                <span>📞 <a href="tel:${esc(p.public_phone)}">${esc(phoneText(p.public_phone))}</a></span>
              </div>
            ` : ''}
            <div class="provider-pills">
              ${getMedicarePills(p)}
              ${getMedicaidPill(p)}
              ${p.telehealth_status === 'yes' ? '<span class="provider-pill verified">✓ Telehealth Documented</span>' : ''}
            </div>
            <div class="provider-actions">
              <button type="button" class="add-care-button ${isSelected ? 'in-cart' : ''}" data-select-provider="${esc(p.npi || p.provider_record_id)}">
                ${isSelected ? '✓ Selected in Care List' : '+ Select for Care List'}
              </button>
              ${sourceUrl ? `
                <a href="${esc(sourceUrl)}" class="source-link" target="_blank" rel="noopener noreferrer">
                  Check CMS Source ↗
                </a>
              ` : ''}
            </div>
          </article>
        `;
      })
      .join('');

    // Attach click listeners for "Select for Care List"
    $$('[data-select-provider]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.selectProvider;
        const provider = (data.providers || []).find((p) => (p.npi || p.provider_record_id) === id);
        if (provider) {
          selectProviderForCareList(provider);
        }
      });
    });

    // Render Load More button if there are more matching
    const loadMoreContainer = $('#loadMoreContainer');
    if (loadMoreContainer) {
      if (totalMatching > displayedCount) {
        loadMoreContainer.innerHTML = `
          <button type="button" class="secondary-button" id="loadMoreBtn" style="margin:20px auto;display:block;">
            Load More Records (${Math.min(60, totalMatching - displayedCount)} more)
          </button>
        `;
        $('#loadMoreBtn')?.addEventListener('click', () => {
          displayedCount += 60;
          render();
        });
      } else {
        loadMoreContainer.innerHTML = '';
      }
    }
  }

  function selectProviderForCareList(p) {
    const fullName = [p.first_name, p.middle_name, p.last_name, p.suffix].filter(Boolean).join(' ');
    careListState.selectedProvider = {
      npi: p.npi || '',
      id: p.provider_record_id || '',
      name: fullName,
      credentials: p.credentials || '',
      practice: p.practice_name || 'Selected Practice',
      specialty: p.specialty || p.taxonomy_description || 'General Practice',
      category: p.provider_category || providerType,
      city: p.city || '',
      state: p.state || state,
      phone: p.public_phone || ''
    };

    // If services list is empty, add a default service based on provider type
    if (careListState.services.length === 0) {
      if (providerType === 'dentist') {
        careListState.services.push('Preventive dental cleaning & exam');
      } else if (providerType === 'eye') {
        careListState.services.push('Comprehensive eye examination');
      } else {
        careListState.services.push('Primary care evaluation / checkup');
      }
    }

    saveCareListState();
    render();
    renderCareList();
  }

  function renderCareList() {
    const container = $('#careListContainer');
    if (!container) return;

    const p = careListState.selectedProvider;
    const services = careListState.services || [];
    const isPcp = careListState.requestPcp;

    const providerHtml = p ? `
      <div class="selected-provider-box">
        <strong>${esc(p.name)} ${p.credentials ? `(${esc(p.credentials)})` : ''}</strong>
        <p>${esc(p.practice)}</p>
        <p>${esc(p.specialty)} · ${esc(p.city)}, ${esc(p.state)}</p>
        ${p.phone ? `<p style="font-size:11px;color:#cbe0d9">📞 ${esc(phoneText(p.phone))}</p>` : ''}
        <button type="button" class="clear-provider" id="removeSelectedProvider">✕ Remove clinician</button>
      </div>
    ` : `
      <p style="font-size:13px;color:#bcd0ca;margin:0;line-height:1.5">
        No clinician selected. Click <strong>"+ Select for Care List"</strong> on any provider card to attach a practice to your inquiry.
      </p>
    `;

    const pcpOptionHtml = (providerType === 'doctor' || (p && p.category === 'doctor_or_other_clinician')) ? `
      <div class="pcp-option-box">
        <label class="pcp-checkbox-label">
          <input type="checkbox" id="requestPcpCheckbox" ${isPcp ? 'checked' : ''} />
          <span>Request this doctor as my PCP</span>
        </label>
        <p class="pcp-disclaimer">
          ⚠️ <strong>Pending Confirmation:</strong> Requesting a Primary Care Provider is an inquiry. Your selection is <em>not</em> confirmed until both the practice accepts you as a patient and your health plan records the designation.
        </p>
      </div>
    ` : '';

    const servicesHtml = services.length ? `
      <ul class="care-services-list">
        ${services.map((s, idx) => `
          <li>
            <span>${esc(s)}</span>
            <button type="button" data-remove-service="${idx}" title="Remove service">×</button>
          </li>
        `).join('')}
      </ul>
    ` : `
      <p style="font-size:12px;color:#bcd0ca;margin:0">No requested services added yet.</p>
    `;

    // Suggested quick chips by type
    const suggested = providerType === 'dentist'
      ? ['Routine cleaning', 'Dental exam & X-rays', 'Tooth pain triage', 'Dentures evaluation']
      : providerType === 'eye'
      ? ['Comprehensive eye exam', 'Refraction & glasses check', 'Glaucoma screening', 'Diabetic eye exam']
      : ['Primary care visit', 'Annual wellness exam', 'Prescription renewal consult', 'Chronic care follow-up'];

    const quickChipsHtml = `
      <div class="quick-service-chips">
        ${suggested.map((item) => `<button type="button" class="quick-chip" data-add-quick="${esc(item)}">+ ${esc(item)}</button>`).join('')}
      </div>
    `;

    const canSubmit = Boolean(p && services.length > 0);

    container.innerHTML = `
      <div class="care-list-section">
        <label for="insuranceCardContext">Insurance / Benefit Card</label>
        <select id="insuranceCardContext">
          <option value="Traditional Medicare (Part A/B)" ${careListState.insuranceContext === 'Traditional Medicare (Part A/B)' ? 'selected' : ''}>Traditional Medicare (Part A/B)</option>
          <option value="Medicare Advantage (HMO/PPO)" ${careListState.insuranceContext === 'Medicare Advantage (HMO/PPO)' ? 'selected' : ''}>Medicare Advantage (HMO/PPO)</option>
          <option value="Medicaid / RIte Care" ${careListState.insuranceContext === 'Medicaid / RIte Care' ? 'selected' : ''}>Medicaid / State Plan</option>
          <option value="Dual Eligible (Medicare + Medicaid)" ${careListState.insuranceContext === 'Dual Eligible (Medicare + Medicaid)' ? 'selected' : ''}>Dual Eligible (Medicare + Medicaid)</option>
          <option value="Commercial / Employer Insurance" ${careListState.insuranceContext === 'Commercial / Employer Insurance' ? 'selected' : ''}>Commercial / Employer Insurance</option>
          <option value="Self-Pay / Uninsured" ${careListState.insuranceContext === 'Self-Pay / Uninsured' ? 'selected' : ''}>Self-Pay / Uninsured</option>
        </select>
      </div>

      <div class="care-list-section">
        <small class="section-title">Designated Clinician & Practice</small>
        ${providerHtml}
        ${pcpOptionHtml}
      </div>

      <div class="care-list-section">
        <small class="section-title">Requested Care or Services</small>
        ${servicesHtml}
        <div class="add-service-box">
          <input type="text" id="customServiceInput" placeholder="Add requested care…" maxlength="80" />
          <button type="button" id="addCustomServiceBtn">Add</button>
        </div>
        ${quickChipsHtml}
      </div>

      <p class="care-list-disclaimer">
        ⚖️ <strong>Legal & Coverage Notice:</strong> A Care List submission is an <em>inquiry</em>, not an insurance claim, medical order, guaranteed appointment, coverage authorization, purchase, or confirmed PCP designation.
      </p>

      <button type="button" class="primary-button" id="reviewInquiryBtn" ${canSubmit ? '' : 'disabled'}>
        <span>Review Care Inquiry</span>
        <span>→</span>
      </button>
    `;

    // Event listeners for Care List controls
    $('#insuranceCardContext')?.addEventListener('change', (e) => {
      careListState.insuranceContext = e.target.value;
      saveCareListState();
    });

    $('#removeSelectedProvider')?.addEventListener('click', () => {
      careListState.selectedProvider = null;
      careListState.requestPcp = false;
      saveCareListState();
      render();
      renderCareList();
    });

    $('#requestPcpCheckbox')?.addEventListener('change', (e) => {
      careListState.requestPcp = e.target.checked;
      saveCareListState();
    });

    $$('[data-remove-service]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const idx = parseInt(btn.dataset.removeService, 10);
        careListState.services.splice(idx, 1);
        saveCareListState();
        renderCareList();
      });
    });

    const addCustom = () => {
      const input = $('#customServiceInput');
      const val = input ? input.value.trim() : '';
      if (val) {
        careListState.services.push(val);
        input.value = '';
        saveCareListState();
        renderCareList();
      }
    };

    $('#addCustomServiceBtn')?.addEventListener('click', addCustom);
    $('#customServiceInput')?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        addCustom();
      }
    });

    $$('[data-add-quick]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const text = btn.dataset.addQuick;
        if (!careListState.services.includes(text)) {
          careListState.services.push(text);
          saveCareListState();
          renderCareList();
        }
      });
    });

    $('#reviewInquiryBtn')?.addEventListener('click', openInquiryReviewModal);
  }

  function openInquiryReviewModal() {
    const p = careListState.selectedProvider;
    if (!p) return;

    let modal = $('#inquiryModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'inquiryModal';
      modal.className = 'modal-overlay';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      modal.setAttribute('aria-labelledby', 'modalTitle');
      document.body.appendChild(modal);
    }

    renderModalReviewContent(modal);
    modal.style.display = 'grid';
  }

  function renderModalReviewContent(modal) {
    const p = careListState.selectedProvider;
    const services = careListState.services || [];
    const isPcp = careListState.requestPcp;

    modal.innerHTML = `
      <div class="modal-window">
        <div class="modal-header">
          <h2 id="modalTitle">Review Care Inquiry Summary</h2>
          <button type="button" class="modal-close" id="closeModalBtn" aria-label="Close review dialog">×</button>
        </div>
        <div class="modal-body">
          <div class="modal-summary-box">
            <dl>
              <dt>Selected Clinician</dt>
              <dd><strong>${esc(p.name)} ${p.credentials ? `(${esc(p.credentials)})` : ''}</strong> (${esc(p.specialty)})</dd>
              <dt>Practice / Clinic</dt>
              <dd>${esc(p.practice)} · ${esc(p.city)}, ${esc(p.state)}</dd>
              <dt>Public Phone</dt>
              <dd>${p.phone ? esc(phoneText(p.phone)) : 'Not available'}</dd>
              <dt>Insurance Context</dt>
              <dd>${esc(careListState.insuranceContext)}</dd>
              <dt>Requested Care</dt>
              <dd>${services.map((s) => `• ${esc(s)}`).join('<br/>')}</dd>
              <dt>PCP Designation</dt>
              <dd>${isPcp ? '<span style="color:#b58914;font-weight:700">⚠️ Requested (Pending practice acceptance & insurance designation)</span>' : 'No PCP designation requested'}</dd>
            </dl>
          </div>

          <div class="security-boundary-box">
            <strong>🔒 Security & Compliance Boundary</strong>
            <p style="margin:0 0 6px">
              This static website does not transmit real patient health information over the public Internet. Real inquiry delivery remains disabled until an approved, encrypted backend with authenticated practice connectors is deployed.
            </p>
            <p style="margin:0">
              To test this workflow safely, use the <strong>synthetic demonstration form</strong> below. Never enter real patient health information.
            </p>
          </div>

          <h3 style="font-size:16px;margin:0 0 12px;color:var(--green-dark)">Synthetic Demonstration Patient Information</h3>
          <form id="syntheticInquiryForm" class="demo-patient-form">
            <div class="field">
              <label for="demoPatientName">Synthetic Patient Name</label>
              <input type="text" id="demoPatientName" value="Alex Rivera (Synthetic Patient)" required />
            </div>
            <div class="field">
              <label for="demoDob">Synthetic Date of Birth</label>
              <input type="date" id="demoDob" value="1982-06-15" required />
            </div>
            <div class="field">
              <label for="demoPhone">Approved Phone Number</label>
              <input type="tel" id="demoPhone" value="(401) 555-0184" required />
            </div>
            <div class="field">
              <label for="demoContactPref">Preferred Contact Time</label>
              <select id="demoContactPref">
                <option value="Morning (8:00 AM – 12:00 PM)">Morning (8:00 AM – 12:00 PM)</option>
                <option value="Afternoon (12:00 PM – 5:00 PM)">Afternoon (12:00 PM – 5:00 PM)</option>
                <option value="Anytime during business hours">Anytime during business hours</option>
              </select>
            </div>
            <div class="field full-width">
              <label style="display:flex;align-items:flex-start;gap:8px;font-size:12px;font-weight:normal;cursor:pointer">
                <input type="checkbox" id="consentCheckbox" checked required style="margin-top:2px;accent-color:var(--green-dark)" />
                <span>I confirm this is synthetic demonstration data. I authorize practice staff to receive these simulated contact details to test inquiry triage.</span>
              </label>
            </div>
          </form>

          <div class="modal-actions">
            <button type="button" class="secondary-button" id="cancelModalBtn">Back to Care List</button>
            <button type="button" class="primary-button" id="submitDemoInquiryBtn" style="width:auto;margin:0;padding:0 24px">
              Submit Synthetic Demo Inquiry →
            </button>
          </div>
        </div>
      </div>
    `;

    $('#closeModalBtn')?.addEventListener('click', () => {
      modal.style.display = 'none';
    });
    $('#cancelModalBtn')?.addEventListener('click', () => {
      modal.style.display = 'none';
    });

    $('#submitDemoInquiryBtn')?.addEventListener('click', () => {
      const consent = $('#consentCheckbox')?.checked;
      if (!consent) {
        alert('Please confirm the demonstration consent checkbox before proceeding.');
        return;
      }
      submitSyntheticInquiry(modal);
    });
  }

  function submitSyntheticInquiry(modal) {
    const p = careListState.selectedProvider;
    const services = careListState.services || [];
    const patientName = $('#demoPatientName')?.value || 'Alex Rivera (Synthetic Patient)';
    const dob = $('#demoDob')?.value || '1982-06-15';
    const phone = $('#demoPhone')?.value || '(401) 555-0184';
    const pref = $('#demoContactPref')?.value || 'Morning (8:00 AM – 12:00 PM)';
    const refNum = `INQ-${state}-${Math.floor(1000 + Math.random() * 9000)}`;
    const now = new Date();
    const timestamp = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Store in demo inquiries array in sessionStorage for the practice portal to read
    const newDemoInquiry = {
      id: refNum,
      name: patientName,
      dob: dob,
      phone: phone,
      received: timestamp,
      submittedDate: now.toISOString().slice(0, 10),
      provider: `${p.name} ${p.credentials ? `(${p.credentials})` : ''}`,
      practice: p.practice,
      practiceId: 'RI-PRAC-014',
      category: p.category || providerType,
      services: [...services],
      status: 'red',
      isPcpRequest: careListState.requestPcp,
      contactPreference: pref,
      notes: '',
      history: [
        {
          timestamp: `${now.toISOString().slice(0, 10)} ${timestamp}`,
          actor: 'Patient Inquiry System',
          action: 'Inquiry submitted',
          prevStatus: null,
          newStatus: 'red',
          note: 'Synthetic inquiry delivered to practice queue. Call needed.'
        }
      ]
    };

    try {
      const existing = JSON.parse(sessionStorage.getItem('bcnPracticeInquiries') || '[]');
      existing.unshift(newDemoInquiry);
      sessionStorage.setItem('bcnPracticeInquiries', JSON.stringify(existing));
    } catch (e) {
      console.warn('Could not persist demo inquiry to portal queue', e);
    }

    // Render Confirmation View inside the modal
    modal.querySelector('.modal-body').innerHTML = `
      <div class="confirmation-view">
        <div class="confirmation-badge">✓</div>
        <h3>Demonstration Inquiry Prepared</h3>
        <p style="color:var(--text-muted);font-size:14px;margin:0 0 12px">
          Your synthetic care inquiry has been logged for practice review with reference ID:
        </p>
        <div class="reference-number-box">${refNum}</div>
        
        <div style="background:#f7faf8;border:1px solid var(--line);border-radius:12px;padding:16px;text-align:left;margin:16px 0;font-size:13px">
          <strong style="color:var(--green-dark);display:block;margin-bottom:6px">What happens next:</strong>
          <ol style="margin:0;padding-left:20px;color:var(--text-main);line-height:1.6">
            <li>Practice staff receive this inquiry in their <strong>Practice Inquiry Portal</strong> queue (marked 🔴 <em>New—call needed</em>).</li>
            <li>Staff verify provider schedule availability and insurance network participation.</li>
            <li>Staff call your approved contact number <strong>${esc(phone)}</strong> to arrange care.</li>
            <li>${careListState.requestPcp ? 'If accepted, the practice guides you through the official PCP notification process with your insurer.' : 'Appointment details and reminders are confirmed directly with the clinic.'}</li>
          </ol>
        </div>

        <p style="font-size:12px;color:var(--text-muted);margin-bottom:20px">
          ⚖️ Reminder: This is an inquiry, not a confirmed appointment or insurance guarantee.
        </p>

        <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
          <a href="${SITE_ROOT}practice/" class="primary-button" style="width:auto;padding:0 24px;text-decoration:none">
            Open Practice Portal Prototype →
          </a>
          <button type="button" class="secondary-button" id="doneModalBtn">
            Back to Directory
          </button>
        </div>
      </div>
    `;

    $('#doneModalBtn')?.addEventListener('click', () => {
      modal.style.display = 'none';
    });
  }

  // Set up event listeners
  function init() {
    loadCareListState();

    // State select change
    $('#providerState')?.addEventListener('change', (e) => {
      loadState(e.target.value);
    });

    // Search and filter inputs
    $('#providerSearch')?.addEventListener('input', () => {
      displayedCount = 60;
      render();
    });

    $('#providerCoverage')?.addEventListener('change', () => {
      displayedCount = 60;
      render();
    });

    $('#providerSpecialty')?.addEventListener('change', () => {
      displayedCount = 60;
      render();
    });

    $('#telehealthFilter')?.addEventListener('change', () => {
      displayedCount = 60;
      render();
    });

    // Provider directory tabs navigation
    $$('.provider-tab').forEach((tab) => {
      tab.addEventListener('click', (e) => {
        const nextType = tab.dataset.providerType;
        if (nextType && nextType !== providerType) {
          // If tab is an anchor to a dedicated route, allow normal navigation or pushState
          const href = tab.getAttribute('href');
          if (href && !href.startsWith('?') && !href.startsWith('#')) {
            // Dedicated route: let the browser navigate to it.
          } else {
            e.preventDefault();
            history.pushState({}, '', `?type=${nextType}&state=${state}`);
            setProviderType(nextType);
          }
        }
      });
    });

    // Handle initial state from URL
    const params = new URLSearchParams(window.location.search);
    const reqState = params.get('state');
    const reqType = params.get('type');

    if (reqType && ['doctor', 'dentist', 'eye'].includes(reqType)) {
      setProviderType(reqType, false);
    } else {
      setProviderType(providerType, false);
    }

    loadState(Object.hasOwn(stateNames, reqState) ? reqState : 'RI');
    renderCareList();
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
