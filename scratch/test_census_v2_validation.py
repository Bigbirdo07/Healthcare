import csv
import json
import unittest

class TestCensusV2Validation(unittest.TestCase):
    def setUp(self):
        self.census_records = []
        with open('NEW_ENGLAND_2026_PLAN_CENSUS_V2.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.census_records.append(row)

    def test_nh_ma_cms_count_reconciliation(self):
        nh_ma = [r for r in self.census_records if r["state"] == "NH" and r["market_segment"] == "MEDICARE_ADVANTAGE"]
        self.assertEqual(len(nh_ma), 19, f"Expected 19 official CMS MA plans for NH, got {len(nh_ma)}")

    def test_nh_pdp_cms_count_reconciliation(self):
        nh_pdp = [r for r in self.census_records if r["state"] == "NH" and r["market_segment"] == "MEDICARE_PART_D"]
        self.assertEqual(len(nh_pdp), 9, f"Expected 9 official CMS PDP plans for NH, got {len(nh_pdp)}")

    def test_independent_contract_plan_segment_enumeration(self):
        ma_pdp_plans = [r for r in self.census_records if r["market_segment"] in ["MEDICARE_ADVANTAGE", "MEDICARE_PART_D"]]
        keys = [f"{r['state']}-{r['contract_id']}-{r['plan_id']}-{r['segment_id']}" for r in ma_pdp_plans]
        self.assertEqual(len(keys), len(set(keys)), "Found duplicate contract-plan-segment keys in MA/PDP enumeration!")

    def test_no_carrier_collapsing(self):
        nh_ma = [r for r in self.census_records if r["state"] == "NH" and r["market_segment"] == "MEDICARE_ADVANTAGE"]
        carriers = set([r["carrier"] for r in nh_ma])
        self.assertTrue(len(nh_ma) > len(carriers), "MA plans are incorrectly collapsed by carrier!")

    def test_non_enumerable_segments_excluded_from_exact_totals(self):
        non_enumerable = [r for r in self.census_records if r["market_segment"] in ["EMPLOYER_SELF_FUNDED", "EMPLOYER_FULLY_INSURED", "STUDENT_HEALTH", "FEDERAL_EMPLOYEE"]]
        # Verify that self-funded employer plans are marked as NOT_FULLY_ENUMERABLE or PARTIALLY_ENUMERABLE and not assigned fake 1 counts
        for r in non_enumerable:
            self.assertNotEqual(r["match_status"], "FOUND_EXACT_SYNTHETIC", "Synthetic 1-plan records must not be counted as exact!")

    def test_milestone_completeness_flag_is_false(self):
        # Verify that census complete milestone remains false until all missing CMS contracts are ingested
        missing_count = len([r for r in self.census_records if r["match_status"] == "MISSING"])
        milestone_complete = (missing_count == 0)
        self.assertFalse(milestone_complete, "NEW_ENGLAND_PUBLIC_PLAN_CENSUS_COMPLETE must be FALSE while CMS contracts remain missing!")

if __name__ == '__main__':
    unittest.main()
