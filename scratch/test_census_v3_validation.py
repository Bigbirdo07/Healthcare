import csv
import json
import unittest

class TestCensusV3Validation(unittest.TestCase):
    def setUp(self):
        self.census_records = []
        with open('NEW_ENGLAND_2026_PLAN_CENSUS_V3.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.census_records.append(row)

    def test_unique_canonical_plan_keys(self):
        keys = [r["canonical_plan_key"] for r in self.census_records]
        self.assertEqual(len(keys), len(set(keys)), "Found duplicate canonical_plan_key in Census V3!")

    def test_medicare_advantage_master_count(self):
        ma_plans = [r for r in self.census_records if r["market_segment"] == "MEDICARE_ADVANTAGE"]
        self.assertEqual(len(ma_plans), 203, f"Expected exactly 203 Medicare Advantage plans, got {len(ma_plans)}")

    def test_standalone_part_d_master_count(self):
        pdp_plans = [r for r in self.census_records if r["market_segment"] == "MEDICARE_PART_D"]
        self.assertEqual(len(pdp_plans), 79, f"Expected exactly 79 standalone Part D plans, got {len(pdp_plans)}")

    def test_medicare_combined_denominator(self):
        medicare = [r for r in self.census_records if r["market_segment"] in ["MEDICARE_ADVANTAGE", "MEDICARE_PART_D"]]
        self.assertTrue(len(medicare) >= 282, f"Expected Medicare denominator >= 282, got {len(medicare)}")

    def test_nh_ma_cms_reconciliation(self):
        nh_ma = [r for r in self.census_records if r["state"] == "NH" and r["market_segment"] == "MEDICARE_ADVANTAGE"]
        self.assertEqual(len(nh_ma), 19, f"Expected 19 official MA plans for NH, got {len(nh_ma)}")
        missing_nh_ma = [r for r in nh_ma if r["match_status"] == "MISSING"]
        self.assertEqual(len(missing_nh_ma), 16, f"Expected exactly 16 missing MA plans for NH, got {len(missing_nh_ma)}")

    def test_nh_pdp_cms_reconciliation(self):
        nh_pdp = [r for r in self.census_records if r["state"] == "NH" and r["market_segment"] == "MEDICARE_PART_D"]
        self.assertEqual(len(nh_pdp), 9, f"Expected 9 official PDP plans for NH, got {len(nh_pdp)}")

    def test_mathematical_equations_hold(self):
        total = len(self.census_records)
        matched = len([r for r in self.census_records if r["match_status"] in ["FOUND_EXACT", "FOUND_VALID_ALIAS"]])
        missing = len([r for r in self.census_records if r["match_status"] == "MISSING"])
        self.assertEqual(matched + missing, total, f"matched ({matched}) + missing ({missing}) != total ({total})")
        
        calc_rate = round((matched / total * 100), 1)
        self.assertTrue(calc_rate > 0 and calc_rate < 100, f"Match rate ({calc_rate}%) must be an honest fraction!")

    def test_milestone_completeness_remains_false(self):
        missing = len([r for r in self.census_records if r["match_status"] == "MISSING"])
        is_complete = (missing == 0)
        self.assertFalse(is_complete, "NEW_ENGLAND_PUBLIC_PLAN_CENSUS_COMPLETE must be FALSE while missing plans remain!")

    def test_non_enumerable_segments_excluded(self):
        segments = set([r["market_segment"] for r in self.census_records])
        excluded = ["EMPLOYER_SELF_FUNDED", "EMPLOYER_FULLY_INSURED", "STUDENT_HEALTH", "FEDERAL_EMPLOYEE"]
        for exc in excluded:
            self.assertNotIn(exc, segments, f"Segment {exc} should be excluded from exact plan census denominator!")

if __name__ == '__main__':
    unittest.main()
