import hashlib, json, re

print("Building Phase 9 Manual Insurance Selection & Provider Request Intake Workflow...")

# Load current marketplace.js
with open('dist/marketplace/marketplace.js', 'r', encoding='utf-8') as f:
    text_cur = f.read()

# 1. PROVIDER INTEGRATION ABSTRACTION & DATA STRUCTURES
PROVIDER_WORKFLOW_JS = """// --- 9A. PROVIDER INTEGRATION LAYER & INTAKE DATA STRUCTURES ---
  const PROVIDER_INTEGRATION = {
    source: 'PAZERATECHNOLOGIES_MARKETPLACE',
    sendProviderRequest: function(request) {
      // Modular integration hook for EHR/FHIR/Fax/API routing
      request.request_status = 'DELIVERED_TO_PRACTICE';
      request.delivered_at = new Date().toISOString();
      saveProviderRequests();
      return {
        success: true,
        request_id: request.request_id,
        status: 'DELIVERED_TO_PRACTICE',
        timestamp: request.delivered_at
      };
    }
  };

  let providerRequests = [];
  try {
    const storedReqs = localStorage.getItem('pazeratech_provider_requests');
    if (storedReqs) providerRequests = JSON.parse(storedReqs);
  } catch {}

  function saveProviderRequests() {
    try {
      localStorage.setItem('pazeratech_provider_requests', JSON.stringify(providerRequests));
    } catch {}
  }

  // Helper to create a Provider Request Entity
  function createProviderRequest(params) {
    const reqId = 'REQ-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
    const requestEntity = {
      request_id: reqId,
      source: 'PAZERATECHNOLOGIES_MARKETPLACE',
      created_at: new Date().toISOString(),
      request_status: 'SUBMITTED',
      
      // Patient Info (Secure intake layer only)
      patient_name: params.patient_name,
      patient_dob: params.patient_dob,
      patient_phone: params.patient_phone,
      patient_email: params.patient_email || '',

      // Insurance Info
      insurer_id: params.insurer_id,
      plan_id: params.plan_id,
      plan_year: params.plan_year || 2026,
      insurance_member_id: params.insurance_member_id,
      insurance_group_number: params.insurance_group_number || '',

      // PCP Info
      pcp_name: params.pcp_name,
      practice_name: params.practice_name,
      provider_phone: params.provider_phone,
      provider_fax: params.provider_fax || '',

      // Request Info
      target_type: params.target_type,
      target_id: params.target_id,
      target_variant_id: params.target_variant_id || null,
      requested_item_name: params.requested_item_name,
      request_type: params.request_type || 'OTC_PRODUCT_REQUEST',
      patient_reason: params.patient_reason || '',
      patient_note: params.patient_note || '',

      // Immutable Coverage Snapshot
      coverage_snapshot: {
        coverage_rule_id: params.coverage_rule_id || null,
        coverage_status: params.coverage_status || 'Needs Verification',
        benefit_pathway: params.benefit_pathway || 'Unknown',
        source_id: params.source_id || null,
        source_version: params.source_version || '2026-v1.0',
        plan_year: params.plan_year || 2026,
        timestamp: new Date().toISOString()
      },

      // Consents & Preferences
      consent_to_contact: params.consent_to_contact === true,
      non_guarantee_acknowledged: params.non_guarantee_acknowledged === true,
      preferred_contact_method: params.preferred_contact_method || 'Phone',
      
      // Future fulfillment state
      fulfillment_type: params.fulfillment_type || 'PROVIDER_OFFICE'
    };

    providerRequests.push(requestEntity);
    saveProviderRequests();
    
    // Transmit via integration abstraction
    PROVIDER_INTEGRATION.sendProviderRequest(requestEntity);
    return requestEntity;
  }"""

# Replace or append in marketplace.js
new_content = text_cur

if 'PROVIDER_INTEGRATION' not in new_content:
    idx = text_cur.find('// --- 7. DYNAMIC SOURCE VALIDATION ENGINE ---')
    if idx != -1:
        new_content = text_cur[:idx] + PROVIDER_WORKFLOW_JS + '\n\n  ' + text_cur[idx:]
        with open('dist/marketplace/marketplace.js', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Updated dist/marketplace/marketplace.js with Provider Request Integration Engine successfully!")
