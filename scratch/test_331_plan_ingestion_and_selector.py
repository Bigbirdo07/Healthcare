import csv
import json
import unittest
import subprocess

class Test331PlanIngestionAndSelector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.census_v4 = []
        with open('NEW_ENGLAND_2026_PLAN_CENSUS_V4.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.census_v4.append(row)

        # Extract PLANS array from dist/marketplace/marketplace.js
        with open('dist/marketplace/marketplace.js', 'r') as f:
            js_text = f.read()

        start_idx = js_text.find('const PLANS = [')
        end_idx = js_text.find('];', start_idx)
        plans_str = js_text[start_idx + len('const PLANS = '):end_idx + 1]

        res = subprocess.run(
            ["node", "-e", f"const plans = {plans_str}; console.log(JSON.stringify(plans));"],
            capture_output=True, text=True
        )
        cls.repo_plans = json.loads(res.stdout)
        cls.repo_plan_map = {p['id']: p for p in cls.repo_plans}

    def test_total_enumerable_plan_count_is_331(self):
        self.assertEqual(len(self.census_v4), 331, f"Expected 331 census records, got {len(self.census_v4)}")
        self.assertEqual(len(self.repo_plans), 331, f"Expected 331 repository plan objects, got {len(self.repo_plans)}")

    def test_zero_missing_plans(self):
        missing = [r for r in self.census_v4 if r["match_status"] == "MISSING"]
        self.assertEqual(len(missing), 0, f"Expected 0 missing plans after ingestion, got {len(missing)}")

    def test_uniqueness_of_keys_and_ids(self):
        keys = [r["canonical_plan_key"] for r in self.census_v4]
        rep_ids = [r["repository_plan_id"] for r in self.census_v4]
        self.assertEqual(len(keys), len(set(keys)), "Found duplicate canonical_plan_key!")
        self.assertEqual(len(rep_ids), len(set(rep_ids)), "Found duplicate repository_plan_id!")

    def test_dynamic_plan_filtering_331_records(self):
        # Iterate through all 331 census records and verify matching repository plan properties
        for r in self.census_v4:
            rep_id = r["repository_plan_id"]
            self.assertIn(rep_id, self.repo_plan_map, f"Repository plan ID {rep_id} not found in PLANS array!")
            p_obj = self.repo_plan_map[rep_id]

            self.assertEqual(p_obj["state"], r["state"], f"State mismatch for {rep_id}")
            self.assertEqual(p_obj["canonical_plan_key"], r["canonical_plan_key"], f"Canonical key mismatch for {rep_id}")
            self.assertEqual(p_obj["plan_year"], 2026, f"Plan year mismatch for {rep_id}")
            self.assertTrue(p_obj["production_visibility"], f"Plan {rep_id} must be production selectable!")

    def test_zero_coverage_rule_newly_ingested_plan(self):
        # Test a newly ingested plan with no verified rules
        new_plan = [p for p in self.repo_plans if p.get("coverage_verification_status") == "VERIFICATION_PENDING"][0]
        self.assertTrue(new_plan["production_visibility"], "Newly ingested plan must be selectable!")
        self.assertEqual(new_plan["coverage_verification_status"], "VERIFICATION_PENDING")

    def test_milestone_completion_flag_is_true(self):
        missing = [r for r in self.census_v4 if r["match_status"] == "MISSING"]
        milestone_complete = (len(missing) == 0 and len(self.census_v4) == 331)
        self.assertTrue(milestone_complete, "NEW_ENGLAND_PUBLIC_PLAN_CENSUS_COMPLETE must be TRUE after 331 plan ingestion!")

    def test_non_enumerable_segments_separated(self):
        segments = set([r["market_segment"] for r in self.census_v4])
        excluded = ["EMPLOYER_SELF_FUNDED", "EMPLOYER_FULLY_INSURED", "STUDENT_HEALTH", "FEDERAL_EMPLOYEE"]
        for exc in excluded:
            self.assertNotIn(exc, segments, f"Non-enumerable segment {exc} must be separate from exact plan census!")

if __name__ == '__main__':
    unittest.main()
