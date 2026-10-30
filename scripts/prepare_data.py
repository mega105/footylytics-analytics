"""Run from any working directory: python scripts/prepare_data.py."""
from pathlib import Path
import sys
import json
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd
from analytics import prepare_data

def main():
    clean, rejected, issues, report = prepare_data(pd.read_csv(ROOT / "data" / "E0.csv"))
    clean.to_csv(ROOT / "data" / "epl_2024_25_clean.csv", index=False)
    rejected.to_csv(ROOT / "data" / "quarantined_matches.csv", index=False)
    issues.to_csv(ROOT / "data" / "validation_issues.csv", index=False)
    (ROOT / "data" / "quality_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
