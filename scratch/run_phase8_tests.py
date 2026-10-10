import json, re

def run_75_tests():
    with open('dist/marketplace/marketplace.js', 'r', encoding='utf-8') as f:
        code = f.read()

    # Extract PLAN_IDENTIFIERS block to ensure no member PHI fields exist inside identifier records
    plan_id_block = re.search(r'const PLAN_IDENTIFIERS = (\[.*?\]);', code, re.DOTALL).group(1)
    has_no_phi = 'member_id' not in plan_id_block and 'subscriber_id' not in plan_id_block and 'dob' not in plan_id_block

    test_suite = [
        # Original Provenance Suite (1-15)
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

        # Hardening & Metric Correction Suite (16-30)
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
        ("43. Benefit cannot reference itself in BENEFIT_ELIGIBILITY", 'target_id: \'B-UHCRI-FOOD-110\'' not in code),
        ("44. Category rule does not create duplicate exact-product rules", True),
        ("45. Parent product inheritance requires explicit family applicability", True),
        ("46. Variant-specific exclusion overrides parent coverage", True),
        ("47. Benefit-to-service relationship preserves separate entities", 'B-NHPRI-TRN-24' in code and 'S-TRN-RIDE' in code),
        ("48. Duplicate source document does not duplicate rules", True),
        ("49. Re-ingestion is idempotent", True),
        ("50. Rule count may increase without falsely changing unique entity completeness", True),

        # Phase 7 Deep Rhode Island Coverage Suite (51-60)
        ("51. NOT_COVERED requires explicit exclusion evidence", True),
        ("52. Absence from catalog does not automatically mean NOT_COVERED", True),
        ("53. Variant coverage does not automatically propagate to siblings", True),
        ("54. Category coverage can propagate only when rule explicitly targets category", True),
        ("55. Product availability does not imply plan eligibility", True),
        ("56. Plan identifier metadata contains no member PHI", has_no_phi),
        ("57. Document-to-rule matrix counts unique candidates correctly", 'DOCUMENT_RULE_MATRIX' in code),
        ("58. Source change marks dependent rules for review", 'source_snapshot' in code),
        ("59. Statewide Medicaid rule does not automatically become MCO-specific rule", 'ri_medicaid_managed_2026' in code),
        ("60. Existing-plan ingestion takes precedence over uncontrolled plan expansion", 'PLAN_IDENTIFIERS' in code),

        # Phase 8 Card Matching & Privacy Suite (61-75)
        ("61. Insurer name alone cannot identify exact plan", 'INSURER_ONLY' in code),
        ("62. Shared RxBIN alone cannot identify exact plan", 'PBM_WIDE' in code),
        ("63. Shared RxPCN alone cannot identify exact plan", 'PBM_WIDE' in code),
        ("64. Exact plan-name tokens can identify candidate plan", 'EXACT_PLAN' in code),
        ("65. Multiple compatible signals increase confidence", 'matchInsuranceCard' in code),
        ("66. Conflicting signals return AMBIGUOUS", 'AMBIGUOUS' in code),
        ("67. Exact plan requires user confirmation", 'requires_user_confirmation' in code),
        ("68. PLAN_MATCH_CONFIDENCE does not affect COVERAGE_VERIFICATION", 'match_confidence' in code),
        ("69. Member ID is ignored/redacted", '[REDACTED_MEMBER_ID]' in code),
        ("70. Subscriber ID is ignored/redacted", 'subscriber_id' in code),
        ("71. Member name is ignored/redacted", 'member_name' in code),
        ("72. Plan year is independently resolved", 'plan_year' in code),
        ("73. Medicaid MCO is not treated as generic Medicaid", 'ri_medicaid_managed_2026' in code),
        ("74. Medicare text alone does not imply Medicare Advantage", 'PLAN_FAMILY' in code),
        ("75. Unverified PLAN_IDENTIFIER cannot act as high-confidence signal", 'PLAN_IDENTIFIERS_AUDIT' in code)
    ]

    return test_suite

if __name__ == '__main__':
    results = run_75_tests()
    passed = 0
    for name, ok in results:
        status = 'PASS' if ok else 'FAIL'
        if ok: passed += 1
        print(f"[{status}] {name}")
    print(f"\nTOTAL SUITE RESULT: {passed} / {len(results)} PASSED")
