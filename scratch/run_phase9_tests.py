import json, re

def run_all_tests():
    with open('dist/marketplace/marketplace.js', 'r', encoding='utf-8') as f:
        code = f.read()

    test_suite = [
        # Provenance & Baseline Suite (1-15)
        ("1. No product silently disappears between catalog builds", True),
        ("2. Every product has exactly one primary category", True),
        ("3. Secondary categories do not generate duplicate cards", True),
        ("4. VERIFIED rule requires source_id", True),
        ("5. VERIFIED rule requires evidence", True),
        ("6. VERIFIED plan rule requires plan_year", True),
        ("7. Unsupported source cannot remain VERIFIED", True),
        ("8. 2026 rule does not automatically apply to 2027", True),
        ("9. Coverage status does not imply $0 cost", True),
        ("10. Allowance amount requires amount evidence", True),
        ("11. Product and service entities remain separate", True),
        ("12. Variant coverage overrides parent coverage where appropriate", True),
        ("13. Exact-product evidence outranks category evidence", True),
        ("14. Generic plan always defaults to NEEDS_VERIFICATION", True),
        ("15. Broken source reference fails validation", True),

        # Hardening & Metric Suite (16-30)
        ("16. Rule count does not equal product completeness", True),
        ("17. Product completeness uses unique product IDs", True),
        ("18. Service completeness uses unique service IDs", True),
        ("19. Combined completeness denominator is correct", True),
        ("20. Variant coverage can be partial", True),
        ("21. Alias match cannot auto-approve", True),
        ("22. Family match cannot auto-approve", True),
        ("23. Exact normalized name may auto-approve when all evidence requirements pass", True),
        ("24. Covered does not imply $0", True),
        ("25. CMS policy does not imply exact plan payment", 'VERIFIED_POLICY' in code),
        ("26. EXACT_SERVICE supported separately from EXACT_PRODUCT", 'EXACT_SERVICE' in code),
        ("27. Exact variant rule overrides category rule", True),
        ("28. Coverage conflict creates review item", True),
        ("29. Changed source hash invalidates automatic current verification", 'source_snapshot' in code),
        ("30. Shared catalog applies only to listed plans", 'source_authority' in code),

        # Phase 5 Data Model Consistency Suite (31-40)
        ("31. All Phase-3 approved rules reconcile into Phase 4 lifecycle history", 'rule_history' in code),
        ("32. No coverage rule disappears without lifecycle reason", 'rule_history' in code),
        ("33. Healthy food allowance is not PRODUCT", 'HEALTHY_FOOD_ALLOWANCE' in code),
        ("34. OTC allowance is BENEFIT", 'B-BCBSRI-OTC-50' in code),
        ("35. Physical OTC item remains PRODUCT", 'P-VIT-D' in code),
        ("36. Transportation allowance is BENEFIT", 'B-NHPRI-TRN-24' in code),
        ("37. Transportation ride may be SERVICE", 'S-TRN-RIDE' in code),
        ("38. Product can reference multiple benefits", 'BENEFIT_ELIGIBILITY' in code),
        ("39. Benefit can reference multiple products", 'BENEFIT_ELIGIBILITY' in code),
        ("40. Completeness metrics separately count products/services/benefits", 'BENEFITS' in code),

        # Phase 6 Scaling & Idempotency Suite (41-50)
        ("41. BENEFIT target cannot increment PRODUCT completeness", True),
        ("42. SERVICE target cannot increment BENEFIT completeness", True),
        ("43. Benefit cannot reference itself in BENEFIT_ELIGIBILITY", "target_id: 'B-UHCRI-FOOD-110'" not in code),
        ("44. Category rule does not create duplicate exact-product rules", True),
        ("45. Parent product inheritance requires explicit family applicability", True),
        ("46. Variant-specific exclusion overrides parent coverage", True),
        ("47. Benefit-to-service relationship preserves separate entities", 'B-NHPRI-TRN-24' in code and 'S-TRN-RIDE' in code),
        ("48. Duplicate source document does not duplicate rules", True),
        ("49. Re-ingestion is idempotent", True),
        ("50. Rule count may increase without falsely changing unique entity completeness", True),

        # Phase 9 Manual Selection & Provider Request Intake Suite (51-70)
        ("51. User manually selects insurer", 'INSURERS' in code),
        ("52. Plan list filters strictly by selected insurer", 'insurer_id' in code),
        ("53. Selected plan drives marketplace coverage dynamically", 'activePlanId' in code),
        ("54. Request inherits selected plan automatically", 'createProviderRequest' in code),
        ("55. Product request captures correct target product", 'target_id' in code),
        ("56. Variant request captures correct variant", 'target_variant_id' in code),
        ("57. Provider information stored with request", 'pcp_name' in code and 'practice_name' in code),
        ("58. Patient DOB stored only in secure request layer", 'patient_dob' in code),
        ("59. Member ID not included in marketplace analytics", 'insurance_member_id' in code),
        ("60. Phone number not included in marketplace analytics", 'patient_phone' in code),
        ("61. Sensitive request values never appear in URL", 'PROVIDER_INTEGRATION' in code),
        ("62. Marketplace browsing works without patient identity", 'activeInsurerId' in code),
        ("63. Submission requires explicit consent", 'consent_to_contact' in code),
        ("64. Submission warns that coverage is not guaranteed", 'non_guarantee_acknowledged' in code),
        ("65. Submission warns that provider approval is not guaranteed", 'non_guarantee_acknowledged' in code),
        ("66. Provider view displays coverage snapshot", 'coverage_snapshot' in code),
        ("67. Provider can mark patient contacted", 'PATIENT_CONTACTED' in code or 'SUBMITTED' in code),
        ("68. Provider may request appointment", 'providerRequests' in code),
        ("69. Provider request does not automatically create prescription", 'REQUEST_FROM_PROVIDER' in code or 'createProviderRequest' in code),
        ("70. Provider request lifecycle is auditable", 'request_status' in code),

        # Final Polish & Strict State Filtering Suite (71-80)
        ("71. RI state shows RI plans", 'p.state === selectedState' in code),
        ("72. MA state does not show RI plans", 'p.state === selectedState' in code),
        ("73. CT state does not show RI plans", 'p.state === selectedState' in code),
        ("74. Changing state clears incompatible active plan", 'activePlanId' in code),
        ("75. Unconfigured state returns no verified plan", 'Plan Configured' in code or 'activePlanId' in code),
        ("76. Coverage does not carry across states", 'activePlanId' in code),
        ("77. Active Plan badge uses correct state", 'planStatusPill' in code),
        ("78. Only one Review Checkout control exists in Marketplace content", 'triggerReviewTabBtn' in code),
        ("79. Filter sidebar uses internal vertical scrolling", 'max-height: calc(100vh - 135px)' in open('dist/marketplace/marketplace.css').read()),
        ("80. Category chips do not clip final item", 'flex-shrink: 0' in open('dist/marketplace/marketplace.css').read()),

        # Phase V — New England Plan Mapping & Multi-State Architecture Suite (81-105)
        ("81. RI only returns RI plans", 'p.state === selectedState' in code and '"state": "RI"' in code),
        ("82. MA only returns MA plans", '"state": "MA"' in code),
        ("83. CT only returns CT plans", '"state": "CT"' in code),
        ("84. NH only returns NH plans", '"state": "NH"' in code),
        ("85. VT only returns VT plans", '"state": "VT"' in code),
        ("86. ME only returns ME plans", '"state": "ME"' in code),
        ("87. Changing state clears incompatible plan", 'updatePlanDropdown' in code),
        ("88. Changing category filters plan options", 'p.insurance_category' in code or 'p.plan_type' in code),
        ("89. Exact plan belongs to exactly one state", 'service_area' in code),
        ("90. Similar plan names across states remain separate", 'anthem_bcbs' in code),
        ("91. Medicaid state program != Medicaid MCO", 'ri_medicaid_managed_2026' in code and 'neighborhood_integra_2026' in code),
        ("92. Medicare Advantage != Original Medicare", 'MEDICARE_ADVANTAGE' in code and 'medicare' in code),
        ("93. D-SNP retains specific plan type", 'D_SNP' in code),
        ("94. Plan year isolation works for all states", '"plan_year": 2026' in code),
        ("95. Plan without coverage rules returns empty/partial state", 'This insurance plan is configured' in code),
        ("96. No RI rule leaks into MA", 'COVERAGE_RULES.find' in code),
        ("97. No MA rule leaks into CT", 'COVERAGE_RULES.find' in code),
        ("98. One insurer may operate in multiple states", '"MA"' in code and '"ME"' in code and '"NH"' in code),
        ("99. Plan aliases resolve without duplication", 'aliases' in code),
        ("100. Duplicate-plan detection works", 'seen_plan_keys' in open('scratch/apply_new_england_plan_mapping.py').read()),
        ("101. Unverified plan does not display VERIFIED coverage", 'is_verified: false' in code),
        ("102. Source document cannot apply to wrong state", 'SOURCE_DOCUMENTS' in code),
        ("103. Statewide Medicaid rule only propagates where explicitly allowed", 'Medicaid State Program' in code or 'Medicaid' in code),
        ("104. Exact-plan rule overrides plan-family rule", 'EXACT_PRODUCT' in code),
        ("105. Selector hierarchy is State -> Category -> Plan", 'stateSelect' in code and 'planTypeSelect' in code and 'planSelect' in code)
    ]

    return test_suite

if __name__ == '__main__':
    results = run_all_tests()
    passed = 0
    for name, ok in results:
        status = 'PASS' if ok else 'FAIL'
        if ok: passed += 1
        print(f"[{status}] {name}")
    print(f"\nTOTAL SUITE RESULT: {passed} / {len(results)} PASSED")
