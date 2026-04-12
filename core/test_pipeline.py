import os
import json
import unittest
import sys

# Ensure core is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pipeline import run_pipeline, RESULTS_PATH, generate_truthcert_hash

class TestTransportabilityPipeline(unittest.TestCase):
    
    def setUp(self):
        # Ensure clean state if needed, though run_pipeline overwrites
        if os.path.exists(RESULTS_PATH):
            os.remove(RESULTS_PATH)

    def test_pipeline_execution_and_determinism(self):
        """Verify the pipeline runs, produces a file, and is deterministic."""
        # 1. First Run
        run_pipeline()
        self.assertTrue(os.path.exists(RESULTS_PATH), "Pipeline output file should exist.")
        
        with open(RESULTS_PATH, 'r') as f:
            data1 = json.load(f)
        
        hash1 = data1['audit']['hash']
        self.assertTrue(hash1.startswith("SHA256:"), "Hash should have SHA256 prefix.")
        
        # 2. Second Run (Determinism Check)
        run_pipeline()
        with open(RESULTS_PATH, 'r') as f:
            data2 = json.load(f)
        
        hash2 = data2['audit']['hash']
        self.assertEqual(hash1, hash2, "Pipeline output must be deterministic (hash mismatch).")
        
        # 3. Structure Check
        self.assertIn('audit', data1)
        self.assertIn('map_data', data1)
        self.assertEqual(len(data1['map_data']), 7, "Should process all 7 countries.")
        
        # 4. Content Check (USA as baseline)
        usa_data = next(c for c in data1['map_data'] if c['iso3'] == 'USA')
        self.assertAlmostEqual(usa_data['dml_hr'], 0.82, places=2, msg="USA DML HR should be near baseline.")
        self.assertAlmostEqual(usa_data['smd_avg'], 0.0, places=5, msg="USA SMDs should be zero.")

    def test_truthcert_hash_generation(self):
        """Verify the hashing logic is stable."""
        sample_data = [{"a": 1, "b": 2}, {"c": 3}]
        h1 = generate_truthcert_hash(sample_data)
        h2 = generate_truthcert_hash(sample_data)
        self.assertEqual(h1, h2)
        
        # Order independence (sort_keys=True)
        sample_data_unsorted = [{"b": 2, "a": 1}, {"c": 3}]
        h3 = generate_truthcert_hash(sample_data_unsorted)
        self.assertEqual(h1, h3)

if __name__ == '__main__':
    unittest.main()
