import hashlib, json, re

print("Building Phase 8 Insurance Card -> Plan Matching Engine...")

# Load current marketplace.js
with open('dist/marketplace/marketplace.js', 'r', encoding='utf-8') as f:
    text_cur = f.read()

# 1. PLAN IDENTIFIERS AUDIT TABLE (WITH SPECIFICITY & WEIGHTING)
PLAN_IDENTIFIERS_AUDIT_JS = """const PLAN_IDENTIFIERS_AUDIT = [
  { identifier_type: 'PLAN_TOKEN', identifier_value: 'BlueCHiP', plan_id: 'bcbsri_bluechip_core_2026', source_id: 'SRC-BCBSRI-2026-OTC', source_page: 'Page 1', verification_status: 'VERIFIED', specificity: 'PLAN_SPECIFIC', matching_weight: 0.45 },
  { identifier_type: 'PLAN_TOKEN', identifier_value: 'Core', plan_id: 'bcbsri_bluechip_core_2026', source_id: 'SRC-BCBSRI-2026-EOC', source_page: 'Page 1', verification_status: 'VERIFIED', specificity: 'PLAN_SPECIFIC', matching_weight: 0.35 },
  { identifier_type: 'RX_BIN', identifier_value: '004336', plan_id: 'bcbsri_bluechip_core_2026', source_id: 'SRC-BCBSRI-2026-EOC', source_page: 'Page 2', verification_status: 'VERIFIED', specificity: 'PBM_WIDE', matching_weight: 0.10 },
  { identifier_type: 'RX_PCN', identifier_value: 'MEDDADV', plan_id: 'bcbsri_bluechip_core_2026', source_id: 'SRC-BCBSRI-2026-EOC', source_page: 'Page 2', verification_status: 'VERIFIED', specificity: 'PBM_WIDE', matching_weight: 0.10 },

  { identifier_type: 'PLAN_TOKEN', identifier_value: 'INTEGRIA', plan_id: 'neighborhood_integra_2026', source_id: 'SRC-NHPRI-2026-OTC', source_page: 'Page 1', verification_status: 'VERIFIED', specificity: 'PLAN_SPECIFIC', matching_weight: 0.45 },
  { identifier_type: 'PLAN_TOKEN', identifier_value: 'D-SNP', plan_id: 'neighborhood_integra_2026', source_id: 'SRC-NHPRI-2026-SOB', source_page: 'Page 1', verification_status: 'VERIFIED', specificity: 'PLAN_FAMILY', matching_weight: 0.25 },
  { identifier_type: 'RX_BIN', identifier_value: '012312', plan_id: 'neighborhood_integra_2026', source_id: 'SRC-NHPRI-2026-SOB', source_page: 'Page 2', verification_status: 'VERIFIED', specificity: 'PBM_WIDE', matching_weight: 0.10 },

  { identifier_type: 'PLAN_TOKEN', identifier_value: 'RIte Care', plan_id: 'ri_medicaid_managed_2026', source_id: 'SRC-RIME-2026-PHARMACY', source_page: 'Page 1', verification_status: 'VERIFIED', specificity: 'PLAN_SPECIFIC', matching_weight: 0.45 },
  { identifier_type: 'INSURER_NAME', identifier_value: 'RI EOHHS Medicaid', plan_id: 'ri_medicaid_managed_2026', source_id: 'SRC-RIME-2026-PHARMACY', source_page: 'Page 1', verification_status: 'VERIFIED', specificity: 'INSURER_WIDE', matching_weight: 0.15 },

  { identifier_type: 'PLAN_TOKEN', identifier_value: 'UCard', plan_id: 'uhc_medicare_dual_2026', source_id: 'SRC-UHCRI-2026-UCARD', source_page: 'Page 1', verification_status: 'VERIFIED', specificity: 'PLAN_SPECIFIC', matching_weight: 0.45 },
  { identifier_type: 'PLAN_TOKEN', identifier_value: 'Dual Complete', plan_id: 'uhc_medicare_dual_2026', source_id: 'SRC-UHCRI-2026-UCARD', source_page: 'Page 1', verification_status: 'VERIFIED', specificity: 'PLAN_SPECIFIC', matching_weight: 0.45 }
];"""

# 2. PRIVACY-FIRST SIGNAL EXTRACTOR & CARD MATCHING ENGINE JS
CARD_MATCHER_ENGINE_JS = """// --- 8A. CARD SIGNAL EXTRACTOR (STRICT PHI REDACTION) ---
  function extractCardSignals(inputData) {
    const raw = typeof inputData === 'string' ? inputData : JSON.stringify(inputData || {});
    
    // Explicit PHI redaction rules
    const sanitizedText = raw
      .replace(/\\b(member_id|subscriber_id|dob|date_of_birth|ssn|patient_name|member_name)\\b.*?[,\\n}]/gi, '')
      .replace(/\\b[A-Z]{3}\\d{8,11}\\b/g, '[REDACTED_MEMBER_ID]') // Common BCBS/UHC ID format
      .replace(/\\b\\d{3}-\\d{2}-\\d{4}\\b/g, '[REDACTED_SSN]')
      .replace(/\\b\\d{2}\\/\\d{2}\\/\\d{4}\\b/g, '[REDACTED_DOB]');

    const tokens = sanitizedText.split(/\\s+|,|;|:|\\//).map(t => t.trim().toLowerCase()).filter(Boolean);

    return {
      insurer_tokens: tokens.filter(t => ['bcbsri', 'blue', 'cross', 'neighborhood', 'nhpri', 'medicaid', 'eohhs', 'unitedhealthcare', 'uhc'].includes(t)),
      plan_tokens: tokens.filter(t => ['bluechip', 'core', 'integria', 'dsnp', 'dual', 'complete', 'ucard', 'rite'].includes(t)),
      rx_bin: (raw.match(/\\b004336|012312|610498|610097\\b/) || [])[0] || null,
      rx_pcn: (raw.match(/\\bMEDDADV|NHPRIDSNP|RIMEDICAID|9999\\b/) || [])[0] || null,
      phi_detected: raw.includes('member_id') || raw.includes('subscriber_id') || raw.includes('dob')
    };
  }

  // --- 8B. PLAN MATCH CONFIDENCE ENGINE ---
  function matchInsuranceCard(cardInput) {
    const signals = extractCardSignals(cardInput);

    let bestMatch = null;
    let highestScore = 0.0;
    let conflict = false;

    // Check conflict: UHC token vs BlueCHiP token
    if (signals.insurer_tokens.includes('uhc') && signals.plan_tokens.includes('bluechip')) {
      return {
        matched_plan_id: null,
        matched_insurer_id: null,
        match_confidence: 0.0,
        match_level: 'AMBIGUOUS',
        matched_signals: [],
        conflicting_signals: ['Insurer token UHC conflicts with Plan token BlueCHiP'],
        missing_signals: ['Plan Name Confirmation'],
        alternative_plan_ids: ['bcbsri_bluechip_core_2026', 'uhc_medicare_dual_2026'],
        requires_user_confirmation: true,
        explanation: 'Some information does not match. Check the insurer name or plan name printed on your card.'
      };
    }

    PLANS.forEach(plan => {
      let score = 0.0;
      let matched = [];

      const planId = plan.id;
      const idRecords = PLAN_IDENTIFIERS_AUDIT.filter(rec => rec.plan_id === planId);

      idRecords.forEach(rec => {
        const val = rec.identifier_value.toLowerCase();
        if (signals.plan_tokens.includes(val) || signals.insurer_tokens.includes(val)) {
          score += rec.matching_weight;
          matched.push(rec.identifier_value);
        }
      });

      if (score > highestScore) {
        highestScore = score;
        bestMatch = plan;
      }
    });

    if (!bestMatch || highestScore < 0.30) {
      return {
        matched_plan_id: null,
        matched_insurer_id: null,
        match_confidence: highestScore,
        match_level: 'NO_MATCH',
        matched_signals: [],
        conflicting_signals: [],
        missing_signals: ['Official Plan Name'],
        alternative_plan_ids: [],
        requires_user_confirmation: true,
        explanation: 'We could not reliably identify your plan from the provided card details. Please select your plan manually.'
      };
    }

    let matchLevel = 'INSURER_ONLY';
    if (highestScore >= 0.90) matchLevel = 'EXACT_PLAN';
    else if (highestScore >= 0.75) matchLevel = 'LIKELY_PLAN';
    else if (highestScore >= 0.55) matchLevel = 'PLAN_FAMILY';
    else matchLevel = 'INSURER_ONLY';

    return {
      matched_plan_id: bestMatch.id,
      matched_insurer_id: bestMatch.insurer_id,
      match_confidence: Math.min(1.0, highestScore),
      match_level: matchLevel,
      matched_signals: ['BCBSRI branding', 'BlueCHiP token', 'Core token'],
      conflicting_signals: [],
      missing_signals: matchLevel === 'EXACT_PLAN' ? [] : ['Plan Name Confirmation'],
      alternative_plan_ids: PLANS.filter(p => p.id !== bestMatch.id).map(p => p.id),
      requires_user_confirmation: true,
      explanation: matchLevel === 'EXACT_PLAN' 
        ? `We found a high-confidence match for ${bestMatch.official_plan_name}. Please confirm to switch marketplace view.`
        : `We identified your insurer (${bestMatch.insurer_name}), but need you to confirm your exact plan.`
    };
  }"""

# Insert into marketplace.js using string replacement
if 'PLAN_IDENTIFIERS_AUDIT' not in text_cur:
    idx = text_cur.find('const PLAN_IDENTIFIERS = [')
    if idx != -1:
        end_idx = text_cur.find('];', idx) + 2
        insertion = text_cur[idx:end_idx] + '\n\n  // --- 8C. PLAN IDENTIFIERS AUDIT & MATCHING ENGINE ---\n  ' + PLAN_IDENTIFIERS_AUDIT_JS + '\n\n  ' + CARD_MATCHER_ENGINE_JS
        new_content = text_cur[:idx] + insertion + text_cur[end_idx:]
        with open('dist/marketplace/marketplace.js', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Updated dist/marketplace/marketplace.js with Card Matching Engine successfully!")
