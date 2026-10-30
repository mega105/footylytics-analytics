# Footylytics
Football performance analysis for the EPL 2024/25 season.

## What this tool helps decide
Prioritize matches for video review when a half-time lead did not become a win.
Lead Protection compares win conversion by team, lead margin and venue, with match evidence and approximate 95% Wilson intervals. Season overview, standings, team profiles and comparisons remain available.

## Run
Use Python 3.11 or newer.
```sh
pip install -r requirements.txt
python scripts/prepare_data.py
streamlit run app.py
```
The app and preparation script both use the same validation function in analytics.py. The app validates the original CSV on load; the script exports an inspectable snapshot and audit reports. Do not replace E0.csv with the cleaned export (their date formats differ).

## Dataset and provenance
- Original file: data/E0.csv (preserved unchanged).
- Source: https://www.football-data.co.uk/mmz4281/2425/E0.csv
- Definitions: https://www.football-data.co.uk/notes.txt
- 380 matches, 20 teams, 16 August 2024 to 25 May 2025.
- Retain source attribution; verify redistribution terms before republishing data.
- No software license has been selected on behalf of the team. Choose one before describing this repository as licensed open source.

## Cleaning
Required identity and final-score fields are validated. Dates use day/month/year.
Core-invalid rows and all ambiguous duplicate match keys are quarantined.
Final results are recalculated from scores, with mismatches logged.
Negative or fractional optional counts, impossible half-time scores and shots-on-target greater than shots are marked unavailable and logged.
Missing odds never cause a valid match to be removed. Missing statistics are never zero-filled.
Raw source data remains available to inspect corrections.

Exports in data/: epl_2024_25_clean.csv, quarantined_matches.csv, validation_issues.csv, quality_report.json.

## Findings and definitions
Arsenal won 12 of 20 matches led at half-time; Liverpool won 17 of 19.
These are descriptive full-season results, not opponent-adjusted estimates or causal conclusions.
Points not secured = 3 minus actual points, only in matches led at half-time.
The league comparator pools eligible matches under the same venue/margin filters.
Intervals approximate uncertainty; repeated opponents and differing match contexts limit inference.
There is no goal timeline, xG, substitutions or player data. This tool cannot explain the tactical cause of a lost lead or claim points could have been recovered.

## Demo walkthrough
1. Open Lead Protection and select Arsenal in the sidebar.
2. Compare all margins with one-goal advantages.
3. Inspect the selected team's dropped-lead matches and download the evidence.
4. Compare Liverpool, read the uncertainty intervals and methodology.
5. Open data quality to inspect coverage and validation.
6. Explore the existing season overview and team comparison below.

## Verification
```sh
python -m unittest discover -s tests -v
```
Regression checks cover the 1,115-goal total, known lead outcomes, invalid dates/scores, duplicate quarantine, missing odds and optional-statistic corruption.
Monthly totals include both home and away goals.

## Submission checklist
Add the public deployed demo URL, team member credits, screenshots and the team's chosen code license. Deployment is not included in this local package.
