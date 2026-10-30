import unittest
from pathlib import Path
import pandas as pd
from analytics import prepare_data, monthly_summary, lead_matches, lead_summary

ROOT = Path(__file__).resolve().parents[1]

class AnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.raw = pd.read_csv(ROOT / "data" / "E0.csv")

    def test_season_reconciles(self):
        clean, rejected, issues, report = prepare_data(self.raw)
        self.assertEqual(len(clean), 380)
        self.assertEqual(len(rejected), 0)
        self.assertEqual(clean["Total goals"].sum(), 1115)
        self.assertEqual(monthly_summary(clean).Goals.sum(), 1115)
        self.assertEqual(report["Lead-analysis eligible"], 380)
        summary = lead_summary(lead_matches(clean)).set_index("Team")
        self.assertEqual(summary.loc["Arsenal", "Wins"], 12)
        self.assertEqual(summary.loc["Arsenal", "Leads"], 20)
        self.assertEqual(summary.loc["Liverpool", "Wins"], 17)
        self.assertEqual(summary.loc["Liverpool", "Points not secured"], 5)

    def test_invalid_core_quarantined_without_odds_filter(self):
        raw = self.raw.head(4).copy()
        raw.loc[0, "Date"] = "bad date"
        raw.loc[1, "FTHG"] = -1
        raw.loc[2, "B365H"] = float("nan")
        clean, rejected, _, _ = prepare_data(raw)
        self.assertEqual(len(clean), 2)
        self.assertEqual(len(rejected), 2)

    def test_duplicates_all_quarantined(self):
        raw = pd.concat([self.raw.head(2), self.raw.head(1)], ignore_index=True)
        clean, rejected, _, _ = prepare_data(raw)
        self.assertEqual(len(clean), 1)
        self.assertEqual(len(rejected), 2)

    def test_optional_corruption_not_zero_filled(self):
        raw = self.raw.head(2).copy()
        raw.loc[0, "HTHG"] = 99
        raw.loc[1, "HST"] = 999
        clean, _, issues, report = prepare_data(raw)
        self.assertEqual(len(clean), 2)
        self.assertEqual(report["Lead-analysis eligible"], 1)
        self.assertEqual(len(issues), 2)
        self.assertTrue(pd.isna(clean.loc[0, "HTHG"]))
        self.assertTrue(pd.isna(clean.loc[1, "HST"]))

if __name__ == "__main__":
    unittest.main()
