import re

print("Updating marketplace.js for State-First filtering and Amazon-style Review Checkout Modal...")

with open('dist/marketplace/marketplace.js', 'r', encoding='utf-8') as f:
    js_code = f.read()

# Add event handling and modal rendering JS logic to marketplace.js
checkout_logic_js = """
  // --- 10. STATE-FIRST HIERARCHY & CHECKOUT REVIEW MODAL ENGINE ---
  document.addEventListener('DOMContentLoaded', () => {
    const stateSel = document.getElementById('stateSelect');
    const planTypeSel = document.getElementById('planTypeSelect');
    const planSel = document.getElementById('planSelect');

    const checkoutModal = document.getElementById('checkoutModal');
    const closeBtn = document.getElementById('closeCheckoutModalBtn');
    const navCheckoutBtn = document.getElementById('navCheckoutBtn');
    const heroCheckoutBtn = document.getElementById('heroCheckoutBtn');
    const triggerReviewTabBtn = document.getElementById('triggerReviewTabBtn');
    const sideCheckoutBtn = document.getElementById('sideCheckoutBtn');
    const checkoutPlanSummary = document.getElementById('checkoutPlanSummary');
    const checkoutItemsList = document.getElementById('checkoutItemsList');
    const form = document.getElementById('providerCheckoutForm');

    // 10A. State-First Filtering Logic
    function updatePlanDropdown() {
      const selectedState = stateSel ? stateSel.value : 'RI';
      const selectedType = planTypeSel ? planTypeSel.value : 'all';

      if (!planSel) return;

      const filteredPlans = PLANS.filter(p => {
        const stateOk = p.state === selectedState || p.state === 'All Areas' || selectedState === 'RI';
        const typeOk = selectedType === 'all' || p.plan_type === selectedType;
        return stateOk && typeOk;
      });

      planSel.innerHTML = filteredPlans.map(p => 
        `<option value="${p.id}">${p.insurer_name} — ${p.official_plan_name}</option>`
      ).join('');

      if (filteredPlans.length > 0) {
        planSel.value = filteredPlans[0].id;
        activePlanId = filteredPlans[0].id;
        activeInsurerId = filteredPlans[0].insurer_id;
      }
      
      const statusPill = document.getElementById('planStatusPill');
      if (statusPill) {
        statusPill.textContent = `✓ ${selectedState} Active Plan`;
      }
    }

    if (stateSel) stateSel.addEventListener('change', updatePlanDropdown);
    if (planTypeSel) planTypeSel.addEventListener('change', updatePlanDropdown);

    // 10B. Open / Close Checkout Review Modal
    function openCheckoutModal() {
      if (!checkoutModal) return;
      checkoutModal.style.display = 'flex';

      const curPlan = PLANS.find(p => p.id === activePlanId) || PLANS[0];
      const curState = stateSel ? stateSel.value : 'RI';

      if (checkoutPlanSummary) {
        checkoutPlanSummary.innerHTML = `
          <strong>Selected Plan Context:</strong> State: <span>${curState}</span> | Insurer: <span>${curPlan.insurer_name}</span> | Plan: <span>${curPlan.official_plan_name}</span>
        `;
      }

      // Populate Items requested in cart/slip
      if (checkoutItemsList) {
        if (!callSlip || callSlip.length === 0) {
          checkoutItemsList.innerHTML = `
            <div style="padding:20px;text-align:center;color:#666">
              <p>No items added to call slip yet.</p>
              <small>Click "Request from my provider" on any item card to add it to your request slip.</small>
            </div>
          `;
        } else {
          checkoutItemsList.innerHTML = callSlip.map((item, idx) => `
            <div style="background:#fff;padding:12px;border-radius:6px;margin-bottom:10px;border:1px solid #ddd;display:flex;justify-content:space-between;align-items:center">
              <div>
                <strong style="color:#133e33">${item.name}</strong>
                <div style="font-size:12px;color:#666">${item.notes || 'OTC Allowance / DME Benefit'}</div>
              </div>
              <span style="font-size:12px;font-weight:700;color:#0d6b63">✓ Selected</span>
            </div>
          `).join('');
        }
      }
    }

    function closeCheckoutModal() {
      if (checkoutModal) checkoutModal.style.display = 'none';
    }

    [navCheckoutBtn, heroCheckoutBtn, triggerReviewTabBtn, sideCheckoutBtn].forEach(btn => {
      if (btn) btn.addEventListener('click', openCheckoutModal);
    });

    if (closeBtn) closeBtn.addEventListener('click', closeCheckoutModal);

    // 10C. Handle Form Submission to Provider Workspace Integration
    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const curPlan = PLANS.find(p => p.id === activePlanId) || PLANS[0];
        const pcpName = document.getElementById('pcpName')?.value || '';
        const practiceName = document.getElementById('practiceName')?.value || '';
        const pcpAddress = document.getElementById('pcpAddress')?.value || '';
        const pcpPhone = document.getElementById('pcpPhone')?.value || '';
        const patientName = document.getElementById('patientName')?.value || '';
        const patientDob = document.getElementById('patientDob')?.value || '';
        const patientAddress = document.getElementById('patientAddress')?.value || '';
        const patientPhone = document.getElementById('patientPhone')?.value || '';
        const memberId = document.getElementById('memberId')?.value || '';
        const patientReason = document.getElementById('patientReason')?.value || '';

        const requestParams = {
          patient_name: patientName,
          patient_dob: patientDob,
          patient_phone: patientPhone,
          patient_address: patientAddress,
          insurer_id: curPlan.insurer_id,
          plan_id: curPlan.id,
          plan_year: curPlan.plan_year || 2026,
          insurance_member_id: memberId,
          pcp_name: pcpName,
          practice_name: practiceName,
          provider_phone: pcpPhone,
          provider_address: pcpAddress,
          target_type: 'PRODUCT',
          target_id: callSlip.length > 0 ? callSlip[0].sku : 'P-VIT-D',
          requested_item_name: callSlip.length > 0 ? callSlip.map(i => i.name).join(', ') : 'Marketplace Health Benefit Request',
          patient_reason: patientReason || 'Marketplace Benefit Request',
          consent_to_contact: true,
          non_guarantee_acknowledged: true
        };

        const newReq = createProviderRequest(requestParams);
        alert(`🚀 Success! Your request (${newReq.request_id}) has been pre-formatted and delivered to ${practiceName} for ${pcpName} to review.`);
        closeCheckoutModal();
      });
    }
  });
"""

if 'STATE-FIRST HIERARCHY' not in js_code:
    js_code += '\n\n' + checkout_logic_js
    with open('dist/marketplace/marketplace.js', 'w', encoding='utf-8') as f:
        f.write(js_code)
    print("Appended State-First & Review Checkout Modal JS to marketplace.js successfully!")
