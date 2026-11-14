"""Exploratory analysis for the SoftwareX illustrative example.

Reads data/processed/nhanes_adults.parquet and writes every table and figure
used in the paper to outputs/. Each step is one eda_toolkit call.

Usage:
    python src/eda.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer
from eda_toolkit import dataframe_profiler, generate_table1

app = typer.Typer(add_completion=False)

PROJECT_DIR = Path(__file__).resolve().parents[1]
PROCESSED = PROJECT_DIR / "data" / "processed" / "nhanes_adults.parquet"
TABLES = PROJECT_DIR / "outputs" / "tables"
FIGURES = PROJECT_DIR / "outputs" / "figures"

GROUP = "diabetes"
CONTINUOUS = [
    "age",
    "income_poverty_ratio",
    "bmi",
    "waist_cm",
    "systolic_bp",
    "diastolic_bp",
    "hba1c",
    "creatinine",
    "albumin",
    "total_cholesterol",
]
CATEGORICAL = ["sex", "race_ethnicity"]


def load() -> pd.DataFrame:
    df = pd.read_parquet(PROCESSED)
    return df.drop(columns=["SEQN"])


def step_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Step 1: per-column profile (dtype, nulls, uniques, mode)."""
    profile = dataframe_profiler(df, return_df=True)
    profile.to_csv(TABLES / "profile.csv", index=False)
    return profile


def step_table1(df: pd.DataFrame) -> pd.DataFrame:
    """Step 2: Table 1 stratified by diabetes (Yes vs No), BH-adjusted tests.

    generate_table1 compares exactly two groups, so the small Borderline
    group is set aside here and described separately in the paper.
    """
    two_group = df.loc[df[GROUP].isin(["Yes", "No"])]
    table1 = generate_table1(
        two_group,
        groupby_col=GROUP,
        continuous_cols=CONTINUOUS,
        categorical_cols=CATEGORICAL,
        apply_bh_fdr=True,
        value_counts=True,
        decimal_places=2,
        export_markdown=True,
        markdown_path=str(TABLES / "table1.md"),
    )
    table1.to_csv(TABLES / "table1.csv", index=False)
    return table1


@app.command()
def main() -> None:
    """Run the EDA steps and write outputs."""
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    df = load()
    typer.echo(f"Loaded {df.shape[0]:,} adults x {df.shape[1]} columns")

    profile = step_profile(df)
    typer.echo(f"[1/2] profile: {profile.shape[0]} columns -> tables/profile.csv")

    table1 = step_table1(df)
    typer.echo(f"[2/2] table1: {table1.shape[0]} rows -> tables/table1_*.md, table1.csv")
    typer.echo(table1.to_string(index=False, max_colwidth=28))


if __name__ == "__main__":
    app()
