
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

SOURCE = ROOT / "data" / "E0.csv"

OUTPUT = ROOT / "data" / "epl_2024_25_clean.csv"


def main():

    if not SOURCE.exists():

        raise FileNotFoundError(
            "E0.csv not found in data folder."
        )

    df = pd.read_csv(SOURCE)

    required = [
        "Date",
        "HomeTeam",
        "AwayTeam",
        "FTHG",
        "FTAG"
    ]

    for column in required:

        if column not in df.columns:

            raise ValueError(
                f"Missing column: {column}"
            )

    df = df.dropna(
        subset=required
    ).copy()

    df["Date"] = pd.to_datetime(
        df["Date"],
        dayfirst=True,
        errors="coerce"
    )

    df["FTHG"] = pd.to_numeric(
        df["FTHG"],
        errors="coerce"
    )

    df["FTAG"] = pd.to_numeric(
        df["FTAG"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["Date", "FTHG", "FTAG"]
    )

    df["FTHG"] = df["FTHG"].astype(int)
    df["FTAG"] = df["FTAG"].astype(int)

    df["FTR"] = df.apply(
        lambda x:
        "H" if x["FTHG"] > x["FTAG"]
        else "A" if x["FTHG"] < x["FTAG"]
        else "D",
        axis=1
    )

    df = df.sort_values("Date")

    df.to_csv(
        OUTPUT,
        index=False
    )

    print("Data cleaning completed!")
    print(f"Total matches: {len(df)}")
    print(f"Total teams: {len(set(df['HomeTeam']) | set(df['AwayTeam']))}")
    print(f"Saved to: {OUTPUT}")


if __name__ == "__main__":

    main()
