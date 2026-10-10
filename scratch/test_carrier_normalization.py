import csv
import json
import unittest
import subprocess

class TestCarrierNormalization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.census_records = []
        with open('NEW_ENGLAND_2026_PLAN_CENSUS_V4.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.census_records.append(row)

        with open('dist/marketplace/marketplace.js', 'r') as f:
            js_text = f.read()

        start_idx = js_text.find('const PLANS = [')
        end_idx = js_text.find('];', start_idx)
        plans_str = js_text[start_idx + len('const PLANS = '):end_idx + 1]

        res = subprocess.run(
            ["node", "-e", f"console.log(JSON.stringify({plans_str}));"],
            capture_output=True, text=True
        )
        cls.repo_plans = json.loads(res.stdout)

    def test_zero_placeholder_carriers_remaining(self):
        placeholders = [
            p for p in self.repo_plans
            if "Regional" in p["insurer_name"] or "Carrier 1" in p["insurer_name"] or "Carrier 2" in p["insurer_name"] or "Placeholder" in p["insurer_name"]
        ]
        self.assertEqual(len(placeholders), 0, f"Found {len(placeholders)} remaining placeholder carriers in PLANS array!")

    def test_exact_plan_count_preserved_331(self):
        self.assertEqual(len(self.census_records), 331, f"Expected 331 census records, got {len(self.census_records)}")
        self.assertEqual(len(self.repo_plans), 331, f"Expected 331 repo plans, got {len(self.repo_plans)}")

    def test_canonical_key_and_id_uniqueness(self):
        keys = [p["canonical_plan_key"] for p in self.repo_plans]
        ids = [p["id"] for p in self.repo_plans]
        self.assertEqual(len(keys), len(set(keys)), "Found duplicate canonical_plan_key!")
        self.assertEqual(len(ids), len(set(ids)), "Found duplicate repository_plan_id!")

    def test_carrier_deduplication(self):
        # Verify that carriers offer multiple plans without creating duplicate insurer dropdown entries
        for st in ["RI", "MA", "CT", "NH", "ME", "VT"]:
            st_plans = [p for p in self.repo_plans if p["state"] == st]
            st_insurers = set([p["insurer_name"] for p in st_plans])
            self.assertTrue(len(st_insurers) < len(st_plans), f"Carriers in {st} are not deduplicated!")

if __name__ == '__main__':
    unittest.main()
