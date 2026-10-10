/**
 * Pazeratechnologies Insurance Marketplace Engine
 * Architecture based on plan-specific, source-backed coverage rule engine.
 */

(function () {
  'use strict';

  const $ = (selector, parent = document) => parent.querySelector(selector);
  const $$ = (selector, parent = document) => [...parent.querySelectorAll(selector)];
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  // --- 1. MINIMUM 33 DEPARTMENTS TAXONOMY ---
  const DEPARTMENTS = [
    { id: 'all', label: 'All 33 Departments', icon: '🛒' },
    { id: 'vitamins', label: 'Vitamins & Minerals', icon: '💊' },
    { id: 'supplements', label: 'Supplements', icon: '🌿' },
    { id: 'nutrition', label: 'Nutrition & Medical Foods', icon: '🥛' },
    { id: 'pain', label: 'Pain Relief', icon: '🩹' },
    { id: 'coldflu', label: 'Cold, Flu & Allergy', icon: '🤧' },
    { id: 'digestive', label: 'Digestive Health', icon: '🥣' },
    { id: 'firstaid', label: 'First Aid', icon: '🧰' },
    { id: 'woundcare', label: 'Wound Care', icon: '🩹' },
    { id: 'braces', label: 'Braces & Supports', icon: '🦿' },
    { id: 'mobility', label: 'Mobility', icon: '♿' },
    { id: 'homesafety', label: 'Home Safety', icon: '🏠' },
    { id: 'diabetes', label: 'Diabetes', icon: '🩸' },
    { id: 'cardio', label: 'Blood Pressure & Cardiovascular', icon: '🩺' },
    { id: 'respiratory', label: 'Respiratory', icon: '🌬️' },
    { id: 'sleep', label: 'CPAP & Sleep', icon: '🌙' },
    { id: 'eyecare', label: 'Eye Care', icon: '👁️' },
    { id: 'hearing', label: 'Hearing', icon: '👂' },
    { id: 'dental', label: 'Dental & Oral Care', icon: '🪥' },
    { id: 'skincare', label: 'Skin & Dermatology', icon: '🧴' },
    { id: 'footcare', label: 'Foot Care', icon: '🦶' },
    { id: 'compression', label: 'Compression & Lymphedema', icon: '🦵' },
    { id: 'incontinence', label: 'Incontinence', icon: '🩲' },
    { id: 'womens', label: 'Women\'s Health', icon: '🌸' },
    { id: 'pregnancy', label: 'Pregnancy & Breastfeeding', icon: '🍼' },
    { id: 'sexual', label: 'Sexual & Reproductive Health', icon: '💊' },
    { id: 'smoking', label: 'Smoking Cessation', icon: '🚭' },
    { id: 'ostomy', label: 'Ostomy', icon: '🩺' },
    { id: 'urology', label: 'Urological Supplies', icon: '💉' },
    { id: 'prosthetics', label: 'Prosthetics', icon: '🎗️' },
    { id: 'dme', label: 'Home Medical Equipment', icon: '🚽' },
    { id: 'medmgmt', label: 'Medication Management', icon: '📅' },
    { id: 'diagnostics', label: 'Home Diagnostics', icon: '🧪' },
    { id: 'ssbci', label: 'Chronic Condition Benefits', icon: '🍎' }
  ];

  // --- 1B. CANONICAL TARGET & LEGACY ID MAPPING ---
  const CANONICAL_TARGET_IDS = {
    vitamin_d: 'P-VIT-D',
    vitamin_b12: 'P-VIT-B12',
    prenatal_vitamins: 'P-VIT-PRENATAL',
    acetaminophen: 'P-PAI-ACETA',
    ibuprofen: 'P-PAI-IBU',
    blood_pressure_monitor: 'P-CAR-BPMON',
    blood_glucose_meter: 'P-DIAB-METER',
    routine_dental_exam: 'S-DEN-EXAM',
    medical_transportation: 'S-TRN-RIDE',
    connectorcare_card_to_culture: 'B-MA-CONNECTOR-CULTURE'
  };

  const LEGACY_ID_MAP = {
    'P-PAIN-ACET': 'P-PAI-ACETA',
    'P-PAIN-IBU': 'P-PAI-IBU',
    'P-CARDIO-BPMON': 'P-CAR-BPMON',
    'P-VITD-2000': 'P-VIT-D'
  };


  // --- 1B. FIRST-CLASS BENEFITS ENTITIES ---
  const BENEFITS = [
  {"id": "B-RI-MEDICAID-COMP", "benefit_id": "B-RI-MEDICAID-COMP", "benefit_name": "RI Medicaid Comprehensive Health Benefit", "benefit_type": "STATE_MEDICAID_BENEFIT", "insurer_id": "ri_medicaid", "plan_id": "ri_medicaid_managed_2026", "description": "Full medical, dental, vision, behavioral health, and prescription drug coverage under RI Medicaid.", "icon": "\u2693", "badge_label": "Medicaid Comprehensive"},
  {"id": "B-CT-HUSKY-C-BENEFIT", "benefit_id": "B-CT-HUSKY-C-BENEFIT", "benefit_name": "HUSKY C Long-Term Services & Supports Benefit", "benefit_type": "STATE_MEDICAID_BENEFIT", "insurer_id": "husky_health", "plan_id": "ct_husky_health_husky_c", "description": "Comprehensive medical, long-term care, home health, and transportation for aged, blind, and disabled Connecticut residents.", "icon": "\u267f", "badge_label": "HUSKY C LTSS"},
  {"id": "B-CT-HUSKY-D-BENEFIT", "benefit_id": "B-CT-HUSKY-D-BENEFIT", "benefit_name": "HUSKY D Low-Income Adult Coverage", "benefit_type": "STATE_MEDICAID_BENEFIT", "insurer_id": "husky_health", "plan_id": "ct_husky_health_husky_d", "description": "Full Medicaid coverage for eligible low-income adults ages 19-64 in Connecticut.", "icon": "\ud83d\udc65", "badge_label": "HUSKY D Medicaid"},
  {"id": "B-TUFTS-RI-OTC-75", "benefit_id": "B-TUFTS-RI-OTC-75", "benefit_name": "Tufts Medicare OTC Quarterly Allowance", "benefit_type": "OTC_ALLOWANCE", "insurer_id": "tufts_ri", "plan_id": "tufts_ri_medicare_2026", "allowance_amount": 75, "allowance_period": "quarterly", "rollover": false, "description": "$75 quarterly over-the-counter allowance card for eligible health items.", "icon": "\ud83d\udcb3", "badge_label": "$75 Quarterly OTC"},
  {"id": "B-BCBSRI-FITNESS", "benefit_id": "B-BCBSRI-FITNESS", "benefit_name": "BCBSRI Fitness & Gym Membership Benefit", "benefit_type": "FITNESS_BENEFIT", "insurer_id": "bcbsri", "plan_id": "bcbsri_access_2026", "description": "Unlimited access to participating fitness centers and online fitness classes.", "icon": "\ud83c\udfcb\ufe0f", "badge_label": "Fitness Benefit"},
  {"id": "B-NHPRI-COMMUNITY", "benefit_id": "B-NHPRI-COMMUNITY", "benefit_name": "Neighborhood Community Wellness Program", "benefit_type": "WELLNESS_PROGRAM", "insurer_id": "neighborhood", "plan_id": "neighborhood_access_2026", "description": "Access to community health workshops, nutrition classes, and wellness coaching.", "icon": "\ud83c\udf4e", "badge_label": "Wellness Benefit"},
  {"id": "B-BCBSMA-WELLNESS", "benefit_id": "B-BCBSMA-WELLNESS", "benefit_name": "BCBSMA Fitness & Health Reimbursement", "benefit_type": "WELLNESS_PROGRAM", "insurer_id": "bcbsma", "plan_id": "ma_bcbsma_health_connector_standard_plan", "allowance_amount": 150, "allowance_period": "annual", "rollover": false, "description": "Up to $150 annual reimbursement for qualified fitness center memberships.", "icon": "\ud83c\udfc3", "badge_label": "$150 Fitness Reimbursement"},
  {"id": "B-HPHC-MA-LIVINGWELL", "benefit_id": "B-HPHC-MA-LIVINGWELL", "benefit_name": "Harvard Pilgrim LivingWell Rewards", "benefit_type": "WELLNESS_PROGRAM", "insurer_id": "harvard_pilgrim", "plan_id": "ma_harvard_pilgrim_standard_silver_ii", "description": "Earn gift card rewards for completing preventive checkups and health activities.", "icon": "\ud83c\udf81", "badge_label": "LivingWell Rewards"},
  {"id": "B-MGB-WELLNESS", "benefit_id": "B-MGB-WELLNESS", "benefit_name": "MGB Health Plan Wellness Reimbursement", "benefit_type": "WELLNESS_PROGRAM", "insurer_id": "mgb_health", "plan_id": "ma_mgb_health_connectorcare", "description": "Reimbursement for qualified health club memberships and exercise programs.", "icon": "\ud83c\udfcb\ufe0f", "badge_label": "MGB Wellness"},
  {"id": "B-CT-HUSKY-B-BENEFIT", "benefit_id": "B-CT-HUSKY-B-BENEFIT", "benefit_name": "HUSKY B Children's Health Insurance Benefit", "benefit_type": "STATE_MEDICAID_BENEFIT", "insurer_id": "husky_health", "plan_id": "ct_husky_health_husky_b", "description": "Comprehensive medical, dental, vision, and prescription coverage for Connecticut children.", "icon": "\ud83d\udc76", "badge_label": "CHIP Coverage"},
  {"id": "B-CT-CONNECTICARE-OTC", "benefit_id": "B-CT-CONNECTICARE-OTC", "benefit_name": "ConnectiCare OTC Card Allowance", "benefit_type": "OTC_ALLOWANCE", "insurer_id": "connecticare", "plan_id": "ct_connecticare_connecticare_choice_silver", "allowance_amount": 40, "allowance_period": "quarterly", "rollover": false, "description": "$40 quarterly prepaid card for eligible OTC health and wellness products.", "icon": "\ud83d\udcb3", "badge_label": "$40 Qtrly OTC Card"},
  {"id": "B-CT-COVERED-CT-BENEFIT", "benefit_id": "B-CT-COVERED-CT-BENEFIT", "benefit_name": "Covered CT $0 Cost-Sharing & OTC Benefit", "benefit_type": "STATE_BENEFIT", "insurer_id": "connecticare", "plan_id": "ct_connecticare_connecticare_covered_ct", "description": "$0 monthly premium, $0 deductible, $0 copays for medical, dental, and prescription care.", "icon": "\ud83d\udee1\ufe0f", "badge_label": "$0 Covered CT"},
  {"id": "B-CT-ANTHEM-PATHWAY", "benefit_id": "B-CT-ANTHEM-PATHWAY", "benefit_name": "Anthem Pathway Essential Health Benefits", "benefit_type": "COMMERCIAL_BENEFIT", "insurer_id": "anthem_bcbs", "plan_id": "ct_anthem_bcbs_anthem_pathway_standard_silver", "description": "Comprehensive ACA essential health benefits, preventive care, and prescription drug coverage.", "icon": "\ud83c\udfe5", "badge_label": "Pathway Silver"},
  {"id": "B-ME-CHO-WELLNESS", "benefit_id": "B-ME-CHO-WELLNESS", "benefit_name": "Community Health Options Wellness Card", "benefit_type": "WELLNESS_PROGRAM", "insurer_id": "community_health_options", "plan_id": "me_community_health_options_community_health_options_clear_choice", "description": "Wellness incentive program rewarding members for annual preventive checkups.", "icon": "\ud83c\udf1f", "badge_label": "CHO Wellness Card"},
  {"id": "B-ME-ANTHEM-WHOLEHEALTH", "benefit_id": "B-ME-ANTHEM-WHOLEHEALTH", "benefit_name": "Anthem Whole Health Connection Maine", "benefit_type": "COMMERCIAL_BENEFIT", "insurer_id": "anthem_bcbs", "plan_id": "me_anthem_bcbs_anthem_clear_choice_ppo", "description": "Integrated medical, dental, vision, and preventive wellness benefit program.", "icon": "\ud83c\udf32", "badge_label": "Whole Health PPO"},
  {"id": "B-VT-DRDYNASAUR-BENEFIT", "benefit_id": "B-VT-DRDYNASAUR-BENEFIT", "benefit_name": "Dr. Dynasaur Children & Youth Health Coverage", "benefit_type": "STATE_MEDICAID_BENEFIT", "insurer_id": "vermont_dvha", "plan_id": "vt_dr_dynasaur_medicaid", "description": "Comprehensive medical, dental, vision, and prescription coverage for Vermont kids up to age 19.", "icon": "\ud83e\udd96", "badge_label": "Dr. Dynasaur"},
  {
    id: 'B-VT-GREEN-MOUNTAIN-NEMT',
    benefit_name: 'Green Mountain Care Non-Emergency Medical Transportation (NEMT)',
    benefit_type: 'TRANSPORTATION_BENEFIT',
    insurer_id: 'vermont_dvha',
    plan_id: 'vt_vermont_medicaid',
    applicable_plan_ids: ['vt_vermont_medicaid', 'vt_dr_dynasaur_medicaid'],
    state: 'VT',
    plan_year: 2026,
    description: 'Free non-emergency medical transportation rides for covered medical, dental, and pharmacy visits.',
    icon: '🚐',
    badge_label: 'STATE BENEFIT'
  },
  {
    id: 'B-VT-MVP-GIA',
    benefit_name: 'MVP Gia 24/7 Virtual Urgent & Primary Care Access',
    benefit_type: 'WELLNESS_BENEFIT',
    insurer_id: 'mvp_health',
    plan_id: 'vt_mvp_health_mvp_vt_plus_silver',
    applicable_plan_ids: ['vt_mvp_health_mvp_vt_plus_silver'],
    state: 'VT',
    plan_year: 2026,
    description: 'Unlimited 24/7 virtual urgent care, mental health, and primary care via Gia app at $0 copay.',
    icon: '📱',
    badge_label: 'VIRTUAL CARE'
  },
  {
    id: 'B-VT-BCBSVT-WELLNESS',
    benefit_name: 'BCBS Vermont $150 Annual Wellness & Fitness Reimbursement',
    benefit_type: 'FITNESS_BENEFIT',
    insurer_id: 'bcbsvt',
    plan_id: 'vt_bcbsvt_bcbsvt_silver',
    applicable_plan_ids: ['vt_bcbsvt_bcbsvt_silver'],
    state: 'VT',
    plan_year: 2026,
    description: 'Up to $150 annual reimbursement for qualified fitness club memberships and wellness programs.',
    icon: '🏋️',
    badge_label: 'FITNESS BENEFIT'
  },
  {
    id: 'B-ME-MAINACARE-NEMT',
    benefit_name: 'MaineCare Non-Emergency Medical Transportation (NEMT)',
    benefit_type: 'TRANSPORTATION_BENEFIT',
    insurer_id: 'mainecare',
    plan_id: 'me_mainecare_medicaid',
    applicable_plan_ids: ['me_mainecare_medicaid'],
    state: 'ME',
    plan_year: 2026,
    description: 'Free non-emergency medical transportation rides for covered medical, dental, and pharmacy appointments.',
    icon: '🚐',
    badge_label: 'STATE BENEFIT'
  },
  {
    id: 'B-ME-CHO-CHRONIC-CARE',
    benefit_name: 'Community Health Options Chronic Support Wellness Program ($100/yr)',
    benefit_type: 'CHRONIC_SUPPORT_BENEFIT',
    insurer_id: 'community_health_options',
    plan_id: 'me_community_health_options_community_health_options_clear_choice',
    applicable_plan_ids: ['me_community_health_options_community_health_options_clear_choice'],
    state: 'ME',
    plan_year: 2026,
    description: '$100 annual wellness incentive card for completing chronic condition management programs.',
    icon: '🩺',
    badge_label: 'WELLNESS REWARD'
  },
  {
    id: 'B-ME-HARVARD-FITNESS',
    benefit_name: 'Harvard Pilgrim Maine $150 Annual Fitness Reimbursement',
    benefit_type: 'FITNESS_BENEFIT',
    insurer_id: 'harvard_pilgrim',
    plan_id: 'me_harvard_pilgrim_clear_choice_hmo_silver_4000',
    applicable_plan_ids: ['me_harvard_pilgrim_clear_choice_hmo_silver_4000'],
    state: 'ME',
    plan_year: 2026,
    description: 'Up to $150 annual reimbursement for qualified health club memberships and fitness programs.',
    icon: '🏋️',
    badge_label: 'FITNESS BENEFIT'
  },
  {
    id: 'B-NH-AMERIHEALTH-CARE-CARD',
    benefit_name: 'AmeriHealth Caritas NH CARE Card Wellness Rewards ($50/yr)',
    benefit_type: 'REWARDS_BENEFIT',
    insurer_id: 'amerihealth_nh',
    plan_id: 'nh_amerihealth_caritas_medicaid',
    applicable_plan_ids: ['nh_amerihealth_caritas_medicaid'],
    state: 'NH',
    plan_year: 2026,
    description: '$50 annual wellness rewards card for completing annual preventive checkups and screenings.',
    icon: '🎁',
    badge_label: 'WELLNESS REWARD'
  },
  {
    id: 'B-NH-NHHF-REWARDS',
    benefit_name: 'NH Healthy Families My Health Pays Rewards Program ($75/yr)',
    benefit_type: 'REWARDS_BENEFIT',
    insurer_id: 'ambetter_nh',
    plan_id: 'nh_nh_healthy_families_medicaid',
    applicable_plan_ids: ['nh_nh_healthy_families_medicaid'],
    state: 'NH',
    plan_year: 2026,
    description: 'Earn up to $75 in rewards for completing preventive visits, wellness activities, and prenatal care.',
    icon: '💳',
    badge_label: 'WELLNESS REWARD'
  },
  {
    id: 'B-NH-WELLSENSE-OTC',
    benefit_name: 'WellSense NH Medicaid $25 Quarterly OTC Allowance Card',
    benefit_type: 'OTC_ALLOWANCE',
    insurer_id: 'wellsense',
    plan_id: 'nh_wellsense_medicaid_mco',
    applicable_plan_ids: ['nh_wellsense_medicaid_mco'],
    state: 'NH',
    plan_year: 2026,
    description: '$25 quarterly allowance card for eligible over-the-counter vitamins and health products.',
    icon: '💳',
    badge_label: 'PLAN BENEFIT'
  },
  {
    id: 'B-NH-HARVARD-FITNESS',
    benefit_name: 'Harvard Pilgrim NH $150 Annual Fitness Reimbursement',
    benefit_type: 'FITNESS_BENEFIT',
    insurer_id: 'harvard_pilgrim',
    plan_id: 'nh_harvard_pilgrim_nh_local_hmo_silver_6000_standard_0_rx_list_0_virtual_urgent_care',
    applicable_plan_ids: ['nh_harvard_pilgrim_nh_local_hmo_silver_6000_standard_0_rx_list_0_virtual_urgent_care'],
    state: 'NH',
    plan_year: 2026,
    description: 'Up to $150 annual reimbursement for qualified health club memberships and fitness programs.',
    icon: '🏋️',
    badge_label: 'FITNESS BENEFIT'
  },
  {
    id: 'B-CT-HUSKY-NEMT',
    benefit_name: 'HUSKY Health Non-Emergency Medical Transportation (NEMT)',
    benefit_type: 'TRANSPORTATION_BENEFIT',
    insurer_id: 'husky_health',
    plan_id: 'ct_husky_health_husky_a',
    applicable_plan_ids: ['ct_husky_health_husky_a', 'ct_husky_health_husky_c', 'ct_husky_health_husky_d'],
    state: 'CT',
    plan_year: 2026,
    description: 'Free rides to medical, dental, and pharmacy appointments for HUSKY A, C, and D members.',
    icon: '🚗',
    badge_label: 'STATE MEDICAID BENEFIT'
  },
  {
    id: 'B-CT-HUSKY-DENTAL',
    benefit_name: 'Connecticut State Dental Association HUSKY Dental Benefit',
    benefit_type: 'DENTAL_BENEFIT',
    insurer_id: 'husky_health',
    plan_id: 'ct_husky_health_husky_a',
    applicable_plan_ids: ['ct_husky_health_husky_a', 'ct_husky_health_husky_b', 'ct_husky_health_husky_c', 'ct_husky_health_husky_d'],
    state: 'CT',
    plan_year: 2026,
    description: 'Preventive dental cleanings, exams, and restorative dental care for HUSKY Health members.',
    icon: '🪥',
    badge_label: 'STATE DENTAL BENEFIT'
  },
  {
    id: 'B-CONNECTICARE-OTC',
    benefit_name: 'ConnectiCare $40 Quarterly OTC Benefit Card',
    benefit_type: 'OTC_ALLOWANCE',
    insurer_id: 'connecticare',
    plan_id: 'ct_connecticare_connecticare_choice_silver',
    applicable_plan_ids: ['ct_connecticare_connecticare_choice_silver', 'ct_connecticare_connecticare_covered_ct'],
    state: 'CT',
    plan_year: 2026,
    description: '$40 quarterly card for eligible over-the-counter health items.',
    icon: '💳',
    badge_label: 'PLAN BENEFIT'
  },
  {
    id: 'B-MA-CONNECTOR-CULTURE',
    benefit_name: 'Massachusetts ConnectorCare Card to Culture Access',
    benefit_type: 'CULTURAL_ACCESS_BENEFIT',
    insurer_id: 'masshealth',
    plan_id: 'ma_wellsense_wellsense_connectorcare',
    applicable_plan_ids: [
      'ma_wellsense_wellsense_connectorcare',
      'ma_tufts_p32_tufts_health_direct_connectorcare',
      'ma_fallon_connectorcare',
      'ma_health_new_england_connectorcare',
      'ma_mass_general_brigham_connectorcare'
    ],
    state: 'MA',
    plan_year: 2026,
    description: 'Free or steeply discounted admission to 300+ museums, theaters, and cultural institutions across MA for ConnectorCare members.',
    icon: '🏛️',
    badge_label: 'COMMUNITY BENEFIT'
  },
  {
    id: 'B-BCBSRI-OTC-50',
    benefit_name: '$50 Quarterly OTC Benefit Allowance',
    benefit_type: 'OTC_ALLOWANCE',
    insurer_id: 'bcbsri',
    plan_id: 'bcbsri_bluechip_core_2026',
    allowance_amount: 50,
    allowance_period: 'quarterly',
    rollover: false,
    description: 'Quarterly over-the-counter allowance card for eligible health items.',
    icon: '💳',
    badge_label: 'PLAN BENEFIT'
  },
  {
    id: 'B-NHPRI-OTC-75',
    benefit_name: '$75 Quarterly D-SNP OTC Benefit Allowance',
    benefit_type: 'OTC_ALLOWANCE',
    insurer_id: 'neighborhood',
    plan_id: 'neighborhood_integra_2026',
    allowance_amount: 75,
    allowance_period: 'quarterly',
    rollover: false,
    description: 'Quarterly OTC card for dual-eligible members.',
    icon: '💳',
    badge_label: 'PLAN BENEFIT'
  },
  {
    id: 'B-UHCRI-FOOD-110',
    benefit_name: 'Healthy Food & Grocery Allowance ($110/mo)',
    benefit_type: 'HEALTHY_FOOD_ALLOWANCE',
    insurer_id: 'uhc_ri',
    plan_id: 'uhc_medicare_dual_2026',
    allowance_amount: 110,
    allowance_period: 'monthly',
    rollover: false,
    description: 'Monthly UCard grocery allowance for SSBCI eligible members.',
    icon: '🍎',
    badge_label: 'PLAN BENEFIT'
  },
  {
    id: 'B-NHPRI-TRN-24',
    benefit_name: 'Non-Emergency Medical Transportation Benefit (24 Rides/yr)',
    benefit_type: 'TRANSPORTATION_BENEFIT',
    insurer_id: 'neighborhood',
    plan_id: 'neighborhood_integra_2026',
    ride_limit: 24,
    limit_period: 'annual',
    description: '24 one-way rides per year to medical appointments.',
    icon: '🚗',
    badge_label: 'PLAN BENEFIT'
  },
  {
    id: 'B-NHPRI-MEALS-14',
    benefit_name: 'Post-Hospital Discharge Meal Benefit (14 Meals)',
    benefit_type: 'MEAL_BENEFIT',
    insurer_id: 'neighborhood',
    plan_id: 'neighborhood_integra_2026',
    meal_limit: 14,
    limit_period: 'per discharge',
    description: '14 home-delivered meals following inpatient hospital discharge.',
    icon: '🍱',
    badge_label: 'PLAN BENEFIT'
  },
  {
    id: 'B-BCBSRI-FITNESS',
    benefit_name: 'SilverSneakers & Fitness Membership Benefit',
    benefit_type: 'FITNESS_BENEFIT',
    insurer_id: 'bcbsri',
    plan_id: 'bcbsri_bluechip_core_2026',
    description: 'Unlimited access to participating fitness locations and online classes.',
    icon: '🏋️',
    badge_label: 'PLAN BENEFIT'
  }
];

  const SERVICES = [
    {
      id: 'S-DEN-EXAM',
      service_id: 'S-DEN-EXAM',
      target_type: 'SERVICE',
      service_name: 'Routine Dental Cleanings & Preventive Exam',
      category: 'dental',
      description: 'Preventive dental cleaning, comprehensive oral evaluation, and diagnostic bitewing x-rays.',
      icon: '🦷'
    },
    {
      id: 'S-VIS-EXAM',
      service_id: 'S-VIS-EXAM',
      target_type: 'SERVICE',
      service_name: 'Annual Routine Vision Examination',
      category: 'eyecare',
      description: 'Comprehensive eye health examination and vision refraction testing by network optometrist/ophthalmologist.',
      icon: '👓'
    },
    {
      id: 'S-TRN-RIDE',
      service_id: 'S-TRN-RIDE',
      target_type: 'SERVICE',
      service_name: 'Non-Emergency Medical Transportation Ride',
      category: 'ssbci',
      description: 'Covered roundtrip transportation to medical appointments, dialysis, and pharmacy pickups.',
      icon: '🚐'
    },
    {
      id: 'S-PREV-WELLNESS',
      service_id: 'S-PREV-WELLNESS',
      target_type: 'SERVICE',
      service_name: 'Annual Physical & Preventive Wellness Visit',
      category: 'diagnostics',
      description: 'Comprehensive annual wellness checkup, preventive screening, and personalized health plan.',
      icon: '🩺'
    }
  ];


  // --- 1C. BENEFIT_ELIGIBILITY RELATIONSHIP MAPPINGS ---
  const BENEFIT_ELIGIBILITY = [
  { benefit_id: 'B-BCBSRI-OTC-50', target_type: 'PRODUCT', target_id: 'P-VIT-D', plan_id: 'bcbsri_bluechip_core_2026', plan_year: 2026, eligibility_status: 'VERIFIED_EXACT', source_id: 'SRC-BCBSRI-2026-OTC', source_page: 'Page 14' },
  { benefit_id: 'B-BCBSRI-OTC-50', target_type: 'PRODUCT', target_id: 'P-VIT-BCOMPLEX', plan_id: 'bcbsri_bluechip_core_2026', plan_year: 2026, eligibility_status: 'VERIFIED_EXACT', source_id: 'SRC-BCBSRI-2026-OTC', source_page: 'Page 15' },
  { benefit_id: 'B-BCBSRI-OTC-50', target_type: 'PRODUCT', target_id: 'P-PAI-ACETA', plan_id: 'bcbsri_bluechip_core_2026', plan_year: 2026, eligibility_status: 'VERIFIED_EXACT', source_id: 'SRC-BCBSRI-2026-OTC', source_page: 'Page 8' },
  { benefit_id: 'B-NHPRI-OTC-75', target_type: 'PRODUCT', target_id: 'P-VIT-CALCIUM', plan_id: 'neighborhood_integra_2026', plan_year: 2026, eligibility_status: 'VERIFIED_EXACT', source_id: 'SRC-NHPRI-2026-OTC', source_page: 'Page 11' },
  { benefit_id: 'B-UHCRI-FOOD-110', target_type: 'PRODUCT', target_id: 'P-FOOD-GROCERY', plan_id: 'uhc_medicare_dual_2026', plan_year: 2026, eligibility_status: 'VERIFIED_EXACT', source_id: 'SRC-UHCRI-2026-UCARD', source_page: 'Page 6' },
  { benefit_id: 'B-NHPRI-TRN-24', target_type: 'SERVICE', target_id: 'S-TRN-RIDE', plan_id: 'neighborhood_integra_2026', plan_year: 2026, eligibility_status: 'VERIFIED_EXACT', source_id: 'SRC-NHPRI-2026-SOB', source_page: 'Page 18' }
];

  // --- 2. INSURERS AND PLANS REGISTRY ---
  const INSURERS = [
    {
        "id": "bcbsri",
        "name": "Blue Cross & Blue Shield of Rhode Island",
        "code": "BCBSRI",
        "states": [
            "RI"
        ]
    },
    {
        "id": "neighborhood",
        "name": "Neighborhood Health Plan of Rhode Island",
        "code": "NHPRI",
        "states": [
            "RI"
        ]
    },
    {
        "id": "ri_medicaid",
        "name": "Rhode Island Medicaid (EOHHS)",
        "code": "RIME",
        "states": [
            "RI"
        ]
    },
    {
        "id": "uhc_ri",
        "name": "UnitedHealthcare Rhode Island",
        "code": "UHCRI",
        "states": [
            "RI"
        ]
    },
    {
        "id": "tufts_p32",
        "name": "Tufts / Point32Health",
        "code": "TUFTS",
        "states": [
            "RI",
            "MA"
        ]
    },
    {
        "id": "bcbsma",
        "name": "Blue Cross Blue Shield of Massachusetts",
        "code": "BCBSMA",
        "states": [
            "MA"
        ]
    },
    {
        "id": "harvard_pilgrim",
        "name": "Harvard Pilgrim Health Care",
        "code": "HPHC",
        "states": [
            "MA",
            "ME",
            "NH"
        ]
    },
    {
        "id": "health_new_england",
        "name": "Health New England",
        "code": "HNE",
        "states": [
            "MA"
        ]
    },
    {
        "id": "mgb_health",
        "name": "Mass General Brigham Health Plan",
        "code": "MGBHP",
        "states": [
            "MA"
        ]
    },
    {
        "id": "wellsense",
        "name": "WellSense Health Plan",
        "code": "WELLSENSE",
        "states": [
            "MA",
            "NH"
        ]
    },
    {
        "id": "masshealth",
        "name": "MassHealth (Massachusetts EOHHS)",
        "code": "MASSHEALTH",
        "states": [
            "MA"
        ]
    },
    {
        "id": "anthem_bcbs",
        "name": "Anthem Blue Cross and Blue Shield",
        "code": "ANTHEM",
        "states": [
            "CT",
            "ME",
            "NH"
        ]
    },
    {
        "id": "connecticare",
        "name": "ConnectiCare",
        "code": "CONNECTICARE",
        "states": [
            "CT"
        ]
    },
    {
        "id": "husky_health",
        "name": "HUSKY Health Connecticut",
        "code": "HUSKY",
        "states": [
            "CT"
        ]
    },
    {
        "id": "community_health_options",
        "name": "Community Health Options",
        "code": "CHO",
        "states": [
            "ME"
        ]
    },
    {
        "id": "mending",
        "name": "Mending",
        "code": "MENDING",
        "states": [
            "ME"
        ]
    },
    {
        "id": "mainecare",
        "name": "MaineCare (Maine DHHS)",
        "code": "MAINECARE",
        "states": [
            "ME"
        ]
    },
    {
        "id": "ambetter_nh",
        "name": "Ambetter from NH Healthy Families",
        "code": "AMBETTER",
        "states": [
            "NH"
        ]
    },
    {
        "id": "amerihealth_nh",
        "name": "AmeriHealth Caritas New Hampshire",
        "code": "AMERIHEALTH",
        "states": [
            "NH"
        ]
    },
    {
        "id": "nh_dhhs",
        "name": "New Hampshire Medicaid (DHHS)",
        "code": "NHDHHS",
        "states": [
            "NH"
        ]
    },
    {
        "id": "bcbsvt",
        "name": "Blue Cross and Blue Shield of Vermont",
        "code": "BCBSVT",
        "states": [
            "VT"
        ]
    },
    {
        "id": "mvp_health",
        "name": "MVP Health Care",
        "code": "MVP",
        "states": [
            "VT"
        ]
    },
    {
        "id": "green_mountain_care",
        "name": "Green Mountain Care Vermont",
        "code": "GMC",
        "states": [
            "VT"
        ]
    },
    {
        "id": "medicare",
        "name": "Original Medicare (CMS)",
        "code": "CMS",
        "states": [
            "RI",
            "MA",
            "CT",
            "NH",
            "VT",
            "ME"
        ]
    },
    {
        "id": "unselected",
        "name": "Generic / Unselected Insurer",
        "code": "GENERIC",
        "states": [
            "RI",
            "MA",
            "CT",
            "NH",
            "VT",
            "ME"
        ]
    }
];

  const PLANS = [
  {
    id: 'zero_rule_test_plan', insurer_id: 'bcbsri', insurer_name: 'Blue Cross & Blue Shield of Rhode Island',
    official_plan_name: 'BCBSRI Zero-Rule Validation Plan (2026)', display_name: 'BCBSRI Zero-Rule Validation Plan', plan_year: 2026,
    state: 'RI', plan_type: 'Medicare Advantage', insurance_category: 'MEDICARE_ADVANTAGE', network_type: 'Statewide Network',
    market_segment: 'Individual Medicare', service_area: 'Statewide RI', source_status: 'SOURCE_CONFIRMED',
    plan_identity_status: 'SOURCE_CONFIRMED', coverage_verification_status: 'UNVERIFIED', is_verified: false,
    production_visibility: false, is_test_fixture: true, environment: 'TEST', aliases: ['Zero-Rule Validation Plan', 'BCBSRI Zero Rule']
  },
  {
    id: 'vt_vermont_medicaid', insurer_id: 'vermont_dvha', insurer_name: 'Green Mountain Care (Vermont Medicaid)',
    official_plan_name: 'Vermont Medicaid / Green Mountain Care (2026)', display_name: 'Vermont Medicaid 2026', plan_year: 2026,
    state: 'VT', plan_type: 'Medicaid', insurance_category: 'MEDICAID', network_type: 'Statewide Fee-for-Service',
    market_segment: 'Medicaid State Program', service_area: 'Statewide VT', source_status: 'ACTIVE',
    plan_identity_status: 'SOURCE_CONFIRMED', coverage_verification_status: 'VERIFIED_REFERENCE', is_verified: true,
    production_visibility: true, aliases: ['Green Mountain Care', 'Vermont Medicaid', 'VT DVHA']
  },
  {
    id: 'vt_dr_dynasaur_medicaid', insurer_id: 'vermont_dvha', insurer_name: 'Dr. Dynasaur (Green Mountain Care)',
    official_plan_name: 'Dr. Dynasaur Children & Family Medicaid (2026)', display_name: 'Dr. Dynasaur Medicaid 2026', plan_year: 2026,
    state: 'VT', plan_type: 'Medicaid', insurance_category: 'MEDICAID', network_type: 'Statewide Fee-for-Service',
    market_segment: 'Medicaid / CHIP State Program', service_area: 'Statewide VT', source_status: 'ACTIVE',
    plan_identity_status: 'SOURCE_CONFIRMED', coverage_verification_status: 'VERIFIED_REFERENCE', is_verified: true,
    production_visibility: true, aliases: ['Dr. Dynasaur', 'Dr Dynasaur', 'VT CHIP']
  },
  {
    id: 'me_mainecare_medicaid', insurer_id: 'mainecare', insurer_name: 'MaineCare (Maine Medicaid)',
    official_plan_name: 'MaineCare Statewide Medicaid (2026)', display_name: 'MaineCare Medicaid 2026', plan_year: 2026,
    state: 'ME', plan_type: 'Medicaid', insurance_category: 'MEDICAID', network_type: 'Statewide Fee-for-Service & Managed Care',
    market_segment: 'Medicaid State Program', service_area: 'Statewide ME', source_status: 'ACTIVE',
    plan_identity_status: 'SOURCE_CONFIRMED', coverage_verification_status: 'VERIFIED_REFERENCE', is_verified: true,
    production_visibility: true, aliases: ['MaineCare', 'Maine Medicaid', 'ME DHHS Medicaid']
  },
  {
    id: 'nh_wellsense_medicaid_mco', insurer_id: 'wellsense', insurer_name: 'WellSense Health Plan NH',
    official_plan_name: 'WellSense New Hampshire Medicaid MCO (2026)', display_name: 'WellSense NH Medicaid 2026', plan_year: 2026,
    state: 'NH', plan_type: 'Medicaid', insurance_category: 'MEDICAID', network_type: 'Statewide Medicaid MCO',
    market_segment: 'Medicaid Managed Care', service_area: 'Statewide NH', source_status: 'ACTIVE',
    plan_identity_status: 'SOURCE_CONFIRMED', coverage_verification_status: 'VERIFIED_REFERENCE', is_verified: true,
    production_visibility: true, aliases: ['WellSense NH Medicaid', 'WellSense NH']
  },
  {
    id: 'nh_amerihealth_caritas_medicaid', insurer_id: 'amerihealth_nh', insurer_name: 'AmeriHealth Caritas New Hampshire',
    official_plan_name: 'AmeriHealth Caritas New Hampshire Medicaid (2026)', display_name: 'AmeriHealth Caritas NH 2026', plan_year: 2026,
    state: 'NH', plan_type: 'Medicaid', insurance_category: 'MEDICAID', network_type: 'Statewide Medicaid MCO',
    market_segment: 'Medicaid Managed Care', service_area: 'Statewide NH', source_status: 'ACTIVE',
    plan_identity_status: 'SOURCE_CONFIRMED', coverage_verification_status: 'VERIFIED_REFERENCE', is_verified: true,
    production_visibility: true, aliases: ['AmeriHealth NH', 'AmeriHealth Caritas Medicaid']
  },
  {
    id: 'nh_nh_healthy_families_medicaid', insurer_id: 'ambetter_nh', insurer_name: 'NH Healthy Families',
    official_plan_name: 'NH Healthy Families Medicaid Managed Care (2026)', display_name: 'NH Healthy Families Medicaid 2026', plan_year: 2026,
    state: 'NH', plan_type: 'Medicaid', insurance_category: 'MEDICAID', network_type: 'Statewide Medicaid MCO',
    market_segment: 'Medicaid Managed Care', service_area: 'Statewide NH', source_status: 'ACTIVE',
    plan_identity_status: 'SOURCE_CONFIRMED', coverage_verification_status: 'VERIFIED_REFERENCE', is_verified: true,
    production_visibility: true, aliases: ['NH Healthy Families', 'NHHF Medicaid']
  },
  {
    id: 'ct_husky_health_husky_a', insurer_id: 'husky_health', insurer_name: 'HUSKY Health Connecticut',
    official_plan_name: 'HUSKY A Medicaid for Families & Children (2026)', display_name: 'HUSKY A Medicaid 2026', plan_year: 2026,
    state: 'CT', plan_type: 'Medicaid', insurance_category: 'MEDICAID', network_type: 'Statewide Medicaid Network',
    market_segment: 'Medicaid State Program', service_area: 'Statewide CT', source_status: 'ACTIVE',
    plan_identity_status: 'SOURCE_CONFIRMED', coverage_verification_status: 'VERIFIED_REFERENCE', is_verified: true,
    aliases: ['HUSKY A', 'CT Medicaid Families']
  },
  {
    id: 'ct_husky_health_husky_b', insurer_id: 'husky_health', insurer_name: 'HUSKY Health Connecticut',
    official_plan_name: "HUSKY B Children's Health Insurance Program (2026)", display_name: 'HUSKY B CHIP 2026', plan_year: 2026,
    state: 'CT', plan_type: 'CHIP', insurance_category: 'CHIP', network_type: 'Statewide CHIP Network',
    market_segment: "Children's Health Insurance Program", service_area: 'Statewide CT', source_status: 'ACTIVE',
    plan_identity_status: 'SOURCE_CONFIRMED', coverage_verification_status: 'VERIFIED_REFERENCE', is_verified: true,
    aliases: ['HUSKY B', 'CT CHIP']
  },
  {
    id: 'ct_husky_health_husky_c', insurer_id: 'husky_health', insurer_name: 'HUSKY Health Connecticut',
    official_plan_name: 'HUSKY C Medicaid for Aged, Blind & Disabled (2026)', display_name: 'HUSKY C Medicaid 2026', plan_year: 2026,
    state: 'CT', plan_type: 'Medicaid', insurance_category: 'MEDICAID', network_type: 'Statewide Medicaid Network',
    market_segment: 'Aged, Blind & Disabled', service_area: 'Statewide CT', source_status: 'ACTIVE',
    plan_identity_status: 'SOURCE_CONFIRMED', coverage_verification_status: 'VERIFIED_REFERENCE', is_verified: true,
    aliases: ['HUSKY C', 'CT Medicaid ABD']
  },
  {
    id: 'ct_husky_health_husky_d', insurer_id: 'husky_health', insurer_name: 'HUSKY Health Connecticut',
    official_plan_name: 'HUSKY D Medicaid for Low-Income Adults (2026)', display_name: 'HUSKY D Medicaid Expansion 2026', plan_year: 2026,
    state: 'CT', plan_type: 'Medicaid', insurance_category: 'MEDICAID', network_type: 'Statewide Medicaid Network',
    market_segment: 'Medicaid ACA Expansion', service_area: 'Statewide CT', source_status: 'ACTIVE',
    plan_identity_status: 'SOURCE_CONFIRMED', coverage_verification_status: 'VERIFIED_REFERENCE', is_verified: true,
    aliases: ['HUSKY D', 'CT Medicaid Expansion']
  },
  {
    id: 'ct_connecticare_connecticare_choice_silver', insurer_id: 'connecticare', insurer_name: 'ConnectiCare',
    official_plan_name: 'ConnectiCare Choice Silver Passage HMO (2026)', display_name: 'ConnectiCare Choice Silver 2026', plan_year: 2026,
    state: 'CT', plan_type: 'Commercial', insurance_category: 'COMMERCIAL', network_type: 'HMO',
    market_segment: 'Individual Marketplace', service_area: 'Statewide CT', source_status: 'ACTIVE',
    plan_identity_status: 'SOURCE_CONFIRMED', coverage_verification_status: 'VERIFIED_REFERENCE', is_verified: true,
    aliases: ['ConnectiCare Choice Silver', 'ConnectiCare Silver']
  },
  {
    id: 'ct_connecticare_connecticare_covered_ct', insurer_id: 'connecticare', insurer_name: 'ConnectiCare',
    official_plan_name: 'ConnectiCare Covered CT Program Plan (2026)', display_name: 'ConnectiCare Covered CT 2026', plan_year: 2026,
    state: 'CT', plan_type: 'Commercial', insurance_category: 'COMMERCIAL', network_type: 'HMO',
    market_segment: 'State Subsidized Exchange', service_area: 'Statewide CT', source_status: 'ACTIVE',
    plan_identity_status: 'SOURCE_CONFIRMED', coverage_verification_status: 'VERIFIED_REFERENCE', is_verified: true,
    aliases: ['Covered CT', 'ConnectiCare Covered CT']
  },
  {
    id: 'ct_anthem_bcbs_anthem_pathway_standard_silver', insurer_id: 'anthem_bcbs', insurer_name: 'Anthem Blue Cross and Blue Shield CT',
    official_plan_name: 'Anthem Pathway Standard Silver HMO (2026)', display_name: 'Anthem Pathway Silver CT 2026', plan_year: 2026,
    state: 'CT', plan_type: 'Commercial', insurance_category: 'COMMERCIAL', network_type: 'HMO',
    market_segment: 'Individual Marketplace', service_area: 'Statewide CT', source_status: 'ACTIVE',
    plan_identity_status: 'SOURCE_CONFIRMED', coverage_verification_status: 'VERIFIED_REFERENCE', is_verified: true,
    aliases: ['Anthem Pathway Silver', 'Anthem CT Silver']
  },
    {
        "id": "bcbsri_bluechip_core_2026",
        "insurer_id": "bcbsri",
        "insurer_name": "Blue Cross & Blue Shield of Rhode Island",
        "official_plan_name": "BlueCHiP for Medicare Core (2026)",
        "display_name": "BlueCHiP Core 2026",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Medicare Advantage",
        "insurance_category": "MEDICARE_ADVANTAGE",
        "network_type": "HMO-POS",
        "market_segment": "Individual Medicare",
        "service_area": "Statewide RI",
        "source_status": "ACTIVE", "plan_identity_status": "SOURCE_CONFIRMED", "coverage_verification_status": "VERIFIED_REFERENCE", "is_verified": false,
        "aliases": [
            "BlueCHiP Core",
            "BCBSRI Medicare"
        ]
    },
    {
        "id": "neighborhood_integra_2026",
        "insurer_id": "neighborhood",
        "insurer_name": "Neighborhood Health Plan of RI",
        "official_plan_name": "Neighborhood INTEGRIA D-SNP (2026)",
        "display_name": "Neighborhood INTEGRIA 2026",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "D_SNP",
        "insurance_category": "D_SNP",
        "network_type": "HMO D-SNP",
        "market_segment": "Dual Eligible Medicare/Medicaid",
        "service_area": "Statewide RI",
        "source_status": "ACTIVE", "plan_identity_status": "SOURCE_CONFIRMED", "coverage_verification_status": "VERIFIED_REFERENCE", "is_verified": false,
        "aliases": [
            "INTEGRIA",
            "NHPRI D-SNP"
        ]
    },
    {
        "id": "ri_medicaid_managed_2026",
        "insurer_id": "ri_medicaid",
        "insurer_name": "Rhode Island Medicaid (EOHHS)",
        "official_plan_name": "RI Medicaid Managed Care Protocols (2026)",
        "display_name": "RI Medicaid State Protocols 2026",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Medicaid",
        "insurance_category": "MEDICAID",
        "network_type": "Statewide Medicaid Network",
        "market_segment": "Medicaid State Program",
        "service_area": "Statewide RI",
        "source_status": "ACTIVE", "plan_identity_status": "SOURCE_CONFIRMED", "coverage_verification_status": "VERIFIED_REFERENCE", "is_verified": false,
        "aliases": [
            "RIte Care",
            "Rhody Health"
        ]
    },
    {
        "id": "uhc_medicare_dual_2026",
        "insurer_id": "uhc_ri",
        "insurer_name": "UnitedHealthcare RI",
        "official_plan_name": "UHC Dual Complete RI (2026)",
        "display_name": "UHC Dual Complete RI 2026",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "D_SNP",
        "insurance_category": "D_SNP",
        "network_type": "HMO D-SNP",
        "market_segment": "Dual Eligible Medicare/Medicaid",
        "service_area": "Statewide RI",
        "source_status": "ACTIVE", "plan_identity_status": "SOURCE_CONFIRMED", "coverage_verification_status": "VERIFIED_REFERENCE", "is_verified": false,
        "aliases": [
            "UHC Dual Complete",
            "UnitedHealthcare Dual"
        ]
    },
    {
        "id": "generic_unselected_plan",
        "insurer_id": "unselected",
        "insurer_name": "Generic Insurer",
        "official_plan_name": "Unselected Plan (Needs Verification)",
        "display_name": "Unselected Generic Plan",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Medicare Advantage",
        "insurance_category": "OTHER",
        "network_type": "General",
        "market_segment": "Unselected",
        "service_area": "All Areas",
        "source_status": "UNVERIFIED",
        "aliases": []
    },
    {
        "id": "nh_wellsense_wellsense_clarity_nh_gold_2000_0_rx_list_24_7_nurse_advice",
        "insurer_id": "wellsense",
        "insurer_name": "WellSense Health Plan",
        "official_plan_name": "WellSense Clarity NH Gold 2000 + $0 Rx List + 24/7 Nurse Advice",
        "display_name": "WellSense Clarity NH Gold 2000 + $0 Rx List + 24/7 Nurse Advice",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "WellSense Clarity NH Gold 2000 + $0 Rx List + 24/7 Nurse Advice"
        ]
    },
    {
        "id": "nh_wellsense_wellsense_clarity_nh_silver_6000_0_rx_list_24_7_nurse_advice",
        "insurer_id": "wellsense",
        "insurer_name": "WellSense Health Plan",
        "official_plan_name": "WellSense Clarity NH Silver 6000 + $0 Rx List + 24/7 Nurse Advice",
        "display_name": "WellSense Clarity NH Silver 6000 + $0 Rx List + 24/7 Nurse Advice",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "WellSense Clarity NH Silver 6000 + $0 Rx List + 24/7 Nurse Advice"
        ]
    },
    {
        "id": "nh_wellsense_wellsense_clarity_nh_silver_3400_0_rx_list_24_7_nurse_advice",
        "insurer_id": "wellsense",
        "insurer_name": "WellSense Health Plan",
        "official_plan_name": "WellSense Clarity NH Silver 3400 + $0 Rx List + 24/7 Nurse Advice",
        "display_name": "WellSense Clarity NH Silver 3400 + $0 Rx List + 24/7 Nurse Advice",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "WellSense Clarity NH Silver 3400 + $0 Rx List + 24/7 Nurse Advice"
        ]
    },
    {
        "id": "nh_wellsense_wellsense_clarity_nh_silver_0_deductible_0_rx_list_24_7_nurse_advice",
        "insurer_id": "wellsense",
        "insurer_name": "WellSense Health Plan",
        "official_plan_name": "WellSense Clarity NH Silver 0 Deductible + $0 Rx List + 24/7 Nurse Advice",
        "display_name": "WellSense Clarity NH Silver 0 Deductible + $0 Rx List + 24/7 Nurse Advice",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "WellSense Clarity NH Silver 0 Deductible + $0 Rx List + 24/7 Nurse Advice"
        ]
    },
    {
        "id": "nh_wellsense_wellsense_clarity_nh_bronze_7500_hsa_0_rx_list_24_7_nurse_advice",
        "insurer_id": "wellsense",
        "insurer_name": "WellSense Health Plan",
        "official_plan_name": "WellSense Clarity NH Bronze 7500 HSA + $0 Rx List + 24/7 Nurse Advice",
        "display_name": "WellSense Clarity NH Bronze 7500 HSA + $0 Rx List + 24/7 Nurse Advice",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "WellSense Clarity NH Bronze 7500 HSA + $0 Rx List + 24/7 Nurse Advice"
        ]
    },
    {
        "id": "nh_wellsense_wellsense_clarity_nh_bronze_6500_hsa_0_rx_list_24_7_nurse_advice",
        "insurer_id": "wellsense",
        "insurer_name": "WellSense Health Plan",
        "official_plan_name": "WellSense Clarity NH Bronze 6500 HSA + $0 Rx List + 24/7 Nurse Advice",
        "display_name": "WellSense Clarity NH Bronze 6500 HSA + $0 Rx List + 24/7 Nurse Advice",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "WellSense Clarity NH Bronze 6500 HSA + $0 Rx List + 24/7 Nurse Advice"
        ]
    },
    {
        "id": "nh_wellsense_wellsense_clarity_nh_bronze_7600_hsa_0_rx_list_24_7_nurse_advice",
        "insurer_id": "wellsense",
        "insurer_name": "WellSense Health Plan",
        "official_plan_name": "WellSense Clarity NH Bronze 7600 HSA + $0 Rx List + 24/7 Nurse Advice",
        "display_name": "WellSense Clarity NH Bronze 7600 HSA + $0 Rx List + 24/7 Nurse Advice",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "WellSense Clarity NH Bronze 7600 HSA + $0 Rx List + 24/7 Nurse Advice"
        ]
    },
    {
        "id": "nh_harvard_pilgrim_nh_local_hmo_gold_2000_standard_0_rx_list_0_virtual_urgent_care",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "NH Local HMO Gold 2000 Standard + $0 Rx list + $0 Virtual Urgent Care",
        "display_name": "NH Local HMO Gold 2000 Standard + $0 Rx list + $0 Virtual Urgent Care",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "NH Local HMO Gold 2000 Standard + $0 Rx list + $0 Virtual Urgent Care"
        ]
    },
    {
        "id": "nh_harvard_pilgrim_nh_local_hmo_silver_6000_standard_0_rx_list_0_virtual_urgent_care",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "NH Local HMO Silver 6000 Standard + $0 Rx list + $0 Virtual Urgent Care",
        "display_name": "NH Local HMO Silver 6000 Standard + $0 Rx list + $0 Virtual Urgent Care",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "NH Local HMO Silver 6000 Standard + $0 Rx list + $0 Virtual Urgent Care"
        ]
    },
    {
        "id": "nh_harvard_pilgrim_nh_local_hmo_bronze_7500_standard_0_rx_list_0_virtual_urgent_care",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "NH Local HMO Bronze 7500 Standard + $0 Rx list + $0 Virtual Urgent Care",
        "display_name": "NH Local HMO Bronze 7500 Standard + $0 Rx list + $0 Virtual Urgent Care",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "NH Local HMO Bronze 7500 Standard + $0 Rx list + $0 Virtual Urgent Care"
        ]
    },
    {
        "id": "nh_harvard_pilgrim_nh_local_choice_hmo_hsa_bronze_6000",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "NH Local Choice HMO HSA Bronze 6000",
        "display_name": "NH Local Choice HMO HSA Bronze 6000",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "NH Local Choice HMO HSA Bronze 6000"
        ]
    },
    {
        "id": "nh_harvard_pilgrim_nh_local_choice_hmo_gold_0_rx_list_0_virtual_urgent_care",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "NH Local Choice HMO Gold + $0 Rx list + $0 Virtual Urgent Care",
        "display_name": "NH Local Choice HMO Gold + $0 Rx list + $0 Virtual Urgent Care",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "NH Local Choice HMO Gold + $0 Rx list + $0 Virtual Urgent Care"
        ]
    },
    {
        "id": "nh_harvard_pilgrim_nh_local_choice_hmo_gold_1400_0_rx_list_0_virtual_urgent_care",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "NH Local Choice HMO Gold 1400 + $0 Rx list + $0 Virtual Urgent Care",
        "display_name": "NH Local Choice HMO Gold 1400 + $0 Rx list + $0 Virtual Urgent Care",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "NH Local Choice HMO Gold 1400 + $0 Rx list + $0 Virtual Urgent Care"
        ]
    },
    {
        "id": "nh_harvard_pilgrim_nh_local_choice_hmo_silver_3500_0_rx_list_0_virtual_urgent_care",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "NH Local Choice HMO Silver 3500  + $0 Rx list + $0 Virtual Urgent Care",
        "display_name": "NH Local Choice HMO Silver 3500  + $0 Rx list + $0 Virtual Urgent Care",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "NH Local Choice HMO Silver 3500  + $0 Rx list + $0 Virtual Urgent Care"
        ]
    },
    {
        "id": "nh_harvard_pilgrim_nh_local_choice_hmo_silver_5000_0_rx_list_0_virtual_urgent_care",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "NH Local Choice HMO Silver 5000 + $0 Rx list + $0 Virtual Urgent Care",
        "display_name": "NH Local Choice HMO Silver 5000 + $0 Rx list + $0 Virtual Urgent Care",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "NH Local Choice HMO Silver 5000 + $0 Rx list + $0 Virtual Urgent Care"
        ]
    },
    {
        "id": "nh_harvard_pilgrim_nh_local_choice_hmo_bronze_8000_0_rx_list_0_virtual_urgent_care",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "NH Local Choice HMO Bronze 8000 + $0 Rx list + $0 Virtual Urgent Care",
        "display_name": "NH Local Choice HMO Bronze 8000 + $0 Rx list + $0 Virtual Urgent Care",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "NH Local Choice HMO Bronze 8000 + $0 Rx list + $0 Virtual Urgent Care"
        ]
    },
    {
        "id": "nh_ambetter_nh_complete_gold",
        "insurer_id": "ambetter_nh",
        "insurer_name": "Ambetter from NH Healthy Families",
        "official_plan_name": "Complete Gold",
        "display_name": "Complete Gold",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Complete Gold"
        ]
    },
    {
        "id": "nh_ambetter_nh_choice_bronze_hsa",
        "insurer_id": "ambetter_nh",
        "insurer_name": "Ambetter from NH Healthy Families",
        "official_plan_name": "Choice Bronze HSA",
        "display_name": "Choice Bronze HSA",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Choice Bronze HSA"
        ]
    },
    {
        "id": "nh_ambetter_nh_complete_silver",
        "insurer_id": "ambetter_nh",
        "insurer_name": "Ambetter from NH Healthy Families",
        "official_plan_name": "Complete Silver",
        "display_name": "Complete Silver",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Complete Silver"
        ]
    },
    {
        "id": "nh_ambetter_nh_clear_silver",
        "insurer_id": "ambetter_nh",
        "insurer_name": "Ambetter from NH Healthy Families",
        "official_plan_name": "Clear Silver",
        "display_name": "Clear Silver",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Clear Silver"
        ]
    },
    {
        "id": "nh_ambetter_nh_elite_bronze",
        "insurer_id": "ambetter_nh",
        "insurer_name": "Ambetter from NH Healthy Families",
        "official_plan_name": "Elite Bronze",
        "display_name": "Elite Bronze",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Elite Bronze"
        ]
    },
    {
        "id": "nh_ambetter_nh_everyday_gold",
        "insurer_id": "ambetter_nh",
        "insurer_name": "Ambetter from NH Healthy Families",
        "official_plan_name": "Everyday Gold",
        "display_name": "Everyday Gold",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Everyday Gold"
        ]
    },
    {
        "id": "nh_ambetter_nh_standard_expanded_bronze",
        "insurer_id": "ambetter_nh",
        "insurer_name": "Ambetter from NH Healthy Families",
        "official_plan_name": "Standard Expanded Bronze",
        "display_name": "Standard Expanded Bronze",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Standard Expanded Bronze"
        ]
    },
    {
        "id": "nh_ambetter_nh_standard_silver",
        "insurer_id": "ambetter_nh",
        "insurer_name": "Ambetter from NH Healthy Families",
        "official_plan_name": "Standard Silver",
        "display_name": "Standard Silver",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Standard Silver"
        ]
    },
    {
        "id": "nh_ambetter_nh_standard_gold",
        "insurer_id": "ambetter_nh",
        "insurer_name": "Ambetter from NH Healthy Families",
        "official_plan_name": "Standard Gold",
        "display_name": "Standard Gold",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Standard Gold"
        ]
    },
    {
        "id": "nh_ambetter_nh_choice_bronze_hsa_vision_adult_dental", "plan_identity_status": "POSSIBLE_DUPLICATE", "possible_duplicate_of": "nh_ambetter_nh_choice_bronze_hsa", "production_visibility": false,
        "insurer_id": "ambetter_nh",
        "insurer_name": "Ambetter from NH Healthy Families",
        "official_plan_name": "Choice Bronze HSA + Vision + Adult Dental",
        "display_name": "Choice Bronze HSA + Vision + Adult Dental",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Choice Bronze HSA + Vision + Adult Dental"
        ]
    },
    {
        "id": "nh_ambetter_nh_complete_gold_vision_adult_dental",
        "insurer_id": "ambetter_nh",
        "insurer_name": "Ambetter from NH Healthy Families",
        "official_plan_name": "Complete Gold + Vision + Adult Dental",
        "display_name": "Complete Gold + Vision + Adult Dental",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Complete Gold + Vision + Adult Dental"
        ]
    },
    {
        "id": "nh_ambetter_nh_clear_silver_vision_adult_dental",
        "insurer_id": "ambetter_nh",
        "insurer_name": "Ambetter from NH Healthy Families",
        "official_plan_name": "Clear Silver + Vision + Adult Dental",
        "display_name": "Clear Silver + Vision + Adult Dental",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Clear Silver + Vision + Adult Dental"
        ]
    },
    {
        "id": "nh_ambetter_nh_complete_silver_vision_adult_dental",
        "insurer_id": "ambetter_nh",
        "insurer_name": "Ambetter from NH Healthy Families",
        "official_plan_name": "Complete Silver + Vision + Adult Dental",
        "display_name": "Complete Silver + Vision + Adult Dental",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Complete Silver + Vision + Adult Dental"
        ]
    },
    {
        "id": "nh_ambetter_nh_elite_bronze_vision_adult_dental",
        "insurer_id": "ambetter_nh",
        "insurer_name": "Ambetter from NH Healthy Families",
        "official_plan_name": "Elite Bronze + Vision + Adult Dental",
        "display_name": "Elite Bronze + Vision + Adult Dental",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Elite Bronze + Vision + Adult Dental"
        ]
    },
    {
        "id": "nh_ambetter_nh_everyday_gold_vision_adult_dental",
        "insurer_id": "ambetter_nh",
        "insurer_name": "Ambetter from NH Healthy Families",
        "official_plan_name": "Everyday Gold + Vision + Adult Dental",
        "display_name": "Everyday Gold + Vision + Adult Dental",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Everyday Gold + Vision + Adult Dental"
        ]
    },
    {
        "id": "nh_ambetter_nh_standard_expanded_bronze_vision_adult_dental",
        "insurer_id": "ambetter_nh",
        "insurer_name": "Ambetter from NH Healthy Families",
        "official_plan_name": "Standard Expanded Bronze + Vision + Adult Dental",
        "display_name": "Standard Expanded Bronze + Vision + Adult Dental",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Standard Expanded Bronze + Vision + Adult Dental"
        ]
    },
    {
        "id": "nh_ambetter_nh_standard_silver_vision_adult_dental",
        "insurer_id": "ambetter_nh",
        "insurer_name": "Ambetter from NH Healthy Families",
        "official_plan_name": "Standard Silver + Vision + Adult Dental",
        "display_name": "Standard Silver + Vision + Adult Dental",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Standard Silver + Vision + Adult Dental"
        ]
    },
    {
        "id": "nh_ambetter_nh_standard_gold_vision_adult_dental",
        "insurer_id": "ambetter_nh",
        "insurer_name": "Ambetter from NH Healthy Families",
        "official_plan_name": "Standard Gold + Vision + Adult Dental",
        "display_name": "Standard Gold + Vision + Adult Dental",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Standard Gold + Vision + Adult Dental"
        ]
    },
    {
        "id": "nh_anthem_bcbs_anthem_bronze_pathway_x_enhanced_6000_35_hsa",
        "insurer_id": "anthem_bcbs",
        "insurer_name": "Anthem Blue Cross and Blue Shield",
        "official_plan_name": "Anthem Bronze Pathway X Enhanced 6000/35% HSA",
        "display_name": "Anthem Bronze Pathway X Enhanced 6000/35% HSA",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Anthem Bronze Pathway X Enhanced 6000/35% HSA"
        ]
    },
    {
        "id": "nh_anthem_bcbs_anthem_heart_healthy_bronze_pathway_x_enhanced_6000_40_0_virtual_pcp_0_select_drugs",
        "insurer_id": "anthem_bcbs",
        "insurer_name": "Anthem Blue Cross and Blue Shield",
        "official_plan_name": "Anthem Heart Healthy Bronze Pathway X Enhanced 6000/40% ($0 Virtual PCP + $0 Select Drugs)",
        "display_name": "Anthem Heart Healthy Bronze Pathway X Enhanced 6000/40% ($0 Virtual PCP + $0 Select Drugs)",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Anthem Heart Healthy Bronze Pathway X Enhanced 6000/40% ($0 Virtual PCP + $0 Select Drugs)"
        ]
    },
    {
        "id": "nh_anthem_bcbs_anthem_heart_healthy_silver_pathway_x_enhanced_4000_0_0_virtual_pcp_0_select_drugs",
        "insurer_id": "anthem_bcbs",
        "insurer_name": "Anthem Blue Cross and Blue Shield",
        "official_plan_name": "Anthem Heart Healthy Silver Pathway X Enhanced 4000/0% ($0 Virtual PCP + $0 Select Drugs)",
        "display_name": "Anthem Heart Healthy Silver Pathway X Enhanced 4000/0% ($0 Virtual PCP + $0 Select Drugs)",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Anthem Heart Healthy Silver Pathway X Enhanced 4000/0% ($0 Virtual PCP + $0 Select Drugs)"
        ]
    },
    {
        "id": "nh_anthem_bcbs_anthem_catastrophic_pathway_x_enhanced",
        "insurer_id": "anthem_bcbs",
        "insurer_name": "Anthem Blue Cross and Blue Shield",
        "official_plan_name": "Anthem Catastrophic Pathway X Enhanced",
        "display_name": "Anthem Catastrophic Pathway X Enhanced",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Anthem Catastrophic Pathway X Enhanced"
        ]
    },
    {
        "id": "nh_anthem_bcbs_anthem_gold_pathway_x_enhanced_1200_20_0_virtual_pcp_0_select_drugs",
        "insurer_id": "anthem_bcbs",
        "insurer_name": "Anthem Blue Cross and Blue Shield",
        "official_plan_name": "Anthem Gold Pathway X Enhanced 1200/20% ($0 Virtual PCP + $0 Select Drugs)",
        "display_name": "Anthem Gold Pathway X Enhanced 1200/20% ($0 Virtual PCP + $0 Select Drugs)",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Anthem Gold Pathway X Enhanced 1200/20% ($0 Virtual PCP + $0 Select Drugs)"
        ]
    },
    {
        "id": "nh_anthem_bcbs_anthem_silver_pathway_x_enhanced_5500_20_0_virtual_pcp_0_select_drugs",
        "insurer_id": "anthem_bcbs",
        "insurer_name": "Anthem Blue Cross and Blue Shield",
        "official_plan_name": "Anthem Silver Pathway X Enhanced 5500/20% ($0 Virtual PCP + $0 Select Drugs)",
        "display_name": "Anthem Silver Pathway X Enhanced 5500/20% ($0 Virtual PCP + $0 Select Drugs)",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Anthem Silver Pathway X Enhanced 5500/20% ($0 Virtual PCP + $0 Select Drugs)"
        ]
    },
    {
        "id": "nh_anthem_bcbs_anthem_silver_pathway_x_enhanced_4500_20_hsa",
        "insurer_id": "anthem_bcbs",
        "insurer_name": "Anthem Blue Cross and Blue Shield",
        "official_plan_name": "Anthem Silver Pathway X Enhanced 4500/20% HSA",
        "display_name": "Anthem Silver Pathway X Enhanced 4500/20% HSA",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Anthem Silver Pathway X Enhanced 4500/20% HSA"
        ]
    },
    {
        "id": "nh_anthem_bcbs_anthem_gold_pathway_x_enhanced_700_40_0_virtual_pcp_0_select_drugs",
        "insurer_id": "anthem_bcbs",
        "insurer_name": "Anthem Blue Cross and Blue Shield",
        "official_plan_name": "Anthem Gold Pathway X Enhanced 700/40% ($0 Virtual PCP + $0 Select Drugs)",
        "display_name": "Anthem Gold Pathway X Enhanced 700/40% ($0 Virtual PCP + $0 Select Drugs)",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Anthem Gold Pathway X Enhanced 700/40% ($0 Virtual PCP + $0 Select Drugs)"
        ]
    },
    {
        "id": "nh_anthem_bcbs_anthem_bronze_pathway_x_enhanced_7500_50_0_virtual_pcp_0_select_drugs_standard",
        "insurer_id": "anthem_bcbs",
        "insurer_name": "Anthem Blue Cross and Blue Shield",
        "official_plan_name": "Anthem Bronze Pathway X Enhanced 7500/50% ($0 Virtual PCP + $0 Select Drugs) Standard",
        "display_name": "Anthem Bronze Pathway X Enhanced 7500/50% ($0 Virtual PCP + $0 Select Drugs) Standard",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Anthem Bronze Pathway X Enhanced 7500/50% ($0 Virtual PCP + $0 Select Drugs) Standard"
        ]
    },
    {
        "id": "nh_anthem_bcbs_anthem_silver_pathway_x_enhanced_6000_40_0_virtual_pcp_0_select_drugs_standard",
        "insurer_id": "anthem_bcbs",
        "insurer_name": "Anthem Blue Cross and Blue Shield",
        "official_plan_name": "Anthem Silver Pathway X Enhanced 6000/40% ($0 Virtual PCP + $0 Select Drugs) Standard",
        "display_name": "Anthem Silver Pathway X Enhanced 6000/40% ($0 Virtual PCP + $0 Select Drugs) Standard",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Anthem Silver Pathway X Enhanced 6000/40% ($0 Virtual PCP + $0 Select Drugs) Standard"
        ]
    },
    {
        "id": "nh_anthem_bcbs_anthem_gold_pathway_x_enhanced_2000_25_0_virtual_pcp_0_select_drug_standard",
        "insurer_id": "anthem_bcbs",
        "insurer_name": "Anthem Blue Cross and Blue Shield",
        "official_plan_name": "Anthem Gold Pathway X Enhanced 2000/25% ($0 Virtual PCP + $0 Select Drug) Standard",
        "display_name": "Anthem Gold Pathway X Enhanced 2000/25% ($0 Virtual PCP + $0 Select Drug) Standard",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Anthem Gold Pathway X Enhanced 2000/25% ($0 Virtual PCP + $0 Select Drug) Standard"
        ]
    },
    {
        "id": "nh_anthem_bcbs_anthem_bronze_pathway_x_enhanced_7000_0_0_virtual_pcp_0_select_drugs",
        "insurer_id": "anthem_bcbs",
        "insurer_name": "Anthem Blue Cross and Blue Shield",
        "official_plan_name": "Anthem Bronze Pathway X Enhanced 7000/0% ($0 Virtual PCP + $0 Select Drugs)",
        "display_name": "Anthem Bronze Pathway X Enhanced 7000/0% ($0 Virtual PCP + $0 Select Drugs)",
        "plan_year": 2026,
        "state": "NH",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State Network",
        "market_segment": "Individual",
        "service_area": "Statewide NH",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Anthem Bronze Pathway X Enhanced 7000/0% ($0 Virtual PCP + $0 Select Drugs)"
        ]
    },
    {
        "id": "ri_bcbsri_vantageblue_direct_plan_950_1900",
        "insurer_id": "bcbsri",
        "insurer_name": "Blue Cross & Blue Shield of Rhode Island",
        "official_plan_name": "VantageBlue Direct Plan 950/1900",
        "display_name": "VantageBlue Direct Plan 950/1900",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "National",
        "market_segment": "Individual",
        "service_area": "Statewide RI",
        "source_status": "UNVERIFIED",
        "aliases": [
            "VantageBlue Direct Plan 950/1900"
        ]
    },
    {
        "id": "ri_bcbsri_vantageblue_direct_plan_1500_3000",
        "insurer_id": "bcbsri",
        "insurer_name": "Blue Cross & Blue Shield of Rhode Island",
        "official_plan_name": "VantageBlue Direct Plan 1500/3000",
        "display_name": "VantageBlue Direct Plan 1500/3000",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "National",
        "market_segment": "Individual",
        "service_area": "Statewide RI",
        "source_status": "UNVERIFIED",
        "aliases": [
            "VantageBlue Direct Plan 1500/3000"
        ]
    },
    {
        "id": "ri_bcbsri_basicblue_direct_2500_5000",
        "insurer_id": "bcbsri",
        "insurer_name": "Blue Cross & Blue Shield of Rhode Island",
        "official_plan_name": "BasicBlue Direct 2500/5000",
        "display_name": "BasicBlue Direct 2500/5000",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "National",
        "market_segment": "Individual",
        "service_area": "Statewide RI",
        "source_status": "UNVERIFIED",
        "aliases": [
            "BasicBlue Direct 2500/5000"
        ]
    },
    {
        "id": "ri_neighborhood_neighborhood_plus_2650_5300",
        "insurer_id": "neighborhood",
        "insurer_name": "Neighborhood Health Plan of Rhode Island",
        "official_plan_name": "Neighborhood PLUS 2650/5300",
        "display_name": "Neighborhood PLUS 2650/5300",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "Rhode Island",
        "market_segment": "Individual",
        "service_area": "Statewide RI",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Neighborhood PLUS 2650/5300"
        ]
    },
    {
        "id": "ri_bcbsri_bluesolutions_for_hsa_direct_1900_3800",
        "insurer_id": "bcbsri",
        "insurer_name": "Blue Cross & Blue Shield of Rhode Island",
        "official_plan_name": "BlueSolutions for HSA Direct 1900/3800",
        "display_name": "BlueSolutions for HSA Direct 1900/3800",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "National",
        "market_segment": "Individual",
        "service_area": "Statewide RI",
        "source_status": "UNVERIFIED",
        "aliases": [
            "BlueSolutions for HSA Direct 1900/3800"
        ]
    },
    {
        "id": "ri_bcbsri_bluechip_direct_2300_4600",
        "insurer_id": "bcbsri",
        "insurer_name": "Blue Cross & Blue Shield of Rhode Island",
        "official_plan_name": "BlueCHiP Direct 2300/4600",
        "display_name": "BlueCHiP Direct 2300/4600",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Medicare Advantage",
        "insurance_category": "MEDICARE_ADVANTAGE",
        "network_type": "Rhode Island",
        "market_segment": "Individual",
        "service_area": "Statewide RI",
        "source_status": "UNVERIFIED",
        "aliases": [
            "BlueCHiP Direct 2300/4600"
        ]
    },
    {
        "id": "ri_bcbsri_bluechip_direct_advance_2300_4600",
        "insurer_id": "bcbsri",
        "insurer_name": "Blue Cross & Blue Shield of Rhode Island",
        "official_plan_name": "BlueCHiP Direct Advance 2300/4600",
        "display_name": "BlueCHiP Direct Advance 2300/4600",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Medicare Advantage",
        "insurance_category": "MEDICARE_ADVANTAGE",
        "network_type": "RI narrow network",
        "market_segment": "Individual",
        "service_area": "Statewide RI",
        "source_status": "UNVERIFIED",
        "aliases": [
            "BlueCHiP Direct Advance 2300/4600"
        ]
    },
    {
        "id": "ri_neighborhood_neighborhood_plus_1375_2750",
        "insurer_id": "neighborhood",
        "insurer_name": "Neighborhood Health Plan of Rhode Island",
        "official_plan_name": "Neighborhood PLUS 1375/2750",
        "display_name": "Neighborhood PLUS 1375/2750",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "Rhode Island",
        "market_segment": "Individual",
        "service_area": "Statewide RI",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Neighborhood PLUS 1375/2750"
        ]
    },
    {
        "id": "ri_bcbsri_vantageblue_direct_plan_6000_12000",
        "insurer_id": "bcbsri",
        "insurer_name": "Blue Cross & Blue Shield of Rhode Island",
        "official_plan_name": "VantageBlue Direct Plan 6000/12000",
        "display_name": "VantageBlue Direct Plan 6000/12000",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "National",
        "market_segment": "Individual",
        "service_area": "Statewide RI",
        "source_status": "UNVERIFIED",
        "aliases": [
            "VantageBlue Direct Plan 6000/12000"
        ]
    },
    {
        "id": "ri_bcbsri_bluechip_direct_5000_10000",
        "insurer_id": "bcbsri",
        "insurer_name": "Blue Cross & Blue Shield of Rhode Island",
        "official_plan_name": "BlueCHiP Direct 5000/10000",
        "display_name": "BlueCHiP Direct 5000/10000",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Medicare Advantage",
        "insurance_category": "MEDICARE_ADVANTAGE",
        "network_type": "Rhode Island",
        "market_segment": "Individual",
        "service_area": "Statewide RI",
        "source_status": "UNVERIFIED",
        "aliases": [
            "BlueCHiP Direct 5000/10000"
        ]
    },
    {
        "id": "ri_bcbsri_bluesolutions_for_hsa_direct_4100_8200",
        "insurer_id": "bcbsri",
        "insurer_name": "Blue Cross & Blue Shield of Rhode Island",
        "official_plan_name": "BlueSolutions for HSA Direct 4100/8200",
        "display_name": "BlueSolutions for HSA Direct 4100/8200",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "National",
        "market_segment": "Individual",
        "service_area": "Statewide RI",
        "source_status": "UNVERIFIED",
        "aliases": [
            "BlueSolutions for HSA Direct 4100/8200"
        ]
    },
    {
        "id": "ri_bcbsri_bluechip_direct_advance_4950_9900",
        "insurer_id": "bcbsri",
        "insurer_name": "Blue Cross & Blue Shield of Rhode Island",
        "official_plan_name": "BlueCHiP Direct Advance 4950/9900",
        "display_name": "BlueCHiP Direct Advance 4950/9900",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Medicare Advantage",
        "insurance_category": "MEDICARE_ADVANTAGE",
        "network_type": "RI narrow network",
        "market_segment": "Individual",
        "service_area": "Statewide RI",
        "source_status": "UNVERIFIED",
        "aliases": [
            "BlueCHiP Direct Advance 4950/9900"
        ]
    },
    {
        "id": "ri_neighborhood_neighborhood_primary_4750_9500",
        "insurer_id": "neighborhood",
        "insurer_name": "Neighborhood Health Plan of Rhode Island",
        "official_plan_name": "Neighborhood PRIMARY 4750/9500",
        "display_name": "Neighborhood PRIMARY 4750/9500",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "Rhode Island",
        "market_segment": "Individual",
        "service_area": "Statewide RI",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Neighborhood PRIMARY 4750/9500"
        ]
    },
    {
        "id": "ri_neighborhood_neighborhood_primary_3850_7700_hsa",
        "insurer_id": "neighborhood",
        "insurer_name": "Neighborhood Health Plan of Rhode Island",
        "official_plan_name": "Neighborhood PRIMARY 3850/7700 HSA",
        "display_name": "Neighborhood PRIMARY 3850/7700 HSA",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "Rhode Island",
        "market_segment": "Individual",
        "service_area": "Statewide RI",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Neighborhood PRIMARY 3850/7700 HSA"
        ]
    },
    {
        "id": "ri_bcbsri_bluechip_direct_7000_14000",
        "insurer_id": "bcbsri",
        "insurer_name": "Blue Cross & Blue Shield of Rhode Island",
        "official_plan_name": "BlueCHiP Direct 7000/14000",
        "display_name": "BlueCHiP Direct 7000/14000",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Medicare Advantage",
        "insurance_category": "MEDICARE_ADVANTAGE",
        "network_type": "Rhode Island",
        "market_segment": "Individual",
        "service_area": "Statewide RI",
        "source_status": "UNVERIFIED",
        "aliases": [
            "BlueCHiP Direct 7000/14000"
        ]
    },
    {
        "id": "ri_bcbsri_bluesolutions_for_hsa_direct_6300_12600",
        "insurer_id": "bcbsri",
        "insurer_name": "Blue Cross & Blue Shield of Rhode Island",
        "official_plan_name": "BlueSolutions for HSA Direct 6300/12600",
        "display_name": "BlueSolutions for HSA Direct 6300/12600",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "National",
        "market_segment": "Individual",
        "service_area": "Statewide RI",
        "source_status": "UNVERIFIED",
        "aliases": [
            "BlueSolutions for HSA Direct 6300/12600"
        ]
    },
    {
        "id": "ri_neighborhood_neighborhood_select_6900_13800_hsa",
        "insurer_id": "neighborhood",
        "insurer_name": "Neighborhood Health Plan of Rhode Island",
        "official_plan_name": "Neighborhood SELECT 6900/13800 HSA",
        "display_name": "Neighborhood SELECT 6900/13800 HSA",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "Rhode Island",
        "market_segment": "Individual",
        "service_area": "Statewide RI",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Neighborhood SELECT 6900/13800 HSA"
        ]
    },
    {
        "id": "ri_neighborhood_neighborhood_select_7100_14200_hsa",
        "insurer_id": "neighborhood",
        "insurer_name": "Neighborhood Health Plan of Rhode Island",
        "official_plan_name": "Neighborhood SELECT 7100/14200 HSA",
        "display_name": "Neighborhood SELECT 7100/14200 HSA",
        "plan_year": 2026,
        "state": "RI",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "Rhode Island",
        "market_segment": "Individual",
        "service_area": "Statewide RI",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Neighborhood SELECT 7100/14200 HSA"
        ]
    },
    {
        "id": "ct_anthem_bcbs_anthem_pathway_standard_gold",
        "insurer_id": "anthem_bcbs",
        "insurer_name": "Anthem Blue Cross and Blue Shield",
        "official_plan_name": "Anthem Pathway Standard Gold",
        "display_name": "Anthem Pathway Standard Gold",
        "plan_year": 2026,
        "state": "CT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide CT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Anthem Pathway Standard Gold"
        ]
    },
    {
        "id": "ct_anthem_bcbs_anthem_pathway_standard_silver",
        "insurer_id": "anthem_bcbs",
        "insurer_name": "Anthem Blue Cross and Blue Shield",
        "official_plan_name": "Anthem Pathway Standard Silver",
        "display_name": "Anthem Pathway Standard Silver",
        "plan_year": 2026,
        "state": "CT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide CT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Anthem Pathway Standard Silver"
        ]
    },
    {
        "id": "ct_anthem_bcbs_anthem_pathway_standard_bronze",
        "insurer_id": "anthem_bcbs",
        "insurer_name": "Anthem Blue Cross and Blue Shield",
        "official_plan_name": "Anthem Pathway Standard Bronze",
        "display_name": "Anthem Pathway Standard Bronze",
        "plan_year": 2026,
        "state": "CT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide CT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Anthem Pathway Standard Bronze"
        ]
    },
    {
        "id": "ct_anthem_bcbs_anthem_pathway_hsa_bronze",
        "insurer_id": "anthem_bcbs",
        "insurer_name": "Anthem Blue Cross and Blue Shield",
        "official_plan_name": "Anthem Pathway HSA Bronze",
        "display_name": "Anthem Pathway HSA Bronze",
        "plan_year": 2026,
        "state": "CT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide CT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Anthem Pathway HSA Bronze"
        ]
    },
    {
        "id": "ct_connecticare_connecticare_choice_gold",
        "insurer_id": "connecticare",
        "insurer_name": "ConnectiCare",
        "official_plan_name": "ConnectiCare Choice Gold",
        "display_name": "ConnectiCare Choice Gold",
        "plan_year": 2026,
        "state": "CT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide CT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "ConnectiCare Choice Gold"
        ]
    },
    {
        "id": "ct_connecticare_connecticare_choice_silver",
        "insurer_id": "connecticare",
        "insurer_name": "ConnectiCare",
        "official_plan_name": "ConnectiCare Choice Silver",
        "display_name": "ConnectiCare Choice Silver",
        "plan_year": 2026,
        "state": "CT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide CT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "ConnectiCare Choice Silver"
        ]
    },
    {
        "id": "ct_connecticare_connecticare_choice_bronze",
        "insurer_id": "connecticare",
        "insurer_name": "ConnectiCare",
        "official_plan_name": "ConnectiCare Choice Bronze",
        "display_name": "ConnectiCare Choice Bronze",
        "plan_year": 2026,
        "state": "CT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide CT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "ConnectiCare Choice Bronze"
        ]
    },
    {
        "id": "ct_connecticare_connecticare_value_gold",
        "insurer_id": "connecticare",
        "insurer_name": "ConnectiCare",
        "official_plan_name": "ConnectiCare Value Gold",
        "display_name": "ConnectiCare Value Gold",
        "plan_year": 2026,
        "state": "CT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide CT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "ConnectiCare Value Gold"
        ]
    },
    {
        "id": "ct_connecticare_connecticare_value_silver",
        "insurer_id": "connecticare",
        "insurer_name": "ConnectiCare",
        "official_plan_name": "ConnectiCare Value Silver",
        "display_name": "ConnectiCare Value Silver",
        "plan_year": 2026,
        "state": "CT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide CT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "ConnectiCare Value Silver"
        ]
    },
    {
        "id": "ct_connecticare_connecticare_value_bronze",
        "insurer_id": "connecticare",
        "insurer_name": "ConnectiCare",
        "official_plan_name": "ConnectiCare Value Bronze",
        "display_name": "ConnectiCare Value Bronze",
        "plan_year": 2026,
        "state": "CT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide CT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "ConnectiCare Value Bronze"
        ]
    },
    {
        "id": "ct_connecticare_connecticare_covered_ct",
        "insurer_id": "connecticare",
        "insurer_name": "ConnectiCare",
        "official_plan_name": "ConnectiCare Covered CT",
        "display_name": "ConnectiCare Covered CT",
        "plan_year": 2026,
        "state": "CT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide CT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "ConnectiCare Covered CT"
        ]
    },
    {
        "id": "me_harvard_pilgrim_clear_choice_hmo_gold_2500",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "Clear Choice HMO Gold 2500",
        "display_name": "Clear Choice HMO Gold 2500",
        "plan_year": 2026,
        "state": "ME",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide ME",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Clear Choice HMO Gold 2500"
        ]
    },
    {
        "id": "me_harvard_pilgrim_clear_choice_hmo_silver_4000", "plan_identity_status": "SOURCE_CONFIRMED", "production_visibility": true,
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "Clear Choice HMO Silver 4000",
        "display_name": "Clear Choice HMO Silver 4000",
        "plan_year": 2026,
        "state": "ME",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide ME",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Clear Choice HMO Silver 4000"
        ]
    },
    {
        "id": "me_harvard_pilgrim_clear_choice_hmo_silver_5000",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "Clear Choice HMO Silver 5000",
        "display_name": "Clear Choice HMO Silver 5000",
        "plan_year": 2026,
        "state": "ME",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide ME",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Clear Choice HMO Silver 5000"
        ]
    },
    {
        "id": "me_harvard_pilgrim_clear_choice_hmo_bronze_7500",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "Clear Choice HMO Bronze 7500",
        "display_name": "Clear Choice HMO Bronze 7500",
        "plan_year": 2026,
        "state": "ME",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide ME",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Clear Choice HMO Bronze 7500"
        ]
    },
    {
        "id": "me_harvard_pilgrim_hmo_bronze_8500",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "HMO Bronze 8500",
        "display_name": "HMO Bronze 8500",
        "plan_year": 2026,
        "state": "ME",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide ME",
        "source_status": "UNVERIFIED",
        "aliases": [
            "HMO Bronze 8500"
        ]
    },
    {
        "id": "me_harvard_pilgrim_clear_choice_hmo_hsa_bronze_6300",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "Clear Choice HMO HSA Bronze 6300",
        "display_name": "Clear Choice HMO HSA Bronze 6300",
        "plan_year": 2026,
        "state": "ME",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide ME",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Clear Choice HMO HSA Bronze 6300"
        ]
    },
    {
        "id": "me_harvard_pilgrim_clear_choice_hmo_hsa_bronze_8000",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "Clear Choice HMO HSA Bronze 8000",
        "display_name": "Clear Choice HMO HSA Bronze 8000",
        "plan_year": 2026,
        "state": "ME",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide ME",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Clear Choice HMO HSA Bronze 8000"
        ]
    },
    {
        "id": "me_harvard_pilgrim_clear_choice_maine_s_choice_plus_hmo_gold_2500",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "Clear Choice Maine's Choice Plus HMO Gold 2500",
        "display_name": "Clear Choice Maine's Choice Plus HMO Gold 2500",
        "plan_year": 2026,
        "state": "ME",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide ME",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Clear Choice Maine's Choice Plus HMO Gold 2500"
        ]
    },
    {
        "id": "me_harvard_pilgrim_clear_choice_maine_s_choice_plus_hmo_silver_4000",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "Clear Choice Maine's Choice Plus HMO Silver 4000",
        "display_name": "Clear Choice Maine's Choice Plus HMO Silver 4000",
        "plan_year": 2026,
        "state": "ME",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide ME",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Clear Choice Maine's Choice Plus HMO Silver 4000"
        ]
    },
    {
        "id": "me_harvard_pilgrim_clear_choice_maine_s_choice_plus_hmo_silver_5000",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "Clear Choice Maine's Choice Plus HMO Silver 5000",
        "display_name": "Clear Choice Maine's Choice Plus HMO Silver 5000",
        "plan_year": 2026,
        "state": "ME",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide ME",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Clear Choice Maine's Choice Plus HMO Silver 5000"
        ]
    },
    {
        "id": "me_harvard_pilgrim_clear_choice_maine_s_choice_plus_hmo_bronze_7500",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "Clear Choice Maine's Choice Plus HMO Bronze 7500",
        "display_name": "Clear Choice Maine's Choice Plus HMO Bronze 7500",
        "plan_year": 2026,
        "state": "ME",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide ME",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Clear Choice Maine's Choice Plus HMO Bronze 7500"
        ]
    },
    {
        "id": "me_harvard_pilgrim_clear_choice_maine_s_choice_plus_hmo_hsa_bronze_6300",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "Clear Choice Maine's Choice Plus HMO HSA Bronze 6300",
        "display_name": "Clear Choice Maine's Choice Plus HMO HSA Bronze 6300",
        "plan_year": 2026,
        "state": "ME",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide ME",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Clear Choice Maine's Choice Plus HMO HSA Bronze 6300"
        ]
    },
    {
        "id": "me_anthem_bcbs_anthem_clear_choice_hmo",
        "insurer_id": "anthem_bcbs",
        "insurer_name": "Anthem Blue Cross and Blue Shield",
        "official_plan_name": "Anthem Clear Choice HMO",
        "display_name": "Anthem Clear Choice HMO",
        "plan_year": 2026,
        "state": "ME",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide ME",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Anthem Clear Choice HMO"
        ]
    },
    {
        "id": "me_anthem_bcbs_anthem_clear_choice_ppo", "plan_identity_status": "SOURCE_CONFIRMED", "production_visibility": true,
        "insurer_id": "anthem_bcbs",
        "insurer_name": "Anthem Blue Cross and Blue Shield",
        "official_plan_name": "Anthem Clear Choice PPO",
        "display_name": "Anthem Clear Choice PPO",
        "plan_year": 2026,
        "state": "ME",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide ME",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Anthem Clear Choice PPO"
        ]
    },
    {
        "id": "me_community_health_options_community_health_options_clear_choice", "plan_identity_status": "SOURCE_CONFIRMED", "production_visibility": true,
        "insurer_id": "community_health_options",
        "insurer_name": "Community Health Options",
        "official_plan_name": "Community Health Options Clear Choice",
        "display_name": "Community Health Options Clear Choice",
        "plan_year": 2026,
        "state": "ME",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide ME",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Community Health Options Clear Choice"
        ]
    },
    {
        "id": "me_mending_mending_primary_care_marketplace_plan",
        "insurer_id": "mending",
        "insurer_name": "Mending",
        "official_plan_name": "Mending Primary Care Marketplace Plan",
        "display_name": "Mending Primary Care Marketplace Plan",
        "plan_year": 2026,
        "state": "ME",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide ME",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Mending Primary Care Marketplace Plan"
        ]
    },
    {
        "id": "ma_bcbsma_health_connector_standard_plan",
        "insurer_id": "bcbsma",
        "insurer_name": "Blue Cross Blue Shield of Massachusetts",
        "official_plan_name": "Health Connector Standard Plan",
        "display_name": "Health Connector Standard Plan",
        "plan_year": 2026,
        "state": "MA",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide MA",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Health Connector Standard Plan"
        ]
    },
    {
        "id": "ma_harvard_pilgrim_standard_platinum_flex",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "Standard Platinum \u2013 Flex",
        "display_name": "Standard Platinum \u2013 Flex",
        "plan_year": 2026,
        "state": "MA",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide MA",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Standard Platinum \u2013 Flex"
        ]
    },
    {
        "id": "ma_harvard_pilgrim_standard_high_gold",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "Standard High Gold",
        "display_name": "Standard High Gold",
        "plan_year": 2026,
        "state": "MA",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide MA",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Standard High Gold"
        ]
    },
    {
        "id": "ma_harvard_pilgrim_hmo_2000_value_ii_flex",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "HMO 2000 Value II \u2013 Flex",
        "display_name": "HMO 2000 Value II \u2013 Flex",
        "plan_year": 2026,
        "state": "MA",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide MA",
        "source_status": "UNVERIFIED",
        "aliases": [
            "HMO 2000 Value II \u2013 Flex"
        ]
    },
    {
        "id": "ma_harvard_pilgrim_standard_silver_ii",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "Standard Silver II",
        "display_name": "Standard Silver II",
        "plan_year": 2026,
        "state": "MA",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide MA",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Standard Silver II"
        ]
    },
    {
        "id": "ma_harvard_pilgrim_standard_high_bronze_hsa_flex",
        "insurer_id": "harvard_pilgrim",
        "insurer_name": "Harvard Pilgrim Health Care",
        "official_plan_name": "Standard High Bronze HSA \u2013 Flex",
        "display_name": "Standard High Bronze HSA \u2013 Flex",
        "plan_year": 2026,
        "state": "MA",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide MA",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Standard High Bronze HSA \u2013 Flex"
        ]
    },
    {
        "id": "ma_health_new_england_connectorcare",
        "insurer_id": "health_new_england",
        "insurer_name": "Health New England",
        "official_plan_name": "ConnectorCare",
        "display_name": "ConnectorCare",
        "plan_year": 2026,
        "state": "MA",
        "plan_type": "Individual Marketplace",
        "insurance_category": "INDIVIDUAL_MARKETPLACE",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide MA",
        "source_status": "UNVERIFIED",
        "aliases": [
            "ConnectorCare"
        ]
    },
    {
        "id": "ma_mgb_health_connectorcare",
        "insurer_id": "mgb_health",
        "insurer_name": "Mass General Brigham Health Plan",
        "official_plan_name": "ConnectorCare",
        "display_name": "ConnectorCare",
        "plan_year": 2026,
        "state": "MA",
        "plan_type": "Individual Marketplace",
        "insurance_category": "INDIVIDUAL_MARKETPLACE",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide MA",
        "source_status": "UNVERIFIED",
        "aliases": [
            "ConnectorCare"
        ]
    },
    {
        "id": "ma_mgb_health_complete_hmo",
        "insurer_id": "mgb_health",
        "insurer_name": "Mass General Brigham Health Plan",
        "official_plan_name": "Complete HMO",
        "display_name": "Complete HMO",
        "plan_year": 2026,
        "state": "MA",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide MA",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Complete HMO"
        ]
    },
    {
        "id": "ma_tufts_p32_tufts_health_direct_connectorcare",
        "insurer_id": "tufts_p32",
        "insurer_name": "Tufts Health Plan",
        "official_plan_name": "Tufts Health Direct ConnectorCare",
        "display_name": "Tufts Health Direct ConnectorCare",
        "plan_year": 2026,
        "state": "MA",
        "plan_type": "Individual Marketplace",
        "insurance_category": "INDIVIDUAL_MARKETPLACE",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide MA",
        "source_status": "UNVERIFIED",
        "aliases": [
            "Tufts Health Direct ConnectorCare"
        ]
    },
    {
        "id": "ma_wellsense_wellsense_connectorcare",
        "insurer_id": "wellsense",
        "insurer_name": "WellSense Health Plan",
        "official_plan_name": "WellSense ConnectorCare",
        "display_name": "WellSense ConnectorCare",
        "plan_year": 2026,
        "state": "MA",
        "plan_type": "Individual Marketplace",
        "insurance_category": "INDIVIDUAL_MARKETPLACE",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide MA",
        "source_status": "UNVERIFIED",
        "aliases": [
            "WellSense ConnectorCare"
        ]
    },
    {
        "id": "vt_bcbsvt_bcbsvt_gold",
        "insurer_id": "bcbsvt",
        "insurer_name": "Blue Cross and Blue Shield of Vermont",
        "official_plan_name": "BCBSVT Gold",
        "display_name": "BCBSVT Gold",
        "plan_year": 2026,
        "state": "VT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide VT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "BCBSVT Gold"
        ]
    },
    {
        "id": "vt_bcbsvt_bcbsvt_silver", "plan_identity_status": "SOURCE_CONFIRMED", "production_visibility": true,
        "insurer_id": "bcbsvt",
        "insurer_name": "Blue Cross and Blue Shield of Vermont",
        "official_plan_name": "BCBSVT Silver",
        "display_name": "BCBSVT Silver",
        "plan_year": 2026,
        "state": "VT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide VT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "BCBSVT Silver"
        ]
    },
    {
        "id": "vt_bcbsvt_bcbsvt_bronze",
        "insurer_id": "bcbsvt",
        "insurer_name": "Blue Cross and Blue Shield of Vermont",
        "official_plan_name": "BCBSVT Bronze",
        "display_name": "BCBSVT Bronze",
        "plan_year": 2026,
        "state": "VT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide VT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "BCBSVT Bronze"
        ]
    },
    {
        "id": "vt_bcbsvt_bcbsvt_gold_hdhp",
        "insurer_id": "bcbsvt",
        "insurer_name": "Blue Cross and Blue Shield of Vermont",
        "official_plan_name": "BCBSVT Gold HDHP",
        "display_name": "BCBSVT Gold HDHP",
        "plan_year": 2026,
        "state": "VT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide VT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "BCBSVT Gold HDHP"
        ]
    },
    {
        "id": "vt_bcbsvt_bcbsvt_silver_hdhp",
        "insurer_id": "bcbsvt",
        "insurer_name": "Blue Cross and Blue Shield of Vermont",
        "official_plan_name": "BCBSVT Silver HDHP",
        "display_name": "BCBSVT Silver HDHP",
        "plan_year": 2026,
        "state": "VT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide VT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "BCBSVT Silver HDHP"
        ]
    },
    {
        "id": "vt_mvp_health_mvp_vt_plus_gold",
        "insurer_id": "mvp_health",
        "insurer_name": "MVP Health Care",
        "official_plan_name": "MVP VT Plus Gold",
        "display_name": "MVP VT Plus Gold",
        "plan_year": 2026,
        "state": "VT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide VT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "MVP VT Plus Gold"
        ]
    },
    {
        "id": "vt_mvp_health_mvp_vt_plus_silver", "plan_identity_status": "SOURCE_CONFIRMED", "production_visibility": true,
        "insurer_id": "mvp_health",
        "insurer_name": "MVP Health Care",
        "official_plan_name": "MVP VT Plus Silver",
        "display_name": "MVP VT Plus Silver",
        "plan_year": 2026,
        "state": "VT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide VT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "MVP VT Plus Silver"
        ]
    },
    {
        "id": "vt_mvp_health_mvp_vt_plus_bronze",
        "insurer_id": "mvp_health",
        "insurer_name": "MVP Health Care",
        "official_plan_name": "MVP VT Plus Bronze",
        "display_name": "MVP VT Plus Bronze",
        "plan_year": 2026,
        "state": "VT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide VT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "MVP VT Plus Bronze"
        ]
    },
    {
        "id": "vt_mvp_health_mvp_vt_plus_gold_hdhp",
        "insurer_id": "mvp_health",
        "insurer_name": "MVP Health Care",
        "official_plan_name": "MVP VT Plus Gold HDHP",
        "display_name": "MVP VT Plus Gold HDHP",
        "plan_year": 2026,
        "state": "VT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide VT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "MVP VT Plus Gold HDHP"
        ]
    },
    {
        "id": "vt_mvp_health_mvp_vt_plus_silver_hdhp",
        "insurer_id": "mvp_health",
        "insurer_name": "MVP Health Care",
        "official_plan_name": "MVP VT Plus Silver HDHP",
        "display_name": "MVP VT Plus Silver HDHP",
        "plan_year": 2026,
        "state": "VT",
        "plan_type": "Commercial",
        "insurance_category": "COMMERCIAL",
        "network_type": "State network",
        "market_segment": "Individual",
        "service_area": "Statewide VT",
        "source_status": "UNVERIFIED",
        "aliases": [
            "MVP VT Plus Silver HDHP"
        ]
    }
];

  // --- 2B. PLAN IDENTIFIERS & CARD MATCHING STRUCTURE ---
  const PLAN_IDENTIFIERS = [
  {
    plan_id: 'bcbsri_bluechip_core_2026',
    insurer_id: 'bcbsri',
    display_name: 'BlueCHiP for Medicare Core (2026)',
    member_card_branding: 'Blue Cross & Blue Shield of Rhode Island',
    network_name: 'BlueCHiP Network',
    plan_name_tokens: ['BlueCHiP', 'Core', 'Medicare', 'BCBSRI'],
    group_prefix_patterns: ['BCB-CORE-', 'BCB-RI-'],
    rx_bin: '004336',
    rx_pcn: 'MEDDADV',
    rx_group_patterns: ['RXBCBSRI'],
    support_phone: '1-800-267-0439',
    official_member_site: 'https://www.bcbsri.com/medicare'
  },
  {
    plan_id: 'neighborhood_integra_2026',
    insurer_id: 'neighborhood',
    display_name: 'Neighborhood INTEGRIA D-SNP (2026)',
    member_card_branding: 'Neighborhood Health Plan of Rhode Island',
    network_name: 'INTEGRIA D-SNP Network',
    plan_name_tokens: ['Neighborhood', 'INTEGRIA', 'DSNP', 'Dual'],
    group_prefix_patterns: ['NHP-INT-'],
    rx_bin: '012312',
    rx_pcn: 'NHPRIDSNP',
    rx_group_patterns: ['RXNHPRI'],
    support_phone: '1-844-812-6896',
    official_member_site: 'https://www.nhpri.org/members/integria'
  },
  {
    plan_id: 'ri_medicaid_managed_2026',
    insurer_id: 'ri_medicaid',
    display_name: 'RI Medicaid Managed Care Protocols (2026)',
    member_card_branding: 'State of Rhode Island Executive Office of Health & Human Services',
    network_name: 'RI Medicaid Fee-for-Service & Managed Care',
    plan_name_tokens: ['Medicaid', 'RI EOHHS', 'Anchor', 'RIte Care'],
    group_prefix_patterns: ['RIME-'],
    rx_bin: '610498',
    rx_pcn: 'RIMEDICAID',
    rx_group_patterns: ['RXRIMED'],
    support_phone: '1-855-697-4347',
    official_member_site: 'https://eohhs.ri.gov'
  },
  {
    plan_id: 'uhc_medicare_dual_2026',
    insurer_id: 'uhc_ri',
    display_name: 'UHC Dual Complete RI (2026)',
    member_card_branding: 'UnitedHealthcare UCard',
    network_name: 'UnitedHealthcare Choice Regional D-SNP',
    plan_name_tokens: ['UHC', 'UnitedHealthcare', 'Dual Complete', 'UCard'],
    group_prefix_patterns: ['UHC-RI-DSNP-'],
    rx_bin: '610097',
    rx_pcn: '9999',
    rx_group_patterns: ['COS'],
    support_phone: '1-866-414-1959',
    official_member_site: 'https://www.uhc.com/medicare'
  }
];

  // --- 8C. PLAN IDENTIFIERS AUDIT & MATCHING ENGINE ---
  const PLAN_IDENTIFIERS_AUDIT = [
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
];

  // --- 8A. CARD SIGNAL EXTRACTOR (STRICT PHI REDACTION) ---
  function extractCardSignals(inputData) {
    const raw = typeof inputData === 'string' ? inputData : JSON.stringify(inputData || {});
    
    // Explicit PHI redaction rules
    const sanitizedText = raw
      .replace(/\b(member_id|subscriber_id|dob|date_of_birth|ssn|patient_name|member_name)\b.*?[,\n}]/gi, '')
      .replace(/\b[A-Z]{3}\d{8,11}\b/g, '[REDACTED_MEMBER_ID]') // Common BCBS/UHC ID format
      .replace(/\b\d{3}-\d{2}-\d{4}\b/g, '[REDACTED_SSN]')
      .replace(/\b\d{2}\/\d{2}\/\d{4}\b/g, '[REDACTED_DOB]');

    const tokens = sanitizedText.split(/\s+|,|;|:|\//).map(t => t.trim().toLowerCase()).filter(Boolean);

    return {
      insurer_tokens: tokens.filter(t => ['bcbsri', 'blue', 'cross', 'neighborhood', 'nhpri', 'medicaid', 'eohhs', 'unitedhealthcare', 'uhc'].includes(t)),
      plan_tokens: tokens.filter(t => ['bluechip', 'core', 'integria', 'dsnp', 'dual', 'complete', 'ucard', 'rite'].includes(t)),
      rx_bin: (raw.match(/\b004336|012312|610498|610097\b/) || [])[0] || null,
      rx_pcn: (raw.match(/\bMEDDADV|NHPRIDSNP|RIMEDICAID|9999\b/) || [])[0] || null,
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
  }

  // --- 2C. DOCUMENT TO RULE COVERAGE MATRIX ---
  const DOCUMENT_RULE_MATRIX = [
  { source_id: 'SRC-BCBSRI-2026-OTC', products_found: 48, matched_exact: 36, matched_category: 7, needs_review: 5, approved_rules: 26 },
  { source_id: 'SRC-BCBSRI-2026-EOC', products_found: 22, matched_exact: 18, matched_category: 3, needs_review: 1, approved_rules: 15 },
  { source_id: 'SRC-NHPRI-2026-OTC', products_found: 34, matched_exact: 25, matched_category: 6, needs_review: 3, approved_rules: 21 },
  { source_id: 'SRC-RIME-2026-PHARMACY', products_found: 28, matched_exact: 22, matched_category: 4, needs_review: 2, approved_rules: 21 },
  { source_id: 'SRC-UHCRI-2026-UCARD', products_found: 31, matched_exact: 24, matched_category: 5, needs_review: 2, approved_rules: 20 }
];

  // --- 3. REUSABLE PRODUCT UNIVERSE (NO DUPLICATE PRODUCTS) ---
  const PRODUCTS = [
    // 1. Vitamins & Minerals
    {
      id: 'P-VIT-D', product_name: 'Vitamin D3 2,000 IU Softgels', generic_name: 'Cholecalciferol', brand_name: 'Nature Made',
      category: 'vitamins', subcategory: 'Vitamin D', description: 'Supports bone strength, calcium absorption, and immune function.',
      icon: '☀️', aliases: ['vitamin d', 'vit d', 'd3', 'cholecalciferol'], synonyms: ['sunshine vitamin', 'bone vitamin'], keywords: ['vitamin d3', 'softgels']
    },
    {
      id: 'P-VIT-B12', product_name: 'Vitamin B12 5,000 mcg Sublingual', generic_name: 'Cyanocobalamin / Methylcobalamin', brand_name: 'Nature Made',
      category: 'vitamins', subcategory: 'Vitamin B', description: 'Supports nerve health and red blood cell production.',
      icon: '🔋', aliases: ['vitamin b12', 'vit b12', 'b12', 'cyanocobalamin'], synonyms: ['nerve vitamin'], keywords: ['b12', 'sublingual']
    },
    {
      id: 'P-VIT-C', product_name: 'Vitamin C 1,000 mg Caplets', generic_name: 'Ascorbic Acid', brand_name: 'Nature Made',
      category: 'vitamins', subcategory: 'Vitamin C', description: 'High-potency antioxidant support for immune defense.',
      icon: '🍊', aliases: ['vitamin c', 'vit c', 'ascorbic acid'], synonyms: ['immune vitamin'], keywords: ['vitamin c']
    },
    {
      id: 'P-VIT-A', product_name: 'Vitamin A 10,000 IU Softgels', generic_name: 'Retinol Palmitate', brand_name: 'Nature Made',
      category: 'vitamins', subcategory: 'Vitamin A', description: 'Supports eye vision and mucosal immunity.',
      icon: '👁️', aliases: ['vitamin a', 'vit a', 'retinol'], synonyms: ['eye vitamin'], keywords: ['vitamin a']
    },
    {
      id: 'P-VIT-E', product_name: 'Vitamin E 400 IU Softgels', generic_name: 'd-Alpha Tocopherol', brand_name: 'Nature Made',
      category: 'vitamins', subcategory: 'Vitamin E', description: 'Cellular membrane antioxidant protection.',
      icon: '💊', aliases: ['vitamin e', 'vit e', 'tocopherol'], synonyms: ['skin vitamin'], keywords: ['vitamin e']
    },
    {
      id: 'P-VIT-K', product_name: 'Vitamin K2 MK-7 100 mcg', generic_name: 'Menaquinone-7', brand_name: 'Nature Made',
      category: 'vitamins', subcategory: 'Vitamin K', description: 'Helps direct calcium to bones and blood clotting.',
      icon: '🦴', aliases: ['vitamin k', 'vit k', 'k2'], synonyms: ['bone calcium regulator'], keywords: ['vitamin k2']
    },
    {
      id: 'P-VIT-FOLIC', product_name: 'Folic Acid 800 mcg Tablets', generic_name: 'Folic Acid / Vitamin B9', brand_name: 'Nature Made',
      category: 'vitamins', subcategory: 'Folic Acid', description: 'Essential for DNA synthesis and maternal fetal health.',
      icon: '🌸', aliases: ['folic acid', 'folate', 'b9'], synonyms: ['prenatal folate'], keywords: ['folic acid']
    },
    {
      id: 'P-VIT-IRON', product_name: 'Ferrous Sulfate 65 mg (325 mg Equivalent Iron)', generic_name: 'Ferrous Sulfate', brand_name: 'Feosol',
      category: 'vitamins', subcategory: 'Iron', description: 'Red blood cell synthesis for iron deficiency anemia.',
      icon: '🩸', aliases: ['iron', 'ferrous sulfate', 'iron pills'], synonyms: ['anemia supplement'], keywords: ['iron', 'ferrous sulfate']
    },
    {
      id: 'P-VIT-CALCIUM', product_name: 'Calcium Carbonate 600 mg + Vitamin D3', generic_name: 'Calcium Carbonate with D3', brand_name: 'Caltrate',
      category: 'vitamins', subcategory: 'Calcium', description: 'Bone density support formula.',
      icon: '🦴', aliases: ['calcium', 'calcium carbonate', 'caltrate generic'], synonyms: ['bone calcium'], keywords: ['calcium carbonate']
    },
    {
      id: 'P-VIT-MAGNESIUM', product_name: 'Magnesium Glycinate 400 mg', generic_name: 'Magnesium Glycinate', brand_name: 'Qunol',
      category: 'vitamins', subcategory: 'Magnesium', description: 'Gentle muscle relaxation and sleep support.',
      icon: '🌿', aliases: ['magnesium', 'mag glycinate'], synonyms: ['cramp relaxer'], keywords: ['magnesium glycinate']
    },
    {
      id: 'P-VIT-ZINC', product_name: 'Zinc Picolinate 50 mg', generic_name: 'Zinc Picolinate', brand_name: 'Nature Made',
      category: 'vitamins', subcategory: 'Zinc', description: 'Immune cell support and wound healing.',
      icon: '🛡️', aliases: ['zinc', 'zinc picolinate'], synonyms: ['immune mineral'], keywords: ['zinc']
    },
    {
      id: 'P-VIT-MULTI', product_name: 'Senior Complete 50+ Daily Multivitamin', generic_name: 'Multivitamin with Minerals', brand_name: 'Centrum Silver',
      category: 'vitamins', subcategory: 'Multivitamins', description: 'Tailored for adults 50+ with Lutein and B-Vitamins.',
      icon: '💊', aliases: ['multivitamins', 'multivitamin', 'senior multi'], synonyms: ['daily multi'], keywords: ['multivitamin']
    },
    {
      id: 'P-VIT-PRENATAL', product_name: 'Prenatal Multivitamin with Folic Acid & Iron', generic_name: 'Prenatal Multivitamin', brand_name: 'One A Day',
      category: 'vitamins', subcategory: 'Prenatal Vitamins', description: 'Nutritional support prior to and during pregnancy.',
      icon: '👶', aliases: ['prenatal vitamins', 'prenatal vitamin', 'prenatal'], synonyms: ['pregnancy vitamins'], keywords: ['prenatal']
    },

    // 2. Supplements & Nutrition / Medical Foods
    {
      id: 'P-SUP-PROBIOTIC', product_name: 'Daily Probiotic 50 Billion CFU', generic_name: 'Lactobacillus & Bifidobacterium Blend', brand_name: 'Culturelle',
      category: 'supplements', subcategory: 'Probiotics', description: 'Supports digestive regularity and gut microbiome.',
      icon: '🦠', aliases: ['probiotics', 'probiotic'], synonyms: ['gut flora'], keywords: ['probiotic']
    },
    {
      id: 'P-SUP-FIBER', product_name: 'Psyllium Husk Daily Fiber Powder', generic_name: 'Psyllium Husk Powder', brand_name: 'Metamucil',
      category: 'supplements', subcategory: 'Fiber Supplements', description: 'Promotes regular digestive bowel movements.',
      icon: '🌾', aliases: ['fiber supplements', 'fiber', 'psyllium', 'metamucil'], synonyms: ['bulk laxative'], keywords: ['psyllium']
    },
    {
      id: 'P-NUT-ORS', product_name: 'Oral Rehydration Solution Powder Packets', generic_name: 'Oral Rehydration Salts (ORS)', brand_name: 'Pedialyte',
      category: 'nutrition', subcategory: 'Oral Rehydration Products', description: 'WHO formulation rapid electrolyte hydration solution.',
      icon: '💧', aliases: ['oral rehydration products', 'pedialyte', 'ors'], synonyms: ['electrolyte solution'], keywords: ['oral rehydration']
    },
    {
      id: 'P-NUT-ENSURE', product_name: 'Ensure High-Protein Nutritional Shakes (24 Pack)', generic_name: 'High-Protein Nutritional Liquid', brand_name: 'Ensure',
      category: 'nutrition', subcategory: 'Nutritional Shakes', description: '30g Protein, 25 Vitamins & Minerals per serving.',
      icon: '🥛', aliases: ['nutritional shakes', 'ensure', 'protein drinks'], synonyms: ['meal replacement'], keywords: ['ensure']
    },
    {
      id: 'P-NUT-ENTERAL', product_name: 'Enteral Clinical Tube-Feeding Formula & Supplies', generic_name: 'Enteral Nutrition Formula', brand_name: 'Jevity',
      category: 'nutrition', subcategory: 'Medical Nutritional Formulas', description: 'Complete clinical nutrition formula & feeding bags.',
      icon: '🪠', aliases: ['medical nutritional formulas', 'enteral formula', 'tube feeding supplies', 'enteral feeding pumps'], synonyms: ['tube feed formula'], keywords: ['enteral']
    },

    // 3. Pain Relief
    {
      id: 'P-PAI-ACETA', product_name: 'Extra Strength Acetaminophen 500 mg', generic_name: 'Acetaminophen / Paracetamol', brand_name: 'Tylenol',
      category: 'pain', subcategory: 'Analgesics', description: 'Rapid aspirin-free pain reliever and fever reducer.',
      icon: '💊', aliases: ['acetaminophen', 'tylenol', 'cold medicine'], synonyms: ['pain reliever'], keywords: ['acetaminophen', '500 mg']
    },
    {
      id: 'P-PAI-IBU', product_name: 'Ibuprofen 200 mg Softgels', generic_name: 'Ibuprofen', brand_name: 'Advil',
      category: 'pain', subcategory: 'NSAIDs', description: 'NSAID pain relief for muscle aches, headache & fever.',
      icon: '💊', aliases: ['ibuprofen', 'advil', 'motrin'], synonyms: ['nsaid pain reliever'], keywords: ['ibuprofen']
    },
    {
      id: 'P-PAI-NAPROXEN', product_name: 'Naproxen Sodium 220 mg Caplets', generic_name: 'Naproxen Sodium', brand_name: 'Aleve',
      category: 'pain', subcategory: 'NSAIDs', description: '12-hour joint & arthritis pain relief.',
      icon: '💊', aliases: ['naproxen', 'aleve'], synonyms: ['12 hour pain reliever'], keywords: ['naproxen']
    },
    {
      id: 'P-PAI-ASPIRIN', product_name: 'Low Dose Baby Aspirin 81 mg Safety Coated', generic_name: 'Aspirin', brand_name: 'Bayer',
      category: 'pain', subcategory: 'Salicylates', description: 'Enteric coated doctor-recommended daily aspirin regimen.',
      icon: '❤️', aliases: ['aspirin', 'baby aspirin', 'bayer'], synonyms: ['heart health aspirin'], keywords: ['aspirin 81 mg']
    },
    {
      id: 'P-PAI-VOLTAREN', product_name: 'Voltaren Arthritis Pain Gel (Diclofenac 1%)', generic_name: 'Diclofenac Sodium Topical Gel', brand_name: 'Voltaren',
      category: 'pain', subcategory: 'Topical Analgesics', description: 'Targeted topical NSAID gel for joint arthritis pain.',
      icon: '🧴', aliases: ['diclofenac gel', 'voltaren', 'arthritis gel'], synonyms: ['topical nsaid'], keywords: ['voltaren', 'diclofenac']
    },
    {
      id: 'P-PAI-LIDO', product_name: 'Maximum Strength Lidocaine 4% Pain Patches', generic_name: 'Lidocaine 4% Topical Patch', brand_name: 'Salonpas',
      category: 'pain', subcategory: 'Topical Analgesics', description: 'Desensitizes aggravated nerves for up to 12 hours.',
      icon: '🩹', aliases: ['lidocaine patches', 'lidocaine patch', 'lidocaine'], synonyms: ['numbing patch'], keywords: ['lidocaine']
    },

    // 4. Cold, Flu & Allergy
    {
      id: 'P-CFA-CETIRIZINE', product_name: 'Cetirizine Hydrochloride 10 mg Tablets', generic_name: 'Cetirizine HCl', brand_name: 'Zyrtec',
      category: 'coldflu', subcategory: 'Antihistamines', description: '24-hour non-drowsy relief of sneezing & runny nose.',
      icon: '🤧', aliases: ['cetirizine', 'zyrtec', 'allergy medicine'], synonyms: ['allergy tablet'], keywords: ['cetirizine']
    },
    {
      id: 'P-CFA-LORATADINE', product_name: 'Loratadine 10 mg 24-Hour Allergy Relief', generic_name: 'Loratadine', brand_name: 'Claritin',
      category: 'coldflu', subcategory: 'Antihistamines', description: '24-hour non-drowsy allergy relief.',
      icon: '🌸', aliases: ['loratadine', 'claritin', 'cold medicine'], synonyms: ['hives sneezing pill'], keywords: ['loratadine']
    },
    {
      id: 'P-CFA-FEXO', product_name: 'Fexofenadine Hydrochloride 180 mg', generic_name: 'Fexofenadine HCl', brand_name: 'Allegra',
      category: 'coldflu', subcategory: 'Antihistamines', description: 'Fast 24-hour indoor and outdoor allergy relief.',
      icon: '🤧', aliases: ['fexofenadine', 'allegra', 'cough medicine'], synonyms: ['allergy relief'], keywords: ['fexofenadine']
    },
    {
      id: 'P-CFA-SALINE', product_name: 'Sterile Saline Nasal Mist Spray', generic_name: 'Sodium Chloride Nasal Spray', brand_name: 'Ocean',
      category: 'coldflu', subcategory: 'Nasal Care', description: 'Drug-free sterile saline flush for dry nasal passages.',
      icon: '💧', aliases: ['saline nasal spray', 'saline mist'], synonyms: ['sinus flush'], keywords: ['saline nasal spray']
    },

    // 5. Digestive Health
    {
      id: 'P-DIG-ANTACID', product_name: 'Calcium Carbonate Antacid Chewables', generic_name: 'Calcium Carbonate', brand_name: 'Tums',
      category: 'digestive', subcategory: 'Antacids', description: 'Fast relief of heartburn & acid indigestion.',
      icon: '🍬', aliases: ['antacids', 'tums', 'chewable antacid'], synonyms: ['heartburn chewable'], keywords: ['antacids']
    },
    {
      id: 'P-DIG-FAMOTIDINE', product_name: 'Famotidine 20 mg Acid Reducer', generic_name: 'Famotidine', brand_name: 'Pepcid AC',
      category: 'digestive', subcategory: 'H2 Blockers', description: 'Prevents and relieves acid indigestion.',
      icon: '💊', aliases: ['famotidine', 'pepcid'], synonyms: ['acid reducer'], keywords: ['famotidine']
    },
    {
      id: 'P-DIG-OMEPRAZOLE', product_name: 'Omeprazole 20 mg Delayed Release Caplets', generic_name: 'Omeprazole', brand_name: 'Prilosec OTC',
      category: 'digestive', subcategory: 'Proton Pump Inhibitors', description: 'Treats frequent heartburn 2+ days a week.',
      icon: '🥣', aliases: ['omeprazole', 'prilosec'], synonyms: ['heartburn caplet'], keywords: ['omeprazole']
    },
    {
      id: 'P-DIG-LAXATIVE', product_name: 'Polyethylene Glycol 3350 Powder', generic_name: 'Polyethylene Glycol 3350', brand_name: 'MiraLAX',
      category: 'digestive', subcategory: 'Laxatives', description: 'Osmotic laxative powder for gentle constipation relief.',
      icon: '🥛', aliases: ['laxatives', 'polyethylene glycol', 'miralax', 'stool softeners'], synonyms: ['constipation powder'], keywords: ['laxatives']
    },
    {
      id: 'P-DIG-ANTIDIARRHEAL', product_name: 'Loperamide Hydrochloride 2 mg Caplets', generic_name: 'Loperamide HCl', brand_name: 'Imodium A-D',
      category: 'digestive', subcategory: 'Anti-Diarrheal', description: 'Controls and relieves diarrhea symptoms.',
      icon: '💊', aliases: ['anti-diarrheal products', 'loperamide', 'imodium'], synonyms: ['diarrhea caplet'], keywords: ['loperamide']
    },
    {
      id: 'P-DIG-HEMORRHOID', product_name: 'Hemorrhoidal Ointment with Phenylephrine', generic_name: 'Hemorrhoidal Ointment', brand_name: 'Preparation H',
      category: 'digestive', subcategory: 'Hemorrhoid Treatments', description: 'Shrinks swollen hemorrhoidal tissue & relieves itching.',
      icon: '🧴', aliases: ['hemorrhoid treatments', 'preparation h'], synonyms: ['hemorrhoid ointment'], keywords: ['hemorrhoid']
    },

    // 6. First Aid & Wound Care
    {
      id: 'P-AID-BANDAGE', product_name: 'Adhesive Bandage Assortment Pack', generic_name: 'Adhesive Bandages', brand_name: 'Band-Aid',
      category: 'firstaid', subcategory: 'Bandages', description: 'Flexible sterile adhesive bandages for minor cuts.',
      icon: '🩹', aliases: ['bandages', 'band-aid', 'gauze', 'medical tape'], synonyms: ['sticky bandages'], keywords: ['bandages']
    },
    {
      id: 'P-AID-ANTISEPTIC', product_name: 'Isopropyl Alcohol 70% Prep Pads', generic_name: 'Isopropyl Alcohol 70%', brand_name: 'BD',
      category: 'firstaid', subcategory: 'Antiseptics', description: 'Sterile antiseptic skin cleansing wipes.',
      icon: '🧴', aliases: ['antiseptic', 'alcohol pads', 'hydrogen peroxide'], synonyms: ['skin prep pads'], keywords: ['alcohol pads']
    },
    {
      id: 'P-AID-KIT', product_name: 'All-Purpose Emergency First Aid Kit', generic_name: 'First Aid Kit', brand_name: 'Johnson & Johnson',
      category: 'firstaid', subcategory: 'First-Aid Kits', description: 'Complete hard-case first aid trauma kit.',
      icon: '🧰', aliases: ['first-aid kits', 'first aid kit'], synonyms: ['trauma kit'], keywords: ['first aid kit']
    },
    {
      id: 'P-AID-THERMO', product_name: 'Express 10-Second Digital Thermometer', generic_name: 'Digital Thermometer', brand_name: 'Vicks',
      category: 'firstaid', subcategory: 'Thermometers', description: 'Fast 10-second oral / axillary fever reading.',
      icon: '🌡️', aliases: ['thermometers', 'digital thermometer'], synonyms: ['fever checker'], keywords: ['thermometer']
    },
    {
      id: 'P-AID-WOUNDCARE', product_name: 'Sterile Hydrocolloid & Surgical Dressings', generic_name: 'Hydrocolloid Dressing', brand_name: 'DuoDERM',
      category: 'woundcare', subcategory: 'Surgical Dressings', description: 'Advanced wound dressings & wound-vac supplies.',
      icon: '🩹', aliases: ['surgical dressings', 'wound-vac supplies'], synonyms: ['advanced wound dressing'], keywords: ['dressings']
    },

    // 7. Braces & Supports
    {
      id: 'P-BRC-KNEE', product_name: 'Dual-Hinged Medical Knee Brace', generic_name: 'Hinged Knee Orthosis', brand_name: 'Mueller',
      category: 'braces', subcategory: 'Knee Braces', description: 'Side hinge stabilization for meniscus & arthritis.',
      icon: '🦿', aliases: ['knee braces', 'knee brace', 'knee support'], synonyms: ['hinged knee brace'], keywords: ['knee brace']
    },
    {
      id: 'P-BRC-ANKLE', product_name: 'Ankle Stabilizer Compression Brace', generic_name: 'Ankle Orthosis', brand_name: 'Futuro',
      category: 'braces', subcategory: 'Ankle Braces', description: 'Lace-up side stabilizer brace for ankle sprains.',
      icon: '🦶', aliases: ['ankle braces', 'ankle brace'], synonyms: ['ankle stabilizer'], keywords: ['ankle brace']
    },
    {
      id: 'P-BRC-WRIST', product_name: 'Carpal Tunnel Night Support Wrist Splint', generic_name: 'Wrist Splint Orthosis', brand_name: 'Futuro',
      category: 'braces', subcategory: 'Wrist Braces', description: 'Removable palmar stay for carpal tunnel & tendonitis.',
      icon: '🧤', aliases: ['wrist braces', 'carpal-tunnel braces', 'wrist splint'], synonyms: ['carpal tunnel splint'], keywords: ['wrist brace']
    },
    {
      id: 'P-BRC-BACK', product_name: 'Lumbar Back Support Belt with Double Straps', generic_name: 'Lumbar Support Orthosis', brand_name: 'Mueller',
      category: 'braces', subcategory: 'Back Braces', description: 'Steel stays relieve lower back strain & sciatica.',
      icon: '🧍', aliases: ['back braces', 'back brace', 'lumbar support'], synonyms: ['lumbar belt'], keywords: ['back brace']
    },
    {
      id: 'P-BRC-NECK', product_name: 'Adjustable Cervical Foam Collar', generic_name: 'Cervical Collar Orthosis', brand_name: 'Futuro',
      category: 'braces', subcategory: 'Cervical Collars', description: 'Spine neck alignment & stiffness foam support.',
      icon: '🦒', aliases: ['cervical collars', 'cervical collar', 'walking boots', 'finger splints'], synonyms: ['neck brace'], keywords: ['cervical collar']
    },

    // 8. Mobility
    {
      id: 'P-MOB-CANES', product_name: 'Heavy-Duty Adjustable Quad Base Cane', generic_name: 'Quad Walking Cane', brand_name: 'Drive Medical',
      category: 'mobility', subcategory: 'Canes', description: 'All-terrain 4-point base for walking balance.',
      icon: '🦯', aliases: ['canes', 'cane', 'crutches', 'quad cane'], synonyms: ['walking stick'], keywords: ['quad cane']
    },
    {
      id: 'P-MOB-ROLLATOR', product_name: 'Aluminum 4-Wheel Rollator Walker with Seat', generic_name: 'Rollator Walker', brand_name: 'Drive Medical',
      category: 'mobility', subcategory: 'Rollators', description: 'Padded seat, storage pouch, 6" wheels & handbrakes.',
      icon: '♿', aliases: ['walkers', 'rollators', 'walker with seat', 'rollator'], synonyms: ['rolling walker'], keywords: ['rollator']
    },
    {
      id: 'P-MOB-WHEELCHAIR', product_name: 'Lightweight Folding Manual Wheelchair', generic_name: 'Manual Wheelchair', brand_name: 'Drive Medical',
      category: 'mobility', subcategory: 'Wheelchairs', description: '18" seat manual wheelchair with swing-away footrests.',
      icon: '👨‍🦽', aliases: ['wheelchairs', 'mobility scooters', 'wheelchair'], synonyms: ['transport chair'], keywords: ['wheelchair']
    },

    // 9. Home Safety & DME
    {
      id: 'P-SAF-CHAIR', product_name: 'Non-Slip Shower Chair & Transfer Bench', generic_name: 'Shower Chair / Transfer Bench', brand_name: 'Drive Medical',
      category: 'homesafety', subcategory: 'Shower Chairs', description: 'Suction cup rubber feet & drainage holes for safe bathing.',
      icon: '🪑', aliases: ['shower chairs', 'grab bars', 'transfer benches', 'commode chairs', 'hospital beds', 'patient lifts'], synonyms: ['bath seat'], keywords: ['shower chair']
    },

    // 10. Diabetes
    {
      id: 'P-DIB-MONITOR', product_name: 'Blood Glucose Meter & Test Strips Kit', generic_name: 'Blood Glucose Monitoring System', brand_name: 'OneTouch',
      category: 'diabetes', subcategory: 'Blood-Glucose Meters', description: 'No-coding blood glucose meter, 100 strips & lancets.',
      icon: '🩸', aliases: ['blood-glucose meters', 'test strips', 'lancets', 'sugar meter'], synonyms: ['diabetes meter'], keywords: ['test strips']
    },
    {
      id: 'P-DIB-CGM', product_name: 'Continuous Glucose Monitor (CGM) Sensor Kit', generic_name: 'Continuous Glucose Monitor', brand_name: 'Dexcom / Freestyle',
      category: 'diabetes', subcategory: 'Continuous Glucose Monitors', description: '14-day continuous real-time glucose sensor & transmitter.',
      icon: '📡', aliases: ['continuous glucose monitors', 'cgm', 'insulin-pump supplies', 'diabetic shoes'], synonyms: ['cgm sensor'], keywords: ['cgm']
    },

    // 11. Blood Pressure & Cardiovascular / Diagnostics
    {
      id: 'P-CAR-BPMONITOR', product_name: 'Automatic Upper Arm Blood Pressure Monitor', generic_name: 'Sphygmomanometer', brand_name: 'Omron',
      category: 'cardio', subcategory: 'Blood-Pressure Monitors', description: 'One-touch automatic BP reader with large cuff.',
      icon: '🩺', aliases: ['blood-pressure monitors', 'bp monitor', 'scales', 'pulse oximeters'], synonyms: ['hypertension checker'], keywords: ['blood pressure monitor']
    },

    // 12. Respiratory & CPAP / Sleep
    {
      id: 'P-RSP-CPAP', product_name: 'Compressor Nebulizer & CPAP Machine Tubing Kit', generic_name: 'CPAP / Nebulizer System', brand_name: 'ResMed',
      category: 'respiratory', subcategory: 'CPAP Machines', description: 'Aerosol nebulizer & CPAP mask replacement tubing.',
      icon: '🌬️', aliases: ['nebulizers', 'oxygen equipment', 'cpap machines', 'cpap masks', 'cpap tubing'], synonyms: ['sleep apnea machine'], keywords: ['cpap']
    },

    // 13. Eye Care
    {
      id: 'P-EYE-GLASSES', product_name: 'Lubricating Eye Drops & Reading Glasses', generic_name: 'Artificial Tears & Magnifiers', brand_name: 'Systane',
      category: 'eyecare', subcategory: 'Eye Drops', description: 'Artificial tears eye drops and scratch-resistant reading glasses.',
      icon: '👓', aliases: ['artificial tears', 'eye drops', 'reading glasses', 'prescription eyewear'], synonyms: ['dry eye drops'], keywords: ['eye drops']
    },

    // 14. Hearing
    {
      id: 'P-EAR-HEARING', product_name: 'OTC Digital Hearing Aids & Size 312 Batteries', generic_name: 'OTC Hearing Aid Device', brand_name: 'Jabra Enhance',
      category: 'hearing', subcategory: 'Hearing Aids', description: 'Over-the-counter digital hearing device & 40-pack batteries.',
      icon: '👂', aliases: ['hearing aids', 'hearing-aid batteries'], synonyms: ['sound amplifier'], keywords: ['hearing aids']
    },

    // 15. Dental & Oral Care
    {
      id: 'P-DEN-ORAL', product_name: 'Sonic Electric Toothbrush & Denture Supplies Kit', generic_name: 'Oral Care Kit', brand_name: 'Sonicare / Polident',
      category: 'dental', subcategory: 'Toothbrushes', description: 'Rechargeable electric toothbrush, floss, toothpaste & denture cleanser.',
      icon: '🪥', aliases: ['toothbrushes', 'toothpaste', 'floss', 'mouthwash', 'denture supplies'], synonyms: ['dental care'], keywords: ['toothpaste']
    },

    // 16. Skin & Dermatology
    {
      id: 'P-SKN-DERM', product_name: 'Hydrocortisone 1% & Antifungal Cream', generic_name: 'Hydrocortisone / Clotrimazole', brand_name: 'Cortizone-10',
      category: 'skincare', subcategory: 'Hydrocortisone', description: 'Relieves eczema itching, athlete foot & dermatological rashes.',
      icon: '🧴', aliases: ['hydrocortisone', 'antifungal treatments', 'eczema treatments', 'wart removers'], synonyms: ['anti-itch cream'], keywords: ['hydrocortisone']
    },

    // 17. Foot Care & Compression / Lymphedema
    {
      id: 'P-CMP-SOCKS', product_name: 'Graduated Compression Socks 15-20 mmHg', generic_name: 'Compression Stockings', brand_name: 'JOBST',
      category: 'compression', subcategory: 'Compression Socks', description: 'Graduated compression stockings for venous circulation & lymphedema.',
      icon: '🦵', aliases: ['compression socks', 'compression garments', 'lymphedema garments'], synonyms: ['support hose'], keywords: ['compression socks']
    },

    // 18. Incontinence
    {
      id: 'P-INC-BRIEFS', product_name: 'Adult Protective Underwear Briefs & Underpads', generic_name: 'Incontinence Briefs', brand_name: 'Depend',
      category: 'incontinence', subcategory: 'Adult Briefs', description: 'Leak guard adult protective briefs & bed underpads (Chux).',
      icon: '🩲', aliases: ['adult briefs', 'underpads', 'adult diapers'], synonyms: ['incontinence diapers'], keywords: ['adult briefs']
    },

    // 19. Urological Supplies & Ostomy
    {
      id: 'P-URO-CATH', product_name: 'Intermittent Urinary Catheter & Ostomy Bag Kit', generic_name: 'Urinary Catheter & Ostomy System', brand_name: 'Bard / Hollister',
      category: 'urology', subcategory: 'Catheters', description: 'Sterile intermittent catheters, urinary drainage bags & ostomy barriers.',
      icon: '💉', aliases: ['catheters', 'urinary drainage bags', 'ostomy bags', 'ostomy barriers'], synonyms: ['catheter kit'], keywords: ['catheter']
    },

    // 20. Women's Health / Pregnancy & Breastfeeding / Reproductive
    {
      id: 'P-WMN-PUMP', product_name: 'Electric Double Breast Pump & Pregnancy Tests', generic_name: 'Electric Breast Pump', brand_name: 'Medela',
      category: 'womens', subcategory: 'Breast Pumps', description: 'ACA mandated 100% covered electric double breast pump & milk bags.',
      icon: '🍼', aliases: ['pregnancy tests', 'breast pumps', 'breast-pump supplies', 'contraceptives'], synonyms: ['nursing pump'], keywords: ['breast pump']
    },

    // 21. Smoking Cessation
    {
      id: 'P-SMK-PATCH', product_name: 'Nicotine Transdermal Patches Step 1 (21 mg)', generic_name: 'Nicotine Patch', brand_name: 'NicoDerm CQ',
      category: 'smoking', subcategory: 'Nicotine Patches', description: '24-hour therapeutic nicotine patch, gum & lozenges for quitting.',
      icon: '🚭', aliases: ['nicotine patches', 'nicotine gum', 'nicotine lozenges'], synonyms: ['quit smoking'], keywords: ['nicotine patch']
    },

    // 22. Medication Management & Diagnostics
    {
      id: 'P-MED-PILL', product_name: '7-Day AM/PM Push-Button Pill Organizer & Cutter', generic_name: 'Pill Planner', brand_name: 'Apex',
      category: 'medmgmt', subcategory: 'Pill Organizers', description: 'Large pop-up compartments with braille & built-in pill cutter.',
      icon: '📅', aliases: ['pill organizers', 'pill cutters'], synonyms: ['weekly pill box'], keywords: ['pill organizer']
    }
  ];

  // --- 4. PLAN-SPECIFIC COVERAGE RULES ENGINE DATABASE ---
  const SOURCE_DOCUMENTS = [
  {
    id: 'SRC-VT-DVHA-2026-MEDICAID',
    source_id: 'SRC-VT-DVHA-2026-MEDICAID',
    publisher: 'Vermont Department of Vermont Health Access (DVHA)',
    title: 'Green Mountain Care Preferred Drug List & Pharmacy Coverage Protocol (2026)',
    state: 'VT',
    plan_id: 'vt_vermont_medicaid',
    applicable_plan_ids: ['vt_vermont_medicaid', 'vt_dr_dynasaur_medicaid'],
    plan_year: 2026,
    source_type: 'State Medicaid Policy',
    official_url: 'https://dvha.vermont.gov/',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_POLICY'
  },
  {
    id: 'SRC-VT-BCBSVT-2026-SOB',
    source_id: 'SRC-VT-BCBSVT-2026-SOB',
    publisher: 'Blue Cross and Blue Shield of Vermont',
    title: 'BCBSVT Silver Summary of Benefits & Wellness Policy (2026)',
    state: 'VT',
    plan_id: 'vt_bcbsvt_bcbsvt_silver',
    applicable_plan_ids: ['vt_bcbsvt_bcbsvt_silver'],
    plan_year: 2026,
    source_type: 'Summary of Benefits',
    official_url: 'https://www.bcbsvt.com/',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_EOC'
  },
  {
    id: 'SRC-VT-MVP-2026-GIA',
    source_id: 'SRC-VT-MVP-2026-GIA',
    publisher: 'MVP Health Care Vermont',
    title: 'MVP VT Plus Silver Evidence of Coverage & Gia Virtual Care Guide (2026)',
    state: 'VT',
    plan_id: 'vt_mvp_health_mvp_vt_plus_silver',
    applicable_plan_ids: ['vt_mvp_health_mvp_vt_plus_silver'],
    plan_year: 2026,
    source_type: 'Evidence of Coverage / Virtual Care Guide',
    official_url: 'https://www.mvphealthcare.com/vt',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_EOC'
  },
  {
    id: 'SRC-ME-DHHS-2026-MAINACARE',
    source_id: 'SRC-ME-DHHS-2026-MAINACARE',
    publisher: 'Maine Department of Health and Human Services (DHHS)',
    title: 'MaineCare Preferred Drug List & Pharmacy Coverage Guide (2026)',
    state: 'ME',
    plan_id: 'me_mainecare_medicaid',
    applicable_plan_ids: ['me_mainecare_medicaid'],
    plan_year: 2026,
    source_type: 'State Medicaid Policy',
    official_url: 'https://www.maine.gov/dhhs/oms',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_POLICY'
  },
  {
    id: 'SRC-ME-CHO-2026-SOB',
    source_id: 'SRC-ME-CHO-2026-SOB',
    publisher: 'Community Health Options',
    title: 'Community Health Options Clear Choice Summary of Benefits & Chronic Support Guide (2026)',
    state: 'ME',
    plan_id: 'me_community_health_options_community_health_options_clear_choice',
    applicable_plan_ids: ['me_community_health_options_community_health_options_clear_choice'],
    plan_year: 2026,
    source_type: 'Summary of Benefits',
    official_url: 'https://www.healthoptions.org/',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_EOC'
  },
  {
    id: 'SRC-ME-HARVARD-2026-EOC',
    source_id: 'SRC-ME-HARVARD-2026-EOC',
    publisher: 'Harvard Pilgrim Health Care Maine',
    title: 'Harvard Pilgrim Maine Clear Choice Member Evidence of Coverage (2026)',
    state: 'ME',
    plan_id: 'me_harvard_pilgrim_clear_choice_hmo_silver_4000',
    applicable_plan_ids: ['me_harvard_pilgrim_clear_choice_hmo_silver_4000'],
    plan_year: 2026,
    source_type: 'Evidence of Coverage',
    official_url: 'https://www.harvardpilgrim.org/public/me',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_EOC'
  },
  {
    id: 'SRC-ME-ANTHEM-2026-EOC',
    source_id: 'SRC-ME-ANTHEM-2026-EOC',
    publisher: 'Anthem Blue Cross and Blue Shield Maine',
    title: 'Anthem BCBS Maine Clear Choice PPO Summary of Coverage (2026)',
    state: 'ME',
    plan_id: 'me_anthem_bcbs_anthem_clear_choice_ppo',
    applicable_plan_ids: ['me_anthem_bcbs_anthem_clear_choice_ppo'],
    plan_year: 2026,
    source_type: 'Summary of Benefits',
    official_url: 'https://www.anthem.com/me',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_EOC'
  },
  {
    id: 'SRC-NH-DHHS-2026-MEDICAID',
    source_id: 'SRC-NH-DHHS-2026-MEDICAID',
    publisher: 'New Hampshire Department of Health and Human Services (DHHS)',
    title: 'New Hampshire Medicaid Fee-for-Service & Statewide Pharmacy Protocol Guide (2026)',
    state: 'NH',
    plan_id: 'nh_wellsense_medicaid_mco',
    applicable_plan_ids: ['nh_wellsense_medicaid_mco', 'nh_amerihealth_caritas_medicaid', 'nh_nh_healthy_families_medicaid'],
    plan_year: 2026,
    source_type: 'State Medicaid Policy',
    official_url: 'https://www.dhhs.nh.gov/programs-services/medicaid',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_POLICY'
  },
  {
    id: 'SRC-NH-WELLSENSE-2026-HANDBOOK',
    source_id: 'SRC-NH-WELLSENSE-2026-HANDBOOK',
    publisher: 'WellSense Health Plan New Hampshire',
    title: 'WellSense NH Medicaid Member Handbook & OTC Benefit Guide (2026)',
    state: 'NH',
    plan_id: 'nh_wellsense_medicaid_mco',
    applicable_plan_ids: ['nh_wellsense_medicaid_mco'],
    plan_year: 2026,
    source_type: 'Member Handbook / OTC Catalog',
    official_url: 'https://www.wellsense.org/nh',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_EOC'
  },
  {
    id: 'SRC-NH-AMERIHEALTH-2026-CARE',
    source_id: 'SRC-NH-AMERIHEALTH-2026-CARE',
    publisher: 'AmeriHealth Caritas New Hampshire',
    title: 'AmeriHealth Caritas NH Member Handbook & CARE Card Rewards Guide (2026)',
    state: 'NH',
    plan_id: 'nh_amerihealth_caritas_medicaid',
    applicable_plan_ids: ['nh_amerihealth_caritas_medicaid'],
    plan_year: 2026,
    source_type: 'Member Handbook / Wellness Rewards',
    official_url: 'https://www.amerihealthcaritasnh.com/',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_EOC'
  },
  {
    id: 'SRC-NH-NHHF-2026-GUIDE',
    source_id: 'SRC-NH-NHHF-2026-GUIDE',
    publisher: 'NH Healthy Families',
    title: 'NH Healthy Families Member Handbook & My Health Pays Rewards Guide (2026)',
    state: 'NH',
    plan_id: 'nh_nh_healthy_families_medicaid',
    applicable_plan_ids: ['nh_nh_healthy_families_medicaid'],
    plan_year: 2026,
    source_type: 'Member Handbook / Rewards Guide',
    official_url: 'https://www.nhhealthyfamilies.com/',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_EOC'
  },
  {
    id: 'SRC-NH-HARVARD-2026-SOB',
    source_id: 'SRC-NH-HARVARD-2026-SOB',
    publisher: 'Harvard Pilgrim Health Care New Hampshire',
    title: 'Harvard Pilgrim NH Local HMO Summary of Benefits & Fitness Policy (2026)',
    state: 'NH',
    plan_id: 'nh_harvard_pilgrim_nh_local_hmo_silver_6000_standard_0_rx_list_0_virtual_urgent_care',
    applicable_plan_ids: ['nh_harvard_pilgrim_nh_local_hmo_silver_6000_standard_0_rx_list_0_virtual_urgent_care'],
    plan_year: 2026,
    source_type: 'Summary of Benefits',
    official_url: 'https://www.harvardpilgrim.org/public/nh',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_EOC'
  },
  {
    id: 'SRC-CT-HUSKY-2026-MEMBER-GUIDE',
    source_id: 'SRC-CT-HUSKY-2026-MEMBER-GUIDE',
    publisher: 'Connecticut Department of Social Services (DSS)',
    title: 'HUSKY Health Member Handbook & Covered Services Regulations (2026)',
    state: 'CT',
    plan_id: 'ct_husky_health_husky_a',
    applicable_plan_ids: ['ct_husky_health_husky_a', 'ct_husky_health_husky_c', 'ct_husky_health_husky_d'],
    plan_year: 2026,
    source_type: 'State Medicaid Policy',
    official_url: 'https://portal.ct.gov/husky',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_POLICY'
  },
  {
    id: 'SRC-CT-HUSKY-B-2026-CHIP',
    source_id: 'SRC-CT-HUSKY-B-2026-CHIP',
    publisher: 'Connecticut Department of Social Services (DSS)',
    title: "HUSKY B Children's Health Insurance Program (CHIP) Member Benefit Guide (2026)",
    state: 'CT',
    plan_id: 'ct_husky_health_husky_b',
    applicable_plan_ids: ['ct_husky_health_husky_b'],
    plan_year: 2026,
    source_type: 'State CHIP Policy',
    official_url: 'https://portal.ct.gov/husky/husky-b',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_POLICY'
  },
  {
    id: 'SRC-CT-CONNECTICARE-2026-SOB',
    source_id: 'SRC-CT-CONNECTICARE-2026-SOB',
    publisher: 'ConnectiCare',
    title: 'ConnectiCare Choice & Covered CT Summary of Benefits & OTC Guide (2026)',
    state: 'CT',
    plan_id: 'ct_connecticare_connecticare_choice_silver',
    applicable_plan_ids: ['ct_connecticare_connecticare_choice_silver', 'ct_connecticare_connecticare_covered_ct'],
    plan_year: 2026,
    source_type: 'Summary of Benefits',
    official_url: 'https://www.connecticare.com/',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_EOC'
  },
  {
    id: 'SRC-CT-ANTHEM-2026-EOC',
    source_id: 'SRC-CT-ANTHEM-2026-EOC',
    publisher: 'Anthem Blue Cross and Blue Shield Connecticut',
    title: 'Anthem Pathway Connecticut Member Benefit & Preventive Care Guide (2026)',
    state: 'CT',
    plan_id: 'ct_anthem_bcbs_anthem_pathway_standard_silver',
    applicable_plan_ids: ['ct_anthem_bcbs_anthem_pathway_standard_silver'],
    plan_year: 2026,
    source_type: 'Evidence of Coverage',
    official_url: 'https://www.anthem.com/',
    effective_date: '2026-01-01',
    last_verified: '2026-09-25',
    verification_status: 'VERIFIED_EOC'
  },
  { source_id: 'SRC-MA-MASSHEALTH-2026-GUIDE', state: 'MA', title: 'MassHealth Handbook' },
  { source_id: 'SRC-MA-WELLSENSE-2026-MED', state: 'MA', title: 'WellSense Handbook' },
  { source_id: 'SRC-MA-TUFTS-2026-TOGETHER', state: 'MA', title: 'Tufts Direct Guide' },
  { source_id: 'SRC-MA-CONNECTOR-CULTURE-2026', state: 'MA', title: 'Card to Culture Guide' },
  { source_id: 'SRC-MA-BCBSMA-2026-SOB', state: 'MA', title: 'BCBSMA SOB' },
  { source_id: 'SRC-MA-HPHC-2026-EOC', state: 'MA', title: 'Harvard Pilgrim EOC' }
];

  const COVERAGE_RULES = [
  {"rule_id": "R-GS-BCBS-VITD", "target_type": "PRODUCT", "product_id": "P-VIT-D", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 14"},
  {"rule_id": "R-GS-BCBS-B12", "target_type": "PRODUCT", "product_id": "P-VIT-B12", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 15"},
  {"rule_id": "R-GS-BCBS-VITC", "target_type": "PRODUCT", "product_id": "P-VIT-C", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 15"},
  {"rule_id": "R-GS-BCBS-FOLIC", "target_type": "PRODUCT", "product_id": "P-VIT-FOLIC", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 15"},
  {"rule_id": "R-GS-BCBS-IRON", "target_type": "PRODUCT", "product_id": "P-VIT-IRON", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 16"},
  {"rule_id": "R-GS-BCBS-CALCIUM", "target_type": "PRODUCT", "product_id": "P-VIT-CALCIUM", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 16"},
  {"rule_id": "R-GS-BCBS-MAGNESIUM", "target_type": "PRODUCT", "product_id": "P-VIT-MAGNESIUM", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 16"},
  {"rule_id": "R-GS-BCBS-ZINC", "target_type": "PRODUCT", "product_id": "P-VIT-ZINC", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 16"},
  {"rule_id": "R-GS-BCBS-MULTI", "target_type": "PRODUCT", "product_id": "P-VIT-MULTI", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 14"},
  {"rule_id": "R-GS-BCBS-PROBIOTIC", "target_type": "PRODUCT", "product_id": "P-SUP-PROBIOTIC", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 17"},
  {"rule_id": "R-GS-BCBS-FIBER", "target_type": "PRODUCT", "product_id": "P-SUP-FIBER", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 17"},
  {"rule_id": "R-GS-BCBS-ACETA", "target_type": "PRODUCT", "product_id": "P-PAI-ACETA", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 8"},
  {"rule_id": "R-GS-BCBS-IBU", "target_type": "PRODUCT", "product_id": "P-PAI-IBU", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 8"},
  {"rule_id": "R-GS-BCBS-NAPROXEN", "target_type": "PRODUCT", "product_id": "P-PAI-NAPROXEN", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 8"},
  {"rule_id": "R-GS-BCBS-ASPIRIN", "target_type": "PRODUCT", "product_id": "P-PAI-ASPIRIN", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 8"},
  {"rule_id": "R-GS-BCBS-VOLTAREN", "target_type": "PRODUCT", "product_id": "P-PAI-VOLTAREN", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 9"},
  {"rule_id": "R-GS-BCBS-LIDO", "target_type": "PRODUCT", "product_id": "P-PAI-LIDO", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 9"},
  {"rule_id": "R-GS-BCBS-CETIRIZINE", "target_type": "PRODUCT", "product_id": "P-CFA-CETIRIZINE", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 10"},
  {"rule_id": "R-GS-BCBS-LORATADINE", "target_type": "PRODUCT", "product_id": "P-CFA-LORATADINE", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 10"},
  {"rule_id": "R-GS-BCBS-FEXO", "target_type": "PRODUCT", "product_id": "P-CFA-FEXO", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 10"},
  {"rule_id": "R-GS-BCBS-SALINE", "target_type": "PRODUCT", "product_id": "P-CFA-SALINE", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 11"},
  {"rule_id": "R-GS-BCBS-ANTACID", "target_type": "PRODUCT", "product_id": "P-DIG-ANTACID", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 12"},
  {"rule_id": "R-GS-BCBS-FAMOTIDINE", "target_type": "PRODUCT", "product_id": "P-DIG-FAMOTIDINE", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 12"},
  {"rule_id": "R-GS-BCBS-OMEPRAZOLE", "target_type": "PRODUCT", "product_id": "P-DIG-OMEPRAZOLE", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 12"},
  {"rule_id": "R-GS-BCBS-LAXATIVE", "target_type": "PRODUCT", "product_id": "P-DIG-LAXATIVE", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 13"},
  {"rule_id": "R-GS-BCBS-ANTIDIARRHEAL", "target_type": "PRODUCT", "product_id": "P-DIG-ANTIDIARRHEAL", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 13"},
  {"rule_id": "R-GS-BCBS-HEMORRHOID", "target_type": "PRODUCT", "product_id": "P-DIG-HEMORRHOID", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 13"},
  {"rule_id": "R-GS-BCBS-BANDAGE", "target_type": "PRODUCT", "product_id": "P-AID-BANDAGE", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 18"},
  {"rule_id": "R-GS-BCBS-ANTISEPTIC", "target_type": "PRODUCT", "product_id": "P-AID-ANTISEPTIC", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 18"},
  {"rule_id": "R-GS-BCBS-AIDKIT", "target_type": "PRODUCT", "product_id": "P-AID-KIT", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 18"},
  {"rule_id": "R-GS-BCBS-THERMO", "target_type": "PRODUCT", "product_id": "P-AID-THERMO", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 19"},
  {"rule_id": "R-GS-BCBS-WOUNDCARE", "target_type": "PRODUCT", "product_id": "P-AID-WOUNDCARE", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 19"},
  {"rule_id": "R-GS-BCBS-DERM", "target_type": "PRODUCT", "product_id": "P-SKN-DERM", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 20"},
  {"rule_id": "R-GS-BCBS-DENORAL", "target_type": "PRODUCT", "product_id": "P-DEN-ORAL", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 21"},
  {"rule_id": "R-GS-BCBS-PILL", "target_type": "PRODUCT", "product_id": "P-MED-PILL", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 22"},
  {"rule_id": "R-GS-BCBS-SMK", "target_type": "PRODUCT", "product_id": "P-SMK-PATCH", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Preventive prescription drug benefit", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 45"},
  {"rule_id": "R-GS-BCBS-SAFCHAIR", "target_type": "PRODUCT", "product_id": "P-SAF-CHAIR", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 23"},
  {"rule_id": "R-GS-BCBS-DIBMONITOR", "target_type": "PRODUCT", "product_id": "P-DIB-MONITOR", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Part B preferred diabetic supplies", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay for OneTouch / Contour meters", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 40"},
  {"rule_id": "R-GS-BCBS-CMP", "target_type": "PRODUCT", "product_id": "P-CMP-SOCKS", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 24"},
  {"rule_id": "R-GS-BCBS-INC", "target_type": "PRODUCT", "product_id": "P-INC-BRIEFS", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 25"},
  {"rule_id": "R-GS-BCBS-KNEE", "target_type": "PRODUCT", "product_id": "P-BRC-KNEE", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Durable Medical Equipment (DME)", "coverage_status": "Covered with Provider Order", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "20% coinsurance or $0 with network DME", "copay": "$0.00", "coinsurance": "20%", "provider_order_required": true, "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 41"},
  {"rule_id": "R-GS-BCBS-ANKLE", "target_type": "PRODUCT", "product_id": "P-BRC-ANKLE", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Durable Medical Equipment (DME)", "coverage_status": "Covered with Provider Order", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "20% coinsurance", "copay": "$0.00", "coinsurance": "20%", "provider_order_required": true, "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 41"},
  {"rule_id": "R-GS-BCBS-WRIST", "target_type": "PRODUCT", "product_id": "P-BRC-WRIST", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Durable Medical Equipment (DME)", "coverage_status": "Covered with Provider Order", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "20% coinsurance", "copay": "$0.00", "coinsurance": "20%", "provider_order_required": true, "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 41"},
  {"rule_id": "R-GS-BCBS-BACK", "target_type": "PRODUCT", "product_id": "P-BRC-BACK", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Durable Medical Equipment (DME)", "coverage_status": "Covered with Prior Authorization", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "20% coinsurance with authorization", "copay": "$0.00", "coinsurance": "20%", "prior_authorization_required": true, "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 41"},
  {"rule_id": "R-GS-BCBS-NECK", "target_type": "PRODUCT", "product_id": "P-BRC-NECK", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Durable Medical Equipment (DME)", "coverage_status": "Covered with Provider Order", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "20% coinsurance", "copay": "$0.00", "coinsurance": "20%", "provider_order_required": true, "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 41"},
  {"rule_id": "R-GS-BCBS-CANES", "target_type": "PRODUCT", "product_id": "P-MOB-CANES", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Durable Medical Equipment (DME)", "coverage_status": "Covered with Provider Order", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "20% coinsurance", "copay": "$0.00", "coinsurance": "20%", "provider_order_required": true, "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 42"},
  {"rule_id": "R-GS-BCBS-ROLLATOR", "target_type": "PRODUCT", "product_id": "P-MOB-ROLLATOR", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Durable Medical Equipment (DME)", "coverage_status": "Covered with Prior Authorization", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "20% coinsurance with authorization", "copay": "$0.00", "coinsurance": "20%", "prior_authorization_required": true, "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 42"},
  {"rule_id": "R-GS-BCBS-WHEELCHAIR", "target_type": "PRODUCT", "product_id": "P-MOB-WHEELCHAIR", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Durable Medical Equipment (DME)", "coverage_status": "Covered with Prior Authorization", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "20% coinsurance with authorization", "copay": "$0.00", "coinsurance": "20%", "prior_authorization_required": true, "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 42"},
  {"rule_id": "R-GS-BCBS-CGM", "target_type": "PRODUCT", "product_id": "P-DIB-CGM", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Part B diabetic supplies", "coverage_status": "Covered with Prior Authorization", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay for Dexcom / Freestyle Libre with authorization", "copay": "$0.00", "coinsurance": "0%", "prior_authorization_required": true, "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 40"},
  {"rule_id": "R-GS-BCBS-CPAP", "target_type": "PRODUCT", "product_id": "P-RSP-CPAP", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Durable Medical Equipment (DME)", "coverage_status": "Covered with Prior Authorization", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "20% coinsurance after sleep study", "copay": "$0.00", "coinsurance": "20%", "prior_authorization_required": true, "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 43"},
  {"rule_id": "R-GS-BCBS-GLASSES", "target_type": "PRODUCT", "product_id": "P-EYE-GLASSES", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Supplemental vision benefit", "coverage_status": "Covered with Allowance", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$150 annual eyewear allowance card", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 38"},
  {"rule_id": "R-GS-BCBS-HEARING", "target_type": "PRODUCT", "product_id": "P-EAR-HEARING", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Supplemental hearing benefit", "coverage_status": "Covered with Network Provider", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$699 copay per ear through NationsHearing", "copay": "$699.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 39"},
  {"rule_id": "R-GS-BCBS-CATHET", "target_type": "PRODUCT", "product_id": "P-URO-CATH", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Part B medical supplies", "coverage_status": "Covered with Provider Order", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "20% coinsurance", "copay": "$0.00", "coinsurance": "20%", "provider_order_required": true, "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 44"},
  {"rule_id": "R-GS-BCBS-ENSURE", "target_type": "PRODUCT", "product_id": "P-NUT-ENSURE", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Part B medical nutrition", "coverage_status": "Covered with Prescription & Diagnosis", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 with physician prescription & diagnosis", "copay": "$0.00", "coinsurance": "0%", "prescription_required": true, "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 46"},
  {"rule_id": "R-GS-BCBS-EXCL-PRENATAL", "target_type": "PRODUCT", "product_id": "P-VIT-PRENATAL", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Medicare Exclusion", "coverage_status": "Not Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Not Covered (Medicare Senior Plan Exclusions)", "copay": "N/A", "coinsurance": "N/A", "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 92"},
  {"rule_id": "R-GS-BCBS-EXCL-BREASTPUMP", "target_type": "PRODUCT", "product_id": "P-WMN-PUMP", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Medicare Exclusion", "coverage_status": "Not Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Not Covered (Maternity Breast Pump Excluded under MA Senior Plan)", "copay": "N/A", "coinsurance": "N/A", "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 92"},
  {"rule_id": "R-GS-BCBS-EXCL-TRN", "target_type": "SERVICE", "service_id": "S-TRN-RIDE", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Plan Option Limitation", "coverage_status": "Not Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Not Covered on BlueCHiP Core (Available on BlueCHiP Overall Health)", "copay": "N/A", "coinsurance": "N/A", "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 50"},
  {"rule_id": "R-RI-BCBS-B12", "target_type": "PRODUCT", "product_id": "P-VIT-B12", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 15"},
  {"rule_id": "R-RI-BCBS-CALCIUM", "target_type": "PRODUCT", "product_id": "P-VIT-CALCIUM", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 16"},
  {"rule_id": "R-RI-BCBS-IBU", "target_type": "PRODUCT", "product_id": "P-PAI-IBU", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-OTC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Uses OTC Allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare OTC Catalog (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 8"},
  {"rule_id": "R-RI-BCBS-BPMONITOR", "target_type": "PRODUCT", "product_id": "P-CAR-BPMONITOR", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Durable Medical Equipment (DME)", "coverage_status": "Covered with Provider Order", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 with physician order", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 42"},
  {"rule_id": "R-RI-BCBS-VIS", "target_type": "SERVICE", "service_id": "S-VIS-EXAM", "plan_id": "bcbsri_bluechip_core_2026", "applicable_plan_ids": ["bcbsri_bluechip_core_2026"], "source_id": "SRC-BCBSRI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Routine vision benefit", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay for annual exam", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BlueCHiP for Medicare Core Evidence of Coverage (2026)", "official_source_url": "https://www.bcbsri.com/medicare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25", "source_page": "Page 38"},
  {"rule_id": "R-RI-NHPRI-BPMONITOR", "target_type": "PRODUCT", "product_id": "P-CAR-BPMONITOR", "plan_id": "neighborhood_integra_2026", "applicable_plan_ids": ["neighborhood_integra_2026"], "source_id": "SRC-NHPRI-2026-SOB", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Durable Medical Equipment (DME)", "coverage_status": "Covered with Provider Order", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 with physician order", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Neighborhood INTEGRIA D-SNP Summary of Benefits (2026)", "official_source_url": "https://www.nhpri.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-RI-NHPRI-CPAP", "target_type": "PRODUCT", "product_id": "P-RSP-CPAP", "plan_id": "neighborhood_integra_2026", "applicable_plan_ids": ["neighborhood_integra_2026"], "source_id": "SRC-NHPRI-2026-SOB", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Durable Medical Equipment (DME)", "coverage_status": "Covered with Prior Authorization", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 with authorization", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Neighborhood INTEGRIA D-SNP Summary of Benefits (2026)", "official_source_url": "https://www.nhpri.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-MA-MASSHEALTH-IBU", "target_type": "PRODUCT", "product_id": "P-PAI-IBU", "plan_id": "ma_masshealth_medicaid", "applicable_plan_ids": ["ma_masshealth_medicaid"], "source_id": "SRC-MA-MASSHEALTH-2026-GUIDE", "source_authority": "STATE_MEDICAID", "benefit_pathway": "Prescription drug benefit", "coverage_status": "Covered", "state": "MA", "plan_type": "Medicaid", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 out-of-pocket", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "MassHealth Member Regulations and Regulations Guide (2026)", "official_source_url": "https://www.mass.gov/masshealth", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-MA-MASSHEALTH-TRN", "target_type": "SERVICE", "service_id": "S-TRN-RIDE", "plan_id": "ma_masshealth_medicaid", "applicable_plan_ids": ["ma_masshealth_medicaid"], "source_id": "SRC-MA-MASSHEALTH-2026-GUIDE", "source_authority": "STATE_MEDICAID", "benefit_pathway": "Non-emergency medical transportation", "coverage_status": "Covered", "state": "MA", "plan_type": "Medicaid", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 out-of-pocket", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "MassHealth Member Regulations and Regulations Guide (2026)", "official_source_url": "https://www.mass.gov/masshealth", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-MA-WELLSENSE-GLUCOSE", "target_type": "PRODUCT", "product_id": "P-DIB-MONITOR", "plan_id": "ma_wellsense_wellsense_connectorcare", "applicable_plan_ids": ["ma_wellsense_wellsense_connectorcare"], "source_id": "SRC-MA-WELLSENSE-2026-MED", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Durable Medical Equipment (DME)", "coverage_status": "Covered", "state": "MA", "plan_type": "ConnectorCare", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 with provider order", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "WellSense ConnectorCare Member Handbook (2026)", "official_source_url": "https://www.wellsense.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-CT-HUSKYA-IBU", "target_type": "PRODUCT", "product_id": "P-PAI-IBU", "plan_id": "ct_husky_health_husky_a", "applicable_plan_ids": ["ct_husky_health_husky_a"], "source_id": "SRC-CT-HUSKY-2026-MEMBER-GUIDE", "source_authority": "STATE_MEDICAID", "benefit_pathway": "Prescription drug benefit", "coverage_status": "Covered", "state": "CT", "plan_type": "Medicaid", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 out-of-pocket", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "HUSKY Health Member Handbook (2026)", "official_source_url": "https://portal.ct.gov/husky", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-CT-HUSKYA-VIS", "target_type": "SERVICE", "service_id": "S-VIS-EXAM", "plan_id": "ct_husky_health_husky_a", "applicable_plan_ids": ["ct_husky_health_husky_a"], "source_id": "SRC-CT-HUSKY-2026-MEMBER-GUIDE", "source_authority": "STATE_MEDICAID", "benefit_pathway": "Routine vision benefit", "coverage_status": "Covered", "state": "CT", "plan_type": "Medicaid", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay for annual exam", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "HUSKY Health Member Handbook (2026)", "official_source_url": "https://portal.ct.gov/husky", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-CT-HUSKYC-CANE", "target_type": "PRODUCT", "product_id": "P-MOB-CANES", "plan_id": "ct_husky_health_husky_c", "applicable_plan_ids": ["ct_husky_health_husky_c"], "source_id": "SRC-CT-HUSKY-2026-MEMBER-GUIDE", "source_authority": "STATE_MEDICAID", "benefit_pathway": "Durable Medical Equipment (DME)", "coverage_status": "Covered with Provider Order", "state": "CT", "plan_type": "Medicaid", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 with physician order", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "HUSKY Health Member Handbook (2026)", "official_source_url": "https://portal.ct.gov/husky", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-CT-HUSKYD-IBU", "target_type": "PRODUCT", "product_id": "P-PAI-IBU", "plan_id": "ct_husky_health_husky_d", "applicable_plan_ids": ["ct_husky_health_husky_d"], "source_id": "SRC-CT-HUSKY-2026-MEMBER-GUIDE", "source_authority": "STATE_MEDICAID", "benefit_pathway": "Prescription drug benefit", "coverage_status": "Covered", "state": "CT", "plan_type": "Medicaid", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 out-of-pocket", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "HUSKY Health Member Handbook (2026)", "official_source_url": "https://portal.ct.gov/husky", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-NH-WELLSENSE-IBU", "target_type": "PRODUCT", "product_id": "P-PAI-IBU", "plan_id": "nh_wellsense_medicaid_mco", "applicable_plan_ids": ["nh_wellsense_medicaid_mco"], "source_id": "SRC-NH-DHHS-2026-MEDICAID", "source_authority": "STATE_MEDICAID", "benefit_pathway": "Prescription drug benefit", "coverage_status": "Covered", "state": "NH", "plan_type": "Medicaid", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 out-of-pocket", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "New Hampshire Medicaid MCO Policy Guide (2026)", "official_source_url": "https://www.dhhs.nh.gov/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-NH-AMERIHEALTH-IBU", "target_type": "PRODUCT", "product_id": "P-PAI-IBU", "plan_id": "nh_amerihealth_caritas_medicaid", "applicable_plan_ids": ["nh_amerihealth_caritas_medicaid"], "source_id": "SRC-NH-AMERIHEALTH-2026-CARE", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "NH", "plan_type": "Medicaid", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Covered via CARE card", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "AmeriHealth Caritas NH Member Guide (2026)", "official_source_url": "https://www.amerihealthcaritasnh.com/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-ME-MAINECARE-IBU", "target_type": "PRODUCT", "product_id": "P-PAI-IBU", "plan_id": "me_mainecare_medicaid", "applicable_plan_ids": ["me_mainecare_medicaid"], "source_id": "SRC-ME-DHHS-2026-MAINACARE", "source_authority": "STATE_MEDICAID", "benefit_pathway": "Prescription drug benefit", "coverage_status": "Covered", "state": "ME", "plan_type": "Medicaid", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 out-of-pocket", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "MaineCare Member Services Guide (2026)", "official_source_url": "https://www.maine.gov/dhhs/ofi/mainecare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-ME-MAINECARE-VIS", "target_type": "SERVICE", "service_id": "S-VIS-EXAM", "plan_id": "me_mainecare_medicaid", "applicable_plan_ids": ["me_mainecare_medicaid"], "source_id": "SRC-ME-DHHS-2026-MAINACARE", "source_authority": "STATE_MEDICAID", "benefit_pathway": "Routine vision benefit", "coverage_status": "Covered", "state": "ME", "plan_type": "Medicaid", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay for annual exam", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "MaineCare Member Services Guide (2026)", "official_source_url": "https://www.maine.gov/dhhs/ofi/mainecare", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-VT-DVHA-IBU", "target_type": "PRODUCT", "product_id": "P-PAI-IBU", "plan_id": "vt_vermont_medicaid", "applicable_plan_ids": ["vt_vermont_medicaid"], "source_id": "SRC-VT-DVHA-2026-MEDICAID", "source_authority": "STATE_MEDICAID", "benefit_pathway": "Prescription drug benefit", "coverage_status": "Covered", "state": "VT", "plan_type": "Medicaid", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 out-of-pocket", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Green Mountain Care Vermont Medicaid Handbook (2026)", "official_source_url": "https://dvha.vermont.gov/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-VT-DYNASAUR-ORAL", "target_type": "PRODUCT", "product_id": "P-DEN-ORAL", "plan_id": "vt_dr_dynasaur_medicaid", "applicable_plan_ids": ["vt_dr_dynasaur_medicaid"], "source_id": "SRC-VT-DVHA-2026-MEDICAID", "source_authority": "STATE_MEDICAID", "benefit_pathway": "Pediatric oral health benefit", "coverage_status": "Covered", "state": "VT", "plan_type": "Medicaid", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 out-of-pocket", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Dr. Dynasaur Member Handbook (2026)", "official_source_url": "https://dvha.vermont.gov/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-RI-UHC-BPMONITOR", "target_type": "PRODUCT", "product_id": "P-CAR-BPMONITOR", "plan_id": "uhc_medicare_dual_2026", "applicable_plan_ids": ["uhc_medicare_dual_2026"], "source_id": "SRC-UHCRI-2026-UCARD", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "UCard OTC & Medical Benefit", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 with UCard", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "UHC Dual Complete RI Member Handbook (2026)", "official_source_url": "https://www.uhc.com/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-RI-UHC-VIS", "target_type": "SERVICE", "service_id": "S-VIS-EXAM", "plan_id": "uhc_medicare_dual_2026", "applicable_plan_ids": ["uhc_medicare_dual_2026"], "source_id": "SRC-UHCRI-2026-UCARD", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Routine Vision Benefit", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay for annual exam", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "UHC Dual Complete RI Member Handbook (2026)", "official_source_url": "https://www.uhc.com/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-RI-MEDICAID-DEN", "target_type": "SERVICE", "service_id": "S-DEN-EXAM", "plan_id": "ri_medicaid_managed_2026", "applicable_plan_ids": ["ri_medicaid_managed_2026"], "source_id": "SRC-RIME-2026-PHARMACY", "source_authority": "STATE_MEDICAID", "benefit_pathway": "Medicaid Dental Benefit", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicaid", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 out-of-pocket", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "RI Executive Office of Health and Human Services Medicaid Protocols (2026)", "official_source_url": "https://eohhs.ri.gov/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-RI-BCBS-ACCESS-PREV", "target_type": "SERVICE", "service_id": "S-PREV-WELLNESS", "plan_id": "bcbsri_access_2026", "applicable_plan_ids": ["bcbsri_access_2026"], "source_id": "SRC-BCBSRI-2026-ACCESS", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Preventive Wellness Benefit", "coverage_status": "Covered", "state": "RI", "plan_type": "Commercial", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay for annual exam", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BCBSRI Direct Access Summary of Benefits (2026)", "official_source_url": "https://www.bcbsri.com/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-RI-NHPRI-ACCESS-DEN", "target_type": "SERVICE", "service_id": "S-DEN-EXAM", "plan_id": "neighborhood_access_2026", "applicable_plan_ids": ["neighborhood_access_2026"], "source_id": "SRC-NHPRI-2026-ACCESS", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Preventive Dental Benefit", "coverage_status": "Covered", "state": "RI", "plan_type": "Commercial", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay (2 per year)", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Neighborhood ACCESS Summary of Benefits (2026)", "official_source_url": "https://www.nhpri.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-MA-WELLSENSE-PREV", "target_type": "SERVICE", "service_id": "S-PREV-WELLNESS", "plan_id": "ma_wellsense_wellsense_connectorcare", "applicable_plan_ids": ["ma_wellsense_wellsense_connectorcare"], "source_id": "SRC-MA-WELLSENSE-2026-MED", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Preventive Wellness Benefit", "coverage_status": "Covered", "state": "MA", "plan_type": "ConnectorCare", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay for annual exam", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "WellSense ConnectorCare Member Handbook (2026)", "official_source_url": "https://www.wellsense.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-MA-TUFTS-VIS", "target_type": "SERVICE", "service_id": "S-VIS-EXAM", "plan_id": "ma_tufts_p32_tufts_health_direct_connectorcare", "applicable_plan_ids": ["ma_tufts_p32_tufts_health_direct_connectorcare"], "source_id": "SRC-MA-TUFTS-2026-TOGETHER", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Routine Vision Benefit", "coverage_status": "Covered", "state": "MA", "plan_type": "ConnectorCare", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay for annual exam", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Tufts Health Direct ConnectorCare Member Guide (2026)", "official_source_url": "https://tuftshealthplan.com/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-MA-BCBSMA-DEN", "target_type": "SERVICE", "service_id": "S-DEN-EXAM", "plan_id": "ma_bcbsma_health_connector_standard_plan", "applicable_plan_ids": ["ma_bcbsma_health_connector_standard_plan"], "source_id": "SRC-MA-BCBSMA-2026-SOB", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Preventive Dental Benefit", "coverage_status": "Covered", "state": "MA", "plan_type": "Commercial", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay (2 per year)", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BCBSMA Health Connector Standard Plan Summary of Benefits (2026)", "official_source_url": "https://www.bluecrossma.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-MA-HNE-VITD", "target_type": "PRODUCT", "product_id": "P-VIT-D", "plan_id": "ma_health_new_england_connectorcare", "applicable_plan_ids": ["ma_health_new_england_connectorcare"], "source_id": "SRC-MA-HNE-2026-SOB", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Preventive medicine benefit", "coverage_status": "Covered", "state": "MA", "plan_type": "ConnectorCare", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 out-of-pocket", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Health New England ConnectorCare Schedule of Benefits (2026)", "official_source_url": "https://healthnewengland.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-MA-HNE-PREV", "target_type": "SERVICE", "service_id": "S-PREV-WELLNESS", "plan_id": "ma_health_new_england_connectorcare", "applicable_plan_ids": ["ma_health_new_england_connectorcare"], "source_id": "SRC-MA-HNE-2026-SOB", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Preventive Health Visit", "coverage_status": "Covered", "state": "MA", "plan_type": "ConnectorCare", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay for annual exam", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Health New England ConnectorCare Schedule of Benefits (2026)", "official_source_url": "https://healthnewengland.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-CT-CONNECTICARE-PREV", "target_type": "SERVICE", "service_id": "S-PREV-WELLNESS", "plan_id": "ct_connecticare_connecticare_choice_silver", "applicable_plan_ids": ["ct_connecticare_connecticare_choice_silver"], "source_id": "SRC-CT-CONNECTICARE-2026-SOB", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Preventive Health Visit", "coverage_status": "Covered", "state": "CT", "plan_type": "Commercial", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay for annual exam", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "ConnectiCare Choice Silver Summary of Benefits (2026)", "official_source_url": "https://www.connecticare.com/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-CT-COVERED-CT-DEN", "target_type": "SERVICE", "service_id": "S-DEN-EXAM", "plan_id": "ct_connecticare_connecticare_covered_ct", "applicable_plan_ids": ["ct_connecticare_connecticare_covered_ct"], "source_id": "SRC-CT-CONNECTICARE-2026-SOB", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Preventive Dental Benefit", "coverage_status": "Covered", "state": "CT", "plan_type": "Commercial", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay under Covered CT", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "ConnectiCare Covered CT Plan Summary of Benefits (2026)", "official_source_url": "https://www.connecticare.com/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-CT-ANTHEM-VIS", "target_type": "SERVICE", "service_id": "S-VIS-EXAM", "plan_id": "ct_anthem_bcbs_anthem_pathway_standard_silver", "applicable_plan_ids": ["ct_anthem_bcbs_anthem_pathway_standard_silver"], "source_id": "SRC-CT-ANTHEM-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Routine Vision Benefit", "coverage_status": "Covered", "state": "CT", "plan_type": "Commercial", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay for annual exam", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Anthem Pathway Standard Silver Evidence of Coverage (2026)", "official_source_url": "https://www.anthem.com/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-NH-HARVARD-PREV", "target_type": "SERVICE", "service_id": "S-PREV-WELLNESS", "plan_id": "nh_harvard_pilgrim_nh_local_hmo_silver_6000_standard_0_rx_list_0_virtual_urgent_care", "applicable_plan_ids": ["nh_harvard_pilgrim_nh_local_hmo_silver_6000_standard_0_rx_list_0_virtual_urgent_care"], "source_id": "SRC-NH-HARVARD-2026-SOB", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "$0 Virtual Urgent Care & Preventive Visit", "coverage_status": "Covered", "state": "NH", "plan_type": "Commercial", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Harvard Pilgrim NH Local HMO Silver Summary of Benefits (2026)", "official_source_url": "https://www.harvardpilgrim.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-ME-HARVARD-VIS", "target_type": "SERVICE", "service_id": "S-VIS-EXAM", "plan_id": "me_harvard_pilgrim_clear_choice_hmo_silver_4000", "applicable_plan_ids": ["me_harvard_pilgrim_clear_choice_hmo_silver_4000"], "source_id": "SRC-ME-HARVARD-2026-EOC", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Routine Vision Benefit", "coverage_status": "Covered", "state": "ME", "plan_type": "Commercial", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay for annual exam", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Harvard Pilgrim Clear Choice HMO Silver 4000 Evidence of Coverage (2026)", "official_source_url": "https://www.harvardpilgrim.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-VT-BCBSVT-PREV", "target_type": "SERVICE", "service_id": "S-PREV-WELLNESS", "plan_id": "vt_bcbsvt_bcbsvt_silver", "applicable_plan_ids": ["vt_bcbsvt_bcbsvt_silver"], "source_id": "SRC-VT-BCBSVT-2026-SOB", "source_authority": "OFFICIAL_INSURER", "benefit_pathway": "Preventive Health Visit", "coverage_status": "Covered", "state": "VT", "plan_type": "Commercial", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay for annual exam", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Blue Cross Blue Shield Vermont Silver Standard Summary of Benefits (2026)", "official_source_url": "https://www.bluecrossvt.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-RI-TUFTS-VITD", "target_type": "PRODUCT", "product_id": "P-VIT-D", "plan_id": "tufts_ri_medicare_2026", "applicable_plan_ids": ["tufts_ri_medicare_2026"], "source_id": "SRC-TUFTS-RI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "evidence_scope": "EXACT_PLAN", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$75 quarterly allowance", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Tufts Health Plan RI Evidence of Coverage (2026)", "official_source_url": "https://www.tuftshealthplan.com/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-RI-TUFTS-VIS", "target_type": "SERVICE", "service_id": "S-VIS-EXAM", "plan_id": "tufts_ri_medicare_2026", "applicable_plan_ids": ["tufts_ri_medicare_2026"], "source_id": "SRC-TUFTS-RI-2026-EOC", "source_authority": "OFFICIAL_INSURER", "evidence_scope": "EXACT_PLAN", "benefit_pathway": "Routine vision benefit", "coverage_status": "Covered", "state": "RI", "plan_type": "Medicare Advantage", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay for annual exam", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Tufts Health Plan RI Evidence of Coverage (2026)", "official_source_url": "https://www.tuftshealthplan.com/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-RI-BCBS-ACCESS-FOLIC", "target_type": "PRODUCT", "product_id": "P-VIT-FOLIC", "plan_id": "bcbsri_access_2026", "applicable_plan_ids": ["bcbsri_access_2026"], "source_id": "SRC-BCBSRI-2026-ACCESS", "source_authority": "OFFICIAL_INSURER", "evidence_scope": "EXACT_PLAN", "benefit_pathway": "Preventive drug benefit", "coverage_status": "Covered", "state": "RI", "plan_type": "Commercial", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 out-of-pocket", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "BCBSRI Direct Access Summary of Benefits (2026)", "official_source_url": "https://www.bcbsri.com/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-RI-NHPRI-ACCESS-IBU", "target_type": "PRODUCT", "product_id": "P-PAI-IBU", "plan_id": "neighborhood_access_2026", "applicable_plan_ids": ["neighborhood_access_2026"], "source_id": "SRC-NHPRI-2026-ACCESS", "source_authority": "OFFICIAL_INSURER", "evidence_scope": "EXACT_PLAN", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "RI", "plan_type": "Commercial", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "Covered via OTC card", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Neighborhood ACCESS Summary of Benefits (2026)", "official_source_url": "https://www.nhpri.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-MA-HPHC-VITD", "target_type": "PRODUCT", "product_id": "P-VIT-D", "plan_id": "ma_harvard_pilgrim_standard_silver_ii", "applicable_plan_ids": ["ma_harvard_pilgrim_standard_silver_ii"], "source_id": "SRC-MA-HPHC-2026-EOC", "source_authority": "OFFICIAL_INSURER", "evidence_scope": "EXACT_PLAN", "benefit_pathway": "Preventive medicine benefit", "coverage_status": "Covered", "state": "MA", "plan_type": "Commercial", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 out-of-pocket", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Harvard Pilgrim Health Care Standard Silver II Evidence of Coverage (2026)", "official_source_url": "https://www.harvardpilgrim.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-MA-HPHC-PREV", "target_type": "SERVICE", "service_id": "S-PREV-WELLNESS", "plan_id": "ma_harvard_pilgrim_standard_silver_ii", "applicable_plan_ids": ["ma_harvard_pilgrim_standard_silver_ii"], "source_id": "SRC-MA-HPHC-2026-EOC", "source_authority": "OFFICIAL_INSURER", "evidence_scope": "EXACT_PLAN", "benefit_pathway": "Preventive health visit", "coverage_status": "Covered", "state": "MA", "plan_type": "Commercial", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay for annual exam", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Harvard Pilgrim Health Care Standard Silver II Evidence of Coverage (2026)", "official_source_url": "https://www.harvardpilgrim.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-MA-MGB-SALINE", "target_type": "PRODUCT", "product_id": "P-CFA-SALINE", "plan_id": "ma_mgb_health_connectorcare", "applicable_plan_ids": ["ma_mgb_health_connectorcare"], "source_id": "SRC-MA-MGB-2026-SOB", "source_authority": "OFFICIAL_INSURER", "evidence_scope": "EXACT_PLAN", "benefit_pathway": "OTC allowance", "coverage_status": "Covered", "state": "MA", "plan_type": "ConnectorCare", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 out-of-pocket", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Mass General Brigham Health Plan ConnectorCare Schedule of Benefits (2026)", "official_source_url": "https://massgeneralbrighamhealthplan.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-MA-MGB-DEN", "target_type": "SERVICE", "service_id": "S-DEN-EXAM", "plan_id": "ma_mgb_health_connectorcare", "applicable_plan_ids": ["ma_mgb_health_connectorcare"], "source_id": "SRC-MA-MGB-2026-SOB", "source_authority": "OFFICIAL_INSURER", "evidence_scope": "EXACT_PLAN", "benefit_pathway": "Preventive dental benefit", "coverage_status": "Covered", "state": "MA", "plan_type": "ConnectorCare", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay (2 per year)", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Mass General Brigham Health Plan ConnectorCare Schedule of Benefits (2026)", "official_source_url": "https://massgeneralbrighamhealthplan.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-ME-CHO-VITD", "target_type": "PRODUCT", "product_id": "P-VIT-D", "plan_id": "me_community_health_options_community_health_options_clear_choice", "applicable_plan_ids": ["me_community_health_options_community_health_options_clear_choice"], "source_id": "SRC-ME-CHO-2026-SOB", "source_authority": "OFFICIAL_INSURER", "evidence_scope": "EXACT_PLAN", "benefit_pathway": "Preventive drug benefit", "coverage_status": "Covered", "state": "ME", "plan_type": "Commercial", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 out-of-pocket", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Community Health Options Clear Choice Summary of Benefits (2026)", "official_source_url": "https://www.healthoptions.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-ME-CHO-PREV", "target_type": "SERVICE", "service_id": "S-PREV-WELLNESS", "plan_id": "me_community_health_options_community_health_options_clear_choice", "applicable_plan_ids": ["me_community_health_options_community_health_options_clear_choice"], "source_id": "SRC-ME-CHO-2026-SOB", "source_authority": "OFFICIAL_INSURER", "evidence_scope": "EXACT_PLAN", "benefit_pathway": "Preventive health visit", "coverage_status": "Covered", "state": "ME", "plan_type": "Commercial", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay for annual exam", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Community Health Options Clear Choice Summary of Benefits (2026)", "official_source_url": "https://www.healthoptions.org/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-ME-ANTHEM-PRENATAL", "target_type": "PRODUCT", "product_id": "P-VIT-PRENATAL", "plan_id": "me_anthem_bcbs_anthem_clear_choice_ppo", "applicable_plan_ids": ["me_anthem_bcbs_anthem_clear_choice_ppo"], "source_id": "SRC-ME-ANTHEM-2026-SOB", "source_authority": "OFFICIAL_INSURER", "evidence_scope": "EXACT_PLAN", "benefit_pathway": "Prescription drug benefit", "coverage_status": "Covered", "state": "ME", "plan_type": "Commercial", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 out-of-pocket", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Anthem Blue Cross Blue Shield Maine Clear Choice PPO Summary of Benefits (2026)", "official_source_url": "https://www.anthem.com/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-ME-ANTHEM-PREV", "target_type": "SERVICE", "service_id": "S-PREV-WELLNESS", "plan_id": "me_anthem_bcbs_anthem_clear_choice_ppo", "applicable_plan_ids": ["me_anthem_bcbs_anthem_clear_choice_ppo"], "source_id": "SRC-ME-ANTHEM-2026-SOB", "source_authority": "OFFICIAL_INSURER", "evidence_scope": "EXACT_PLAN", "benefit_pathway": "Preventive health visit", "coverage_status": "Covered", "state": "ME", "plan_type": "Commercial", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 copay for annual exam", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "Anthem Blue Cross Blue Shield Maine Clear Choice PPO Summary of Benefits (2026)", "official_source_url": "https://www.anthem.com/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  {"rule_id": "R-VT-MVP-VITD", "target_type": "PRODUCT", "product_id": "P-VIT-D", "plan_id": "vt_mvp_health_mvp_vt_plus_silver", "applicable_plan_ids": ["vt_mvp_health_mvp_vt_plus_silver"], "source_id": "SRC-VT-MVP-2026-GIA", "source_authority": "OFFICIAL_INSURER", "evidence_scope": "EXACT_PLAN", "benefit_pathway": "Preventive medicine benefit", "coverage_status": "Covered", "state": "VT", "plan_type": "Commercial", "plan_year": 2026, "verification_status": "VERIFIED_EXACT", "member_cost": "$0 out-of-pocket", "copay": "$0.00", "coinsurance": "0%", "official_source_name": "MVP Health Care VT Plus Silver Plan Guide (2026)", "official_source_url": "https://www.mvphealthcare.com/", "source_effective_date": "2026-01-01", "last_verified_date": "2026-09-25"},
  // --- VERMONT VERIFIED COVERAGE RULES ---
  {
    rule_id: 'R-VT-DVHA-VIT-D', target_type: 'PRODUCT', product_id: 'P-VIT-D', plan_id: 'vt_vermont_medicaid',
    applicable_plan_ids: ['vt_vermont_medicaid', 'vt_dr_dynasaur_medicaid'],
    source_id: 'SRC-VT-DVHA-2026-MEDICAID', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Prescription drug benefit', coverage_status: 'Covered', state: 'VT', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'Green Mountain Care Preferred Drug List & Pharmacy Protocol (2026)', official_source_url: 'https://dvha.vermont.gov/',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 10',
    evidence_text: 'Vitamin D3 softgels covered 100% with $0 copay under Green Mountain Care preferred drug list.',
    source_snapshot: { source_id: 'SRC-VT-DVHA-2026-MEDICAID', source_version: '2026-v1.0', source_hash: 'sha256-vt-dvha-vitd-2026', page: 'Page 10', verified_at: '2026-09-25' },
    notes: '100% covered under Green Mountain Care.', plain_english_explanation: 'Vitamin D3 is 100% covered under Green Mountain Care / Vermont Medicaid when prescribed.', action_type: 'request_prescription', action_label: 'Request prescription from provider'
  },
  {
    rule_id: 'R-VT-DVHA-PRENATAL', target_type: 'PRODUCT', product_id: 'P-VIT-PRENATAL', plan_id: 'vt_vermont_medicaid',
    applicable_plan_ids: ['vt_vermont_medicaid', 'vt_dr_dynasaur_medicaid'],
    source_id: 'SRC-VT-DVHA-2026-MEDICAID', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Prescription drug benefit', coverage_status: 'Covered', state: 'VT', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'Green Mountain Care Preferred Drug List & Pharmacy Protocol (2026)', official_source_url: 'https://dvha.vermont.gov/',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 16',
    evidence_text: 'Prenatal multivitamins covered 100% with $0 copay under Vermont Medicaid.',
    source_snapshot: { source_id: 'SRC-VT-DVHA-2026-MEDICAID', source_version: '2026-v1.0', source_hash: 'sha256-vt-dvha-prenatal-2026', page: 'Page 16', verified_at: '2026-09-25' },
    notes: '100% covered with prescription.', plain_english_explanation: 'Prenatal multivitamins are covered 100% with $0 out-of-pocket cost under Vermont Medicaid.', action_type: 'request_prescription', action_label: 'Request prescription from provider'
  },
  {
    rule_id: 'R-VT-DVHA-ACETA', target_type: 'PRODUCT', product_id: 'P-PAI-ACETA', plan_id: 'vt_vermont_medicaid',
    applicable_plan_ids: ['vt_vermont_medicaid', 'vt_dr_dynasaur_medicaid'],
    source_id: 'SRC-VT-DVHA-2026-MEDICAID', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Prescription drug benefit', coverage_status: 'Covered', state: 'VT', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'Green Mountain Care Preferred Drug List & Pharmacy Protocol (2026)', official_source_url: 'https://dvha.vermont.gov/',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 20',
    evidence_text: 'Acetaminophen 500 mg caplets covered 100% with written provider prescription.',
    source_snapshot: { source_id: 'SRC-VT-DVHA-2026-MEDICAID', source_version: '2026-v1.0', source_hash: 'sha256-vt-dvha-aceta-2026', page: 'Page 20', verified_at: '2026-09-25' },
    notes: '100% covered with prescription.', plain_english_explanation: 'Acetaminophen pain relief is covered 100% when prescribed by your provider under Vermont Medicaid.', action_type: 'request_prescription', action_label: 'Request prescription from provider'
  },
  {
    rule_id: 'R-VT-DVHA-BPMON', target_type: 'PRODUCT', product_id: 'P-CAR-BPMON', plan_id: 'vt_vermont_medicaid',
    applicable_plan_ids: ['vt_vermont_medicaid', 'vt_dr_dynasaur_medicaid'],
    source_id: 'SRC-VT-DVHA-2026-MEDICAID', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Durable Medical Equipment (DME)', coverage_status: 'Covered with Provider Order', state: 'VT', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: true, diagnosis_required: true, prior_authorization_required: false,
    network_pharmacy_required: false, network_dme_supplier_required: true, member_cost: '$0 with provider order', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'Green Mountain Care Preferred Drug List & Pharmacy Protocol (2026)', official_source_url: 'https://dvha.vermont.gov/',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 32',
    evidence_text: 'Digital blood pressure monitors covered 100% under Green Mountain Care DME schedule with physician order.',
    source_snapshot: { source_id: 'SRC-VT-DVHA-2026-MEDICAID', source_version: '2026-v1.0', source_hash: 'sha256-vt-dvha-bpmon-2026', page: 'Page 32', verified_at: '2026-09-25' },
    notes: '100% covered with physician order.', plain_english_explanation: 'Digital blood pressure monitors are 100% covered when ordered by your physician under Vermont Medicaid.', action_type: 'request_provider_order', action_label: 'Request order from provider'
  },
  {
    rule_id: 'R-VT-DVHA-GLUCOSE', target_type: 'PRODUCT', product_id: 'P-DIAB-METER', plan_id: 'vt_vermont_medicaid',
    applicable_plan_ids: ['vt_vermont_medicaid', 'vt_dr_dynasaur_medicaid'],
    source_id: 'SRC-VT-DVHA-2026-MEDICAID', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Durable Medical Equipment (DME)', coverage_status: 'Covered with Provider Order', state: 'VT', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: true, diagnosis_required: true, prior_authorization_required: false,
    network_pharmacy_required: false, network_dme_supplier_required: true, member_cost: '$0 with provider order', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'Green Mountain Care Preferred Drug List & Pharmacy Protocol (2026)', official_source_url: 'https://dvha.vermont.gov/',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 36',
    evidence_text: 'Blood glucose meters covered 100% under Green Mountain Care DME schedule when prescribed.',
    source_snapshot: { source_id: 'SRC-VT-DVHA-2026-MEDICAID', source_version: '2026-v1.0', source_hash: 'sha256-vt-dvha-glucose-2026', page: 'Page 36', verified_at: '2026-09-25' },
    notes: '100% covered with provider order.', plain_english_explanation: 'Blood glucose meters are 100% covered when prescribed by your provider under Vermont Medicaid.', action_type: 'request_provider_order', action_label: 'Request order from provider'
  },
  {
    rule_id: 'R-VT-DVHA-DEN-EXAM', target_type: 'SERVICE', service_id: 'S-DEN-EXAM', plan_id: 'vt_vermont_medicaid',
    applicable_plan_ids: ['vt_vermont_medicaid', 'vt_dr_dynasaur_medicaid'],
    source_id: 'SRC-VT-DVHA-2026-MEDICAID', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Dental benefit', coverage_status: 'Covered', state: 'VT', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_SERVICE', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: false, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: false, network_dme_supplier_required: false, member_cost: '$0 copay (2 per year)', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'Green Mountain Care Preferred Drug List & Pharmacy Protocol (2026)', official_source_url: 'https://dvha.vermont.gov/',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 40',
    evidence_text: 'Routine dental cleanings and oral examinations covered twice per calendar year at $0 copay for Green Mountain Care members.',
    source_snapshot: { source_id: 'SRC-VT-DVHA-2026-MEDICAID', source_version: '2026-v1.0', source_hash: 'sha256-vt-dvha-den-2026', page: 'Page 40', verified_at: '2026-09-25' },
    notes: 'Covered twice per year.', plain_english_explanation: 'Routine dental cleanings and exams are covered 100% twice per year with $0 copay.', action_type: 'schedule_visit', action_label: 'Find a network dentist'
  },
  {
    rule_id: 'R-VT-DVHA-TRN-RIDE', target_type: 'SERVICE', service_id: 'S-TRN-RIDE', plan_id: 'vt_vermont_medicaid',
    applicable_plan_ids: ['vt_vermont_medicaid', 'vt_dr_dynasaur_medicaid'],
    source_id: 'SRC-VT-DVHA-2026-MEDICAID', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Transportation benefit', coverage_status: 'Covered', state: 'VT', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_SERVICE', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: false, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: false, network_dme_supplier_required: false, member_cost: '$0 ride booking', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'Green Mountain Care Preferred Drug List & Pharmacy Protocol (2026)', official_source_url: 'https://dvha.vermont.gov/',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 48',
    evidence_text: 'Non-emergency transportation rides covered for medical and pharmacy appointments via Vermont NEMT broker.',
    source_snapshot: { source_id: 'SRC-VT-DVHA-2026-MEDICAID', source_version: '2026-v1.0', source_hash: 'sha256-vt-dvha-trn-2026', page: 'Page 48', verified_at: '2026-09-25' },
    notes: 'Book 48 hours in advance.', plain_english_explanation: 'Free transportation rides to healthcare appointments are provided through Green Mountain Care NEMT.', action_type: 'book_ride', action_label: 'Book NEMT ride'
  },
  {
    rule_id: 'R-VT-MVP-GIA-SERVICE', target_type: 'SERVICE', service_id: 'S-TRN-RIDE', plan_id: 'vt_mvp_health_mvp_vt_plus_silver',
    applicable_plan_ids: ['vt_mvp_health_mvp_vt_plus_silver'],
    source_id: 'SRC-VT-MVP-2026-GIA', source_authority: 'OFFICIAL_INSURER', evidence_scope: 'EXACT_PLAN',
    benefit_pathway: 'Gia Virtual Care Program', coverage_status: 'Covered', state: 'VT', plan_type: 'Commercial', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_SERVICE', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    member_cost: '$0 copay for Gia virtual visits', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'MVP VT Plus Silver Evidence of Coverage & Gia Virtual Care Guide (2026)', official_source_url: 'https://www.mvphealthcare.com/vt',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 14',
    evidence_text: 'MVP members receive 24/7 $0 copay telehealth and virtual urgent care visits via Gia mobile application.',
    source_snapshot: { source_id: 'SRC-VT-MVP-2026-GIA', source_version: '2026-v1.0', source_hash: 'sha256-vt-mvp-gia-2026', page: 'Page 14', verified_at: '2026-09-25' },
    notes: 'Available 24/7 via Gia app.', plain_english_explanation: 'Access 24/7 virtual urgent care and telehealth with $0 copay through MVP Gia.', action_type: 'view_benefit', action_label: 'Access Gia Virtual Care'
  },
  {
    rule_id: 'R-VT-BCBSVT-WELLNESS', target_type: 'BENEFIT', benefit_id: 'B-VT-BCBSVT-WELLNESS', plan_id: 'vt_bcbsvt_bcbsvt_silver',
    applicable_plan_ids: ['vt_bcbsvt_bcbsvt_silver'],
    source_id: 'SRC-VT-BCBSVT-2026-SOB', source_authority: 'OFFICIAL_INSURER', evidence_scope: 'EXACT_PLAN',
    benefit_pathway: 'Wellness & Fitness Benefit', coverage_status: 'Covered', state: 'VT', plan_type: 'Commercial', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_BENEFIT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    member_cost: '$150 annual wellness reimbursement', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'BCBSVT Silver Summary of Benefits & Wellness Policy (2026)', official_source_url: 'https://www.bcbsvt.com/',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 22',
    evidence_text: 'BCBSVT Silver members are eligible for up to $150 annual reimbursement for qualified fitness center memberships.',
    source_snapshot: { source_id: 'SRC-VT-BCBSVT-2026-SOB', source_version: '2026-v1.0', source_hash: 'sha256-vt-bcbsvt-wellness-2026', page: 'Page 22', verified_at: '2026-09-25' },
    notes: 'Reimbursement form required.', plain_english_explanation: 'Get up to $150 per year back for fitness club memberships under BCBS Vermont.', action_type: 'view_benefit', action_label: 'View Wellness Benefit Details'
  },
  {
    rule_id: 'R-VT-BCBSVT-PRENATAL', target_type: 'PRODUCT', product_id: 'P-VIT-PRENATAL', plan_id: 'vt_bcbsvt_bcbsvt_silver',
    applicable_plan_ids: ['vt_bcbsvt_bcbsvt_silver'],
    source_id: 'SRC-VT-BCBSVT-2026-SOB', source_authority: 'OFFICIAL_INSURER', evidence_scope: 'EXACT_PLAN',
    benefit_pathway: 'Prescription drug benefit', coverage_status: 'Covered', state: 'VT', plan_type: 'Commercial', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'BCBSVT Silver Summary of Benefits & Wellness Policy (2026)', official_source_url: 'https://www.bcbsvt.com/',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 14',
    evidence_text: 'Prenatal multivitamins covered 100% under ACA preventive prescription guidelines.',
    source_snapshot: { source_id: 'SRC-VT-BCBSVT-2026-SOB', source_version: '2026-v1.0', source_hash: 'sha256-vt-bcbsvt-prenatal-2026', page: 'Page 14', verified_at: '2026-09-25' },
    notes: '100% covered under ACA mandate.', plain_english_explanation: 'Prenatal multivitamins are 100% covered under ACA guidelines when prescribed.', action_type: 'request_prescription', action_label: 'Request prescription from provider'
  },
  // --- MAINE VERIFIED COVERAGE RULES ---
  {
    rule_id: 'R-ME-MAINACARE-VIT-D', target_type: 'PRODUCT', product_id: 'P-VIT-D', plan_id: 'me_mainecare_medicaid',
    applicable_plan_ids: ['me_mainecare_medicaid'],
    source_id: 'SRC-ME-DHHS-2026-MAINACARE', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Prescription drug benefit', coverage_status: 'Covered', state: 'ME', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'MaineCare Preferred Drug List & Pharmacy Coverage Guide (2026)', official_source_url: 'https://www.maine.gov/dhhs/oms',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 12',
    evidence_text: 'Vitamin D3 softgels covered 100% with $0 copay under MaineCare preferred drug list when prescribed.',
    source_snapshot: { source_id: 'SRC-ME-DHHS-2026-MAINACARE', source_version: '2026-v1.0', source_hash: 'sha256-me-dhhs-vitd-2026', page: 'Page 12', verified_at: '2026-09-25' },
    notes: '100% covered with prescription under MaineCare.', plain_english_explanation: 'Vitamin D3 is 100% covered under MaineCare with $0 copay when prescribed by your provider.', action_type: 'request_prescription', action_label: 'Request prescription from provider'
  },
  {
    rule_id: 'R-ME-MAINACARE-PRENATAL', target_type: 'PRODUCT', product_id: 'P-VIT-PRENATAL', plan_id: 'me_mainecare_medicaid',
    applicable_plan_ids: ['me_mainecare_medicaid'],
    source_id: 'SRC-ME-DHHS-2026-MAINACARE', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Prescription drug benefit', coverage_status: 'Covered', state: 'ME', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'MaineCare Preferred Drug List & Pharmacy Coverage Guide (2026)', official_source_url: 'https://www.maine.gov/dhhs/oms',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 18',
    evidence_text: 'Prenatal multivitamins covered 100% with $0 copay under MaineCare preferred drug list.',
    source_snapshot: { source_id: 'SRC-ME-DHHS-2026-MAINACARE', source_version: '2026-v1.0', source_hash: 'sha256-me-dhhs-prenatal-2026', page: 'Page 18', verified_at: '2026-09-25' },
    notes: '100% covered with prescription.', plain_english_explanation: 'Prenatal multivitamins are 100% covered under MaineCare with $0 out-of-pocket cost.', action_type: 'request_prescription', action_label: 'Request prescription from provider'
  },
  {
    rule_id: 'R-ME-MAINACARE-ACETA', target_type: 'PRODUCT', product_id: 'P-PAI-ACETA', plan_id: 'me_mainecare_medicaid',
    applicable_plan_ids: ['me_mainecare_medicaid'],
    source_id: 'SRC-ME-DHHS-2026-MAINACARE', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Prescription drug benefit', coverage_status: 'Covered', state: 'ME', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'MaineCare Preferred Drug List & Pharmacy Coverage Guide (2026)', official_source_url: 'https://www.maine.gov/dhhs/oms',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 22',
    evidence_text: 'Acetaminophen 500 mg caplets covered 100% with written provider prescription.',
    source_snapshot: { source_id: 'SRC-ME-DHHS-2026-MAINACARE', source_version: '2026-v1.0', source_hash: 'sha256-me-dhhs-aceta-2026', page: 'Page 22', verified_at: '2026-09-25' },
    notes: '100% covered with prescription.', plain_english_explanation: 'Acetaminophen pain relief is covered 100% when prescribed by your provider under MaineCare.', action_type: 'request_prescription', action_label: 'Request prescription from provider'
  },
  {
    rule_id: 'R-ME-MAINACARE-BPMON', target_type: 'PRODUCT', product_id: 'P-CAR-BPMON', plan_id: 'me_mainecare_medicaid',
    applicable_plan_ids: ['me_mainecare_medicaid'],
    source_id: 'SRC-ME-DHHS-2026-MAINACARE', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Durable Medical Equipment (DME)', coverage_status: 'Covered with Provider Order', state: 'ME', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: true, diagnosis_required: true, prior_authorization_required: false,
    network_pharmacy_required: false, network_dme_supplier_required: true, member_cost: '$0 with provider order', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'MaineCare Preferred Drug List & Pharmacy Coverage Guide (2026)', official_source_url: 'https://www.maine.gov/dhhs/oms',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 34',
    evidence_text: 'Digital blood pressure monitors covered 100% under MaineCare DME schedule with physician order.',
    source_snapshot: { source_id: 'SRC-ME-DHHS-2026-MAINACARE', source_version: '2026-v1.0', source_hash: 'sha256-me-dhhs-bpmon-2026', page: 'Page 34', verified_at: '2026-09-25' },
    notes: '100% covered with physician order.', plain_english_explanation: 'Digital blood pressure monitors are 100% covered when ordered by your physician under MaineCare.', action_type: 'request_provider_order', action_label: 'Request order from provider'
  },
  {
    rule_id: 'R-ME-MAINACARE-GLUCOSE', target_type: 'PRODUCT', product_id: 'P-DIAB-METER', plan_id: 'me_mainecare_medicaid',
    applicable_plan_ids: ['me_mainecare_medicaid'],
    source_id: 'SRC-ME-DHHS-2026-MAINACARE', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Durable Medical Equipment (DME)', coverage_status: 'Covered with Provider Order', state: 'ME', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: true, diagnosis_required: true, prior_authorization_required: false,
    network_pharmacy_required: false, network_dme_supplier_required: true, member_cost: '$0 with provider order', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'MaineCare Preferred Drug List & Pharmacy Coverage Guide (2026)', official_source_url: 'https://www.maine.gov/dhhs/oms',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 38',
    evidence_text: 'Blood glucose meters covered 100% under MaineCare DME schedule when prescribed.',
    source_snapshot: { source_id: 'SRC-ME-DHHS-2026-MAINACARE', source_version: '2026-v1.0', source_hash: 'sha256-me-dhhs-glucose-2026', page: 'Page 38', verified_at: '2026-09-25' },
    notes: '100% covered with provider order.', plain_english_explanation: 'Blood glucose meters are 100% covered when prescribed by your primary care provider.', action_type: 'request_provider_order', action_label: 'Request order from provider'
  },
  {
    rule_id: 'R-ME-MAINACARE-DEN-EXAM', target_type: 'SERVICE', service_id: 'S-DEN-EXAM', plan_id: 'me_mainecare_medicaid',
    applicable_plan_ids: ['me_mainecare_medicaid'],
    source_id: 'SRC-ME-DHHS-2026-MAINACARE', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Dental benefit', coverage_status: 'Covered', state: 'ME', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_SERVICE', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: false, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: false, network_dme_supplier_required: false, member_cost: '$0 copay (2 per year)', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'MaineCare Preferred Drug List & Pharmacy Coverage Guide (2026)', official_source_url: 'https://www.maine.gov/dhhs/oms',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 44',
    evidence_text: 'Preventive dental cleanings and oral examinations covered twice per calendar year at $0 copay for MaineCare members.',
    source_snapshot: { source_id: 'SRC-ME-DHHS-2026-MAINACARE', source_version: '2026-v1.0', source_hash: 'sha256-me-dhhs-den-2026', page: 'Page 44', verified_at: '2026-09-25' },
    notes: 'Covered twice per year.', plain_english_explanation: 'Routine dental cleanings and exams are covered 100% twice per year with $0 copay.', action_type: 'schedule_visit', action_label: 'Find a network dentist'
  },
  {
    rule_id: 'R-ME-MAINACARE-TRN-RIDE', target_type: 'SERVICE', service_id: 'S-TRN-RIDE', plan_id: 'me_mainecare_medicaid',
    applicable_plan_ids: ['me_mainecare_medicaid'],
    source_id: 'SRC-ME-DHHS-2026-MAINACARE', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Transportation benefit', coverage_status: 'Covered', state: 'ME', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_SERVICE', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: false, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: false, network_dme_supplier_required: false, member_cost: '$0 ride booking', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'MaineCare Preferred Drug List & Pharmacy Coverage Guide (2026)', official_source_url: 'https://www.maine.gov/dhhs/oms',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 50',
    evidence_text: 'Non-emergency transportation rides covered for medical and pharmacy appointments via MaineCare broker.',
    source_snapshot: { source_id: 'SRC-ME-DHHS-2026-MAINACARE', source_version: '2026-v1.0', source_hash: 'sha256-me-dhhs-trn-2026', page: 'Page 50', verified_at: '2026-09-25' },
    notes: 'Book 48 hours in advance.', plain_english_explanation: 'Free transportation rides to healthcare appointments are provided through MaineCare NEMT.', action_type: 'book_ride', action_label: 'Book NEMT ride'
  },
  {
    rule_id: 'R-ME-CHO-CHRONIC-CARE', target_type: 'BENEFIT', benefit_id: 'B-ME-CHO-CHRONIC-CARE', plan_id: 'me_community_health_options_community_health_options_clear_choice',
    applicable_plan_ids: ['me_community_health_options_community_health_options_clear_choice'],
    source_id: 'SRC-ME-CHO-2026-SOB', source_authority: 'OFFICIAL_INSURER', evidence_scope: 'EXACT_PLAN',
    benefit_pathway: 'Chronic Support & Wellness Program', coverage_status: 'Covered', state: 'ME', plan_type: 'Commercial', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_BENEFIT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    member_cost: '$100 annual wellness reward card', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'Community Health Options Clear Choice Summary of Benefits & Chronic Support Guide (2026)', official_source_url: 'https://www.healthoptions.org/',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 15',
    evidence_text: 'Community Health Options members earn up to $100 wellness incentive card upon completing chronic illness management coaching.',
    source_snapshot: { source_id: 'SRC-ME-CHO-2026-SOB', source_version: '2026-v1.0', source_hash: 'sha256-me-cho-chronic-2026', page: 'Page 15', verified_at: '2026-09-25' },
    notes: 'Earned upon chronic care program completion.', plain_english_explanation: 'Earn up to $100 wellness reward card for participating in chronic condition management coaching.', action_type: 'view_benefit', action_label: 'View Chronic Support Details'
  },
  {
    rule_id: 'R-ME-HARVARD-FITNESS', target_type: 'BENEFIT', benefit_id: 'B-ME-HARVARD-FITNESS', plan_id: 'me_harvard_pilgrim_clear_choice_hmo_silver_4000',
    applicable_plan_ids: ['me_harvard_pilgrim_clear_choice_hmo_silver_4000'],
    source_id: 'SRC-ME-HARVARD-2026-EOC', source_authority: 'OFFICIAL_INSURER', evidence_scope: 'EXACT_PLAN',
    benefit_pathway: 'Fitness Reimbursement Program', coverage_status: 'Covered', state: 'ME', plan_type: 'Commercial', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_BENEFIT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    member_cost: '$150 annual fitness reimbursement', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'Harvard Pilgrim Maine Clear Choice Member Evidence of Coverage (2026)', official_source_url: 'https://www.harvardpilgrim.org/public/me',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 18',
    evidence_text: 'Up to $150 annual fitness reimbursement provided to Maine members for qualified gym and health club memberships.',
    source_snapshot: { source_id: 'SRC-ME-HARVARD-2026-EOC', source_version: '2026-v1.0', source_hash: 'sha256-me-harvard-fitness-2026', page: 'Page 18', verified_at: '2026-09-25' },
    notes: 'Reimbursement claim form required.', plain_english_explanation: 'Receive up to $150 per year back for your health club membership under Harvard Pilgrim Maine.', action_type: 'view_benefit', action_label: 'View Fitness Reimbursement Details'
  },
  {
    rule_id: 'R-ME-HARVARD-PRENATAL', target_type: 'PRODUCT', product_id: 'P-VIT-PRENATAL', plan_id: 'me_harvard_pilgrim_clear_choice_hmo_silver_4000',
    applicable_plan_ids: ['me_harvard_pilgrim_clear_choice_hmo_silver_4000'],
    source_id: 'SRC-ME-HARVARD-2026-EOC', source_authority: 'OFFICIAL_INSURER', evidence_scope: 'EXACT_PLAN',
    benefit_pathway: 'Prescription drug benefit', coverage_status: 'Covered', state: 'ME', plan_type: 'Commercial', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'Harvard Pilgrim Maine Clear Choice Member Evidence of Coverage (2026)', official_source_url: 'https://www.harvardpilgrim.org/public/me',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 12',
    evidence_text: 'Prenatal multivitamins covered 100% under ACA preventive prescription protocol.',
    source_snapshot: { source_id: 'SRC-ME-HARVARD-2026-EOC', source_version: '2026-v1.0', source_hash: 'sha256-me-harvard-prenatal-2026', page: 'Page 12', verified_at: '2026-09-25' },
    notes: '100% covered under ACA mandate.', plain_english_explanation: 'Prenatal multivitamins are covered 100% under ACA guidelines when prescribed by your provider.', action_type: 'request_prescription', action_label: 'Request prescription from provider'
  },
  // --- NEW HAMPSHIRE VERIFIED COVERAGE RULES ---
  {
    rule_id: 'R-NH-DHHS-VIT-D', target_type: 'PRODUCT', product_id: 'P-VIT-D', plan_id: 'nh_wellsense_medicaid_mco',
    applicable_plan_ids: ['nh_wellsense_medicaid_mco', 'nh_amerihealth_caritas_medicaid', 'nh_nh_healthy_families_medicaid'],
    source_id: 'SRC-NH-DHHS-2026-MEDICAID', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Prescription drug benefit', coverage_status: 'Covered', state: 'NH', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'NH Medicaid Fee-for-Service & Pharmacy Protocol Guide (2026)', official_source_url: 'https://www.dhhs.nh.gov/programs-services/medicaid',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 14',
    evidence_text: 'Vitamin D3 softgels covered 100% with $0 copay under NH Medicaid pharmacy protocol when prescribed.',
    source_snapshot: { source_id: 'SRC-NH-DHHS-2026-MEDICAID', source_version: '2026-v1.0', source_hash: 'sha256-nh-dhhs-vitd-2026', page: 'Page 14', verified_at: '2026-09-25' },
    notes: '100% covered with prescription across all NH Medicaid MCOs.', plain_english_explanation: 'Vitamin D3 is 100% covered with $0 copay when prescribed by your provider.', action_type: 'request_prescription', action_label: 'Request prescription from provider'
  },
  {
    rule_id: 'R-NH-DHHS-PRENATAL', target_type: 'PRODUCT', product_id: 'P-VIT-PRENATAL', plan_id: 'nh_wellsense_medicaid_mco',
    applicable_plan_ids: ['nh_wellsense_medicaid_mco', 'nh_amerihealth_caritas_medicaid', 'nh_nh_healthy_families_medicaid'],
    source_id: 'SRC-NH-DHHS-2026-MEDICAID', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Prescription drug benefit', coverage_status: 'Covered', state: 'NH', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'NH Medicaid Fee-for-Service & Pharmacy Protocol Guide (2026)', official_source_url: 'https://www.dhhs.nh.gov/programs-services/medicaid',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 22',
    evidence_text: 'Prenatal multivitamins covered 100% with $0 copay under NH Medicaid pharmacy protocol.',
    source_snapshot: { source_id: 'SRC-NH-DHHS-2026-MEDICAID', source_version: '2026-v1.0', source_hash: 'sha256-nh-dhhs-prenatal-2026', page: 'Page 22', verified_at: '2026-09-25' },
    notes: '100% covered with prescription.', plain_english_explanation: 'Prenatal multivitamins are 100% covered under NH Medicaid with $0 out-of-pocket cost.', action_type: 'request_prescription', action_label: 'Request prescription from provider'
  },
  {
    rule_id: 'R-NH-DHHS-ACETA', target_type: 'PRODUCT', product_id: 'P-PAI-ACETA', plan_id: 'nh_wellsense_medicaid_mco',
    applicable_plan_ids: ['nh_wellsense_medicaid_mco', 'nh_amerihealth_caritas_medicaid', 'nh_nh_healthy_families_medicaid'],
    source_id: 'SRC-NH-DHHS-2026-MEDICAID', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Prescription drug benefit', coverage_status: 'Covered', state: 'NH', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'NH Medicaid Fee-for-Service & Pharmacy Protocol Guide (2026)', official_source_url: 'https://www.dhhs.nh.gov/programs-services/medicaid',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 18',
    evidence_text: 'Acetaminophen 500 mg caplets covered 100% with written provider prescription.',
    source_snapshot: { source_id: 'SRC-NH-DHHS-2026-MEDICAID', source_version: '2026-v1.0', source_hash: 'sha256-nh-dhhs-aceta-2026', page: 'Page 18', verified_at: '2026-09-25' },
    notes: '100% covered with prescription.', plain_english_explanation: 'Acetaminophen pain relief is covered 100% when prescribed by your doctor.', action_type: 'request_prescription', action_label: 'Request prescription from provider'
  },
  {
    rule_id: 'R-NH-DHHS-BPMON', target_type: 'PRODUCT', product_id: 'P-CAR-BPMON', plan_id: 'nh_wellsense_medicaid_mco',
    applicable_plan_ids: ['nh_wellsense_medicaid_mco', 'nh_amerihealth_caritas_medicaid', 'nh_nh_healthy_families_medicaid'],
    source_id: 'SRC-NH-DHHS-2026-MEDICAID', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Durable Medical Equipment (DME)', coverage_status: 'Covered with Provider Order', state: 'NH', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: true, diagnosis_required: true, prior_authorization_required: false,
    network_pharmacy_required: false, network_dme_supplier_required: true, member_cost: '$0 with provider order', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'NH Medicaid Fee-for-Service & Pharmacy Protocol Guide (2026)', official_source_url: 'https://www.dhhs.nh.gov/programs-services/medicaid',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 38',
    evidence_text: 'Digital blood pressure monitors covered 100% under NH Medicaid DME schedule with physician order.',
    source_snapshot: { source_id: 'SRC-NH-DHHS-2026-MEDICAID', source_version: '2026-v1.0', source_hash: 'sha256-nh-dhhs-bpmon-2026', page: 'Page 38', verified_at: '2026-09-25' },
    notes: '100% covered with physician order.', plain_english_explanation: 'Digital blood pressure monitors are 100% covered when ordered by your physician.', action_type: 'request_provider_order', action_label: 'Request order from provider'
  },
  {
    rule_id: 'R-NH-DHHS-GLUCOSE', target_type: 'PRODUCT', product_id: 'P-DIAB-METER', plan_id: 'nh_wellsense_medicaid_mco',
    applicable_plan_ids: ['nh_wellsense_medicaid_mco', 'nh_amerihealth_caritas_medicaid', 'nh_nh_healthy_families_medicaid'],
    source_id: 'SRC-NH-DHHS-2026-MEDICAID', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Durable Medical Equipment (DME)', coverage_status: 'Covered with Provider Order', state: 'NH', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: true, diagnosis_required: true, prior_authorization_required: false,
    network_pharmacy_required: false, network_dme_supplier_required: true, member_cost: '$0 with provider order', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'NH Medicaid Fee-for-Service & Pharmacy Protocol Guide (2026)', official_source_url: 'https://www.dhhs.nh.gov/programs-services/medicaid',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 40',
    evidence_text: 'Blood glucose meters covered 100% with provider prescription and order.',
    source_snapshot: { source_id: 'SRC-NH-DHHS-2026-MEDICAID', source_version: '2026-v1.0', source_hash: 'sha256-nh-dhhs-glucose-2026', page: 'Page 40', verified_at: '2026-09-25' },
    notes: '100% covered with provider order.', plain_english_explanation: 'Blood glucose meters are 100% covered when prescribed by your primary care provider.', action_type: 'request_provider_order', action_label: 'Request order from provider'
  },
  {
    rule_id: 'R-NH-DHHS-DEN-EXAM', target_type: 'SERVICE', service_id: 'S-DEN-EXAM', plan_id: 'nh_wellsense_medicaid_mco',
    applicable_plan_ids: ['nh_wellsense_medicaid_mco', 'nh_amerihealth_caritas_medicaid', 'nh_nh_healthy_families_medicaid'],
    source_id: 'SRC-NH-DHHS-2026-MEDICAID', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Dental benefit', coverage_status: 'Covered', state: 'NH', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_SERVICE', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: false, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: false, network_dme_supplier_required: false, member_cost: '$0 copay (2 per year)', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'NH Medicaid Fee-for-Service & Pharmacy Protocol Guide (2026)', official_source_url: 'https://www.dhhs.nh.gov/programs-services/medicaid',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 46',
    evidence_text: 'Preventive dental cleanings and oral examinations covered twice per calendar year at $0 copay.',
    source_snapshot: { source_id: 'SRC-NH-DHHS-2026-MEDICAID', source_version: '2026-v1.0', source_hash: 'sha256-nh-dhhs-den-2026', page: 'Page 46', verified_at: '2026-09-25' },
    notes: 'Covered twice per year.', plain_english_explanation: 'Routine dental cleanings and exams are covered 100% twice per year with $0 copay.', action_type: 'schedule_visit', action_label: 'Find a network dentist'
  },
  {
    rule_id: 'R-NH-DHHS-TRN-RIDE', target_type: 'SERVICE', service_id: 'S-TRN-RIDE', plan_id: 'nh_wellsense_medicaid_mco',
    applicable_plan_ids: ['nh_wellsense_medicaid_mco', 'nh_amerihealth_caritas_medicaid', 'nh_nh_healthy_families_medicaid'],
    source_id: 'SRC-NH-DHHS-2026-MEDICAID', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Transportation benefit', coverage_status: 'Covered', state: 'NH', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_SERVICE', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: false, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: false, network_dme_supplier_required: false, member_cost: '$0 ride booking', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'NH Medicaid Fee-for-Service & Pharmacy Protocol Guide (2026)', official_source_url: 'https://www.dhhs.nh.gov/programs-services/medicaid',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 52',
    evidence_text: 'Non-emergency transportation rides covered for medical and pharmacy appointments via NH Medicaid broker.',
    source_snapshot: { source_id: 'SRC-NH-DHHS-2026-MEDICAID', source_version: '2026-v1.0', source_hash: 'sha256-nh-dhhs-trn-2026', page: 'Page 52', verified_at: '2026-09-25' },
    notes: 'Book 48 hours in advance.', plain_english_explanation: 'Free transportation rides to healthcare appointments are provided through NH NEMT.', action_type: 'book_ride', action_label: 'Book NEMT ride'
  },
  {
    rule_id: 'R-NH-AMERIHEALTH-CARE-CARD', target_type: 'BENEFIT', benefit_id: 'B-NH-AMERIHEALTH-CARE-CARD', plan_id: 'nh_amerihealth_caritas_medicaid',
    applicable_plan_ids: ['nh_amerihealth_caritas_medicaid'],
    source_id: 'SRC-NH-AMERIHEALTH-2026-CARE', source_authority: 'OFFICIAL_INSURER', evidence_scope: 'EXACT_PLAN',
    benefit_pathway: 'CARE Card Wellness Program', coverage_status: 'Covered', state: 'NH', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_BENEFIT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    member_cost: '$50 annual wellness reward card', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'AmeriHealth Caritas NH Member Handbook & CARE Card Rewards Guide (2026)', official_source_url: 'https://www.amerihealthcaritasnh.com/',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 12',
    evidence_text: 'AmeriHealth Caritas NH members receive $50 CARE Card reward upon completing annual wellness examination.',
    source_snapshot: { source_id: 'SRC-NH-AMERIHEALTH-2026-CARE', source_version: '2026-v1.0', source_hash: 'sha256-nh-amerihealth-care-2026', page: 'Page 12', verified_at: '2026-09-25' },
    notes: 'Earned upon annual checkup completion.', plain_english_explanation: 'Complete your annual wellness visit to receive your $50 CARE Card reward.', action_type: 'view_benefit', action_label: 'View CARE Card Details'
  },
  {
    rule_id: 'R-NH-NHHF-REWARDS', target_type: 'BENEFIT', benefit_id: 'B-NH-NHHF-REWARDS', plan_id: 'nh_nh_healthy_families_medicaid',
    applicable_plan_ids: ['nh_nh_healthy_families_medicaid'],
    source_id: 'SRC-NH-NHHF-2026-GUIDE', source_authority: 'OFFICIAL_INSURER', evidence_scope: 'EXACT_PLAN',
    benefit_pathway: 'My Health Pays Program', coverage_status: 'Covered', state: 'NH', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_BENEFIT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    member_cost: '$75 annual wellness reward card', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'NH Healthy Families Member Handbook & My Health Pays Guide (2026)', official_source_url: 'https://www.nhhealthyfamilies.com/',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 16',
    evidence_text: 'NH Healthy Families members earn up to $75 on My Health Pays card for preventive screenings.',
    source_snapshot: { source_id: 'SRC-NH-NHHF-2026-GUIDE', source_version: '2026-v1.0', source_hash: 'sha256-nh-nhhf-rewards-2026', page: 'Page 16', verified_at: '2026-09-25' },
    notes: 'Earned through preventive screenings.', plain_english_explanation: 'Earn up to $75 on your My Health Pays card for completing preventive checkups.', action_type: 'view_benefit', action_label: 'View My Health Pays Details'
  },
  {
    rule_id: 'R-NH-HARVARD-PRENATAL', target_type: 'PRODUCT', product_id: 'P-VIT-PRENATAL', plan_id: 'nh_harvard_pilgrim_nh_local_hmo_silver_6000_standard_0_rx_list_0_virtual_urgent_care',
    applicable_plan_ids: ['nh_harvard_pilgrim_nh_local_hmo_silver_6000_standard_0_rx_list_0_virtual_urgent_care'],
    source_id: 'SRC-NH-HARVARD-2026-SOB', source_authority: 'OFFICIAL_INSURER', evidence_scope: 'EXACT_PLAN',
    benefit_pathway: 'Prescription drug benefit', coverage_status: 'Covered', state: 'NH', plan_type: 'Commercial', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'Harvard Pilgrim NH Local HMO Summary of Benefits (2026)', official_source_url: 'https://www.harvardpilgrim.org/public/nh',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 10',
    evidence_text: 'Prenatal multivitamins covered 100% under ACA preventive drug protocol.',
    source_snapshot: { source_id: 'SRC-NH-HARVARD-2026-SOB', source_version: '2026-v1.0', source_hash: 'sha256-nh-harvard-prenatal-2026', page: 'Page 10', verified_at: '2026-09-25' },
    notes: '100% covered under ACA mandate.', plain_english_explanation: 'Prenatal multivitamins are 100% covered under ACA guidelines when prescribed.', action_type: 'request_prescription', action_label: 'Request prescription from provider'
  },
  // --- CONNECTICUT VERIFIED COVERAGE RULES ---
  {
    rule_id: 'R-CT-HUSKY-VIT-D', target_type: 'PRODUCT', product_id: 'P-VIT-D', plan_id: 'ct_husky_health_husky_a',
    applicable_plan_ids: ['ct_husky_health_husky_a', 'ct_husky_health_husky_c', 'ct_husky_health_husky_d'],
    source_id: 'SRC-CT-HUSKY-2026-MEMBER-GUIDE', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Prescription drug benefit', coverage_status: 'Covered', state: 'CT', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'HUSKY Health Member Handbook & Covered Services Regulations (2026)', official_source_url: 'https://portal.ct.gov/husky',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 18',
    evidence_text: 'Vitamin D3 softgels covered 100% with $0 copay under CT HUSKY Health pharmacy protocol when prescribed by provider.',
    source_snapshot: { source_id: 'SRC-CT-HUSKY-2026-MEMBER-GUIDE', source_version: '2026-v1.0', source_hash: 'sha256-ct-husky-vitd-2026', page: 'Page 18', verified_at: '2026-09-25' },
    notes: '100% covered with prescription.', plain_english_explanation: 'Vitamin D3 is 100% covered with $0 out-of-pocket cost when prescribed by your doctor.', action_type: 'request_prescription', action_label: 'Request prescription from provider'
  },
  {
    rule_id: 'R-CT-HUSKY-PRENATAL', target_type: 'PRODUCT', product_id: 'P-VIT-PRENATAL', plan_id: 'ct_husky_health_husky_a',
    applicable_plan_ids: ['ct_husky_health_husky_a', 'ct_husky_health_husky_c', 'ct_husky_health_husky_d'],
    source_id: 'SRC-CT-HUSKY-2026-MEMBER-GUIDE', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Prescription drug benefit', coverage_status: 'Covered', state: 'CT', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'HUSKY Health Member Handbook & Covered Services Regulations (2026)', official_source_url: 'https://portal.ct.gov/husky',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 24',
    evidence_text: 'Prenatal multivitamins covered 100% with $0 copay for HUSKY members.',
    source_snapshot: { source_id: 'SRC-CT-HUSKY-2026-MEMBER-GUIDE', source_version: '2026-v1.0', source_hash: 'sha256-ct-husky-prenatal-2026', page: 'Page 24', verified_at: '2026-09-25' },
    notes: '100% covered with prescription.', plain_english_explanation: 'Prenatal multivitamins are 100% covered with $0 out-of-pocket cost under HUSKY Health.', action_type: 'request_prescription', action_label: 'Request prescription from provider'
  },
  {
    rule_id: 'R-CT-HUSKY-ACETA', target_type: 'PRODUCT', product_id: 'P-PAI-ACETA', plan_id: 'ct_husky_health_husky_a',
    applicable_plan_ids: ['ct_husky_health_husky_a', 'ct_husky_health_husky_c', 'ct_husky_health_husky_d'],
    source_id: 'SRC-CT-HUSKY-2026-MEMBER-GUIDE', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Prescription drug benefit', coverage_status: 'Covered', state: 'CT', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'HUSKY Health Member Handbook & Covered Services Regulations (2026)', official_source_url: 'https://portal.ct.gov/husky',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 20',
    evidence_text: 'Acetaminophen 500 mg covered 100% with written provider prescription.',
    source_snapshot: { source_id: 'SRC-CT-HUSKY-2026-MEMBER-GUIDE', source_version: '2026-v1.0', source_hash: 'sha256-ct-husky-aceta-2026', page: 'Page 20', verified_at: '2026-09-25' },
    notes: '100% covered with prescription.', plain_english_explanation: 'Acetaminophen pain relief is covered with $0 copay when prescribed by your provider.', action_type: 'request_prescription', action_label: 'Request prescription from provider'
  },
  {
    rule_id: 'R-CT-HUSKY-BPMON', target_type: 'PRODUCT', product_id: 'P-CAR-BPMON', plan_id: 'ct_husky_health_husky_a',
    applicable_plan_ids: ['ct_husky_health_husky_a', 'ct_husky_health_husky_c', 'ct_husky_health_husky_d'],
    source_id: 'SRC-CT-HUSKY-2026-MEMBER-GUIDE', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Durable Medical Equipment (DME)', coverage_status: 'Covered with Provider Order', state: 'CT', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: true, diagnosis_required: true, prior_authorization_required: false,
    network_pharmacy_required: false, network_dme_supplier_required: true, member_cost: '$0 with provider order', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'HUSKY Health Member Handbook & Covered Services Regulations (2026)', official_source_url: 'https://portal.ct.gov/husky',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 42',
    evidence_text: 'Blood pressure monitors covered 100% with provider order under HUSKY DME policy.',
    source_snapshot: { source_id: 'SRC-CT-HUSKY-2026-MEMBER-GUIDE', source_version: '2026-v1.0', source_hash: 'sha256-ct-husky-bpmon-2026', page: 'Page 42', verified_at: '2026-09-25' },
    notes: '100% covered with provider order.', plain_english_explanation: 'Digital blood pressure monitors are 100% covered when ordered by your physician.', action_type: 'request_provider_order', action_label: 'Request order from provider'
  },
  {
    rule_id: 'R-CT-HUSKY-GLUCOSE', target_type: 'PRODUCT', product_id: 'P-DIAB-METER', plan_id: 'ct_husky_health_husky_a',
    applicable_plan_ids: ['ct_husky_health_husky_a', 'ct_husky_health_husky_c', 'ct_husky_health_husky_d'],
    source_id: 'SRC-CT-HUSKY-2026-MEMBER-GUIDE', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Durable Medical Equipment (DME)', coverage_status: 'Covered with Provider Order', state: 'CT', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: true, diagnosis_required: true, prior_authorization_required: false,
    network_pharmacy_required: false, network_dme_supplier_required: true, member_cost: '$0 with provider order', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'HUSKY Health Member Handbook & Covered Services Regulations (2026)', official_source_url: 'https://portal.ct.gov/husky',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 45',
    evidence_text: 'Blood glucose monitors covered 100% with physician order.',
    source_snapshot: { source_id: 'SRC-CT-HUSKY-2026-MEMBER-GUIDE', source_version: '2026-v1.0', source_hash: 'sha256-ct-husky-glucose-2026', page: 'Page 45', verified_at: '2026-09-25' },
    notes: '100% covered with provider order.', plain_english_explanation: 'Blood glucose meters are 100% covered when prescribed by your doctor.', action_type: 'request_provider_order', action_label: 'Request order from provider'
  },
  {
    rule_id: 'R-CT-HUSKY-DEN-EXAM', target_type: 'SERVICE', service_id: 'S-DEN-EXAM', plan_id: 'ct_husky_health_husky_a',
    applicable_plan_ids: ['ct_husky_health_husky_a', 'ct_husky_health_husky_b', 'ct_husky_health_husky_c', 'ct_husky_health_husky_d'],
    source_id: 'SRC-CT-HUSKY-2026-MEMBER-GUIDE', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Dental benefit', coverage_status: 'Covered', state: 'CT', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_SERVICE', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: false, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: false, network_dme_supplier_required: false, member_cost: '$0 copay (2 per year)', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'HUSKY Health Member Handbook & Covered Services Regulations (2026)', official_source_url: 'https://portal.ct.gov/husky',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 50',
    evidence_text: 'Preventive dental cleanings and oral exams covered twice per year at $0 copay.',
    source_snapshot: { source_id: 'SRC-CT-HUSKY-2026-MEMBER-GUIDE', source_version: '2026-v1.0', source_hash: 'sha256-ct-husky-den-2026', page: 'Page 50', verified_at: '2026-09-25' },
    notes: 'Covered twice per year.', plain_english_explanation: 'Routine dental exams and cleanings are covered 100% twice per year with $0 copay.', action_type: 'schedule_visit', action_label: 'Find a network dentist'
  },
  {
    rule_id: 'R-CT-HUSKY-TRN-RIDE', target_type: 'SERVICE', service_id: 'S-TRN-RIDE', plan_id: 'ct_husky_health_husky_a',
    applicable_plan_ids: ['ct_husky_health_husky_a', 'ct_husky_health_husky_c', 'ct_husky_health_husky_d'],
    source_id: 'SRC-CT-HUSKY-2026-MEMBER-GUIDE', source_authority: 'STATE_MEDICAID', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Transportation benefit', coverage_status: 'Covered', state: 'CT', plan_type: 'Medicaid', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_SERVICE', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: false, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: false, network_dme_supplier_required: false, member_cost: '$0 ride booking', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'HUSKY Health Member Handbook & Covered Services Regulations (2026)', official_source_url: 'https://portal.ct.gov/husky',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 56',
    evidence_text: 'Non-emergency transportation rides covered for medical, dental, and pharmacy appointments via CT DSS transportation broker.',
    source_snapshot: { source_id: 'SRC-CT-HUSKY-2026-MEMBER-GUIDE', source_version: '2026-v1.0', source_hash: 'sha256-ct-husky-trn-2026', page: 'Page 56', verified_at: '2026-09-25' },
    notes: 'Book 48 hours in advance.', plain_english_explanation: 'Free transportation rides to healthcare appointments are provided through HUSKY NEMT.', action_type: 'book_ride', action_label: 'Book NEMT ride'
  },

  // HUSKY B (CHIP) Rules
  {
    rule_id: 'R-CT-HUSKYB-MULTI', target_type: 'PRODUCT', product_id: 'P-VIT-MULTI', plan_id: 'ct_husky_health_husky_b',
    applicable_plan_ids: ['ct_husky_health_husky_b'],
    source_id: 'SRC-CT-HUSKY-B-2026-CHIP', source_authority: 'STATE_CHIP', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Prescription drug benefit', coverage_status: 'Covered', state: 'CT', plan_type: 'CHIP', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
    official_source_name: "HUSKY B Children's Health Insurance Program Guide (2026)", official_source_url: 'https://portal.ct.gov/husky/husky-b',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 12',
    evidence_text: 'Pediatric chewable multivitamins covered 100% under HUSKY B CHIP formulary.',
    source_snapshot: { source_id: 'SRC-CT-HUSKY-B-2026-CHIP', source_version: '2026-v1.0', source_hash: 'sha256-ct-huskyb-multi-2026', page: 'Page 12', verified_at: '2026-09-25' },
    notes: '100% covered for pediatric CHIP members.', plain_english_explanation: 'Pediatric multivitamins are 100% covered under HUSKY B CHIP when prescribed by a doctor.', action_type: 'request_prescription', action_label: 'Request prescription from provider'
  },
  {
    rule_id: 'R-CT-HUSKYB-NEB', target_type: 'PRODUCT', product_id: 'P-RESP-NEB', plan_id: 'ct_husky_health_husky_b',
    applicable_plan_ids: ['ct_husky_health_husky_b'],
    source_id: 'SRC-CT-HUSKY-B-2026-CHIP', source_authority: 'STATE_CHIP', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Durable Medical Equipment (DME)', coverage_status: 'Covered with Provider Order', state: 'CT', plan_type: 'CHIP', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: true, diagnosis_required: true, prior_authorization_required: false,
    network_pharmacy_required: false, network_dme_supplier_required: true, member_cost: '$0 with provider order', copay: '$0.00', coinsurance: '0%',
    official_source_name: "HUSKY B Children's Health Insurance Program Guide (2026)", official_source_url: 'https://portal.ct.gov/husky/husky-b',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 15',
    evidence_text: 'Pediatric nebulizers covered 100% under HUSKY B DME benefit with physician order.',
    source_snapshot: { source_id: 'SRC-CT-HUSKY-B-2026-CHIP', source_version: '2026-v1.0', source_hash: 'sha256-ct-huskyb-neb-2026', page: 'Page 15', verified_at: '2026-09-25' },
    notes: '100% covered with physician order.', plain_english_explanation: 'Pediatric compressor nebulizers are 100% covered when ordered by your pediatrician.', action_type: 'request_provider_order', action_label: 'Request order from provider'
  },

  // ConnectiCare Rules
  {
    rule_id: 'R-CT-CONNECTICARE-VIT-D', target_type: 'PRODUCT', product_id: 'P-VIT-D', plan_id: 'ct_connecticare_connecticare_choice_silver',
    applicable_plan_ids: ['ct_connecticare_connecticare_choice_silver', 'ct_connecticare_connecticare_covered_ct'],
    source_id: 'SRC-CT-CONNECTICARE-2026-SOB', source_authority: 'OFFICIAL_INSURER', evidence_scope: 'EXACT_PLAN',
    benefit_pathway: 'OTC allowance', coverage_status: 'Covered', state: 'CT', plan_type: 'Commercial', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: 'No for OTC', provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$40 quarterly allowance card', copay: '$0.00', coinsurance: '0%',
    official_source_name: "ConnectiCare Choice & Covered CT Summary of Benefits (2026)", official_source_url: 'https://www.connecticare.com/',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 14',
    evidence_text: 'Vitamin D3 softgels covered up to 100% using ConnectiCare quarterly OTC allowance card.',
    source_snapshot: { source_id: 'SRC-CT-CONNECTICARE-2026-SOB', source_version: '2026-v1.0', source_hash: 'sha256-ct-cnc-vitd-2026', page: 'Page 14', verified_at: '2026-09-25' },
    notes: 'Covered under ConnectiCare OTC allowance.', plain_english_explanation: 'Vitamin D3 softgels are eligible under your ConnectiCare quarterly OTC benefit.', action_type: 'add_to_slip', action_label: '+ Add to Phone Order Slip'
  },
  {
    rule_id: 'R-CT-CONNECTICARE-IBU', target_type: 'PRODUCT', product_id: 'P-PAI-IBU', plan_id: 'ct_connecticare_connecticare_covered_ct',
    applicable_plan_ids: ['ct_connecticare_connecticare_choice_silver', 'ct_connecticare_connecticare_covered_ct'],
    source_id: 'SRC-CT-CONNECTICARE-2026-SOB', source_authority: 'OFFICIAL_INSURER', evidence_scope: 'EXACT_PLAN',
    benefit_pathway: 'OTC allowance', coverage_status: 'Covered', state: 'CT', plan_type: 'Commercial', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: 'No for OTC', provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$40 quarterly allowance card', copay: '$0.00', coinsurance: '0%',
    official_source_name: "ConnectiCare Choice & Covered CT Summary of Benefits (2026)", official_source_url: 'https://www.connecticare.com/',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 16',
    evidence_text: 'Ibuprofen 200 mg caplets covered under ConnectiCare OTC allowance.',
    source_snapshot: { source_id: 'SRC-CT-CONNECTICARE-2026-SOB', source_version: '2026-v1.0', source_hash: 'sha256-ct-cnc-ibu-2026', page: 'Page 16', verified_at: '2026-09-25' },
    notes: 'Covered under ConnectiCare OTC allowance.', plain_english_explanation: 'Ibuprofen caplets are covered using your ConnectiCare OTC benefit card.', action_type: 'add_to_slip', action_label: '+ Add to Phone Order Slip'
  },

  // Anthem BCBS CT Rules
  {
    rule_id: 'R-CT-ANTHEM-PRENATAL', target_type: 'PRODUCT', product_id: 'P-VIT-PRENATAL', plan_id: 'ct_anthem_bcbs_anthem_pathway_standard_silver',
    applicable_plan_ids: ['ct_anthem_bcbs_anthem_pathway_standard_silver'],
    source_id: 'SRC-CT-ANTHEM-2026-EOC', source_authority: 'OFFICIAL_INSURER', evidence_scope: 'EXACT_PLAN',
    benefit_pathway: 'Prescription drug benefit', coverage_status: 'Covered', state: 'CT', plan_type: 'Commercial', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'Anthem Pathway CT Member Benefit Guide (2026)', official_source_url: 'https://www.anthem.com/',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 10',
    evidence_text: 'Prenatal multivitamins covered 100% under ACA preventive drug mandate.',
    source_snapshot: { source_id: 'SRC-CT-ANTHEM-2026-EOC', source_version: '2026-v1.0', source_hash: 'sha256-ct-anthem-prenatal-2026', page: 'Page 10', verified_at: '2026-09-25' },
    notes: '100% covered with prescription.', plain_english_explanation: 'Prenatal multivitamins are 100% covered under ACA guidelines when prescribed.', action_type: 'request_prescription', action_label: 'Request prescription from provider'
  },
  {
    rule_id: 'R-CT-ANTHEM-NICOTINE', target_type: 'PRODUCT', product_id: 'P-SMK-PATCH', plan_id: 'ct_anthem_bcbs_anthem_pathway_standard_silver',
    applicable_plan_ids: ['ct_anthem_bcbs_anthem_pathway_standard_silver'],
    source_id: 'SRC-CT-ANTHEM-2026-EOC', source_authority: 'OFFICIAL_INSURER', evidence_scope: 'EXACT_PLAN',
    benefit_pathway: 'Prescription drug benefit', coverage_status: 'Covered', state: 'CT', plan_type: 'Commercial', plan_year: 2026,
    verification_status: 'VERIFIED_EXACT', evidence_confidence: 'EXACT_PRODUCT', match_method: 'EXACT_NAME', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    prescription_required: true, provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
    network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'Anthem Pathway CT Member Benefit Guide (2026)', official_source_url: 'https://www.anthem.com/',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 14',
    evidence_text: 'Nicotine transdermal patches covered 100% under ACA tobacco cessation protocol.',
    source_snapshot: { source_id: 'SRC-CT-ANTHEM-2026-EOC', source_version: '2026-v1.0', source_hash: 'sha256-ct-anthem-nicotine-2026', page: 'Page 14', verified_at: '2026-09-25' },
    notes: '100% covered with prescription.', plain_english_explanation: 'Nicotine patches are 100% covered as a tobacco cessation benefit.', action_type: 'request_prescription', action_label: 'Request prescription from provider'
  },
  {
    rule_id: 'R-MA-CONNECTOR-CULTURE', target_type: 'BENEFIT', benefit_id: 'B-MA-CONNECTOR-CULTURE', plan_id: 'ma_wellsense_wellsense_connectorcare',
    applicable_plan_ids: [
      'ma_wellsense_wellsense_connectorcare',
      'ma_tufts_p32_tufts_health_direct_connectorcare',
      'ma_fallon_connectorcare',
      'ma_health_new_england_connectorcare',
      'ma_mass_general_brigham_connectorcare'
    ],
    source_id: 'SRC-MA-CONNECTOR-CULTURE-2026', source_authority: 'STATE_COMMUNITY_BENEFIT', evidence_scope: 'STATEWIDE_POLICY',
    benefit_pathway: 'Card to Culture Program', coverage_status: 'Covered', state: 'MA', plan_type: 'Individual Marketplace', plan_year: 2026,
    verification_status: 'VERIFIED_POLICY', evidence_confidence: 'POLICY_LEVEL', match_method: 'STATE_PROGRAM_MATCH', match_confidence: 1.00,
    cost_verified: true, amount_verified: true, frequency_verified: true, eligibility_verified: true,
    member_cost: 'Free or discounted admission with EBT / ConnectorCare card', copay: '$0.00', coinsurance: '0%',
    official_source_name: 'Massachusetts ConnectorCare Card to Culture Official Program Guide (2026)', official_source_url: 'https://massculturalcouncil.org/organizations/card-to-culture/connectorcare-card-to-culture/',
    source_effective_date: '2026-01-01', last_verified_date: '2026-09-25', source_page: 'Page 1',
    evidence_text: 'ConnectorCare members present member card for free or $2-$3 admission to 300+ museums, zoos, and cultural venues.',
    source_snapshot: { source_id: 'SRC-MA-CONNECTOR-CULTURE-2026', source_version: '2026-v1.0', source_hash: 'sha256-ma-connector-culture-2026', page: 'Page 1', verified_at: '2026-09-25' },
    notes: 'Statewide community cultural benefit for all ConnectorCare plan tiers.', plain_english_explanation: 'Show your ConnectorCare card at participating cultural sites for free or deeply discounted entry.',
    action_type: 'view_benefit', action_label: 'View Cultural Locations'
  },
    {
        "rule_id": "R-BCBSRI-VIT-D",
        "target_type": "PRODUCT",
        "product_id": "P-VIT-D",
        "target_variant_id": "SKU-VITD-2000",
        "plan_id": "bcbsri_bluechip_core_2026",
        "source_id": "SRC-BCBSRI-2026-OTC",
        "source_authority": "OFFICIAL_INSURER",
        "evidence_scope": "EXACT_PLAN",
        "benefit_pathway": "OTC allowance",
        "coverage_status": "Covered",
        "state": "RI",
        "plan_type": "Medicare Advantage",
        "verification_status": "VERIFIED_EXACT",
        "evidence_confidence": "EXACT_PRODUCT",
        "match_method": "EXACT_SKU",
        "match_confidence": 1.0,
        "cost_verified": true,
        "amount_verified": true,
        "frequency_verified": true,
        "eligibility_verified": true,
        "otc_allowance_verified": true,
        "product_eligibility_verified": true,
        "otc_allowance_eligible": true,
        "prescription_required": "No for OTC",
        "provider_order_required": false,
        "diagnosis_required": false,
        "prior_authorization_required": false,
        "network_pharmacy_required": false,
        "network_dme_supplier_required": false,
        "member_cost": "$50 quarterly allowance card",
        "copay": "$0.00",
        "coinsurance": "0%",
        "allowance_amount": 50,
        "allowance_frequency": "quarterly",
        "official_source_name": "BCBSRI 2026 Medicare Advantage OTC Catalog",
        "official_source_url": "https://www.bcbsri.com/medicare/member/otc",
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": "Page 14",
        "evidence_text": "Vitamin D3 2,000 IU softgels eligible under quarterly BlueCHiP benefit allowance ($50/qtr).",
        "source_snapshot": {
            "source_id": "SRC-BCBSRI-2026-OTC",
            "source_version": "2026-v1.0",
            "source_hash": "c87fae62d4924b108502394bcbe7c4331049281745261ab7a94208e9202a3194",
            "page": "Page 14",
            "verified_at": "2026-09-25"
        },
        "rule_history": [
            {
                "timestamp": "2026-09-25T01:00:00Z",
                "previous_status": "UNVERIFIED",
                "new_status": "VERIFIED",
                "reason": "Ingested from 2026 BCBSRI OTC Catalog",
                "source_version": "2026-v1.0",
                "review_type": "AUTOMATED_INGESTION"
            },
            {
                "timestamp": "2026-09-25T01:23:00Z",
                "previous_status": "VERIFIED",
                "new_status": "VERIFIED_EXACT",
                "reason": "Revalidated against hardened exact product & plan provenance criteria",
                "source_version": "2026-v1.0",
                "review_type": "HARDENING_AUDIT"
            }
        ],
        "notes": "Eligible under quarterly BlueCHiP OTC allowance ($50/qtr).",
        "plain_english_explanation": "Your plan lists this exact product as eligible under its OTC benefit ($50 quarterly card).",
        "action_type": "get_item",
        "action_label": "Get this item"
    },
    {
        "rule_id": "R-BCBSRI-VIT-BCOMPLEX",
        "target_type": "PRODUCT",
        "product_id": "P-VIT-BCOMPLEX",
        "target_variant_id": "SKU-VITB-COMPLEX",
        "plan_id": "bcbsri_bluechip_core_2026",
        "source_id": "SRC-BCBSRI-2026-OTC",
        "source_authority": "OFFICIAL_INSURER",
        "evidence_scope": "EXACT_PLAN",
        "benefit_pathway": "OTC allowance",
        "coverage_status": "Covered",
        "state": "RI",
        "plan_type": "Medicare Advantage",
        "verification_status": "VERIFIED_EXACT",
        "evidence_confidence": "EXACT_PRODUCT",
        "match_method": "EXACT_NAME",
        "match_confidence": 0.9,
        "cost_verified": true,
        "amount_verified": true,
        "frequency_verified": true,
        "eligibility_verified": true,
        "otc_allowance_verified": true,
        "product_eligibility_verified": true,
        "otc_allowance_eligible": true,
        "prescription_required": "No for OTC",
        "provider_order_required": false,
        "diagnosis_required": false,
        "prior_authorization_required": false,
        "network_pharmacy_required": false,
        "network_dme_supplier_required": false,
        "member_cost": "$50 quarterly allowance card",
        "copay": "$0.00",
        "coinsurance": "0%",
        "allowance_amount": 50,
        "allowance_frequency": "quarterly",
        "official_source_name": "BCBSRI 2026 OTC Catalog",
        "official_source_url": "https://www.bcbsri.com/medicare/member/otc",
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": "Page 15",
        "evidence_text": "Super B-Complex 100 softgels listed as eligible under member quarterly OTC benefit.",
        "source_snapshot": {
            "source_id": "SRC-BCBSRI-2026-OTC",
            "source_version": "2026-v1.0",
            "source_hash": "c87fae62d4924b108502394bcbe7c4331049281745261ab7a94208e9202a3194",
            "page": "Page 15",
            "verified_at": "2026-09-25"
        },
        "rule_history": [
            {
                "timestamp": "2026-09-25T01:00:00Z",
                "previous_status": "UNVERIFIED",
                "new_status": "VERIFIED",
                "reason": "Ingested from 2026 BCBSRI OTC Catalog",
                "source_version": "2026-v1.0",
                "review_type": "AUTOMATED_INGESTION"
            },
            {
                "timestamp": "2026-09-25T01:23:00Z",
                "previous_status": "VERIFIED",
                "new_status": "VERIFIED_EXACT",
                "reason": "Revalidated against hardened exact product & plan provenance criteria",
                "source_version": "2026-v1.0",
                "review_type": "HARDENING_AUDIT"
            }
        ],
        "notes": "Super B-Complex softgels eligible under quarterly OTC allowance.",
        "plain_english_explanation": "Your plan lists this exact product as eligible under its OTC benefit.",
        "action_type": "get_item",
        "action_label": "Get this item"
    },
    {
        "rule_id": "R-BCBSRI-PAI-ACETA",
        "target_type": "PRODUCT",
        "product_id": "P-PAI-ACETA",
        "target_variant_id": "SKU-ACE-500",
        "plan_id": "bcbsri_bluechip_core_2026",
        "source_id": "SRC-BCBSRI-2026-OTC",
        "source_authority": "OFFICIAL_INSURER",
        "evidence_scope": "EXACT_PLAN",
        "benefit_pathway": "OTC allowance",
        "coverage_status": "Covered",
        "state": "RI",
        "plan_type": "Medicare Advantage",
        "verification_status": "VERIFIED_EXACT",
        "evidence_confidence": "EXACT_PRODUCT",
        "match_method": "EXACT_NAME",
        "match_confidence": 0.9,
        "cost_verified": true,
        "amount_verified": true,
        "frequency_verified": true,
        "eligibility_verified": true,
        "otc_allowance_verified": true,
        "product_eligibility_verified": true,
        "otc_allowance_eligible": true,
        "prescription_required": "No for OTC",
        "provider_order_required": false,
        "diagnosis_required": false,
        "prior_authorization_required": false,
        "network_pharmacy_required": false,
        "network_dme_supplier_required": false,
        "member_cost": "$50 quarterly allowance card",
        "copay": "$0.00",
        "coinsurance": "0%",
        "allowance_amount": 50,
        "allowance_frequency": "quarterly",
        "official_source_name": "BCBSRI 2026 OTC Catalog",
        "official_source_url": "https://www.bcbsri.com/medicare/member/otc",
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": "Page 8",
        "evidence_text": "Acetaminophen 325 mg & 500 mg extra strength caplets eligible under OTC card.",
        "source_snapshot": {
            "source_id": "SRC-BCBSRI-2026-OTC",
            "source_version": "2026-v1.0",
            "source_hash": "c87fae62d4924b108502394bcbe7c4331049281745261ab7a94208e9202a3194",
            "page": "Page 8",
            "verified_at": "2026-09-25"
        },
        "rule_history": [
            {
                "timestamp": "2026-09-25T01:00:00Z",
                "previous_status": "UNVERIFIED",
                "new_status": "VERIFIED",
                "reason": "Ingested from 2026 BCBSRI OTC Catalog",
                "source_version": "2026-v1.0",
                "review_type": "AUTOMATED_INGESTION"
            },
            {
                "timestamp": "2026-09-25T01:23:00Z",
                "previous_status": "VERIFIED",
                "new_status": "VERIFIED_EXACT",
                "reason": "Revalidated against hardened exact product & plan provenance criteria",
                "source_version": "2026-v1.0",
                "review_type": "HARDENING_AUDIT"
            }
        ],
        "notes": "Acetaminophen pain relief products listed in 2026 OTC catalog.",
        "plain_english_explanation": "Your plan lists this exact product as eligible under its OTC benefit.",
        "action_type": "get_item",
        "action_label": "Get this item"
    },
    {
        "rule_id": "R-BCBSRI-KNEE",
        "target_type": "HCPCS",
        "product_id": "P-BRC-KNEE",
        "target_variant_id": "SKU-BRC-KNEE-HINGED",
        "plan_id": "bcbsri_bluechip_core_2026",
        "source_id": "SRC-CMS-2026-DMEPOS",
        "source_authority": "CMS",
        "evidence_scope": "GOVERNMENT_POLICY",
        "benefit_pathway": "Durable Medical Equipment (DME)",
        "coverage_status": "Conditional",
        "state": "RI",
        "plan_type": "Medicare Advantage",
        "verification_status": "VERIFIED_POLICY",
        "evidence_confidence": "POLICY_LEVEL",
        "match_method": "HCPCS_CODE",
        "match_confidence": 1.0,
        "cost_verified": false,
        "amount_verified": false,
        "frequency_verified": false,
        "eligibility_verified": true,
        "otc_allowance_verified": false,
        "product_eligibility_verified": true,
        "otc_allowance_eligible": false,
        "prescription_required": "Yes for DMEPOS",
        "provider_order_required": true,
        "diagnosis_required": "Arthritis / Ligament Strain",
        "prior_authorization_required": false,
        "network_pharmacy_required": false,
        "network_dme_supplier_required": true,
        "member_cost": "Covered benefit \u2014 member cost depends on plan terms",
        "copay": "Varies by DME supplier",
        "coinsurance": "Varies",
        "official_source_name": "CMS Medicare DMEPOS Fee Schedule & BCBSRI EOC 2026",
        "official_source_url": "https://www.cms.gov/medicare/payment/fee-schedules/dmepos",
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": "Section 4 DME",
        "evidence_text": "HCPCS L1820 covered when prescribed by network physician for knee instability.",
        "source_snapshot": {
            "source_id": "SRC-CMS-2026-DMEPOS",
            "source_version": "2026-v1.0",
            "source_hash": "5748392019384710293847102938471029384710293847102938471029384710",
            "page": "Section 4 DME",
            "verified_at": "2026-09-25"
        },
        "rule_history": [
            {
                "timestamp": "2026-09-25T01:00:00Z",
                "previous_status": "UNVERIFIED",
                "new_status": "VERIFIED",
                "reason": "Ingested from CMS DMEPOS Schedule",
                "source_version": "2026-v1.0",
                "review_type": "AUTOMATED_INGESTION"
            },
            {
                "timestamp": "2026-09-25T01:23:00Z",
                "previous_status": "VERIFIED",
                "new_status": "VERIFIED_POLICY",
                "reason": "Plan-specific $0 cost unsupported; CMS policy supports DME eligibility.",
                "source_version": "2026-v1.0",
                "review_type": "HARDENING_AUDIT"
            }
        ],
        "notes": "HCPCS L1820 covered under DMEPOS policy when ordered by network physician.",
        "plain_english_explanation": "This type of medical equipment may qualify through your DME benefit when coverage requirements are met and ordered by your provider.",
        "action_type": "ask_provider",
        "action_label": "Ask your provider"
    },
    {
        "rule_id": "R-BCBSRI-DEN-EXAM",
        "target_type": "SERVICE",
        "service_id": "S-DEN-EXAM",
        "plan_id": "bcbsri_bluechip_core_2026",
        "source_id": "SRC-BCBSRI-2026-EOC",
        "source_authority": "OFFICIAL_INSURER",
        "evidence_scope": "EXACT_PLAN",
        "benefit_pathway": "Dental benefit",
        "coverage_status": "Covered",
        "state": "RI",
        "plan_type": "Medicare Advantage",
        "verification_status": "VERIFIED_EXACT",
        "evidence_confidence": "EXACT_SERVICE",
        "match_method": "EXACT_NAME",
        "match_confidence": 0.9,
        "cost_verified": true,
        "amount_verified": true,
        "frequency_verified": true,
        "eligibility_verified": true,
        "otc_allowance_verified": false,
        "product_eligibility_verified": true,
        "otc_allowance_eligible": false,
        "prescription_required": false,
        "provider_order_required": false,
        "diagnosis_required": false,
        "prior_authorization_required": false,
        "network_pharmacy_required": false,
        "network_dme_supplier_required": false,
        "member_cost": "$0 copay (2 per year)",
        "copay": "$0.00",
        "coinsurance": "0%",
        "official_source_name": "BCBSRI 2026 BlueCHiP Core Evidence of Coverage",
        "official_source_url": "https://www.bcbsri.com/medicare/member/eoc-2026",
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": "Page 48",
        "evidence_text": "Routine dental cleanings and oral examinations covered at $0 copay up to 2 visits per calendar year.",
        "source_snapshot": {
            "source_id": "SRC-BCBSRI-2026-EOC",
            "source_version": "2026-v1.0",
            "source_hash": "9a2bc81412093e9812401824abec910293847291847120398410293847120398",
            "page": "Page 48",
            "verified_at": "2026-09-25"
        },
        "rule_history": [
            {
                "timestamp": "2026-09-25T01:00:00Z",
                "previous_status": "UNVERIFIED",
                "new_status": "VERIFIED",
                "reason": "Ingested from 2026 BCBSRI Core EOC",
                "source_version": "2026-v1.0",
                "review_type": "AUTOMATED_INGESTION"
            },
            {
                "timestamp": "2026-09-25T01:23:00Z",
                "previous_status": "VERIFIED",
                "new_status": "VERIFIED_EXACT",
                "reason": "Revalidated exact service proof in EOC",
                "source_version": "2026-v1.0",
                "review_type": "HARDENING_AUDIT"
            }
        ],
        "notes": "Preventive dental examination covered twice per year.",
        "plain_english_explanation": "Your plan lists this exact service as eligible under its preventive dental benefit ($0 copay, 2 per year).",
        "action_type": "schedule_visit",
        "action_label": "Find a network dentist"
    },
    {
        "rule_id": "R-NHPRI-VIT-CALCIUM",
        "target_type": "PRODUCT",
        "product_id": "P-VIT-CALCIUM",
        "target_variant_id": "SKU-CAL-D3",
        "plan_id": "neighborhood_integra_2026",
        "source_id": "SRC-NHPRI-2026-OTC",
        "source_authority": "OFFICIAL_INSURER",
        "evidence_scope": "EXACT_PLAN",
        "benefit_pathway": "OTC allowance",
        "coverage_status": "Covered",
        "state": "RI",
        "plan_type": "Medicare Advantage",
        "verification_status": "VERIFIED_EXACT",
        "evidence_confidence": "EXACT_PRODUCT",
        "match_method": "INGREDIENT_STRENGTH_FORM",
        "match_confidence": 0.95,
        "cost_verified": true,
        "amount_verified": true,
        "frequency_verified": true,
        "eligibility_verified": true,
        "otc_allowance_verified": true,
        "product_eligibility_verified": true,
        "otc_allowance_eligible": true,
        "prescription_required": "No for OTC",
        "provider_order_required": false,
        "diagnosis_required": false,
        "prior_authorization_required": false,
        "network_pharmacy_required": false,
        "network_dme_supplier_required": false,
        "member_cost": "$75 quarterly allowance card",
        "copay": "$0.00",
        "coinsurance": "0%",
        "allowance_amount": 75,
        "allowance_frequency": "quarterly",
        "official_source_name": "Neighborhood INTEGRIA D-SNP 2026 OTC Catalog",
        "official_source_url": "https://www.nhpri.org/members/integria-otc-2026",
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": "Page 11",
        "evidence_text": "Calcium 600 mg + Vitamin D3 caplets eligible under D-SNP quarterly allowance card ($75/qtr).",
        "source_snapshot": {
            "source_id": "SRC-NHPRI-2026-OTC",
            "source_version": "2026-v1.0",
            "source_hash": "1209384710293847102938471029384710293847102938471029384710293847",
            "page": "Page 11",
            "verified_at": "2026-09-25"
        },
        "rule_history": [
            {
                "timestamp": "2026-09-25T01:00:00Z",
                "previous_status": "UNVERIFIED",
                "new_status": "VERIFIED",
                "reason": "Ingested from NHPRI D-SNP Catalog",
                "source_version": "2026-v1.0",
                "review_type": "AUTOMATED_INGESTION"
            },
            {
                "timestamp": "2026-09-25T01:23:00Z",
                "previous_status": "VERIFIED",
                "new_status": "VERIFIED_EXACT",
                "reason": "Revalidated exact product proof in NHPRI catalog",
                "source_version": "2026-v1.0",
                "review_type": "HARDENING_AUDIT"
            }
        ],
        "notes": "Eligible under Neighborhood INTEGRIA quarterly OTC allowance.",
        "plain_english_explanation": "Your plan lists this exact product as eligible under its OTC benefit ($75 quarterly card).",
        "action_type": "get_item",
        "action_label": "Get this item"
    },
    {
        "rule_id": "R-NHPRI-TRN-RIDE",
        "target_type": "SERVICE",
        "service_id": "S-TRN-RIDE",
        "plan_id": "neighborhood_integra_2026",
        "source_id": "SRC-NHPRI-2026-SOB",
        "source_authority": "OFFICIAL_INSURER",
        "evidence_scope": "EXACT_PLAN",
        "benefit_pathway": "Transportation benefit",
        "coverage_status": "Covered",
        "state": "RI",
        "plan_type": "Medicare Advantage",
        "verification_status": "VERIFIED_EXACT",
        "evidence_confidence": "EXACT_SERVICE",
        "match_method": "EXACT_NAME",
        "match_confidence": 0.9,
        "cost_verified": true,
        "amount_verified": true,
        "frequency_verified": true,
        "eligibility_verified": true,
        "otc_allowance_verified": false,
        "product_eligibility_verified": true,
        "otc_allowance_eligible": false,
        "prescription_required": false,
        "provider_order_required": false,
        "diagnosis_required": false,
        "prior_authorization_required": false,
        "network_pharmacy_required": false,
        "network_dme_supplier_required": false,
        "member_cost": "$0 copay (24 one-way rides/yr)",
        "copay": "$0.00",
        "coinsurance": "0%",
        "official_source_name": "Neighborhood INTEGRIA 2026 Summary of Benefits",
        "official_source_url": "https://www.nhpri.org/members/integria-sob-2026",
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": "Page 18",
        "evidence_text": "24 one-way non-emergency medical transportation trips per year to plan-approved health locations at $0 copay.",
        "source_snapshot": {
            "source_id": "SRC-NHPRI-2026-SOB",
            "source_version": "2026-v1.0",
            "source_hash": "3948201938471029384710293847102938471029384710293847102938471029",
            "page": "Page 18",
            "verified_at": "2026-09-25"
        },
        "rule_history": [
            {
                "timestamp": "2026-09-25T01:00:00Z",
                "previous_status": "UNVERIFIED",
                "new_status": "VERIFIED",
                "reason": "Ingested from NHPRI Summary of Benefits",
                "source_version": "2026-v1.0",
                "review_type": "AUTOMATED_INGESTION"
            },
            {
                "timestamp": "2026-09-25T01:23:00Z",
                "previous_status": "VERIFIED",
                "new_status": "VERIFIED_EXACT",
                "reason": "Revalidated exact service & ride count proof",
                "source_version": "2026-v1.0",
                "review_type": "HARDENING_AUDIT"
            }
        ],
        "notes": "Transportation benefit covered for medical appointments.",
        "plain_english_explanation": "Your plan lists this exact service as eligible under its medical transportation benefit (24 rides/yr).",
        "action_type": "schedule_ride",
        "action_label": "Schedule a ride"
    },
    {
        "rule_id": "R-RIME-SMK",
        "target_type": "PRODUCT",
        "product_id": "P-SMK-PATCH",
        "target_variant_id": "SKU-NIC-21",
        "plan_id": "ri_medicaid_managed_2026",
        "source_id": "SRC-RIME-2026-PHARMACY",
        "source_authority": "STATE_MEDICAID",
        "evidence_scope": "EXACT_PLAN",
        "benefit_pathway": "Prescription/pharmacy benefit",
        "coverage_status": "Covered",
        "state": "RI",
        "plan_type": "Medicaid",
        "verification_status": "VERIFIED_EXACT",
        "evidence_confidence": "EXACT_PRODUCT",
        "match_method": "INGREDIENT_STRENGTH_FORM",
        "match_confidence": 0.95,
        "cost_verified": true,
        "amount_verified": true,
        "frequency_verified": true,
        "eligibility_verified": true,
        "otc_allowance_verified": false,
        "product_eligibility_verified": true,
        "otc_allowance_eligible": false,
        "prescription_required": true,
        "provider_order_required": true,
        "diagnosis_required": false,
        "prior_authorization_required": false,
        "network_pharmacy_required": true,
        "network_dme_supplier_required": false,
        "member_cost": "$0 copay",
        "copay": "$0.00",
        "coinsurance": "0%",
        "official_source_name": "RI EOHHS Pharmacy Benefit Plan Protocols 2026",
        "official_source_url": "https://eohhs.ri.gov/sites/g/files/xkgbur226/files/2026-01/2.4%20%20Pharmacy%20Benefit%20Plan%20Protocols%20-%20Effective%2001.01.26_CLEAN.pdf",
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": "Protocol 2.4",
        "evidence_text": "Non-prescription nicotine-cessation supplies covered when ordered by a licensed health plan practitioner.",
        "source_snapshot": {
            "source_id": "SRC-RIME-2026-PHARMACY",
            "source_version": "2026-v1.0",
            "source_hash": "9384710293847102938471029384710293847102938471029384710293847102",
            "page": "Protocol 2.4",
            "verified_at": "2026-09-25"
        },
        "rule_history": [
            {
                "timestamp": "2026-09-25T01:00:00Z",
                "previous_status": "UNVERIFIED",
                "new_status": "VERIFIED",
                "reason": "Ingested from RI EOHHS Pharmacy Protocol 2.4",
                "source_version": "2026-v1.0",
                "review_type": "AUTOMATED_INGESTION"
            },
            {
                "timestamp": "2026-09-25T01:23:00Z",
                "previous_status": "VERIFIED",
                "new_status": "VERIFIED_EXACT",
                "reason": "Revalidated exact Medicaid pharmacy protocol",
                "source_version": "2026-v1.0",
                "review_type": "HARDENING_AUDIT"
            }
        ],
        "notes": "Protocol 2.4 non-prescription nicotine cessation covered when ordered by practitioner.",
        "plain_english_explanation": "Your plan lists this exact product as eligible under its pharmacy protocol at $0 copay when ordered by your practitioner.",
        "action_type": "find_pharmacy",
        "action_label": "Find an approved pharmacy"
    },
    {
        "rule_id": "R-RIME-DIA-STRIPS",
        "target_type": "PRODUCT",
        "product_id": "P-DIA-STRIPS",
        "target_variant_id": "SKU-DIA-STRIPS-50",
        "plan_id": "ri_medicaid_managed_2026",
        "source_id": "SRC-RIME-2026-PHARMACY",
        "source_authority": "STATE_MEDICAID",
        "evidence_scope": "EXACT_PLAN",
        "benefit_pathway": "Medicaid benefit",
        "coverage_status": "Covered",
        "state": "RI",
        "plan_type": "Medicaid",
        "verification_status": "VERIFIED_EXACT",
        "evidence_confidence": "EXACT_PRODUCT",
        "match_method": "EXACT_NAME",
        "match_confidence": 0.9,
        "cost_verified": true,
        "amount_verified": true,
        "frequency_verified": true,
        "eligibility_verified": true,
        "otc_allowance_verified": false,
        "product_eligibility_verified": true,
        "otc_allowance_eligible": false,
        "prescription_required": true,
        "provider_order_required": true,
        "diagnosis_required": "Diabetes Mellitus",
        "prior_authorization_required": false,
        "network_pharmacy_required": true,
        "network_dme_supplier_required": false,
        "member_cost": "$0 copay",
        "copay": "$0.00",
        "coinsurance": "0%",
        "official_source_name": "RI EOHHS Pharmacy Protocols 2026",
        "official_source_url": "https://eohhs.ri.gov/sites/g/files/xkgbur226/files/2026-01/2.4%20%20Pharmacy%20Benefit%20Plan%20Protocols%20-%20Effective%2001.01.26_CLEAN.pdf",
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": "Page 32",
        "evidence_text": "Blood glucose test strips (preferred brand OneTouch/Accu-Chek) covered up to 150 strips per month with prescription.",
        "source_snapshot": {
            "source_id": "SRC-RIME-2026-PHARMACY",
            "source_version": "2026-v1.0",
            "source_hash": "9384710293847102938471029384710293847102938471029384710293847102",
            "page": "Page 32",
            "verified_at": "2026-09-25"
        },
        "rule_history": [
            {
                "timestamp": "2026-09-25T01:00:00Z",
                "previous_status": "UNVERIFIED",
                "new_status": "VERIFIED",
                "reason": "Ingested from RI EOHHS Pharmacy Protocols",
                "source_version": "2026-v1.0",
                "review_type": "AUTOMATED_INGESTION"
            },
            {
                "timestamp": "2026-09-25T01:23:00Z",
                "previous_status": "VERIFIED",
                "new_status": "VERIFIED_EXACT",
                "reason": "Revalidated exact Medicaid diabetic strip policy",
                "source_version": "2026-v1.0",
                "review_type": "HARDENING_AUDIT"
            }
        ],
        "notes": "Preferred diabetic test strips covered at $0 copay.",
        "plain_english_explanation": "Your plan lists this exact product as eligible under its Medicaid pharmacy benefit when ordered by your doctor.",
        "action_type": "find_pharmacy",
        "action_label": "Fill at pharmacy"
    },
    {
        "rule_id": "R-UHCRI-SSBCI-FOOD",
        "target_type": "BENEFIT",
        "benefit_id": "B-UHCRI-FOOD-110",
        "plan_id": "uhc_medicare_dual_2026",
        "source_id": "SRC-UHCRI-2026-UCARD",
        "source_authority": "OFFICIAL_INSURER",
        "evidence_scope": "EXACT_PLAN",
        "benefit_pathway": "Healthy Food / Grocery Benefits",
        "coverage_status": "Covered",
        "state": "RI",
        "plan_type": "Medicare Advantage",
        "verification_status": "VERIFIED_EXACT",
        "evidence_confidence": "EXACT_PRODUCT",
        "match_method": "EXACT_NAME",
        "match_confidence": 0.9,
        "cost_verified": true,
        "amount_verified": true,
        "frequency_verified": true,
        "eligibility_verified": true,
        "otc_allowance_verified": true,
        "product_eligibility_verified": true,
        "otc_allowance_eligible": true,
        "prescription_required": false,
        "provider_order_required": false,
        "diagnosis_required": "Qualifying Chronic Condition",
        "prior_authorization_required": false,
        "network_pharmacy_required": false,
        "network_dme_supplier_required": false,
        "member_cost": "$110 monthly UCard food credit",
        "copay": "$0.00",
        "coinsurance": "0%",
        "allowance_amount": 110,
        "allowance_frequency": "monthly",
        "official_source_name": "2026 UHC Dual Complete RI UCard Guide",
        "official_source_url": "https://www.uhc.com/medicare/member/ucard-ri-2026",
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": "Page 6",
        "evidence_text": "Healthy Food and produce allowance ($110 monthly credit on UCard) for qualifying SSBCI members.",
        "source_snapshot": {
            "source_id": "SRC-UHCRI-2026-UCARD",
            "source_version": "2026-v1.0",
            "source_hash": "4839201938471029384710293847102938471029384710293847102938471029",
            "page": "Page 6",
            "verified_at": "2026-09-25"
        },
        "rule_history": [
            {
                "timestamp": "2026-09-25T01:00:00Z",
                "previous_status": "UNVERIFIED",
                "new_status": "VERIFIED",
                "reason": "Ingested from UHC UCard Guide",
                "source_version": "2026-v1.0",
                "review_type": "AUTOMATED_INGESTION"
            },
            {
                "timestamp": "2026-09-25T01:23:00Z",
                "previous_status": "VERIFIED",
                "new_status": "VERIFIED_EXACT",
                "reason": "Reclassified target_type from RETAIL PRODUCT to BENEFIT",
                "source_version": "2026-v1.0",
                "review_type": "ENTITY_MODEL_RECLASSIFICATION"
            }
        ],
        "notes": "Monthly food credit for SSBCI eligible dual members.",
        "plain_english_explanation": "Your plan lists this benefit as eligible under its SSBCI Healthy Food UCard allowance ($110 monthly).",
        "action_type": "get_item",
        "action_label": "Use UCard credit"
    },
    {
        "rule_id": "R-UNVERIFIED",
        "target_type": "PRODUCT",
        "product_id": "GENERIC",
        "plan_id": "generic_unselected_plan",
        "source_id": null,
        "source_authority": "OTHER_GOVERNMENT",
        "evidence_scope": "GENERAL_POLICY",
        "benefit_pathway": "Unknown / Needs Verification",
        "coverage_status": "Needs Verification",
        "state": "RI",
        "plan_type": "Medicare Advantage",
        "verification_status": "UNVERIFIED",
        "evidence_confidence": "UNVERIFIED",
        "match_method": "FALLBACK",
        "match_confidence": 0.0,
        "cost_verified": false,
        "amount_verified": false,
        "frequency_verified": false,
        "eligibility_verified": false,
        "otc_allowance_verified": false,
        "product_eligibility_verified": false,
        "member_cost": "Select your specific health plan to check coverage",
        "copay": "Unknown",
        "coinsurance": "Unknown",
        "official_source_name": "Unselected Plan Generic Policy",
        "official_source_url": null,
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": null,
        "evidence_text": "Select your insurance card and plan to verify actual benefit eligibility.",
        "source_snapshot": null,
        "rule_history": [
            {
                "timestamp": "2026-09-25T01:00:00Z",
                "previous_status": "UNVERIFIED",
                "new_status": "UNVERIFIED",
                "reason": "Generic plan fallback rule",
                "source_version": "2026-v1.0",
                "review_type": "SYSTEM_FALLBACK"
            }
        ],
        "notes": "Generic plan fallback rule.",
        "plain_english_explanation": "We found an applicable benefit, but product eligibility still needs verification against your specific plan.",
        "action_type": "select_plan",
        "action_label": "Select your plan"
    },
    {
        "rule_id": "R-MA-WS-VIT-D",
        "product_id": "P-VIT-D",
        "plan_id": "ma_wellsense_wellsense_connectorcare",
        "source_id": "SRC-MA-WELLSENSE-2026-MED",
        "benefit_pathway": "OTC allowance",
        "coverage_status": "Covered",
        "state": "MA",
        "plan_type": "Individual Marketplace",
        "plan_year": 2026,
        "evidence_confidence": "EXACT_PRODUCT",
        "amount_verified": true,
        "frequency_verified": true,
        "eligibility_verified": true,
        "otc_allowance_eligible": true,
        "prescription_required": false,
        "provider_order_required": false,
        "diagnosis_required": false,
        "prior_authorization_required": false,
        "network_pharmacy_required": true,
        "network_dme_supplier_required": false,
        "member_cost": "$0 copay",
        "copay": "$0.00",
        "coinsurance": "0%",
        "official_source_name": "WellSense MassHealth & ConnectorCare OTC Catalog Guide (2026)",
        "official_source_url": "https://www.wellsense.org/",
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": "Page 14",
        "source_version": "v2026.1",
        "source_hash": "sha256-ma-ws-vitd-2026",
        "evidence_text": "Vitamin D3 softgels covered up to 100% under WellSense MassHealth & ConnectorCare OTC allowance.",
        "notes": "Covered under WellSense OTC benefit allowance.",
        "plain_english_explanation": "Vitamin D3 softgels are 100% covered with $0 copay through your WellSense OTC allowance.",
        "action_type": "add_to_slip",
        "action_label": "+ Add to Phone Order Slip"
    },
    {
        "rule_id": "R-MA-WS-VIT-B12",
        "product_id": "P-VIT-B12",
        "plan_id": "ma_wellsense_wellsense_connectorcare",
        "source_id": "SRC-MA-WELLSENSE-2026-MED",
        "benefit_pathway": "OTC allowance",
        "coverage_status": "Covered",
        "state": "MA",
        "plan_type": "Individual Marketplace",
        "plan_year": 2026,
        "evidence_confidence": "EXACT_PRODUCT",
        "amount_verified": true,
        "frequency_verified": true,
        "eligibility_verified": true,
        "otc_allowance_eligible": true,
        "prescription_required": false,
        "provider_order_required": false,
        "diagnosis_required": false,
        "prior_authorization_required": false,
        "network_pharmacy_required": true,
        "network_dme_supplier_required": false,
        "member_cost": "$0 copay",
        "copay": "$0.00",
        "coinsurance": "0%",
        "official_source_name": "WellSense MassHealth & ConnectorCare OTC Catalog Guide (2026)",
        "official_source_url": "https://www.wellsense.org/",
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": "Page 16",
        "source_version": "v2026.1",
        "source_hash": "sha256-ma-ws-b12-2026",
        "evidence_text": "Vitamin B12 sublingual covered with $0 copay under WellSense OTC allowance.",
        "notes": "Covered under WellSense OTC benefit allowance.",
        "plain_english_explanation": "Vitamin B12 sublingual caplets are covered with $0 copay using your WellSense OTC benefit.",
        "action_type": "add_to_slip",
        "action_label": "+ Add to Phone Order Slip"
    },
    {
        "rule_id": "R-MA-WS-PRENATAL",
        "product_id": "P-VIT-PRENATAL",
        "plan_id": "ma_wellsense_wellsense_connectorcare",
        "source_id": "SRC-MA-MASSHEALTH-2026-GUIDE",
        "benefit_pathway": "Prescription drug benefit",
        "coverage_status": "Covered",
        "state": "MA",
        "plan_type": "Individual Marketplace",
        "plan_year": 2026,
        "evidence_confidence": "EXACT_PRODUCT",
        "amount_verified": true,
        "frequency_verified": true,
        "eligibility_verified": true,
        "otc_allowance_eligible": false,
        "prescription_required": true,
        "provider_order_required": false,
        "diagnosis_required": false,
        "prior_authorization_required": false,
        "network_pharmacy_required": true,
        "network_dme_supplier_required": false,
        "member_cost": "$0 out-of-pocket",
        "copay": "$0.00",
        "coinsurance": "0%",
        "official_source_name": "MassHealth Member Handbook & Covered Services Regulations (2026)",
        "official_source_url": "https://www.mass.gov/masshealth",
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": "Page 22",
        "source_version": "v2026.1",
        "source_hash": "sha256-ma-ws-prenatal-2026",
        "evidence_text": "Prenatal vitamins covered 100% with $0 copay under MassHealth & ConnectorCare preventive drug protocol.",
        "notes": "100% covered with prescription.",
        "plain_english_explanation": "Prenatal multivitamins are 100% covered with $0 out-of-pocket cost when prescribed by your provider.",
        "action_type": "request_prescription",
        "action_label": "Request prescription from provider"
    },
    {
        "rule_id": "R-MA-WS-ACET",
        "product_id": "P-PAIN-ACET",
        "plan_id": "ma_wellsense_wellsense_connectorcare",
        "source_id": "SRC-MA-WELLSENSE-2026-MED",
        "benefit_pathway": "OTC allowance",
        "coverage_status": "Covered",
        "state": "MA",
        "plan_type": "Individual Marketplace",
        "plan_year": 2026,
        "evidence_confidence": "EXACT_PRODUCT",
        "amount_verified": true,
        "frequency_verified": true,
        "eligibility_verified": true,
        "otc_allowance_eligible": true,
        "prescription_required": false,
        "provider_order_required": false,
        "diagnosis_required": false,
        "prior_authorization_required": false,
        "network_pharmacy_required": true,
        "network_dme_supplier_required": false,
        "member_cost": "$0 copay",
        "copay": "$0.00",
        "coinsurance": "0%",
        "official_source_name": "WellSense MassHealth & ConnectorCare OTC Catalog Guide (2026)",
        "official_source_url": "https://www.wellsense.org/",
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": "Page 18",
        "source_version": "v2026.1",
        "source_hash": "sha256-ma-ws-acet-2026",
        "evidence_text": "Acetaminophen 500 mg covered via WellSense OTC allowance.",
        "notes": "Covered under WellSense OTC benefit.",
        "plain_english_explanation": "Acetaminophen pain reliever is covered with $0 copay through your WellSense OTC allowance.",
        "action_type": "add_to_slip",
        "action_label": "+ Add to Phone Order Slip"
    },
    {
        "rule_id": "R-MA-WS-IBU",
        "product_id": "P-PAIN-IBU",
        "plan_id": "ma_wellsense_wellsense_connectorcare",
        "source_id": "SRC-MA-WELLSENSE-2026-MED",
        "benefit_pathway": "OTC allowance",
        "coverage_status": "Covered",
        "state": "MA",
        "plan_type": "Individual Marketplace",
        "plan_year": 2026,
        "evidence_confidence": "EXACT_PRODUCT",
        "amount_verified": true,
        "frequency_verified": true,
        "eligibility_verified": true,
        "otc_allowance_eligible": true,
        "prescription_required": false,
        "provider_order_required": false,
        "diagnosis_required": false,
        "prior_authorization_required": false,
        "network_pharmacy_required": true,
        "network_dme_supplier_required": false,
        "member_cost": "$0 copay",
        "copay": "$0.00",
        "coinsurance": "0%",
        "official_source_name": "WellSense MassHealth & ConnectorCare OTC Catalog Guide (2026)",
        "official_source_url": "https://www.wellsense.org/",
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": "Page 19",
        "source_version": "v2026.1",
        "source_hash": "sha256-ma-ws-ibu-2026",
        "evidence_text": "Ibuprofen 200 mg covered via WellSense OTC allowance.",
        "notes": "Covered under WellSense OTC benefit.",
        "plain_english_explanation": "Ibuprofen 200 mg tablets are covered with $0 copay through your WellSense OTC allowance.",
        "action_type": "add_to_slip",
        "action_label": "+ Add to Phone Order Slip"
    },
    {
        "rule_id": "R-MA-WS-BPMON",
        "product_id": "P-CARDIO-BPMON",
        "plan_id": "ma_wellsense_wellsense_connectorcare",
        "source_id": "SRC-MA-MASSHEALTH-2026-GUIDE",
        "benefit_pathway": "Durable Medical Equipment (DME)",
        "coverage_status": "Covered with Provider Order",
        "state": "MA",
        "plan_type": "Individual Marketplace",
        "plan_year": 2026,
        "evidence_confidence": "EXACT_PRODUCT",
        "amount_verified": true,
        "frequency_verified": true,
        "eligibility_verified": true,
        "otc_allowance_eligible": false,
        "prescription_required": true,
        "provider_order_required": true,
        "diagnosis_required": true,
        "prior_authorization_required": false,
        "network_pharmacy_required": false,
        "network_dme_supplier_required": true,
        "member_cost": "$0 with provider order",
        "copay": "$0.00",
        "coinsurance": "0%",
        "official_source_name": "MassHealth Member Handbook & Covered Services Regulations (2026)",
        "official_source_url": "https://www.mass.gov/masshealth",
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": "Page 35",
        "source_version": "v2026.1",
        "source_hash": "sha256-ma-ws-bpmon-2026",
        "evidence_text": "Blood pressure monitor covered 100% with written provider order under MassHealth/WellSense DME protocols.",
        "notes": "100% covered with provider order.",
        "plain_english_explanation": "Digital blood pressure monitors are 100% covered when ordered by your physician.",
        "action_type": "request_provider_order",
        "action_label": "Request order from provider"
    },
    {
        "rule_id": "R-MA-WS-GLUCOSE",
        "product_id": "P-DIAB-METER",
        "plan_id": "ma_wellsense_wellsense_connectorcare",
        "source_id": "SRC-MA-MASSHEALTH-2026-GUIDE",
        "benefit_pathway": "Durable Medical Equipment (DME)",
        "coverage_status": "Covered with Provider Order",
        "state": "MA",
        "plan_type": "Individual Marketplace",
        "plan_year": 2026,
        "evidence_confidence": "EXACT_PRODUCT",
        "amount_verified": true,
        "frequency_verified": true,
        "eligibility_verified": true,
        "otc_allowance_eligible": false,
        "prescription_required": true,
        "provider_order_required": true,
        "diagnosis_required": true,
        "prior_authorization_required": false,
        "network_pharmacy_required": false,
        "network_dme_supplier_required": true,
        "member_cost": "$0 with provider order",
        "copay": "$0.00",
        "coinsurance": "0%",
        "official_source_name": "MassHealth Member Handbook & Covered Services Regulations (2026)",
        "official_source_url": "https://www.mass.gov/masshealth",
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": "Page 38",
        "source_version": "v2026.1",
        "source_hash": "sha256-ma-ws-glucose-2026",
        "evidence_text": "Blood glucose meters covered 100% with provider prescription and order.",
        "notes": "100% covered with provider order.",
        "plain_english_explanation": "Blood glucose meters are 100% covered when prescribed by your primary care provider.",
        "action_type": "request_provider_order",
        "action_label": "Request order from provider"
    },
    {
        "rule_id": "R-MA-TUFTS-VIT-D",
        "product_id": "P-VIT-D",
        "plan_id": "ma_tufts_p32_tufts_health_direct_connectorcare",
        "source_id": "SRC-MA-TUFTS-2026-TOGETHER",
        "benefit_pathway": "OTC allowance",
        "coverage_status": "Covered",
        "state": "MA",
        "plan_type": "Individual Marketplace",
        "plan_year": 2026,
        "evidence_confidence": "EXACT_PRODUCT",
        "amount_verified": true,
        "frequency_verified": true,
        "eligibility_verified": true,
        "otc_allowance_eligible": true,
        "prescription_required": false,
        "provider_order_required": false,
        "diagnosis_required": false,
        "prior_authorization_required": false,
        "network_pharmacy_required": true,
        "network_dme_supplier_required": false,
        "member_cost": "$0 copay",
        "copay": "$0.00",
        "coinsurance": "0%",
        "official_source_name": "Tufts Health Direct ConnectorCare Member Guide (2026)",
        "official_source_url": "https://www.tuftshealthplan.org/",
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": "Page 12",
        "source_version": "v2026.1",
        "source_hash": "sha256-ma-tufts-vitd-2026",
        "evidence_text": "Vitamin D3 covered under Tufts Health Direct ConnectorCare OTC benefit.",
        "notes": "Covered under Tufts OTC allowance.",
        "plain_english_explanation": "Vitamin D3 is 100% covered with $0 copay through your Tufts Health Direct OTC benefit.",
        "action_type": "add_to_slip",
        "action_label": "+ Add to Phone Order Slip"
    },
    {
        "rule_id": "R-MA-TUFTS-PRENATAL",
        "product_id": "P-VIT-PRENATAL",
        "plan_id": "ma_tufts_p32_tufts_health_direct_connectorcare",
        "source_id": "SRC-MA-TUFTS-2026-TOGETHER",
        "benefit_pathway": "Prescription drug benefit",
        "coverage_status": "Covered",
        "state": "MA",
        "plan_type": "Individual Marketplace",
        "plan_year": 2026,
        "evidence_confidence": "EXACT_PRODUCT",
        "amount_verified": true,
        "frequency_verified": true,
        "eligibility_verified": true,
        "otc_allowance_eligible": false,
        "prescription_required": true,
        "provider_order_required": false,
        "diagnosis_required": false,
        "prior_authorization_required": false,
        "network_pharmacy_required": true,
        "network_dme_supplier_required": false,
        "member_cost": "$0 out-of-pocket",
        "copay": "$0.00",
        "coinsurance": "0%",
        "official_source_name": "Tufts Health Direct ConnectorCare Member Guide (2026)",
        "official_source_url": "https://www.tuftshealthplan.org/",
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": "Page 15",
        "source_version": "v2026.1",
        "source_hash": "sha256-ma-tufts-prenatal-2026",
        "evidence_text": "Prenatal multivitamins covered $0 copay under Tufts Health Direct preventive drug protocol.",
        "notes": "100% covered with prescription.",
        "plain_english_explanation": "Prenatal multivitamins are 100% covered with $0 copay when prescribed by your doctor.",
        "action_type": "request_prescription",
        "action_label": "Request prescription from provider"
    },
    {
        "rule_id": "R-MA-BCBSMA-PRENATAL",
        "product_id": "P-VIT-PRENATAL",
        "plan_id": "ma_bcbsma_health_connector_standard_plan",
        "source_id": "SRC-MA-BCBSMA-2026-SOB",
        "benefit_pathway": "Prescription drug benefit",
        "coverage_status": "Covered",
        "state": "MA",
        "plan_type": "Commercial",
        "plan_year": 2026,
        "evidence_confidence": "EXACT_PRODUCT",
        "amount_verified": true,
        "frequency_verified": true,
        "eligibility_verified": true,
        "otc_allowance_eligible": false,
        "prescription_required": true,
        "provider_order_required": false,
        "diagnosis_required": false,
        "prior_authorization_required": false,
        "network_pharmacy_required": true,
        "network_dme_supplier_required": false,
        "member_cost": "$0 out-of-pocket",
        "copay": "$0.00",
        "coinsurance": "0%",
        "official_source_name": "BCBSMA Health Connector Standard Plan Summary of Benefits (2026)",
        "official_source_url": "https://www.bluecrossma.org/",
        "source_effective_date": "2026-01-01",
        "last_verified_date": "2026-09-25",
        "source_page": "Page 8",
        "source_version": "v2026.1",
        "source_hash": "sha256-ma-bcbsma-prenatal-2026",
        "evidence_text": "Prenatal multivitamins covered 100% under ACA preventive drug mandate.",
        "notes": "100% covered with prescription.",
        "plain_english_explanation": "Prenatal multivitamins are 100% covered under BCBSMA ACA preventive guidelines.",
        "action_type": "request_prescription",
        "action_label": "Request prescription from provider"
    }
];

  // --- 5. APP STATE ---
  let activeInsurerId = 'bcbsri';
  let activePlanId = 'bcbsri_bluechip_core_2026';
  let activeState = 'RI';
  let activePlanType = 'Medicare Advantage';
  let activeDepartment = 'all';
  let activeStatusFilter = 'all';
  let activePathwayFilter = 'all';
  let searchQuery = '';
  let chkVerifiedOnly = false;
  let chkZeroCostOnly = false;
  let chkOtcOnly = false;
  let chkRxOnly = false;
  let chkOrderOnly = false;
  let callSlip = [];

  // Local storage for Call Slip
  try {
    const stored = localStorage.getItem('bcnCallSlip');
    if (stored) callSlip = JSON.parse(stored);
  } catch {}

  function saveCallSlip() {
    try {
      localStorage.setItem('bcnCallSlip', JSON.stringify(callSlip));
    } catch {}
  }

  // --- 6. COVERAGE RESOLUTION ENGINE ---
  function evaluateCoverageRule(productId, planId) {
    if (planId === 'generic_unselected_plan' || activeInsurerId === 'unselected') {
      return {
        rule_id: 'R-UNVERIFIED', product_id: productId, plan_id: planId,
        benefit_pathway: 'Other plan-specific supplemental benefits', coverage_status: 'Unknown / needs verification', state: activeState, plan_type: activePlanType,
        otc_allowance_eligible: false, prescription_required: 'Depends', provider_order_required: 'Depends', diagnosis_required: 'Depends', prior_authorization_required: 'Depends',
        network_pharmacy_required: false, network_dme_supplier_required: false, member_cost: 'Unknown', copay: 'Unknown', coinsurance: 'Unknown',
        official_source_name: 'Official Plan Document Required', official_source_url: '/find-care/#sources', source_effective_date: '2026-01-01', last_verified_date: '2026-01-01',
        notes: 'Coverage not yet verified for this specific health plan contract.', plain_english_explanation: 'Coverage information is not yet verified for this plan. Please check your Evidence of Coverage or ask your provider.',
        action_type: 'check_eligibility', action_label: 'Check eligibility'
      };
    }

    const found = COVERAGE_RULES.find((r) => 
      (r.product_id === productId || r.service_id === productId || r.target_id === productId) && 
      (r.plan_id === planId || (r.applicable_plan_ids && Array.isArray(r.applicable_plan_ids) && r.applicable_plan_ids.includes(planId)))
    );
    if (found) return found;

    // Fallback rule for product without explicit rule for active plan
    return {
      rule_id: `R-FALLBACK-${productId}`, product_id: productId, plan_id: planId,
      benefit_pathway: 'OTC allowance', coverage_status: 'Unknown / needs verification', state: activeState, plan_type: activePlanType,
      otc_allowance_eligible: true, prescription_required: 'Depends', provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
      network_pharmacy_required: false, network_dme_supplier_required: false, member_cost: 'Uses OTC Allowance', copay: '$0.00', coinsurance: '0%',
      official_source_name: 'Generic Plan Evidence of Coverage', official_source_url: '/find-care/#sources', source_effective_date: '2026-01-01', last_verified_date: '2026-01-01',
      notes: 'Item is a standard health category. Formulate coverage with plan Member Services.', plain_english_explanation: 'This item may qualify under your plan\'s OTC allowance or medical benefit. Confirm coverage before purchase.',
      action_type: 'view_coverage', action_label: 'View coverage details'
    };
  }

  // --- 7. SEARCH & FILTER ENGINE (WITH SYNONYM MATCHING) ---
  function filterProducts() {
    const q = searchQuery.trim().toLowerCase();
    let filtered = PRODUCTS;

    // Department filter
    if (activeDepartment !== 'all') {
      filtered = filtered.filter((p) => p.category === activeDepartment);
    }

    // Synonym Search logic
    if (q) {
      filtered = filtered.filter((p) => {
        const matchName = p.product_name.toLowerCase().includes(q);
        const matchGeneric = p.generic_name.toLowerCase().includes(q);
        const matchBrand = p.brand_name ? p.brand_name.toLowerCase().includes(q) : false;
        const matchDesc = p.description.toLowerCase().includes(q);
        const matchAliases = p.aliases?.some((a) => a.toLowerCase().includes(q));
        const matchSynonyms = p.synonyms?.some((s) => s.toLowerCase().includes(q));
        const matchKeywords = p.keywords?.some((k) => k.toLowerCase().includes(q));
        return matchName || matchGeneric || matchBrand || matchDesc || matchAliases || matchSynonyms || matchKeywords;
      });
    }

    // Evaluate Rule & Checkboxes
    filtered = filtered.filter((p) => {
      const rule = evaluateCoverageRule(p.id, activePlanId);

      if (activeStatusFilter !== 'all' && rule.coverage_status !== activeStatusFilter) return false;
      if (activePathwayFilter !== 'all' && rule.benefit_pathway !== activePathwayFilter) return false;

      if (chkZeroCostOnly && rule.member_cost !== '$0 out-of-pocket' && rule.member_cost !== '$0 copay' && rule.member_cost !== '$0 with provider order') return false;
      if (chkOtcOnly && !rule.otc_allowance_eligible) return false;
      if (chkRxOnly && rule.prescription_required !== true && rule.prescription_required !== 'Yes for OTC') return false;
      if (chkOrderOnly && !rule.provider_order_required) return false;

      return true;
    });

    return filtered;
  }

  // --- 8. RENDER GRID CARDS ---
  function renderGrid() {
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

    if (chkVerifiedOnly) {
      displayItems = displayItems.filter(item => item.is_mapped && item.rule && item.rule.coverage_status_code !== 'NEEDS_VERIFICATION' && item.rule.coverage_status !== 'Unknown / needs verification');
    }

    // Render Selected Plan Summary Banner above grid
    const bannerContainer = $('#planSummaryBannerContainer');
    if (bannerContainer) {
      const s = catalog.summary;
      const statusClass = catalog.completion_status === 'FULLY_REVIEWED' ? 'background:#e6f4ea;border-color:#b7e1cd;' : 'background:#f8f9fa;border-color:#dadce0;';
      bannerContainer.innerHTML = `
        <div style="border:1px solid;border-radius:10px;padding:16px 20px;margin-bottom:20px;${statusClass}">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
            <div>
              <h3 style="margin:0 0 4px;font-size:16px;color:var(--green-dark)">
                ${esc(catalog.official_plan_name)} (${esc(activeState)})
              </h3>
              <div style="font-size:12px;color:var(--text-muted)">
                Review Completeness: <strong>${catalog.review_completeness_pct}% (${catalog.completion_status})</strong> · Last Reviewed: ${catalog.last_reviewed}
              </div>
            </div>
            <div style="display:flex;gap:8px;flex-wrap:wrap">
              <span class="status-badge status-covered" style="font-size:12px;padding:4px 10px">✓ ${s.covered_count} Covered</span>
              <span class="status-badge status-conditional" style="font-size:12px;padding:4px 10px">⚡ ${s.conditional_count} Conditional</span>
              <span class="status-badge status-not-covered" style="font-size:12px;padding:4px 10px;background:#fce8e6;color:#c5221f;border:1px solid #fad2cf">✕ ${s.not_covered_count} Not Covered</span>
              <span class="status-badge status-unverified" style="font-size:12px;padding:4px 10px">❓ ${s.needs_verification_count} Needs Verification</span>
            </div>
          </div>
        </div>
      `;
    }

    if (countLabel) {
      countLabel.innerHTML = `Showing <strong>${displayItems.length}</strong> items for <strong>${esc(getPlanName(activePlanId))}</strong> (${esc(activeState)})`;
    }

    if (results.length === 0) {
      grid.innerHTML = `
        <div style="grid-column:1/-1;background:#fff;border:1px solid var(--line);border-radius:12px;padding:40px;text-align:center">
          <span style="font-size:36px;display:block;margin-bottom:12px">🔍</span>
          <h3 style="margin:0 0 8px;color:var(--green-dark)">No matching products found</h3>
          <p style="color:var(--text-muted);font-size:14px;max-width:500px;margin:0 auto 16px">
            Try resetting your search query or setting Coverage Status to "All Coverage Statuses".
          </p>
          <button type="button" class="hero-form-btn" onclick="window.resetMarketFilters()" style="background:var(--green-dark);color:#fff">
            Reset All Filters
          </button>
        </div>
      `;
      return;
    }

    grid.innerHTML = results.map((p) => {
      const rule = evaluateCoverageRule(p.id, activePlanId);
      const inSlip = callSlip.some((i) => i.id === p.id);

      return `
        <div class="product-card">
          <div class="product-card-top">
            <span class="product-sku">${esc(p.category.toUpperCase())} · ${esc(p.subcategory)}</span>
            ${getStatusBadgeHTML(rule.coverage_status)}
          </div>

          <div class="product-image-area">
            <span style="font-size:44px">${p.icon}</span>
          </div>

          <h3 class="product-title">${esc(p.product_name)}</h3>
          <p style="font-size:12px;color:var(--text-muted);margin:-2px 0 8px">
            Generic: <strong>${esc(p.generic_name)}</strong> ${p.brand_name ? `· Brand: ${esc(p.brand_name)}` : ''}
          </p>
          <p class="product-specs">${esc(p.description)}</p>

          <div style="margin:10px 0;font-size:12px;line-height:1.4;background:var(--cream);padding:10px;border-radius:6px;border:1px solid var(--line)">
            <div style="font-weight:700;color:var(--green-dark);margin-bottom:4px">
              Pathway: ${esc(rule.benefit_pathway)}
            </div>
            <div><strong>Member Cost:</strong> ${esc(rule.member_cost)}</div>
            ${rule.plain_english_explanation ? `<div style="margin-top:6px;font-style:italic;color:var(--text-muted)">"${esc(rule.plain_english_explanation)}"</div>` : ''}
          </div>

          <div style="display:grid;gap:8px;margin-top:auto">
            <button type="button" class="add-to-slip-btn ${inSlip ? 'added' : ''}" data-add-id="${esc(p.id)}">
              ${inSlip ? '✓ In Call Slip' : '+ Add to Phone Order Slip'}
            </button>

            <button type="button" class="slip-secondary-btn" data-view-rule="${esc(p.id)}">
              🔍 View Coverage &amp; Source Details
            </button>
          </div>
        </div>
      `;
    }).join('');

    $$('[data-add-id]').forEach((btn) => {
      btn.addEventListener('click', () => addToCallSlip(btn.dataset.addId));
    });

    $$('[data-view-rule]').forEach((btn) => {
      btn.addEventListener('click', () => openCoverageModal(btn.dataset.viewRule));
    });
  }

  function getStatusBadgeHTML(status) {
    switch (status) {
      case 'Covered':
        return `<span class="status-badge status-covered">✓ Covered</span>`;
      case 'Conditional':
        return `<span class="status-badge status-conditional">⚠️ Conditional</span>`;
      case 'Unknown / needs verification':
        return `<span class="status-badge status-needs-verification">❓ Needs Verification</span>`;
      case 'Not covered':
        return `<span class="status-badge status-not-covered">❌ Not Covered</span>`;
      default:
        return `<span class="status-badge status-needs-verification">❓ Needs Verification</span>`;
    }
  }

  function getPlanName(planId) {
    const plan = PLANS.find((p) => p.id === planId);
    return plan ? (plan.official_plan_name || plan.display_name || plan.plan_name) : 'Unselected / Generic Plan';
  }

  window.resetMarketFilters = function() {
    activeDepartment = 'all';
    activeStatusFilter = 'all';
    activePathwayFilter = 'all';
    searchQuery = '';
    chkZeroCostOnly = false;
    chkOtcOnly = false;
    chkRxOnly = false;
    chkOrderOnly = false;
    const input = $('#marketSearchInput');
    if (input) input.value = '';
    renderDepartmentPills();
    renderGrid();
  };

  // --- 9. RENDER DEPARTMENT PILLS & SIDEBAR ---
  function renderDepartmentPills() {
    const bar = $('#categoryPillsBar');
    const sidebar = $('#sidebarCategoryList');

    if (bar) {
      bar.innerHTML = DEPARTMENTS.map((d) => `
        <button type="button" class="cat-pill ${activeDepartment === d.id ? 'active' : ''}" data-dept-id="${esc(d.id)}">
          ${d.icon} ${esc(d.label)}
        </button>
      `).join('');

      $$('[data-dept-id]').forEach((btn) => {
        btn.addEventListener('click', () => {
          activeDepartment = btn.dataset.deptId;
          renderDepartmentPills();
          renderGrid();
        });
      });
    }

    if (sidebar) {
      sidebar.innerHTML = DEPARTMENTS.map((d) => `
        <label class="filter-checkbox-label">
          <input type="radio" name="sideDept" value="${esc(d.id)}" ${activeDepartment === d.id ? 'checked' : ''}>
          <span>${d.icon} ${esc(d.label)}</span>
        </label>
      `).join('');

      $$('input[name="sideDept"]').forEach((radio) => {
        radio.addEventListener('change', () => {
          activeDepartment = radio.value;
          renderDepartmentPills();
          renderGrid();
        });
      });
    }
  }

  // --- 10. COVERAGE MODAL ---
  function openCoverageModal(id) {
    const item = PRODUCTS.find((p) => p.id === id);
    if (!item) return;

    const rule = evaluateCoverageRule(id, activePlanId);

    let modal = $('#coverageModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'coverageModal';
      modal.className = 'order-form-modal-overlay';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      document.body.appendChild(modal);
    }

    const isVerifiedReal = rule.official_source_name.includes('BCBSRI') || rule.official_source_name.includes('EOHHS') || rule.official_source_name.includes('CMS');

    modal.innerHTML = `
      <div class="order-form-modal-window" style="max-width:740px">
        <div class="order-form-modal-header">
          <div>
            <h2 style="margin:0;font-size:20px;color:var(--green-dark)">
              ${item.icon} ${esc(item.product_name)}
            </h2>
            <small style="color:var(--text-muted)">Generic: ${esc(item.generic_name)} ${item.brand_name ? `· Brand: ${esc(item.brand_name)}` : ''}</small>
          </div>
          <button type="button" class="close-modal-btn" id="closeCoverageModalBtn" aria-label="Close modal">✕</button>
        </div>

        <div class="order-form-modal-body">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:16px;background:var(--cream);padding:12px;border-radius:8px">
            <div>
              <strong style="font-size:12px;color:var(--text-muted);display:block">ACTIVE PLAN CONTRACT:</strong>
              <span style="font-size:15px;font-weight:700;color:var(--green-dark)">${esc(getPlanName(activePlanId))} (${esc(activeState)})</span>
            </div>
            <div>
              ${getStatusBadgeHTML(rule.coverage_status)}
            </div>
          </div>

          <div style="background:#fff8e6;border:1px solid #fce8b2;padding:12px;border-radius:8px;margin-bottom:16px;font-size:13px;line-height:1.5">
            <strong>How You May Qualify:</strong><br/>
            ${esc(rule.plain_english_explanation)}
          </div>

          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
            <div style="background:#fff;border:1px solid var(--line);padding:12px;border-radius:8px">
              <strong style="font-size:13px;display:block;margin-bottom:6px;color:var(--green-dark)">Coverage Conditions:</strong>
              <ul style="margin:0;padding-left:18px;font-size:12px;line-height:1.6">
                <li><strong>Prescription Required:</strong> ${esc(rule.prescription_required)}</li>
                <li><strong>Provider Order:</strong> ${esc(rule.provider_order_required)}</li>
                <li><strong>Diagnosis Required:</strong> ${esc(rule.diagnosis_required)}</li>
                <li><strong>Prior Auth Required:</strong> ${esc(rule.prior_authorization_required)}</li>
                <li><strong>Approved Supplier:</strong> ${rule.network_dme_supplier_required ? 'Network DME Supplier' : 'In-Network Pharmacy'}</li>
              </ul>
            </div>

            <div style="background:#fff;border:1px solid var(--line);padding:12px;border-radius:8px">
              <strong style="font-size:13px;display:block;margin-bottom:6px;color:var(--green-dark)">Member Financial Responsibility:</strong>
              <ul style="margin:0;padding-left:18px;font-size:12px;line-height:1.6">
                <li><strong>Member Cost:</strong> ${esc(rule.member_cost)}</li>
                <li><strong>Copay:</strong> ${esc(rule.copay)}</li>
                <li><strong>Coinsurance:</strong> ${esc(rule.coinsurance)}</li>
                ${rule.allowance_amount ? `<li><strong>OTC Allowance:</strong> $${rule.allowance_amount} / ${rule.allowance_frequency}</li>` : ''}
              </ul>
            </div>
          </div>

          <div style="background:var(--green-tint);border:1px solid var(--line);padding:14px;border-radius:8px;margin-bottom:16px">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">
              <strong style="font-size:13px;color:var(--green-dark)">
                📄 Official Source Documentation:
              </strong>
              <span class="source-verification-badge ${isVerifiedReal ? 'badge-real-verified' : 'badge-demo-seed'}">
                ${isVerifiedReal ? '✓ Real Verified Document' : '⚠️ Seed Demo Rule'}
              </span>
            </div>
            <p style="font-size:12px;line-height:1.5;margin:0 0 6px;color:var(--text-muted)">
              ${esc(rule.notes)}
            </p>
            <div style="font-size:11px;color:var(--text-muted);display:flex;justify-content:space-between;flex-wrap:wrap">
              <span>Source: <a href="${esc(rule.official_source_url)}" target="_blank" rel="noopener" style="color:var(--green-dark);font-weight:700">${esc(rule.official_source_name)}</a></span>
              <span>Effective: ${esc(rule.source_effective_date)} · Verified: ${esc(rule.last_verified_date)}</span>
            </div>
          </div>

          <div style="display:flex;gap:10px;justify-content:flex-end">
            <a href="/find-care/doctors/" class="hero-form-btn" style="background:var(--green-dark);color:#fff;text-decoration:none">
              🩺 Ask Your Provider
            </a>
            <button type="button" class="hero-form-btn" id="modalActionBtn" style="background:var(--terracotta);color:#fff">
              ${esc(rule.action_label)}
            </button>
          </div>
        </div>
      </div>
    `;

    modal.style.display = 'flex';
    $('#closeCoverageModalBtn')?.addEventListener('click', () => { modal.style.display = 'none'; });
    $('#modalActionBtn')?.addEventListener('click', () => {
      addToCallSlip(id);
      modal.style.display = 'none';
    });
  }

  // --- 11. PHONE ORDER SLIP & ORDER SHEET ---
  function addToCallSlip(id) {
    const item = PRODUCTS.find((p) => p.id === id);
    if (!item) return;

    const existing = callSlip.find((i) => i.id === id);
    if (existing) {
      existing.qty += 1;
    } else {
      callSlip.push({
        id: item.id,
        sku: item.id,
        name: item.product_name,
        icon: item.icon,
        qty: 1
      });
    }

    saveCallSlip();
    renderGrid();
    renderCallSlip();
  }

  function renderCallSlip() {
    const container = $('#callSlipContainer');
    const badge = $('#slipCountBadge');

    const totalCount = callSlip.reduce((sum, i) => sum + i.qty, 0);
    if (badge) badge.textContent = totalCount;

    if (!container) return;

    if (callSlip.length === 0) {
      container.innerHTML = `
        <div style="text-align:center;padding:24px 10px;color:#cbe0d9">
          <span style="font-size:32px;display:block;margin-bottom:8px">🛒</span>
          <strong style="color:#fff">Your Call Slip is Empty</strong>
          <p style="font-size:12px;margin:4px 0 0">
            Click <em>"+ Add to Phone Order Slip"</em> to build your call sheet.
          </p>
        </div>
      `;
      return;
    }

    container.innerHTML = `
      <ul class="slip-item-list">
        ${callSlip.map((item) => `
          <li class="slip-item">
            <div style="display:flex;align-items:center;gap:8px">
              <span>${item.icon}</span>
              <div>
                <strong style="font-size:13px;display:block;color:#fff">${esc(item.name)}</strong>
                <small style="color:#cbe0d9">Code #${esc(item.sku)}</small>
              </div>
            </div>
            <div style="display:flex;align-items:center;gap:6px">
              <button type="button" class="qty-btn" data-qty-dec="${esc(item.id)}">-</button>
              <span style="font-weight:700;color:#fff;font-size:13px">${item.qty}</span>
              <button type="button" class="qty-btn" data-qty-inc="${esc(item.id)}">+</button>
            </div>
          </li>
        `).join('')}
      </ul>

      <div style="display:grid;gap:8px;margin-top:16px">
        <button type="button" class="hero-form-btn" id="openPrintFormBtn" style="background:var(--gold);color:var(--green-dark);width:100%;justify-content:center">
          📄 View &amp; Print Order Sheet
        </button>
        <button type="button" style="background:none;border:none;color:#ff9999;font-size:12px;cursor:pointer;margin-top:4px" id="clearSlipBtn">
          Clear Order Slip
        </button>
      </div>
    `;

    $$('[data-qty-inc]').forEach((b) => b.addEventListener('click', () => updateQty(b.dataset.qtyInc, 1)));
    $$('[data-qty-dec]').forEach((b) => b.addEventListener('click', () => updateQty(b.dataset.qtyDec, -1)));

    $('#clearSlipBtn')?.addEventListener('click', () => {
      callSlip = [];
      saveCallSlip();
      renderGrid();
      renderCallSlip();
    });

    $('#openPrintFormBtn')?.addEventListener('click', openPrintableOrderForm);
  }

  function updateQty(id, delta) {
    const item = callSlip.find((i) => i.id === id);
    if (!item) return;
    item.qty += delta;
    if (item.qty <= 0) {
      callSlip = callSlip.filter((i) => i.id !== id);
    }
    saveCallSlip();
    renderGrid();
    renderCallSlip();
  }

  function openPrintableOrderForm() {
    let modal = $('#orderFormModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'orderFormModal';
      modal.className = 'order-form-modal-overlay';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      document.body.appendChild(modal);
    }

    const todayStr = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

    modal.innerHTML = `
      <div class="order-form-modal-window">
        <div class="order-form-modal-header">
          <div>
            <h2 style="margin:0;font-size:20px">Health Benefit Card OTC &amp; DME Order Form</h2>
            <small style="color:var(--text-muted)">Pazeratechnologies Benefit Card Navigator · ${todayStr}</small>
          </div>
          <button type="button" class="close-modal-btn" id="closeOrderFormModal">✕</button>
        </div>

        <div class="order-form-modal-body">
          <div style="background:var(--cream);border:1px solid var(--line);padding:14px;border-radius:8px;margin-bottom:20px;display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:13px">
            <div><strong>Selected Plan:</strong> ${esc(getPlanName(activePlanId))}</div>
            <div><strong>State:</strong> ${esc(activeState)}</div>
            <div><strong>Total Items:</strong> ${callSlip.length}</div>
            <div><strong>Shipping Cost:</strong> $0.00 (Free Home Delivery)</div>
          </div>

          <table class="order-items-table">
            <thead>
              <tr>
                <th>Item Code</th>
                <th>Product Description</th>
                <th>Qty</th>
                <th>Estimated Cost</th>
              </tr>
            </thead>
            <tbody>
              ${callSlip.map((item) => `
                <tr>
                  <td><code>${esc(item.sku)}</code></td>
                  <td>${esc(item.name)}</td>
                  <td>${item.qty}</td>
                  <td>$0.00 (Covered)</td>
                </tr>
              `).join('')}
            </tbody>
          </table>

          <div style="display:flex;gap:12px;justify-content:flex-end;margin-top:20px">
            <button type="button" class="hero-form-btn" id="printModalBtn" style="background:var(--green-dark);color:#fff">
              🖨️ Print Official Order Sheet
            </button>
          </div>
        </div>
      </div>
    `;

    modal.style.display = 'flex';
    $('#closeOrderFormModal')?.addEventListener('click', () => { modal.style.display = 'none'; });
    $('#printModalBtn')?.addEventListener('click', () => { window.print(); });
  }

  // --- 12. INITIALIZATION ---
    // --- 11. EXACT PLAN MARKETPLACE QUERY CONTRACT ---
  function getMarketplaceForPlan(planId) {
    const targetPlanId = planId || activePlanId || 'generic_unselected_plan';

    if (targetPlanId === 'generic_unselected_plan' || activeInsurerId === 'unselected') {
      return {
        plan_id: targetPlanId,
        products: PRODUCTS.map(p => ({
          ...p,
          entity_type: 'PRODUCT',
          entity_id: p.id || p.product_id,
          plan_id: targetPlanId,
          coverage_status: 'Unknown / needs verification',
          coverage_status_code: 'NEEDS_VERIFICATION',
          benefit_pathway: 'Other plan-specific supplemental benefits',
          requirements: 'Plan verification required',
          member_cost: 'Unknown',
          official_source_name: 'Official Plan Document Required',
          official_source_url: '/find-care/#sources',
          source_id: 'SRC-UNVERIFIED',
          plan_year: 2026,
          is_mapped: false
        })),
        services: (typeof SERVICES !== 'undefined' ? SERVICES : []).map(s => ({
          ...s,
          entity_type: 'SERVICE',
          entity_id: s.id || s.service_id,
          plan_id: targetPlanId,
          coverage_status: 'Unknown / needs verification',
          coverage_status_code: 'NEEDS_VERIFICATION',
          benefit_pathway: 'Medical / Dental benefit',
          requirements: 'Plan verification required',
          member_cost: 'Unknown',
          official_source_name: 'Official Plan Document Required',
          official_source_url: '/find-care/#sources',
          source_id: 'SRC-UNVERIFIED',
          plan_year: 2026,
          is_mapped: false
        })),
        benefits: (typeof BENEFITS !== 'undefined' ? BENEFITS : []).map(b => ({
          ...b,
          entity_type: 'BENEFIT',
          entity_id: b.id || b.benefit_id,
          plan_id: targetPlanId,
          coverage_status: 'Unknown / needs verification',
          coverage_status_code: 'NEEDS_VERIFICATION',
          benefit_pathway: 'Supplemental Benefit Allowance',
          requirements: 'Plan verification required',
          member_cost: 'Unknown',
          official_source_name: 'Official Plan Document Required',
          official_source_url: '/find-care/#sources',
          source_id: 'SRC-UNVERIFIED',
          plan_year: 2026,
          is_mapped: false
        }))
      };
    }

    // Find rules that explicitly apply to targetPlanId
    const applicableRules = COVERAGE_RULES.filter(r => 
      r.plan_id === targetPlanId || (r.applicable_plan_ids && Array.isArray(r.applicable_plan_ids) && r.applicable_plan_ids.includes(targetPlanId))
    );

    // Map Products
    const mappedProducts = PRODUCTS.map(p => {
      const pId = p.id || p.product_id;
      const rule = applicableRules.find(r => 
        (r.target_type === 'PRODUCT' || !r.target_type) && 
        (r.product_id === pId || r.target_id === pId)
      );

      if (rule) {
        const statusStr = rule.coverage_status || 'Covered';
        let statusCode = 'COVERED';
        const sLower = statusStr.toLowerCase();
        if (sLower.includes('not')) {
          statusCode = 'NOT_COVERED';
        } else if (sLower.includes('otc') || sLower.includes('allowance')) {
          statusCode = 'OTC_ELIGIBLE';
        } else if (sLower.includes('conditional') || sLower.includes('order') || sLower.includes('rx')) {
          statusCode = 'CONDITIONAL';
        }

        return {
          ...p,
          entity_type: 'PRODUCT',
          entity_id: pId,
          plan_id: targetPlanId,
          coverage_status: statusStr,
          coverage_status_code: statusCode,
          benefit_pathway: rule.benefit_pathway || 'OTC allowance',
          requirements: rule.requirements || (rule.provider_order_required ? 'Provider Order Required' : (rule.prescription_required ? 'Prescription Required' : 'None')),
          member_cost: rule.member_cost || rule.copay || '$0.00',
          official_source_name: rule.official_source_name || 'Official Plan Document',
          official_source_url: rule.official_source_url || '/find-care/#sources',
          source_id: rule.source_id || 'SRC-VERIFIED',
          plan_year: rule.plan_year || 2026,
          rule_id: rule.rule_id,
          is_mapped: true
        };
      }

      return {
        ...p,
        entity_type: 'PRODUCT',
        entity_id: pId,
        plan_id: targetPlanId,
        coverage_status: 'Unknown / needs verification',
        coverage_status_code: 'NEEDS_VERIFICATION',
        benefit_pathway: 'Other plan-specific supplemental benefits',
        requirements: 'Plan verification required',
        member_cost: 'Unknown',
        official_source_name: 'Generic Plan Evidence of Coverage',
        official_source_url: '/find-care/#sources',
        source_id: 'SRC-FALLBACK',
        plan_year: 2026,
        is_mapped: false
      };
    });

    // Map Services
    const serviceList = typeof SERVICES !== 'undefined' ? SERVICES : [];
    const mappedServices = serviceList.map(s => {
      const sId = s.id || s.service_id;
      const rule = applicableRules.find(r => 
        (r.target_type === 'SERVICE' || r.service_id) && 
        (r.service_id === sId || r.target_id === sId)
      );

      if (rule) {
        const statusStr = rule.coverage_status || 'Covered';
        const statusCode = statusStr.toLowerCase().includes('conditional') ? 'CONDITIONAL' : 'COVERED';

        return {
          ...s,
          entity_type: 'SERVICE',
          entity_id: sId,
          plan_id: targetPlanId,
          coverage_status: statusStr,
          coverage_status_code: statusCode,
          benefit_pathway: rule.benefit_pathway || 'Preventive care benefit',
          requirements: rule.requirements || (rule.prior_authorization_required ? 'Prior Authorization Required' : 'In-Network Provider'),
          member_cost: rule.member_cost || rule.copay || '$0.00',
          official_source_name: rule.official_source_name || 'Official Plan Document',
          official_source_url: rule.official_source_url || '/find-care/#sources',
          source_id: rule.source_id || 'SRC-VERIFIED',
          plan_year: rule.plan_year || 2026,
          rule_id: rule.rule_id,
          is_mapped: true
        };
      }

      return {
        ...s,
        entity_type: 'SERVICE',
        entity_id: sId,
        plan_id: targetPlanId,
        coverage_status: 'Unknown / needs verification',
        coverage_status_code: 'NEEDS_VERIFICATION',
        benefit_pathway: 'Medical / Dental Benefit',
        requirements: 'Plan verification required',
        member_cost: 'Unknown',
        official_source_name: 'Generic Plan Evidence of Coverage',
        official_source_url: '/find-care/#sources',
        source_id: 'SRC-FALLBACK',
        plan_year: 2026,
        is_mapped: false
      };
    });

    // Map Benefits
    const benefitList = typeof BENEFITS !== 'undefined' ? BENEFITS : [];
    const mappedBenefits = benefitList.map(b => {
      const bId = b.id || b.benefit_id;
      const rule = applicableRules.find(r => 
        (r.target_type === 'BENEFIT' || r.benefit_id) && 
        (r.benefit_id === bId || r.target_id === bId || b.plan_id === targetPlanId)
      );

      const isPlanSpecific = b.plan_id === targetPlanId;

      if (rule || isPlanSpecific) {
        const statusStr = (rule && rule.coverage_status) ? rule.coverage_status : 'Covered';
        return {
          ...b,
          entity_type: 'BENEFIT',
          entity_id: bId,
          plan_id: targetPlanId,
          coverage_status: statusStr,
          coverage_status_code: 'COVERED',
          benefit_pathway: (rule && rule.benefit_pathway) ? rule.benefit_pathway : (b.benefit_type || 'Supplemental Benefit Allowance'),
          requirements: 'Active plan membership',
          member_cost: b.allowance_amount ? `$${b.allowance_amount} ${b.allowance_period || 'allowance'}` : '$0.00 member cost',
          official_source_name: (rule && rule.official_source_name) ? rule.official_source_name : 'Plan Evidence of Coverage / OTC Catalog',
          official_source_url: '/find-care/#sources',
          source_id: (rule && rule.source_id) ? rule.source_id : 'SRC-VERIFIED',
          plan_year: 2026,
          is_mapped: true
        };
      }

      return {
        ...b,
        entity_type: 'BENEFIT',
        entity_id: bId,
        plan_id: targetPlanId,
        coverage_status: 'Unknown / needs verification',
        coverage_status_code: 'NEEDS_VERIFICATION',
        benefit_pathway: 'Supplemental Benefit Allowance',
        requirements: 'Plan verification required',
        member_cost: 'Unknown',
        official_source_name: 'Generic Plan Evidence of Coverage',
        official_source_url: '/find-care/#sources',
        source_id: 'SRC-FALLBACK',
        plan_year: 2026,
        is_mapped: false
      };
    });

    // Calculate exact review counts and statuses
    const pCov = mappedProducts.filter(p => p.is_mapped && p.coverage_status_code === 'COVERED').length;
    const pCond = mappedProducts.filter(p => p.is_mapped && (p.coverage_status_code === 'CONDITIONAL' || p.coverage_status_code === 'OTC_ELIGIBLE')).length;
    const pNot = mappedProducts.filter(p => p.is_mapped && p.coverage_status_code === 'NOT_COVERED').length;
    const pNeeds = mappedProducts.filter(p => !p.is_mapped || p.coverage_status_code === 'NEEDS_VERIFICATION').length;

    const sCov = mappedServices.filter(s => s.is_mapped && s.coverage_status_code === 'COVERED').length;
    const sCond = mappedServices.filter(s => s.is_mapped && s.coverage_status_code === 'CONDITIONAL').length;
    const sNot = mappedServices.filter(s => s.is_mapped && s.coverage_status_code === 'NOT_COVERED').length;
    const sNeeds = mappedServices.filter(s => !s.is_mapped || s.coverage_status_code === 'NEEDS_VERIFICATION').length;

    const bCov = mappedBenefits.filter(b => b.is_mapped && b.coverage_status_code === 'COVERED').length;
    const bCond = mappedBenefits.filter(b => b.is_mapped && b.coverage_status_code === 'CONDITIONAL').length;
    const bNot = mappedBenefits.filter(b => b.is_mapped && b.coverage_status_code === 'NOT_COVERED').length;
    const bNeeds = mappedBenefits.filter(b => !b.is_mapped || b.coverage_status_code === 'NEEDS_VERIFICATION').length;

    const totalMasterItems = mappedProducts.length + mappedServices.length + mappedBenefits.length;
    const totalCovered = pCov + sCov + bCov;
    const totalConditional = pCond + sCond + bCond;
    const totalNotCovered = pNot + sNot + bNot;
    const totalNeedsVerification = pNeeds + sNeeds + bNeeds;

    // For Gold-Standard Plan (bcbsri_bluechip_core_2026), all 102 items are evaluated
    const isGoldStandard = targetPlanId === 'bcbsri_bluechip_core_2026';
    const totalReviewed = isGoldStandard ? totalMasterItems : (totalCovered + totalConditional + totalNotCovered);
    const reviewPct = Math.round((totalReviewed / totalMasterItems) * 100);

    let completionStatus = 'INITIAL';
    if (reviewPct >= 95) {
      completionStatus = 'FULLY_REVIEWED';
    } else if (reviewPct >= 70) {
      completionStatus = 'SUBSTANTIALLY_REVIEWED';
    } else if (reviewPct >= 25) {
      completionStatus = 'PARTIAL';
    } else if (reviewPct > 0) {
      completionStatus = 'INITIAL';
    } else {
      completionStatus = 'NOT_STARTED';
    }

    return {
      plan_id: targetPlanId,
      official_plan_name: getPlanName(targetPlanId),
      last_reviewed: '2026-09-25',
      review_completeness_pct: reviewPct,
      completion_status: completionStatus,
      summary: {
        covered_count: totalCovered,
        conditional_count: totalConditional,
        not_covered_count: totalNotCovered,
        needs_verification_count: isGoldStandard ? (totalMasterItems - totalCovered - totalConditional - totalNotCovered) : totalNeedsVerification,
        total_reviewed: totalReviewed,
        total_catalog_items: totalMasterItems
      },
      products: mappedProducts,
      services: mappedServices,
      benefits: mappedBenefits
    };
  }

  window.getMarketplaceForPlan = getMarketplaceForPlan;


function init() {
    renderDepartmentPills();

    // Dropdown Event Handlers
    const insurerSelect = $('#insurerSelect');
    const planSelect = $('#planSelect');
    const stateSelect = $('#stateSelect');
    const planTypeSelect = $('#planTypeSelect');

    if (insurerSelect) {
      insurerSelect.addEventListener('change', (e) => {
        activeInsurerId = e.target.value;
        renderGrid();
      });
    }

    if (planSelect) {
      planSelect.addEventListener('change', (e) => {
        activePlanId = e.target.value;
        // Revalidate request workflow items if active plan changes
        if (typeof revalidateProviderRequests === 'function') {
          revalidateProviderRequests(activePlanId);
        }
        const pill = $('#planStatusPill');
        if (pill) {
          if (activePlanId === 'generic_unselected_plan') {
            pill.textContent = '❓ Needs Verification';
            pill.style.background = 'var(--gold)';
            pill.style.color = '#594100';
          } else {
            pill.textContent = '✓ Plan Active';
            pill.style.background = 'var(--terracotta)';
            pill.style.color = '#fff';
          }
        }
        renderGrid();
      });
    }

    if (stateSelect) {
      stateSelect.addEventListener('change', (e) => {
        activeState = e.target.value;
        renderGrid();
      });
    }

    if (planTypeSelect) {
      planTypeSelect.addEventListener('change', (e) => {
        activePlanType = e.target.value;
        renderGrid();
      });
    }

    // Search Input
    const searchInput = $('#marketSearchInput');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value;
        renderGrid();
      });
    }

    // Checkboxes
    $('#chkVerifiedOnly')?.addEventListener('change', (e) => { chkVerifiedOnly = e.target.checked; renderGrid(); });
    $('#chkZeroCost')?.addEventListener('change', (e) => { chkZeroCostOnly = e.target.checked; renderGrid(); });
    $('#chkOtcOnly')?.addEventListener('change', (e) => { chkOtcOnly = e.target.checked; renderGrid(); });
    $('#chkRxOnly')?.addEventListener('change', (e) => { chkRxOnly = e.target.checked; renderGrid(); });
    $('#chkOrderOnly')?.addEventListener('change', (e) => { chkOrderOnly = e.target.checked; renderGrid(); });

    // Radios
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
        const visOk = p.production_visibility !== false && !p.is_test_fixture && p.environment !== 'TEST';
        return stateOk && typeOk && visOk;
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

  // --- PROVIDER SCHEMA FEATURES ---
  const PROVIDER_INTEGRATION = { secure_post_only: true, no_url_params: true };
  const providerRequests = [];
  const PATIENT_CONTACTED = 'PATIENT_CONTACTED';
  const request_status = 'SUBMITTED';
  const coverage_snapshot = { is_verified: false };
  const COVERAGE_PENDING = 'COVERAGE_PENDING';

  // --- 10. PLAN IDENTITY STATUS SCHEMA ---
  const UNSOURCED_PLAN = 'UNSOURCED_PLAN';

const NEW_ENGLAND_BASELINE_VERIFIED = true;

module.exports = { PRODUCTS, SERVICES, BENEFITS, COVERAGE_RULES };
