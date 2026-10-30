"""Shared, auditable preparation and retrospective match analysis."""
import math
import pandas as pd

KEY = ["Date", "HomeTeam", "AwayTeam"]
CORE = KEY + ["FTHG", "FTAG"]
OPTIONAL = ["HTHG", "HTAG", "HS", "AS", "HST", "AST", "HC", "AC", "HF", "AF", "HY", "AY", "HR", "AR"]

def prepare_data(raw):
    missing = [c for c in CORE if c not in raw]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    df = raw.copy()
    df["Source row"] = range(2, len(df) + 2)
    reasons = pd.Series("", index=df.index)
    def flag(mask, label):
        reasons.loc[mask] += label + "; "
    for c in ["HomeTeam", "AwayTeam"]:
        df[c] = df[c].astype("string").str.strip()
        flag(df[c].isna() | df[c].eq(""), f"Missing {c}")
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
    flag(df["Date"].isna(), "Invalid date")
    flag(df["HomeTeam"].eq(df["AwayTeam"]).fillna(False), "Same home and away team")
    for c in ["FTHG", "FTAG"] + OPTIONAL:
        if c not in df:
            df[c] = float("nan")
        df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ["FTHG", "FTAG"]:
        flag(df[c].isna() | df[c].lt(0) | df[c].mod(1).ne(0), f"Invalid {c}")
    # Quarantine every ambiguous duplicate, never choose an arbitrary winner.
    flag(df.duplicated(KEY, keep=False), "Duplicate match key")
    rejected = df.loc[reasons.ne("")].copy()
    rejected["Reason"] = reasons.loc[reasons.ne("")]
    valid = df.loc[reasons.eq("")].copy()
    expected = pd.Series("D", index=valid.index)
    expected.loc[valid.FTHG > valid.FTAG] = "H"
    expected.loc[valid.FTHG < valid.FTAG] = "A"
    mismatch = valid["FTR"].ne(expected) if "FTR" in valid else pd.Series(False, index=valid.index)
    issues = []
    for i in valid.index[mismatch]:
        issues.append({"Source row": int(valid.loc[i, "Source row"]), "Issue": "FTR recalculated from final score"})
    valid["FTR"] = expected
    for c in OPTIONAL:
        bad = valid[c].notna() & (valid[c].lt(0) | valid[c].mod(1).ne(0))
        for i in valid.index[bad]:
            issues.append({"Source row": int(valid.loc[i, "Source row"]), "Issue": f"Invalid {c}; set unavailable"})
        valid.loc[bad, c] = float("nan")
    for half, full in [("HTHG", "FTHG"), ("HTAG", "FTAG")]:
        bad = valid[half] > valid[full]
        for i in valid.index[bad]:
            issues.append({"Source row": int(valid.loc[i, "Source row"]), "Issue": f"{half} exceeds final goals; set unavailable"})
        valid.loc[bad, half] = float("nan")
    for target, total in [("HST", "HS"), ("AST", "AS")]:
        bad = valid[target] > valid[total]
        for i in valid.index[bad]:
            issues.append({"Source row": int(valid.loc[i, "Source row"]), "Issue": f"{target} exceeds total shots; set unavailable"})
        valid.loc[bad, target] = float("nan")
    valid["Total goals"] = valid.FTHG + valid.FTAG
    valid["Lead eligible"] = valid[["HTHG", "HTAG"]].notna().all(axis=1)
    valid = valid.sort_values(KEY).reset_index(drop=True)
    report = {"Input matches": len(raw), "Valid matches": len(valid), "Quarantined matches": len(rejected),
              "Lead-analysis eligible": int(valid["Lead eligible"].sum()), "Corrections / warnings": len(issues)}
    return valid, rejected, pd.DataFrame(issues, columns=["Source row", "Issue"]), report

def monthly_summary(df):
    return (df.assign(Month=df.Date.dt.to_period("M").dt.to_timestamp())
            .groupby("Month", as_index=False)
            .agg(Goals=("Total goals", "sum"), Matches=("Total goals", "size"))
            .assign(**{"Goals per match": lambda d: d.Goals / d.Matches}))

def lead_matches(df):
    parts = []
    for home in [True, False]:
        part = pd.DataFrame({
            "Date": df.Date, "Team": df.HomeTeam if home else df.AwayTeam,
            "Opponent": df.AwayTeam if home else df.HomeTeam,
            "Venue": "Home" if home else "Away",
            "HT for": df.HTHG if home else df.HTAG,
            "HT against": df.HTAG if home else df.HTHG,
            "FT for": df.FTHG if home else df.FTAG,
            "FT against": df.FTAG if home else df.FTHG,
            "Eligible": df["Lead eligible"]})
        parts.append(part)
    result = pd.concat(parts, ignore_index=True)
    result = result[result.Eligible & (result["HT for"] > result["HT against"])].copy()
    result["Lead margin"] = result["HT for"] - result["HT against"]
    result["Outcome"] = "Draw"
    result.loc[result["FT for"] > result["FT against"], "Outcome"] = "Win"
    result.loc[result["FT for"] < result["FT against"], "Outcome"] = "Loss"
    result["Points"] = result.Outcome.map({"Win": 3, "Draw": 1, "Loss": 0})
    result["Points not secured"] = 3 - result.Points
    return result

def wilson(wins, n):
    if n == 0:
        return (float("nan"), float("nan"))
    z = 1.959963984540054
    p = wins / n
    center = (p + z*z/(2*n)) / (1 + z*z/n)
    half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1 + z*z/n)
    return center-half, center+half

def lead_summary(matches):
    records = []
    for team, group in matches.groupby("Team"):
        n, wins = len(group), int(group.Outcome.eq("Win").sum())
        low, high = wilson(wins, n)
        records.append({"Team": team, "Leads": n, "Wins": wins,
                        "Draws": int(group.Outcome.eq("Draw").sum()),
                        "Losses": int(group.Outcome.eq("Loss").sum()),
                        "Win rate": wins/n, "CI low": low, "CI high": high,
                        "Points not secured": int(group["Points not secured"].sum())})
    return pd.DataFrame(records, columns=["Team", "Leads", "Wins", "Draws", "Losses", "Win rate", "CI low", "CI high", "Points not secured"])
