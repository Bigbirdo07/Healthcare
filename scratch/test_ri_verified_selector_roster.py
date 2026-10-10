import json
import re
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JS_PATHS = [ROOT / "dist" / "marketplace" / "marketplace.js", ROOT / "dist" / "app.js"]


def official_plans(code: str):
    match = re.search(
        r"const RI_OFFICIAL_SELECTOR_PLANS = (\[.*?\]);\n\n  function getProductionSelectorPlans",
        code,
        re.S,
    )
    if not match:
        raise AssertionError("official RI roster block missing")
    return json.loads(match.group(1))


class RhodeIslandVerifiedSelectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.codes = [p.read_text(encoding="utf-8") for p in JS_PATHS]
        cls.code = cls.codes[0]
        cls.plans = official_plans(cls.code)

    def test_runtime_bundles_are_identical(self):
        self.assertEqual(self.codes[0], self.codes[1])

    def test_official_roster_has_73_unique_plans(self):
        self.assertEqual(len(self.plans), 73)
        self.assertEqual(len({p["id"] for p in self.plans}), 73)

    def test_official_market_distribution(self):
        self.assertEqual(
            Counter(p["market_segment"] for p in self.plans),
            {
                "MEDICARE_ADVANTAGE": 23,
                "MEDICARE_PART_D": 11,
                "INDIVIDUAL_ACA": 21,
                "SMALL_GROUP": 18,
            },
        )

    def test_historical_ri_rows_are_quarantined_from_selector(self):
        self.assertIn("...PLANS.filter((plan) => plan.state !== 'RI')", self.code)
        self.assertIn("...RI_OFFICIAL_SELECTOR_PLANS", self.code)
        self.assertNotIn("CMS:RI:H5987:001:000:2026\"", json.dumps(self.plans))

    def test_core_uses_official_cms_identity(self):
        core = next(p for p in self.plans if p["official_plan_name"] == "BlueCHiP for Medicare Core (HMO)")
        self.assertEqual(core["id"], "CMS:RI:H4152:004:000:2026")
        self.assertEqual(core["contract_id"], "H4152")
        self.assertEqual(core["plan_id"], "004")

    def test_all_new_plans_are_identity_verified_and_benefits_verified(self):
        for plan in self.plans:
            self.assertEqual(plan["plan_identity_status"], "OFFICIAL_2026_ROSTER_VERIFIED")
            self.assertEqual(plan["coverage_verification_status"], "VERIFIED_AUTHENTIC_2026_EOC")
            self.assertFalse(plan["benefits_under_review"])
            self.assertTrue(plan["is_verified"])

    def test_unverified_status_copy_is_visible(self):
        self.assertIn("Official 2026 Plan · Benefits under review", self.code)
        self.assertIn("Coverage details are not yet verified for this plan", self.code)

    def test_selector_uses_overlay_and_url_handoff_accepts_it(self):
        self.assertIn("const prodPlans = getProductionSelectorPlans().filter", self.code)
        self.assertIn("getProductionSelectorPlans().some(p => p.id === paramPlanId)", self.code)
        self.assertIn("function getMarketplacePlan(planId)", self.code)

    def test_dsnp_remains_an_insurance_card_plan(self):
        self.assertIn("return cat.includes('MEDICAID') || cat.includes('CHIP');", self.code)
        dsnp = [p for p in self.plans if "D-SNP" in p["plan_type"]]
        self.assertTrue(dsnp)
        self.assertTrue(all(p["insurance_category"] == "Medicare Advantage" for p in dsnp))

    def test_no_database_or_coverage_rule_generation(self):
        generator = (ROOT / "scratch" / "apply_ri_verified_selector_roster.py").read_text(encoding="utf-8")
        self.assertNotIn("INSERT INTO", generator.upper())
        self.assertNotIn("UPDATE COVERAGE_RULES", generator.upper())
        self.assertNotIn("DELETE FROM", generator.upper())


if __name__ == "__main__":
    unittest.main()
