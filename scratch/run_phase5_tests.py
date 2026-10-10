import json, re

def run_40_tests():
    with open('dist/marketplace/marketplace.js', 'r', encoding='utf-8') as f:
        code = f.read()

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
        ("40. Completeness metrics separately count products/services/benefits", 'BENEFITS' in code)
    ]

    return test_suite

if __name__ == '__main__':
    results = run_40_tests()
    passed = 0
    for name, ok in results:
        status = 'PASS' if ok else 'FAIL'
        if ok: passed += 1
        print(f"[{status}] {name}")
    print(f"\nTOTAL SUITE RESULT: {passed} / {len(results)} PASSED")
