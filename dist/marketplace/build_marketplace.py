import sys

js_code = """/**
 * Benefit Card Navigator — OTC & Health Products Marketplace
 * Architecture based on Pazeratechnologies multi-pathway data model:
 * - OTC (Plan OTC Allowance, e.g. BCBSRI BlueCHiP $25-$50/qtr, CarePartners)
 * - Rx (Pharmacy Prescribed Benefit, e.g. RI Medicaid EOHHS 2026 protocols)
 * - DME (Durable Medical Equipment / CMS DMEPOS)
 * - Preventive (100% ACA Preventive Care)
 * - Supplemental (Medicare Advantage D-SNP / SSBCI Special Benefits)
 */

(function () {
  'use strict';

  const $ = (selector, parent = document) => parent.querySelector(selector);
  const $$ = (selector, parent = document) => [...parent.querySelectorAll(selector)];
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  // Multi-Pathway Insurance-Eligible Catalog
  const PRODUCTS = [
    // --- 1. VITAMINS & MINERALS ---
    {
      sku: 'VIT-101',
      name: 'High-Potency Vitamin D3 2,000 IU (50 mcg)',
      department: 'Vitamins & Supplements',
      category: 'vitamins',
      categoryLabel: 'Vitamins & Minerals',
      pathway: 'OTC / Rx',
      pathwayBadge: 'pathway-otc',
      eligibilityTag: '✓ Usually eligible OTC / Rx when prescribed',
      eligibilityClass: 'tag-otc',
      specs: 'Supports strong bones, teeth, and immune health · 100 Softgels',
      icon: '💊',
      retailValue: '$12.99',
      allowanceCost: 11.00,
      rxNeeded: 'Depends on Plan (Rx for Medicaid)',
      dmeNeeded: 'No',
      riMedicaidNote: 'RI Medicaid 2026: Covered under pharmacy benefit when prescribed by practitioner.',
      bcbsriNote: 'BCBSRI 2026: Eligible under BlueCHiP quarterly OTC allowance ($25–$50/qtr).'
    },
    {
      sku: 'VIT-102',
      name: 'Vitamin D3 Maximum Strength 5,000 IU (125 mcg)',
      department: 'Vitamins & Supplements',
      category: 'vitamins',
      categoryLabel: 'Vitamins & Minerals',
      pathway: 'OTC / Rx',
      pathwayBadge: 'pathway-otc',
      eligibilityTag: '✓ Usually eligible OTC / Rx when prescribed',
      eligibilityClass: 'tag-otc',
      specs: 'Dietary supplement for calcium absorption & immune defense · 90 Softgels',
      icon: '☀️',
      retailValue: '$15.50',
      allowanceCost: 13.50,
      rxNeeded: 'Depends on Plan',
      dmeNeeded: 'No'
    },
    {
      sku: 'VIT-103',
      name: 'Vitamin C 1,000 mg with Rose Hips & Bioflavonoids',
      department: 'Vitamins & Supplements',
      category: 'vitamins',
      categoryLabel: 'Vitamins & Minerals',
      pathway: 'OTC',
      pathwayBadge: 'pathway-otc',
      eligibilityTag: '✓ Usually eligible OTC',
      eligibilityClass: 'tag-otc',
      specs: 'High-potency antioxidant support for immune function · 100 Caplets',
      icon: '🍊',
      retailValue: '$13.99',
      allowanceCost: 12.00,
      rxNeeded: 'No',
      dmeNeeded: 'No'
    },
    {
      sku: 'VIT-104',
      name: 'Folic Acid 800 mcg (Preventive Care Coverage)',
      department: 'Vitamins & Supplements',
      category: 'vitamins',
      categoryLabel: 'Vitamins & Minerals',
      pathway: 'Preventive / Rx',
      pathwayBadge: 'pathway-preventive',
      eligibilityTag: '✓ 100% ACA Preventive Benefit for women',
      eligibilityClass: 'tag-otc',
      specs: 'ACA mandated 100% preventive coverage for women of childbearing age · 250 Tablets',
      icon: '🌸',
      retailValue: '$12.50',
      allowanceCost: 0.00,
      rxNeeded: 'Yes for 100% ACA Copay',
      dmeNeeded: 'No',
      riMedicaidNote: 'RI Medicaid 2026: 100% covered under preventive pharmacy protocol.'
    },
    {
      sku: 'VIT-105',
      name: 'Magnesium Glycinate 400 mg High Absorption Chelate',
      department: 'Vitamins & Supplements',
      category: 'vitamins',
      categoryLabel: 'Vitamins & Minerals',
      pathway: 'OTC / Rx',
      pathwayBadge: 'pathway-otc',
      eligibilityTag: '✓ Usually eligible OTC',
      eligibilityClass: 'tag-otc',
      specs: 'Gentle on stomach; promotes muscle relaxation & sleep · 120 Capsules',
      icon: '🌿',
      retailValue: '$18.99',
      allowanceCost: 16.50,
      rxNeeded: 'Depends on Plan',
      dmeNeeded: 'No'
    },
    {
      sku: 'VIT-106',
      name: 'Iron / Ferrous Sulfate 65 mg (325 mg Equivalent)',
      department: 'Vitamins & Supplements',
      category: 'vitamins',
      categoryLabel: 'Vitamins & Minerals',
      pathway: 'OTC / Rx',
      pathwayBadge: 'pathway-rx',
      eligibilityTag: '✓ Usually eligible OTC / Rx',
      eligibilityClass: 'tag-otc',
      specs: 'Essential mineral for red blood cell production & anemia · 100 Tablets',
      icon: '🩸',
      retailValue: '$10.50',
      allowanceCost: 8.50,
      rxNeeded: 'Depends on Plan',
      dmeNeeded: 'No'
    },
    {
      sku: 'VIT-107',
      name: 'Vitamin B12 5,000 mcg Sublingual Methylcobalamin',
      department: 'Vitamins & Supplements',
      category: 'vitamins',
      categoryLabel: 'Vitamins & Minerals',
      pathway: 'OTC / Rx',
      pathwayBadge: 'pathway-otc',
      eligibilityTag: '✓ Usually eligible OTC',
      eligibilityClass: 'tag-otc',
      specs: 'Nerve health, red blood cell synthesis & cellular energy · 90 Tablets',
      icon: '🔋',
      retailValue: '$17.50',
      allowanceCost: 14.00,
      rxNeeded: 'No',
      dmeNeeded: 'No'
    },

    // --- 2. NUTRITION & DIETARY SUPPLEMENTS ---
    {
      sku: 'NUT-201',
      name: 'Medically Necessary High-Protein Nutritional Shakes (Ensure 24-Pack)',
      department: 'Nutrition & Supplements',
      category: 'nutrition',
      categoryLabel: 'Nutrition & Supplements',
      pathway: 'Rx / Supplemental',
      pathwayBadge: 'pathway-rx',
      eligibilityTag: '📋 May require Rx or prior authorization',
      eligibilityClass: 'tag-rx-auth',
      specs: '30g Protein, 25 Vitamins & Minerals · 24 Ready-to-Drink 11 fl oz Bottles',
      icon: '🥛',
      retailValue: '$46.00',
      allowanceCost: 39.00,
      rxNeeded: 'Yes for Medicaid Coverage',
      dmeNeeded: 'No',
      riMedicaidNote: 'RI EOHHS 2026: Medically necessary nutritional supplements covered when ordered by practitioner.'
    },
    {
      sku: 'NUT-202',
      name: 'Glucerna Hunger Smart Diabetic Nutrition Shakes (Chocolate 24-Pack)',
      department: 'Nutrition & Supplements',
      category: 'nutrition',
      categoryLabel: 'Nutrition & Supplements',
      pathway: 'Supplemental / OTC',
      pathwayBadge: 'pathway-supplemental',
      eligibilityTag: '⚠️ Eligible only with select plans',
      eligibilityClass: 'tag-select-plans',
      specs: 'CARBSTEADY slow-release carbs to manage blood sugar spikes · 24 Bottles',
      icon: '🍫',
      retailValue: '$48.00',
      allowanceCost: 41.00,
      rxNeeded: 'No',
      dmeNeeded: 'No'
    },
    {
      sku: 'NUT-203',
      name: 'Enteral Tube-Feeding Formula & Nutrition Bags',
      department: 'Nutrition & Supplements',
      category: 'nutrition',
      categoryLabel: 'Nutrition & Supplements',
      pathway: 'DME / Medical',
      pathwayBadge: 'pathway-dme',
      eligibilityTag: '🩺 Covered under medical/DME benefit, not OTC allowance',
      eligibilityClass: 'tag-dme',
      specs: 'Complete enteral clinical nutrition formula for tube feeding · Case of 24',
      icon: '🪠',
      retailValue: '$120.00',
      allowanceCost: 0.00,
      rxNeeded: 'Yes',
      dmeNeeded: 'Yes (CMS DMEPOS Benefit)'
    },

    // --- 3. PAIN RELIEF ---
    {
      sku: 'PAI-301',
      name: 'Extra Strength Acetaminophen 500 mg (100 Caplets)',
      department: 'Pain Relief',
      category: 'pain',
      categoryLabel: 'Pain Relief & Topicals',
      pathway: 'OTC',
      pathwayBadge: 'pathway-otc',
      eligibilityTag: '✓ Usually eligible OTC',
      eligibilityClass: 'tag-otc',
      specs: 'Aspirin-free rapid-release pain reliever & fever reducer · 100 Caplets',
      icon: '💊',
      retailValue: '$10.99',
      allowanceCost: 8.50,
      rxNeeded: 'No',
      dmeNeeded: 'No',
      bcbsriNote: 'BCBSRI 2026: Eligible under quarterly OTC spending card allowance.'
    },
    {
      sku: 'PAI-302',
      name: 'Voltaren Arthritis Pain Relief Gel (Diclofenac Sodium 1%)',
      department: 'Pain Relief',
      category: 'pain',
      categoryLabel: 'Pain Relief & Topicals',
      pathway: 'OTC / Rx',
      pathwayBadge: 'pathway-otc',
      eligibilityTag: '✓ Usually eligible OTC / Rx',
      eligibilityClass: 'tag-otc',
      specs: 'Topical NSAID gel for daily arthritis joint pain relief · 100g Tube',
      icon: '🧴',
      retailValue: '$22.50',
      allowanceCost: 17.50,
      rxNeeded: 'No',
      dmeNeeded: 'No'
    },
    {
      sku: 'PAI-303',
      name: 'Maximum Strength Lidocaine 4% Pain Relief Patches (5 Pack)',
      department: 'Pain Relief',
      category: 'pain',
      categoryLabel: 'Pain Relief & Topicals',
      pathway: 'OTC / Rx',
      pathwayBadge: 'pathway-otc',
      eligibilityTag: '✓ Usually eligible OTC',
      eligibilityClass: 'tag-otc',
      specs: 'Numbing relief for back, neck, shoulder & joint stiffness · 5 Patches',
      icon: '🩹',
      retailValue: '$16.99',
      allowanceCost: 13.50,
      rxNeeded: 'No',
      dmeNeeded: 'No'
    },
    {
      sku: 'PAI-304',
      name: 'Dual-Channel TENS Unit Muscle Stimulator with 8 Pads',
      department: 'Pain Relief',
      category: 'pain',
      categoryLabel: 'Pain Relief & Topicals',
      pathway: 'DME / Supplemental',
      pathwayBadge: 'pathway-dme',
      eligibilityTag: '📋 May require Rx or prior authorization',
      eligibilityClass: 'tag-rx-auth',
      specs: 'Drug-free nerve stimulation for chronic pain relief · 24 EMS modes',
      icon: '⚡',
      retailValue: '$45.00',
      allowanceCost: 36.00,
      rxNeeded: 'Yes for DME coverage',
      dmeNeeded: 'Yes'
    },

    // --- 4. COLD, FLU & ALLERGY ---
    {
      sku: 'CFA-401',
      name: 'Non-Drowsy 24-Hour Allergy Relief Cetirizine 10 mg (100 CT)',
      department: 'Cold & Allergy',
      category: 'coldflu',
      categoryLabel: 'Cold, Flu & Allergy',
      pathway: 'OTC / Rx',
      pathwayBadge: 'pathway-otc',
      eligibilityTag: '✓ Usually eligible OTC',
      eligibilityClass: 'tag-otc',
      specs: '24-hour relief of sneezing, runny nose & itchy eyes · 100 Tablets',
      icon: '🤧',
      retailValue: '$18.99',
      allowanceCost: 15.00,
      rxNeeded: 'No',
      dmeNeeded: 'No'
    },
    {
      sku: 'CFA-402',
      name: 'FDA-Authorized At-Home COVID-19 Rapid Antigen Test Kit (2 Tests)',
      department: 'Cold & Allergy',
      category: 'coldflu',
      categoryLabel: 'Cold, Flu & Allergy',
      pathway: 'Supplemental / OTC',
      pathwayBadge: 'pathway-supplemental',
      eligibilityTag: '⚠️ Eligible only with select plans',
      eligibilityClass: 'tag-select-plans',
      specs: '15-minute nasal swab results for active SARS-CoV-2 infection',
      icon: '🧪',
      retailValue: '$24.00',
      allowanceCost: 20.00,
      rxNeeded: 'No',
      dmeNeeded: 'No'
    },

    // --- 5. DIGESTIVE HEALTH ---
    {
      sku: 'DIG-501',
      name: 'Omeprazole 20 mg Acid Reducer (42 Tablets, 3-Pack)',
      department: 'Digestive Health',
      category: 'digestive',
      categoryLabel: 'Digestive Health',
      pathway: 'OTC / Rx',
      pathwayBadge: 'pathway-otc',
      eligibilityTag: '✓ Usually eligible OTC / Rx',
      eligibilityClass: 'tag-otc',
      specs: 'Treats frequent heartburn 2+ days a week · 42 Delayed-Release Tablets',
      icon: '🥣',
      retailValue: '$22.99',
      allowanceCost: 18.50,
      rxNeeded: 'Depends on Plan',
      dmeNeeded: 'No'
    },

    // --- 6. FIRST AID & WOUND CARE ---
    {
      sku: 'AID-601',
      name: '200-Piece All-Purpose Emergency First Aid & Trauma Kit',
      department: 'First Aid',
      category: 'firstaid',
      categoryLabel: 'First Aid & Wound Care',
      pathway: 'OTC',
      pathwayBadge: 'pathway-otc',
      eligibilityTag: '✓ Usually eligible OTC',
      eligibilityClass: 'tag-otc',
      specs: 'Bandages, sterile gauze, medical tape, antiseptic wipes & scissors',
      icon: '🧰',
      retailValue: '$27.99',
      allowanceCost: 22.00,
      rxNeeded: 'No',
      dmeNeeded: 'No'
    },

    // --- 7. BRACES & ORTHOPEDICS ---
    {
      sku: 'BRC-701',
      name: 'Dual-Hinged Medical Knee Brace with Side Stabilizers & Gel Ring',
      department: 'Braces & Supports',
      category: 'braces',
      categoryLabel: 'Braces & Orthopedics',
      pathway: 'OTC / DME',
      pathwayBadge: 'pathway-dme',
      eligibilityTag: '📋 Requires Physician Order for DME Billing (or OTC allowance)',
      eligibilityClass: 'tag-rx-auth',
      specs: 'Medical-grade knee stabilization for arthritis, meniscus, or ligament tears',
      icon: '🦿',
      retailValue: '$48.00',
      allowanceCost: 38.00,
      rxNeeded: 'Yes for DME billing',
      dmeNeeded: 'Yes',
      dualPathwayInfo: 'Pathway A: Purchase directly with OTC Allowance ($0 out-of-pocket balance).\nPathway B: Obtain physician Rx for 100% Medicare/Medicaid DMEPOS Coverage.'
    },
    {
      sku: 'BRC-702',
      name: 'Ergonomic Carpal Tunnel Wrist Brace & Night Support Splint',
      department: 'Braces & Supports',
      category: 'braces',
      categoryLabel: 'Braces & Orthopedics',
      pathway: 'OTC / DME',
      pathwayBadge: 'pathway-otc',
      eligibilityTag: '✓ Usually eligible OTC',
      eligibilityClass: 'tag-otc',
      specs: 'Removable palmar stay relieves wrist pain & tendonitis · Left/Right',
      icon: '🧤',
      retailValue: '$23.50',
      allowanceCost: 18.00,
      rxNeeded: 'No',
      dmeNeeded: 'No'
    },
    {
      sku: 'BRC-703',
      name: 'Lumbar Back Support Belt with Adjustable Double-Pull Straps',
      department: 'Braces & Supports',
      category: 'braces',
      categoryLabel: 'Braces & Orthopedics',
      pathway: 'OTC / DME',
      pathwayBadge: 'pathway-dme',
      eligibilityTag: '📋 May require Rx or prior authorization',
      eligibilityClass: 'tag-rx-auth',
      specs: 'Reinforced lumbar stays relieve lower back pain, sciatica & strain',
      icon: '🧍',
      retailValue: '$39.00',
      allowanceCost: 32.00,
      rxNeeded: 'Depends on Plan',
      dmeNeeded: 'Yes for DME'
    },

    // --- 8. MOBILITY PRODUCTS ---
    {
      sku: 'MOB-801',
      name: 'Heavy-Duty Adjustable Quad Walking Cane (4-Point Sturdy Base)',
      department: 'Mobility',
      category: 'mobility',
      categoryLabel: 'Mobility Products',
      pathway: 'DME / OTC',
      pathwayBadge: 'pathway-dme',
      eligibilityTag: '🩺 Covered under medical/DME benefit, not OTC allowance',
      eligibilityClass: 'tag-dme',
      specs: 'All-terrain non-skid rubber base with soft foam handle · Height 29"-38"',
      icon: '🦯',
      retailValue: '$34.99',
      allowanceCost: 28.00,
      rxNeeded: 'Yes for DME',
      dmeNeeded: 'Yes (CMS DMEPOS Benefit)'
    },
    {
      sku: 'MOB-802',
      name: 'Lightweight Folding Aluminum Rollator Walker with Seat & Brakes',
      department: 'Mobility',
      category: 'mobility',
      categoryLabel: 'Mobility Products',
      pathway: 'DME / Medical',
      pathwayBadge: 'pathway-dme',
      eligibilityTag: '🩺 Covered under medical/DME benefit, not OTC allowance',
      eligibilityClass: 'tag-dme',
      specs: '6" wheels, padded seat, storage pouch & adjustable handles (300 lb cap)',
      icon: '♿',
      retailValue: '$89.00',
      allowanceCost: 75.00,
      rxNeeded: 'Yes',
      dmeNeeded: 'Yes (CMS DMEPOS Benefit)'
    },

    // --- 9. HOME SAFETY ---
    {
      sku: 'SAF-901',
      name: 'Suction-Cup Bathroom Grab Bar Handle (12-Inch 2 Pack)',
      department: 'Home Safety',
      category: 'homesafety',
      categoryLabel: 'Home Safety & Fall Prevention',
      pathway: 'OTC / Supplemental',
      pathwayBadge: 'pathway-supplemental',
      eligibilityTag: '✓ Usually eligible OTC / Highmark SSBCI Covered',
      eligibilityClass: 'tag-otc',
      specs: 'Heavy-duty non-slip grip for shower & bathtub safety without drilling',
      icon: '🏠',
      retailValue: '$24.99',
      allowanceCost: 20.00,
      rxNeeded: 'No',
      dmeNeeded: 'No'
    },
    {
      sku: 'SAF-902',
      name: 'Non-Slip Bath & Shower Transfer Bench with Backrest & Arms',
      department: 'Home Safety',
      category: 'homesafety',
      categoryLabel: 'Home Safety & Fall Prevention',
      pathway: 'DME / Supplemental',
      pathwayBadge: 'pathway-dme',
      eligibilityTag: '📋 May require Rx or prior authorization',
      eligibilityClass: 'tag-rx-auth',
      specs: 'Suction cup rubber feet & drainage holes for safe tub transfers',
      icon: '🪑',
      retailValue: '$44.00',
      allowanceCost: 36.00,
      rxNeeded: 'Depends on Plan',
      dmeNeeded: 'Yes'
    },

    // --- 10. DIABETES PRODUCTS ---
    {
      sku: 'DIB-1001',
      name: 'Blood Glucose Test Strips & Lancets Starter Bundle (100 Strips)',
      department: 'Diabetes',
      category: 'diabetes',
      categoryLabel: 'Diabetes Products',
      pathway: 'DME / Rx / OTC',
      pathwayBadge: 'pathway-dme',
      eligibilityTag: '📋 Covered under Medicare Part B / DME / Rx benefit',
      eligibilityClass: 'tag-rx-auth',
      specs: 'No-coding blood glucose test strips + 100 sterile 30G lancets',
      icon: '🩸',
      retailValue: '$34.00',
      allowanceCost: 28.00,
      rxNeeded: 'Yes for Part B 100% Coverage',
      dmeNeeded: 'Yes'
    },

    // --- 11. SMOKING CESSATION (RI MEDICAID COVERED) ---
    {
      sku: 'SMK-1101',
      name: 'Nicotine Transdermal System 21 mg Patches (Step 1, 14 Count)',
      department: 'Smoking Cessation',
      category: 'smoking',
      categoryLabel: 'Smoking Cessation',
      pathway: 'Rx / OTC / Medicaid',
      pathwayBadge: 'pathway-rx',
      eligibilityTag: '✓ Covered under RI Medicaid 2026 Pharmacy Protocols when prescribed',
      eligibilityClass: 'tag-otc',
      specs: '24-hour therapeutic nicotine patch to aid quit-smoking journey',
      icon: '🚭',
      retailValue: '$39.00',
      allowanceCost: 0.00,
      rxNeeded: 'Yes for 100% Medicaid Coverage',
      dmeNeeded: 'No',
      riMedicaidNote: 'RI Medicaid 2026: Non-prescription nicotine-cessation supplies covered when ordered by practitioner.'
    },

    // --- 12. CHRONIC ILLNESS SSBCI SUPPORT ---
    {
      sku: 'SSB-1201',
      name: 'Fresh Farm Produce & Grocery Basket ($25 Plan Allowance)',
      department: 'SSBCI / Grocery',
      category: 'ssbci',
      categoryLabel: 'Chronic Illness SSBCI Support',
      pathway: 'Supplemental / SSBCI',
      pathwayBadge: 'pathway-supplemental',
      eligibilityTag: '🍎 Food-benefit eligible only (D-SNP / SSBCI)',
      eligibilityClass: 'tag-food-only',
      specs: 'Seasonal apples, oranges, leafy greens, carrots, potatoes & berries',
      icon: '🍎',
      retailValue: '$29.99',
      allowanceCost: 25.00,
      rxNeeded: 'No',
      dmeNeeded: 'No'
    },

    // --- 13. NON-PRODUCT SERVICES & SUPPORTS ---
    {
      sku: 'SRV-1301',
      name: 'Routine Dental Care & Comprehensive Exam Coverage',
      department: 'Services & Supports',
      category: 'services',
      categoryLabel: 'Services & Supports',
      pathway: 'Supplemental / Dental',
      pathwayBadge: 'pathway-supplemental',
      eligibilityTag: '⚠️ Eligible only with select plans ($0 Copay)',
      eligibilityClass: 'tag-select-plans',
      specs: 'In-network cleanings, X-rays, fillings & denture consultations',
      icon: '🏥',
      retailValue: 'Plan Covered',
      allowanceCost: 0.00,
      rxNeeded: 'No',
      dmeNeeded: 'No',
      isService: true
    },
    {
      sku: 'SRV-1302',
      name: 'Medical Appointment Transportation Rides (100% Covered)',
      department: 'Services & Supports',
      category: 'services',
      categoryLabel: 'Services & Supports',
      pathway: 'Supplemental / Transport',
      pathwayBadge: 'pathway-supplemental',
      eligibilityTag: '⚠️ Eligible only with select plans',
      eligibilityClass: 'tag-select-plans',
      specs: 'Round-trip Uber/Lyft/wheelchair van rides to doctors & pharmacies',
      icon: '🚗',
      retailValue: 'Plan Covered',
      allowanceCost: 0.00,
      rxNeeded: 'No',
      dmeNeeded: 'No',
      isService: true
    },
    {
      sku: 'SRV-1303',
      name: 'Post-Hospitalization Home Meal Delivery Program (14 Days)',
      department: 'Services & Supports',
      category: 'services',
      categoryLabel: 'Services & Supports',
      pathway: 'Supplemental / Post-Acute',
      pathwayBadge: 'pathway-rx',
      eligibilityTag: '📋 May require Rx or prior authorization',
      eligibilityClass: 'tag-rx-auth',
      specs: '28 nutritionally balanced meals delivered directly after hospital discharge',
      icon: '🍱',
      retailValue: 'Plan Covered',
      allowanceCost: 0.00,
      rxNeeded: 'Yes',
      dmeNeeded: 'No',
      isService: true
    },
    {
      sku: 'SRV-1304',
      name: 'SilverSneakers / Fitness Program Membership ($0 Copay)',
      department: 'Services & Supports',
      category: 'services',
      categoryLabel: 'Services & Supports',
      pathway: 'Supplemental / Fitness',
      pathwayBadge: 'pathway-supplemental',
      eligibilityTag: '⚠️ Eligible only with select plans',
      eligibilityClass: 'tag-select-plans',
      specs: 'Unlimited access to 15,000+ participating gyms, YMCAs & live classes',
      icon: '👟',
      retailValue: 'Plan Covered',
      allowanceCost: 0.00,
      rxNeeded: 'No',
      dmeNeeded: 'No',
      isService: true
    }
  ];

  let callSlip = [];

  function loadCallSlip() {
    try {
      const stored = JSON.parse(sessionStorage.getItem('bcnCallSlip') || '[]');
      if (Array.isArray(stored)) callSlip = stored;
    } catch {
      callSlip = [];
    }
  }

  function saveCallSlip() {
    try {
      sessionStorage.setItem('bcnCallSlip', JSON.stringify(callSlip));
    } catch {}
  }

  let activeCategory = 'all';
  let activePathwayFilter = 'all';
  let searchQuery = '';

  function renderProducts() {
    let filtered = PRODUCTS;

    if (activeCategory !== 'all') {
      filtered = filtered.filter((p) => p.category === activeCategory);
    }

    if (activePathwayFilter !== 'all') {
      filtered = filtered.filter((p) => {
        if (activePathwayFilter === 'otc') return p.pathway.includes('OTC');
        if (activePathwayFilter === 'rx') return p.pathway.includes('Rx');
        if (activePathwayFilter === 'dme') return p.pathway.includes('DME');
        if (activePathwayFilter === 'preventive') return p.pathway.includes('Preventive');
        if (activePathwayFilter === 'supplemental') return p.pathway.includes('Supplemental');
        return true;
      });
    }

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter((p) =>
        [p.sku, p.name, p.categoryLabel, p.department, p.specs, p.eligibilityTag, p.pathway].join(' ').toLowerCase().includes(q)
      );
    }

    const grid = $('#productGrid');
    const countLabel = $('#productCountLabel');

    if (countLabel) {
      countLabel.innerHTML = `Showing <strong>${filtered.length}</strong> items &amp; services across all benefit pathways`;
    }

    if (!grid) return;

    if (!filtered.length) {
      grid.innerHTML = `
        <div style="grid-column:1/-1;padding:48px 24px;text-align:center;background:#fff;border:1px solid var(--line);border-radius:14px">
          <strong style="font-size:18px;color:var(--green-dark)">No items match "${esc(searchQuery)}"</strong>
          <p style="color:var(--text-muted);margin:8px 0 0">Try searching for generic terms like "vitamin d", "knee brace", "folic acid", "nicotine", or "food".</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = filtered.map((p) => {
      const inSlip = callSlip.find((item) => item.sku === p.sku);
      const isService = p.isService;

      return `
        <article class="product-card" data-sku="${esc(p.sku)}">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:6px">
            <span class="product-sku-badge">${isService ? 'Service' : 'Item'} #${esc(p.sku)}</span>
            <span class="pathway-badge ${esc(p.pathwayBadge || 'pathway-otc')}">${esc(p.pathway)}</span>
          </div>

          <div class="product-image-container" aria-hidden="true">${p.icon}</div>
          <span class="product-category-tag">${esc(p.categoryLabel)}</span>
          <h3>${esc(p.name)}</h3>
          <p class="product-specs">${esc(p.specs)}</p>

          <!-- Mandatory Multi-Pathway Guidance Tag -->
          <div class="eligibility-tag ${esc(p.eligibilityClass || 'tag-otc')}">
            ${esc(p.eligibilityTag)}
          </div>

          ${p.riMedicaidNote ? `
            <div style="font-size:11px;color:#1e4b85;background:#eaf1f8;padding:4px 8px;border-radius:4px;margin-top:6px;line-height:1.3">
              🏛️ <strong>RI EOHHS 2026:</strong> ${esc(p.riMedicaidNote)}
            </div>
          ` : ''}

          <div class="product-pricing-box" style="margin-top:10px">
            <div class="product-cost-display">
              <span class="covered-zero-price">$0.00</span>
              <span class="retail-value">${esc(p.retailValue)}</span>
            </div>
          </div>

          <button type="button" class="add-to-slip-btn ${inSlip ? 'added' : ''}" data-add-sku="${esc(p.sku)}">
            ${inSlip ? `✓ In Call Slip (${inSlip.qty})` : (isService ? '+ Add Service to Request Slip' : '+ Add to Phone Order Slip')}
          </button>

          <button type="button" class="slip-secondary-btn" data-view-pathway="${esc(p.sku)}" style="margin-top:6px;color:var(--green-dark);border-color:#bce2d3">
            ℹ️ View Coverage &amp; PCP Approval Rules
          </button>
        </article>
      `;
    }).join('');

    $$('[data-add-sku]').forEach((btn) => {
      btn.addEventListener('click', () => addToCallSlip(btn.dataset.addSku));
    });

    $$('[data-view-pathway]').forEach((btn) => {
      btn.addEventListener('click', () => openPathwayModal(btn.dataset.viewPathway));
    });
  }

  function openPathwayModal(sku) {
    const p = PRODUCTS.find((item) => item.sku === sku);
    if (!p) return;

    let modal = $('#pathwayDetailModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'pathwayDetailModal';
      modal.className = 'order-form-modal-overlay';
      document.body.appendChild(modal);
    }

    modal.innerHTML = `
      <div class="order-form-modal-window" style="max-width:720px">
        <div class="order-form-header">
          <h2 style="font-family:Georgia,serif;font-size:20px;margin:0;color:var(--green-dark)">${p.icon} ${esc(p.name)}</h2>
          <button type="button" style="border:0;background:transparent;font-size:24px;cursor:pointer" id="closePathwayModalBtn">×</button>
        </div>
        <div class="order-form-body">
          <div class="eligibility-tag ${esc(p.eligibilityClass)}" style="font-size:13px;padding:6px 12px;margin-bottom:14px">
            ${esc(p.eligibilityTag)}
          </div>

          <p style="font-size:14px;line-height:1.5;color:#333;margin-bottom:16px">${esc(p.specs)}</p>

          <div class="policy-guidance-box">
            <strong style="font-size:14px;display:block;margin-bottom:6px">How Insurance Pays for This Item:</strong>
            <ul style="margin:0;padding-left:18px;line-height:1.6">
              <li><strong>Benefit Pathway:</strong> ${esc(p.pathway)}</li>
              <li><strong>Prescription Required:</strong> ${esc(p.rxNeeded || 'No')}</li>
              <li><strong>DME Supplier Required:</strong> ${esc(p.dmeNeeded || 'No')}</li>
              ${p.riMedicaidNote ? `<li><strong>RI Medicaid 2026 Protocol:</strong> ${esc(p.riMedicaidNote)}</li>` : ''}
              ${p.bcbsriNote ? `<li><strong>BCBSRI 2026 BlueCHiP Allowance:</strong> ${esc(p.bcbsriNote)}</li>` : ''}
            </ul>
          </div>

          ${p.dualPathwayInfo ? `
            <div style="background:#fff8e6;border:1px solid #f3d484;padding:12px;border-radius:8px;font-size:13px;line-height:1.5;margin-bottom:16px">
              <strong>Dual Coverage Pathways Available:</strong><br/>
              ${esc(p.dualPathwayInfo).replace(/\n/g, '<br/>')}
            </div>
          ` : ''}

          <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:20px">
            <a href="/find-care/doctors/" class="hero-form-btn" style="background:var(--green-dark);color:#fff;text-decoration:none">
              🩺 Ask My Doctor / Select PCP
            </a>
            <button type="button" class="hero-form-btn" id="modalAddSlipBtn">
              + Add to Phone Order Slip
            </button>
          </div>
        </div>
      </div>
    `;

    modal.style.display = 'grid';

    $('#closePathwayModalBtn')?.addEventListener('click', () => {
      modal.style.display = 'none';
    });

    $('#modalAddSlipBtn')?.addEventListener('click', () => {
      addToCallSlip(p.sku);
      modal.style.display = 'none';
    });
  }

  function addToCallSlip(sku) {
    const product = PRODUCTS.find((p) => p.sku === sku);
    if (!product) return;

    const existing = callSlip.find((item) => item.sku === sku);
    if (existing) {
      existing.qty += 1;
    } else {
      callSlip.push({
        sku: product.sku,
        name: product.name,
        allowanceCost: typeof product.allowanceCost === 'number' ? product.allowanceCost : 0,
        icon: product.icon,
        qty: 1
      });
    }

    saveCallSlip();
    renderProducts();
    renderCallSlip();
  }

  function updateQty(sku, delta) {
    const item = callSlip.find((i) => i.sku === sku);
    if (!item) return;

    item.qty += delta;
    if (item.qty <= 0) {
      callSlip = callSlip.filter((i) => i.sku !== sku);
    }

    saveCallSlip();
    renderProducts();
    renderCallSlip();
  }

  function renderCallSlip() {
    const container = $('#callSlipContainer');
    const badge = $('#slipCountBadge');

    const totalCount = callSlip.reduce((sum, i) => sum + i.qty, 0);
    const totalAllowance = callSlip.reduce((sum, i) => sum + (i.allowanceCost * i.qty), 0);

    if (badge) badge.textContent = totalCount;

    if (!container) return;

    if (!callSlip.length) {
      container.innerHTML = `
        <div style="padding:16px 0;text-align:center;color:#bdd2ca">
          <p style="font-size:14px;margin:0 0 4px">Your phone order slip is empty.</p>
          <small>Click <strong>"+ Add to Phone Order Slip"</strong> on items you want to order over the phone.</small>
        </div>
      `;
      return;
    }

    container.innerHTML = `
      <ul class="slip-items-list">
        ${callSlip.map((item) => `
          <li class="slip-item-row">
            <div class="slip-item-meta">
              <small>Item #${esc(item.sku)}</small>
              <strong>${item.icon} ${esc(item.name)}</strong>
              <span style="font-size:11px;color:#cbe0d9">$0.00 with card ($${(item.allowanceCost * item.qty).toFixed(2)} allowance)</span>
            </div>
            <div class="slip-item-actions">
              <button type="button" class="slip-qty-btn" data-qty-dec="${esc(item.sku)}" aria-label="Decrease quantity">−</button>
              <strong style="min-width:18px;text-align:center">${item.qty}</strong>
              <button type="button" class="slip-qty-btn" data-qty-inc="${esc(item.sku)}" aria-label="Increase quantity">+</button>
            </div>
          </li>
        `).join('')}
      </ul>

      <div class="slip-totals-box">
        <div class="slip-totals-row">
          <span>Items in Call Slip:</span>
          <strong>${totalCount} items</strong>
        </div>
        <div class="slip-totals-row">
          <span>Total Benefit Value:</span>
          <span>$${totalAllowance.toFixed(2)}</span>
        </div>
        <div class="slip-totals-row final">
          <span>Your Out-of-Pocket:</span>
          <span style="color:#ffd982">$0.00 (Covered)</span>
        </div>
      </div>

      <div class="phone-instructions-box">
        <strong>📞 How to Order by Phone Call:</strong>
        1. Call the toll-free OTC or Member Services phone number on the back of your insurance card.<br/>
        2. Have your Member ID number ready.<br/>
        3. Quote the <strong>Item Numbers</strong> (e.g. <code>${callSlip.map((x) => x.sku).join(', ')}</code>) to the representative.<br/>
        4. Confirm your home delivery address. Shipping is 100% free.
      </div>

      <button type="button" class="slip-action-btn" id="openPrintFormBtn">
        <span>📄 View &amp; Print Order Form</span>
      </button>

      <button type="button" class="slip-secondary-btn" id="copyScriptBtn">
        📋 Copy Phone Order Script
      </button>

      <button type="button" class="slip-secondary-btn" id="clearSlipBtn" style="margin-top:6px;border-color:transparent;color:#f9b5ab">
        ✕ Clear Call Slip
      </button>
    `;

    $$('[data-qty-inc]').forEach((b) => b.addEventListener('click', () => updateQty(b.dataset.qtyInc, 1)));
    $$('[data-qty-dec]').forEach((b) => b.addEventListener('click', () => updateQty(b.dataset.qtyDec, -1)));

    $('#clearSlipBtn')?.addEventListener('click', () => {
      callSlip = [];
      saveCallSlip();
      renderProducts();
      renderCallSlip();
    });

    $('#copyScriptBtn')?.addEventListener('click', copyPhoneScript);
    $('#openPrintFormBtn')?.addEventListener('click', openPrintableOrderForm);
  }

  function copyPhoneScript() {
    const lines = [
      'HEALTH PLAN OTC PHONE ORDER CALL SCRIPT',
      '----------------------------------------',
      'Representative: "How can I help you today?"',
      'Member: "Hello, I would like to place an order using my health plan OTC allowance."',
      '',
      'ITEMS TO READ TO REPRESENTATIVE:',
      ...callSlip.map((item, idx) => `${idx + 1}. Item #${item.sku} - ${item.name} (Quantity: ${item.qty})`),
      '',
      'CONFIRMATION:',
      '- Please deliver to my address on file.',
      '- Please confirm the total deduction from my OTC allowance balance ($0.00 copay).'
    ];

    navigator.clipboard.writeText(lines.join('\n')).then(() => {
      alert('✓ Phone order script copied to clipboard! You can paste it into your notes or read it directly during your phone call.');
    }).catch(() => {
      alert('Could not copy automatically. You can read the item numbers directly from your call slip.');
    });
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
        <div class="order-form-header">
          <h2 style="font-family:Georgia,serif;font-size:22px;margin:0;color:var(--green-dark)">Health Benefit Card OTC &amp; DME Order Form</h2>
          <button type="button" style="border:0;background:transparent;font-size:24px;cursor:pointer" id="closeFormModalBtn">×</button>
        </div>
        <div class="order-form-body">
          <div style="display:flex;justify-content:flex-end;margin-bottom:14px">
            <button type="button" class="hero-form-btn" id="printSheetAction">
              🖨️ Print / Save as PDF
            </button>
          </div>

          <div class="form-print-sheet" id="printArea">
            <div class="form-sheet-title">
              <h2>HEALTH PLAN OVER-THE-COUNTER (OTC) &amp; DME ORDER FORM</h2>
              <p style="margin:0;font-size:13px;color:#444">Official Catalog &amp; Mail/Telephone Order Document · Program Year 2026</p>
            </div>

            <div class="member-info-grid">
              <div class="info-blank-field">
                <label>1. Cardholder / Member Full Name:</label>
                <div class="info-blank-line">________________________________________________</div>
              </div>
              <div class="info-blank-field">
                <label>2. Member ID # (from front of card):</label>
                <div class="info-blank-line">________________________________________________</div>
              </div>
              <div class="info-blank-field">
                <label>3. Date of Birth (MM/DD/YYYY):</label>
                <div class="info-blank-line">____ / ____ / ________</div>
              </div>
              <div class="info-blank-field">
                <label>4. Daytime Phone Number:</label>
                <div class="info-blank-line">(___ ___) ______ - _________</div>
              </div>
              <div class="info-blank-field" style="grid-column:1/-1">
                <label>5. Shipping Delivery Street Address (No P.O. Boxes):</label>
                <div class="info-blank-line">________________________________________________________________________________</div>
              </div>
              <div class="info-blank-field">
                <label>6. City, State, ZIP Code:</label>
                <div class="info-blank-line">__________________________________, _______  __________</div>
              </div>
              <div class="info-blank-field">
                <label>7. Health Plan Name:</label>
                <div class="info-blank-line">Benefit Card Navigator / Participating Health Plan</div>
              </div>
            </div>

            <h3 style="font-size:15px;margin:16px 0 8px;text-transform:uppercase;letter-spacing:0.04em">
              Selected Items for This Order:
            </h3>

            <table class="catalog-order-table">
              <thead>
                <tr>
                  <th style="width:90px">Item #</th>
                  <th>Product Description &amp; Specifications</th>
                  <th style="width:110px">Category</th>
                  <th style="width:80px">Unit Value</th>
                  <th style="width:60px;text-align:center">Qty</th>
                  <th style="width:90px;text-align:right">Copay</th>
                </tr>
              </thead>
              <tbody>
                ${(callSlip.length ? callSlip : PRODUCTS.slice(0, 10)).map((item) => `
                  <tr>
                    <td style="font-family:ui-monospace,monospace;font-weight:700">${item.sku}</td>
                    <td><strong>${item.name}</strong></td>
                    <td>${item.categoryLabel || 'Health / OTC'}</td>
                    <td>$${(item.allowanceCost || 12).toFixed(2)}</td>
                    <td style="text-align:center;font-weight:800">${item.qty || 1}</td>
                    <td style="text-align:right;font-weight:700;color:#133e33">$0.00</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>

            <div style="background:#f6f6f6;border:1px solid #ccc;padding:12px;margin-top:16px;font-size:12px;line-height:1.5">
              <strong>Order Submission Options:</strong><br/>
              <strong>Option A (Fastest — Telephone):</strong> Call the toll-free OTC or Member Services phone number on the back of your insurance card. Read the <strong>Item Numbers</strong> listed in the table above to the customer care specialist.<br/>
              <strong>Option B (Mail):</strong> Mail this completed form to: <em>Benefit Card Processing Center, P.O. Box 2026, Providence, RI</em>.<br/>
              <em>Allowance Rules: Items are covered under your plan's supplemental OTC or wellness benefit allowance. Out-of-pocket cost is $0.00 when within your benefit balance. Delivery takes 3 to 5 business days with no shipping charge.</em>
            </div>

            <div style="margin-top:20px;display:flex;justify-content:space-between;font-size:12px;border-top:1px solid #888;padding-top:10px">
              <span>Date Generated: ${todayStr}</span>
              <span>Benefit Card Navigator Marketplace Catalog v2026</span>
            </div>
          </div>
        </div>
      </div>
    `;

    modal.style.display = 'grid';

    $('#closeFormModalBtn')?.addEventListener('click', () => {
      modal.style.display = 'none';
    });

    $('#printSheetAction')?.addEventListener('click', () => {
      window.print();
    });
  }

  function init() {
    loadCallSlip();

    // Search input
    $('#marketSearchInput')?.addEventListener('input', (e) => {
      searchQuery = e.target.value.trim();
      renderProducts();
    });

    // Category pills
    $$('.cat-pill').forEach((pill) => {
      pill.addEventListener('click', () => {
        $$('.cat-pill').forEach((p) => p.classList.remove('active'));
        pill.classList.add('active');
        activeCategory = pill.dataset.category || 'all';

        const radio = $(`input[name="sideCat"][value="${activeCategory}"]`);
        if (radio) radio.checked = true;

        renderProducts();
      });
    });

    // Sidebar Category Radios
    $$('input[name="sideCat"]').forEach((radio) => {
      radio.addEventListener('change', () => {
        activeCategory = radio.value;
        $$('.cat-pill').forEach((p) => {
          p.classList.toggle('active', p.dataset.category === activeCategory);
        });
        renderProducts();
      });
    });

    // Benefit Pathway Radios
    $$('input[name="sidePathway"]').forEach((radio) => {
      radio.addEventListener('change', () => {
        activePathwayFilter = radio.value;
        renderProducts();
      });
    });

    // Trigger open form from hero
    $('#heroViewFormBtn')?.addEventListener('click', openPrintableOrderForm);

    renderProducts();
    renderCallSlip();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
"""

with open('dist/marketplace/marketplace.js', 'w') as f:
    f.write(js_code)

print("Successfully written dist/marketplace/marketplace.js")
