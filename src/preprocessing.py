"""Build the analysis table from the raw NHANES components.

Steps: merge on SEQN, keep adults (20+), keep the paper's variables,
recode categorical codes to labels, drop respondents with unknown
diabetes status.

Usage:
    python src/preprocessing.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from core.nhanes import (
    COMPONENTS,
    DIABETES,
    RACE_ETHNICITY,
    RENAME,
    SEX,
    merge_on_seqn,
    read_components,
)

app = typer.Typer(add_completion=False)

PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

MIN_AGE = 20
COLUMNS = ["SEQN", *RENAME.values()]


def build_adults(raw_dir: Path) -> pd.DataFrame:
    frames = read_components(raw_dir, COMPONENTS)
    df = merge_on_seqn(frames)

    df = df.loc[df["RIDAGEYR"] >= MIN_AGE].rename(columns=RENAME)

    df["sex"] = df["sex"].map(SEX)
    df["race_ethnicity"] = df["race_ethnicity"].map(RACE_ETHNICITY)
    df["diabetes"] = df["diabetes"].map(DIABETES)

    # refused / don't know (codes 7 and 9) map to NaN and are dropped
    df = df.dropna(subset=["diabetes"])

    return df[COLUMNS].reset_index(drop=True)


@app.command()
def main(
    raw_dir: Path = typer.Option(RAW_DIR, help="Raw Parquet files from data_gen.py."),
    out_dir: Path = typer.Option(PROCESSED_DIR, help="Where to save the analysis table."),
    csv: bool = typer.Option(False, "--csv", help="Also write a CSV copy."),
) -> None:
    """Merge, filter and recode the raw components into one analysis table."""
    out_dir.mkdir(parents=True, exist_ok=True)

    df = build_adults(raw_dir)
    out_path = out_dir / "nhanes_adults.parquet"
    df.to_parquet(out_path, index=False)
    if csv:
        df.to_csv(out_dir / "nhanes_adults.csv", index=False)

    typer.echo(f"Adults 20+ with known diabetes status: {df.shape[0]:,} rows x {df.shape[1]} cols")
    typer.echo(df["diabetes"].value_counts().to_string())
    typer.echo(f"Saved -> {out_path}")


if __name__ == "__main__":
    app()
