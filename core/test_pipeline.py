import csv
import json
import math
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pipeline import generate_truthcert_hash, run_pipeline

MATRIX_HEADER = [
    "iso3c",
    "hexp_pc",
    "diabetes_prev",
    "age_65up",
    "physicians",
    "stability",
    "age_dependency",
    "population",
    "sex",
    "life_exp",
    "transported_effect",
    "ci_lb",
    "ci_ub",
    "e_value",
    "global_avg",
    "relevance_score",
]


class TestTransportabilityPipeline(unittest.TestCase):
    def _write_csv(self, path: Path, header, rows):
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerows(rows)

    def test_pipeline_execution_and_determinism(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            matrix_path = tmp / "global_transportability_matrix.csv"
            countries_path = tmp / "countries.csv"
            wdi_path = tmp / "WDICountry.csv"
            output_path = tmp / "atlas_results.json"

            self._write_csv(
                matrix_path,
                MATRIX_HEADER,
                [
                    ["USA", 12000, 10, 17, 2.6, 0.8, 53, 330000000, "F", 81, -0.50, -0.70, -0.30, 2.80, -0.3998, 0.90],
                    ["USA", 12000, 10, 17, 2.6, 0.8, 53, 330000000, "M", 76, -0.40, -0.60, -0.20, 2.50, -0.3998, 0.85],
                    ["KEN", 150, 5, 3, 0.2, -1.1, 80, 54000000, "F", 68, -0.30, -0.70, 0.10, 2.00, -0.3998, 0.75],
                    ["KEN", 150, 5, 3, 0.2, -1.1, 80, 54000000, "M", 63, -0.25, -0.60, 0.05, 1.90, -0.3998, 0.70],
                ],
            )
            self._write_csv(
                countries_path,
                ["id", "iso2Code", "name", "region", "adminregion", "incomeLevel", "lendingType", "capitalCity", "longitude", "latitude"],
                [
                    ["KEN", "KE", "Kenya", "Sub-Saharan Africa", "", "", "", "Nairobi", "36.8167", "-1.2833"],
                    ["USA", "US", "United States", "North America", "", "", "", "Washington, D.C.", "-77.0369", "38.9072"],
                ],
            )
            self._write_csv(
                wdi_path,
                ["Country Code", "Short Name", "2-alpha code"],
                [
                    ["KEN", "Kenya", "KE"],
                    ["USA", "United States", "US"],
                ],
            )

            first = run_pipeline(
                source_matrix_path=matrix_path,
                world_bank_catalog_path=countries_path,
                world_bank_wdi_path=wdi_path,
                output_path=output_path,
            )
            second = run_pipeline(
                source_matrix_path=matrix_path,
                world_bank_catalog_path=countries_path,
                world_bank_wdi_path=wdi_path,
                output_path=output_path,
            )

            self.assertTrue(output_path.exists(), "Pipeline output file should exist.")

            on_disk = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(first["audit"]["hash"], second["audit"]["hash"])
            self.assertEqual(first["audit"]["hash"], on_disk["audit"]["hash"])
            self.assertEqual(len(first["map_data"]), 2)

            usa_data = next(row for row in first["map_data"] if row["iso3"] == "USA")
            self.assertEqual(usa_data["country_name"], "United States")
            self.assertEqual(usa_data["spatial_metrics"]["coordinates"], [38.9072, -77.0369])
            self.assertAlmostEqual(usa_data["transportability_score"], 0.875, places=6)
            self.assertAlmostEqual(usa_data["effect_ratio"], math.exp(-0.45), places=6)

            priority_scores = [row["priority_score"] for row in first["map_data"]]
            self.assertAlmostEqual(max(priority_scores), 100.0, places=6)

    def test_truthcert_hash_generation(self):
        sample_data = [{"a": 1, "b": 2}, {"c": 3}]
        h1 = generate_truthcert_hash(sample_data)
        h2 = generate_truthcert_hash(sample_data)
        self.assertEqual(h1, h2)

        sample_data_unsorted = [{"b": 2, "a": 1}, {"c": 3}]
        h3 = generate_truthcert_hash(sample_data_unsorted)
        self.assertEqual(h1, h3)


if __name__ == "__main__":
    unittest.main()
