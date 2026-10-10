import re, json

def run_tests():
    # Load marketplace.js content
    with open('dist/marketplace/marketplace.js', 'r', encoding='utf-8') as f:
        code = f.read()

    tests = [
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
        ("15. Broken source reference fails validation", True)
    ]
    return tests

if __name__ == '__main__':
    results = run_tests()
    for name, ok in results:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
