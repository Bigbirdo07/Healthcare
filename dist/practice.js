/**
 * Benefit Card Navigator — Practice Inquiry Portal Prototype
 * Private authenticated staff triage queue with append-only status history,
 * text+icon accessibility, and local practice data boundaries.
 */

(function () {
  'use strict';

  const $ = (selector, parent = document) => parent.querySelector(selector);
  const $$ = (selector, parent = document) => [...parent.querySelectorAll(selector)];
  const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  const STATUS_CONFIG = {
    red: {
      key: 'red',
      icon: '🔴',
      label: 'New — call needed',
      actionVerb: 'Call Needed',
      badgeClass: 'red'
    },
    yellow: {
      key: 'yellow',
      icon: '🟡',
      label: 'Outreach attempted — no answer',
      actionVerb: 'Attempted (No Answer)',
      badgeClass: 'yellow'
    },
    green: {
      key: 'green',
      icon: '🟢',
      label: 'Patient reached / request handled',
      actionVerb: 'Reached / Handled',
      badgeClass: 'green'
    },
    blue: {
      key: 'blue',
      icon: '🔵',
      label: 'Appointment made',
      actionVerb: 'Appointment Made',
      badgeClass: 'blue'
    }
  };

  const DEFAULT_DEMO_INQUIRIES = [
    {
      id: 'INQ-RI-1001',
      name: 'Maria Example (Synthetic)',
      dob: '1978-04-12',
      phone: '(401) 555-0101',
      received: '8:35 AM',
      submittedDate: '2026-09-24',
      provider: 'Dr. Sarah Jenkins, MD (Internal Medicine)',
      practice: 'Coastal Medical Group (RI-PRAC-014)',
      category: 'doctor_or_other_clinician',
      services: ['Primary care visit', 'Nutrition counseling'],
      status: 'red',
      isPcpRequest: true,
      contactPreference: 'Morning (8:00 AM – 12:00 PM)',
      notes: 'Initial inquiry delivered to queue. Patient requested Dr. Jenkins as PCP.',
      history: [
        {
          timestamp: '2026-09-24 08:35 AM',
          actor: 'Inquiry Routing Queue',
          action: 'Inquiry received',
          prevStatus: null,
          newStatus: 'red',
          note: 'Encrypted payload verified and written to local database.'
        }
      ]
    },
    {
      id: 'INQ-RI-1002',
      name: 'Omar Sample (Synthetic)',
      dob: '1965-11-03',
      phone: '(401) 555-0102',
      received: '9:10 AM',
      submittedDate: '2026-09-24',
      provider: 'Dr. Robert Lang, MD (Family Medicine)',
      practice: 'Coastal Medical Group (RI-PRAC-014)',
      category: 'doctor_or_other_clinician',
      services: ['Annual preventive wellness visit'],
      status: 'yellow',
      isPcpRequest: false,
      contactPreference: 'Anytime during business hours',
      notes: 'Called at 9:45 AM, no answer. Left standardized voicemail requesting callback.',
      history: [
        {
          timestamp: '2026-09-24 09:10 AM',
          actor: 'Inquiry Routing Queue',
          action: 'Inquiry received',
          prevStatus: null,
          newStatus: 'red',
          note: 'Payload logged in queue.'
        },
        {
          timestamp: '2026-09-24 09:45 AM',
          actor: 'Sarah Jenkins, RN',
          action: 'Outreach attempted (no answer)',
          prevStatus: 'red',
          newStatus: 'yellow',
          note: 'Left approved non-clinical callback message on voicemail.'
        }
      ]
    },
    {
      id: 'INQ-RI-1003',
      name: 'Taylor Test (Synthetic)',
      dob: '1991-07-28',
      phone: '(401) 555-0103',
      received: '10:05 AM',
      submittedDate: '2026-09-24',
      provider: 'Dr. Emily Chen, OD (Optometry)',
      practice: 'Coastal Eye & Vision Associates (RI-PRAC-014)',
      category: 'ophthalmologist',
      services: ['Comprehensive eye examination', 'Vision refraction check'],
      status: 'green',
      isPcpRequest: false,
      contactPreference: 'Afternoon (12:00 PM – 5:00 PM)',
      notes: 'Patient reached. Verified vision coverage with RIte Care. Sent intake paperwork.',
      history: [
        {
          timestamp: '2026-09-24 10:05 AM',
          actor: 'Inquiry Routing Queue',
          action: 'Inquiry received',
          prevStatus: null,
          newStatus: 'red',
          note: 'Inquiry entered local triage queue.'
        },
        {
          timestamp: '2026-09-24 10:20 AM',
          actor: 'Sarah Jenkins, RN',
          action: 'Patient reached / request handled',
          prevStatus: 'red',
          newStatus: 'green',
          note: 'Spoke directly with patient; confirmed routine vision benefit parameters.'
        }
      ]
    },
    {
      id: 'INQ-RI-1004',
      name: 'Jordan Demo (Synthetic)',
      dob: '1984-02-17',
      phone: '(401) 555-0104',
      received: '7:50 AM',
      submittedDate: '2026-09-24',
      provider: 'Dr. Michael Vance, DDS (General Dentistry)',
      practice: 'Coastal Dental Suite (RI-PRAC-014)',
      category: 'dentist',
      services: ['Routine dental cleaning & assessment'],
      status: 'blue',
      isPcpRequest: false,
      contactPreference: 'Morning (8:00 AM – 12:00 PM)',
      notes: 'Appointment booked for Oct 4, 2026 at 10:30 AM.',
      history: [
        {
          timestamp: '2026-09-24 07:50 AM',
          actor: 'Inquiry Routing Queue',
          action: 'Inquiry received',
          prevStatus: null,
          newStatus: 'red',
          note: 'Delivered to local dental triage queue.'
        },
        {
          timestamp: '2026-09-24 08:15 AM',
          actor: 'Sarah Jenkins, RN',
          action: 'Patient reached / request handled',
          prevStatus: 'red',
          newStatus: 'green',
          note: 'Connected with patient and verified open chair slots.'
        },
        {
          timestamp: '2026-09-24 08:30 AM',
          actor: 'Sarah Jenkins, RN',
          action: 'Appointment made',
          prevStatus: 'green',
          newStatus: 'blue',
          note: 'Scheduled for in-person appointment on 10/04/2026 at 10:30 AM.'
        }
      ]
    }
  ];

  let inquiries = [];
  let selectedId = null;
  let statusFilter = 'all';
  let searchQuery = '';

  function loadInquiries() {
    try {
      const stored = JSON.parse(sessionStorage.getItem('bcnPracticeInquiries') || '[]');
      if (Array.isArray(stored) && stored.length) {
        // Merge stored with default inquiries (avoid duplicate IDs)
        const storedIds = new Set(stored.map((x) => x.id));
        const combined = [...stored, ...DEFAULT_DEMO_INQUIRIES.filter((x) => !storedIds.has(x.id))];
        inquiries = combined;
        return;
      }
    } catch (e) {
      console.warn('Could not read session inquiries', e);
    }
    inquiries = [...DEFAULT_DEMO_INQUIRIES];
  }

  function saveInquiries() {
    try {
      sessionStorage.setItem('bcnPracticeInquiries', JSON.stringify(inquiries));
    } catch (e) {
      console.warn('Could not write session inquiries', e);
    }
  }

  function updateMetrics() {
    const redCount = inquiries.filter((x) => x.status === 'red').length;
    const yellowCount = inquiries.filter((x) => x.status === 'yellow').length;
    const greenCount = inquiries.filter((x) => x.status === 'green').length;
    const blueCount = inquiries.filter((x) => x.status === 'blue').length;

    if ($('#countRed')) $('#countRed').textContent = redCount;
    if ($('#countYellow')) $('#countYellow').textContent = yellowCount;
    if ($('#countGreen')) $('#countGreen').textContent = greenCount;
    if ($('#countBlue')) $('#countBlue').textContent = blueCount;
    if ($('#openCount')) $('#openCount').textContent = redCount;
  }

  function renderQueue() {
    updateMetrics();

    let filtered = inquiries;

    if (statusFilter !== 'all') {
      filtered = filtered.filter((x) => x.status === statusFilter);
    }

    if (searchQuery) {
      filtered = filtered.filter((x) =>
        [x.id, x.name, x.provider, x.practice, ...(x.services || [])]
          .join(' ')
          .toLowerCase()
          .includes(searchQuery)
      );
    }

    const queueEl = $('#practiceQueue');
    if (!queueEl) return;

    if (!filtered.length) {
      queueEl.innerHTML = `
        <div style="padding:32px;text-align:center;background:#fff;border:1px solid var(--line);border-radius:12px">
          <strong>No inquiries match this status or search filter.</strong>
          <p style="margin:6px 0 0;color:var(--text-muted);font-size:13px">Select "All Inquiries" or adjust your search term.</p>
        </div>
      `;
      return;
    }

    queueEl.innerHTML = filtered
      .map((x) => {
        const conf = STATUS_CONFIG[x.status] || STATUS_CONFIG.red;
        const isSelected = selectedId === x.id;
        const servicesText = (x.services || []).join(' · ');

        return `
          <article class="queue-card ${conf.key} ${isSelected ? 'selected' : ''}" data-id="${esc(x.id)}">
            <button class="queue-select" type="button" data-open="${esc(x.id)}">
              <span class="status-dot ${conf.key}" title="${conf.label}"></span>
              <span class="queue-meta">
                <span class="queue-meta-top">
                  <span>${esc(x.received)}</span>
                  <span>·</span>
                  <span style="font-family:ui-monospace,monospace;font-weight:700">${esc(x.id)}</span>
                  ${x.isPcpRequest ? '<span style="color:#b58914;font-weight:700">· PCP Requested</span>' : ''}
                </span>
                <strong>${esc(x.name)}</strong>
                <em>${esc(servicesText)}</em>
                <span class="queue-provider-tag">Clinician: ${esc(x.provider)}</span>
              </span>
              <span class="status-pill-badge ${conf.badgeClass}">
                <span>${conf.icon}</span>
                <span>${conf.label}</span>
              </span>
            </button>
            <div class="queue-actions-bar" aria-label="Status transitions for ${esc(x.name)}">
              ${Object.values(STATUS_CONFIG).map((cfg) => `
                <button type="button" class="${cfg.key === x.status ? 'active' : ''}" data-status="${cfg.key}" data-id="${esc(x.id)}">
                  <span>${cfg.icon}</span>
                  <span>${cfg.actionVerb}</span>
                </button>
              `).join('')}
            </div>
          </article>
        `;
      })
      .join('');

    // Attach listeners
    $$('[data-open]').forEach((btn) => {
      btn.addEventListener('click', () => selectInquiry(btn.dataset.open));
    });

    $$('[data-status]').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        updateStatus(btn.dataset.id, btn.dataset.status);
      });
    });
  }

  function selectInquiry(id) {
    selectedId = id;
    const x = inquiries.find((i) => i.id === id);
    if (!x) return;

    const conf = STATUS_CONFIG[x.status] || STATUS_CONFIG.red;

    if ($('#recordTitle')) $('#recordTitle').textContent = x.name;

    const detailEl = $('#recordDetail');
    if (detailEl) {
      detailEl.innerHTML = `
        <dl>
          <div>
            <dt>Reference ID</dt>
            <dd style="font-family:ui-monospace,monospace">${esc(x.id)}</dd>
          </div>
          <div>
            <dt>Date of Birth</dt>
            <dd>${esc(x.dob)}</dd>
          </div>
          <div>
            <dt>Approved Phone</dt>
            <dd><a href="tel:${esc(x.phone)}">📞 ${esc(x.phone)}</a></dd>
          </div>
          <div>
            <dt>Contact Preference</dt>
            <dd>${esc(x.contactPreference || 'Business hours')}</dd>
          </div>
          <div>
            <dt>Clinician</dt>
            <dd>${esc(x.provider)}</dd>
          </div>
          <div>
            <dt>Practice ID</dt>
            <dd>${esc(x.practice || 'RI-PRAC-014')}</dd>
          </div>
          <div>
            <dt>Requested Care</dt>
            <dd>${(x.services || []).map((s) => `• ${esc(s)}`).join('<br/>')}</dd>
          </div>
          <div>
            <dt>PCP Request</dt>
            <dd>${x.isPcpRequest ? '<span style="color:#b58914;font-weight:700">⚠️ Requested (Pending practice acceptance & insurance designation)</span>' : 'None'}</dd>
          </div>
          <div>
            <dt>Current Status</dt>
            <dd>
              <span class="status-pill-badge ${conf.badgeClass}">
                <span>${conf.icon}</span>
                <span>${conf.label}</span>
              </span>
            </dd>
          </div>
        </dl>
      `;
    }

    // Render Append-Only History Timeline
    const historyContainer = $('#historyContainer');
    if (historyContainer) {
      const events = x.history || [];
      historyContainer.innerHTML = events.length ? `
        <ul class="history-timeline">
          ${events.map((ev) => `
            <li class="history-item">
              <div class="history-item-content">
                <span class="history-item-time">${esc(ev.timestamp)}</span>
                <span class="history-item-actor">${esc(ev.actor)}: ${esc(ev.action)}</span>
                ${ev.note ? `<span class="history-item-note">${esc(ev.note)}</span>` : ''}
              </div>
            </li>
          `).join('')}
        </ul>
      ` : '<p style="font-size:12px;color:var(--text-muted)">No history events recorded.</p>';
    }

    // Local Practice Notes
    const notesEl = $('#localNotes');
    if (notesEl) {
      notesEl.disabled = false;
      notesEl.value = x.notes || '';
      notesEl.oninput = () => {
        x.notes = notesEl.value;
        saveInquiries();
      };
    }

    const downloadBtn = $('#downloadRecord');
    if (downloadBtn) downloadBtn.disabled = false;

    renderQueue();
  }

  function updateStatus(id, newStatusKey) {
    const x = inquiries.find((i) => i.id === id);
    if (!x || x.status === newStatusKey) return;

    const prevStatus = x.status;
    x.status = newStatusKey;

    const now = new Date();
    const timestampStr = `${now.toISOString().slice(0, 10)} ${now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;

    const actionNames = {
      red: 'Reopened for follow-up (Call needed)',
      yellow: 'Outreach attempted (no answer)',
      green: 'Patient reached / request handled',
      blue: 'In-person appointment scheduled'
    };

    const auditEvent = {
      timestamp: timestampStr,
      actor: 'Sarah Jenkins, RN (Staff Coordinator)',
      action: actionNames[newStatusKey] || `Status updated to ${newStatusKey}`,
      prevStatus: prevStatus,
      newStatus: newStatusKey,
      note: `Transitioned from ${STATUS_CONFIG[prevStatus]?.label || prevStatus} to ${STATUS_CONFIG[newStatusKey]?.label || newStatusKey}.`
    };

    x.history = x.history || [];
    x.history.push(auditEvent);

    saveInquiries();
    renderQueue();
    if (selectedId === id) {
      selectInquiry(id);
    }
  }

  function downloadLocalRecord() {
    const x = inquiries.find((i) => i.id === selectedId);
    if (!x) return;

    const exportPayload = {
      _notice: 'PROTOTYPE EXPORT: Represents verified write to practice-controlled local database.',
      export_timestamp: new Date().toISOString(),
      practice_id: 'RI-PRAC-014',
      practice_name: 'Coastal Medical Group',
      inquiry_id: x.id,
      patient_identity: {
        name: x.name,
        date_of_birth: x.dob,
        approved_phone: x.phone,
        contact_preference: x.contactPreference
      },
      care_request: {
        clinician: x.provider,
        services: x.services,
        pcp_requested: x.isPcpRequest
      },
      status_current: x.status,
      append_only_event_history: x.history || [],
      local_clinical_notes: x.notes || '',
      compliance_safeguards: {
        storage_tier: 'Local encrypted database (AES-256)',
        routing_payload_purged: true,
        audit_trail_immutable: true,
        backup_verified: true
      }
    };

    const blob = new Blob([JSON.stringify(exportPayload, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `${x.id}-practice-local-record.json`;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(a.href);
    }, 1000);
  }

  function init() {
    loadInquiries();

    // Check if URL has ?id= to pre-select
    const params = new URLSearchParams(window.location.search);
    const targetId = params.get('id');

    renderQueue();

    if (targetId && inquiries.some((i) => i.id === targetId)) {
      selectInquiry(targetId);
    } else if (inquiries.length > 0) {
      selectInquiry(inquiries[0].id);
    }

    // Filter selects
    $('#queueFilterSelect')?.addEventListener('change', (e) => {
      statusFilter = e.target.value;
      renderQueue();
    });

    $('#queueSearch')?.addEventListener('input', (e) => {
      searchQuery = e.target.value.trim().toLowerCase();
      renderQueue();
    });

    $('#downloadRecord')?.addEventListener('click', downloadLocalRecord);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
