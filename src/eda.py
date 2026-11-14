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
import matplotlib

matplotlib.use("Agg")  # headless: write files, never open windows

from eda_toolkit import (
    data_doctor,
    dataframe_profiler,
    detect_outliers,
    distribution_gof_plots,
    ensure_directory,
    flex_corr_matrix,
    generate_table1,
    normality_tests,
    plot_distributions,
)

app = typer.Typer(add_completion=False)

PROJECT_DIR = Path(__file__).resolve().parents[1]
PROCESSED = PROJECT_DIR / "data" / "processed" / "nhanes_adults.parquet"
OUTPUTS = PROJECT_DIR / "outputs"
TABLES = OUTPUTS / "tables"
FIGURES = OUTPUTS / "figures"
FIG_PNG = FIGURES / "png"
FIG_SVG = FIGURES / "svg"
FIG_PDF = FIGURES / "pdf"

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

# readable axis labels for figures
PRETTY = {
    "age": "Age",
    "income_poverty_ratio": "Income / poverty",
    "bmi": "BMI",
    "waist_cm": "Waist (cm)",
    "systolic_bp": "Systolic BP",
    "diastolic_bp": "Diastolic BP",
    "hba1c": "HbA1c",
    "creatinine": "Creatinine",
    "albumin": "Albumin",
    "total_cholesterol": "Total cholesterol",
}


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


def step_screening(df: pd.DataFrame) -> tuple:
    """Step 3: batch outlier detection (IQR) and normality tests."""
    outliers = detect_outliers(df, features=CONTINUOUS, method="iqr", threshold=1.5)
    outliers.to_csv(TABLES / "outliers_iqr.csv", index=False)

    normality = normality_tests(df, features=CONTINUOUS, alpha=0.05)
    normality.to_csv(TABLES / "normality.csv", index=False)
    return outliers, normality


def step_figures(df: pd.DataFrame) -> None:
    """Step 4: correlation matrix with FDR-adjusted significance, and
    distributions of key measures by diabetes status."""
    flex_corr_matrix(
        df,
        cols=CONTINUOUS,
        label_names=PRETTY,
        corr_method="spearman",
        show_significance=True,
        significance_method="stars",
        p_adjust="fdr_bh",
        triangular=True,
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        figsize=(11, 9.5),
        label_fontsize=11,
        annot_fontsize=9,
        tick_fontsize=10,
        xlabel_rot=40,
        text_wrap=70,
        title="Spearman correlations, adults 20+ (NHANES 2021-2023)",
        save_plots=True,
        image_path_png=str(FIG_PNG),
        image_path_svg=str(FIG_SVG),
        # a full path with extension is saved verbatim, so this yields the PDF
        # alongside the PNG and SVG written to the directories above
        image_filename=str(FIG_PDF / "fig1_corr_matrix.pdf"),
    )

    two_group = df.loc[df[GROUP].isin(["Yes", "No"])]
    plot_distributions(
        two_group,
        vars_of_interest=["hba1c", "bmi", "systolic_bp"],
        hue=GROUP,
        plot_type="both",
        fill=True,
        fill_alpha=0.4,
        n_rows=1,
        n_cols=3,
        subplot_figsize=(15, 4.5),
        bins=40,
        label_fontsize=12,
        tick_fontsize=10,
        image_path_png=str(FIG_PNG),
        image_path_svg=str(FIG_SVG),
        image_filename=str(FIG_PDF / "fig2_distributions_by_diabetes.pdf"),
        bbox_inches="tight",
    )


def step_gof_and_transform(df: pd.DataFrame) -> pd.DataFrame:
    """Step 5: goodness-of-fit diagnostics for a skewed lab value, then a
    reproducible Box-Cox transform of it written back as a new column."""
    # creatinine is right-skewed (dialysis-range values in the tail); compare
    # a normal fit against a lognormal fit on QQ plots
    for dist in ("norm", "lognorm"):
        distribution_gof_plots(
            df,
            var="creatinine",
            dist=dist,
            plot_types=["qq"],
            figsize=(5.5, 4.5),
            image_path_png=str(FIG_PNG),
            image_path_svg=str(FIG_SVG),
            image_filename=str(FIG_PDF / f"fig3_gof_creatinine_{dist}.pdf"),
        )

    # transform in place: adds creatinine_boxcox and reports the change
    data_doctor(
        df,
        feature_name="creatinine",
        scale_conversion="boxcox",
        apply_as_new_col_to_df=True,
        plot_type="all",
        figsize=(15, 4.5),
        image_path_png=str(FIG_PNG),
        image_path_svg=str(FIG_SVG),
        image_filename=str(FIG_PDF / "fig4_data_doctor_creatinine_boxcox.pdf"),
    )
    return df


@app.command()
def main() -> None:
    """Run the EDA steps and write outputs."""
    for directory in (TABLES, FIG_PNG, FIG_SVG, FIG_PDF):
        ensure_directory(str(directory))

    df = load()
    typer.echo(f"Loaded {df.shape[0]:,} adults x {df.shape[1]} columns")

    profile = step_profile(df)
    typer.echo(f"[1/5] profile: {profile.shape[0]} columns -> tables/profile.csv")

    table1 = step_table1(df)
    typer.echo(f"[2/5] table1: {table1.shape[0]} rows -> tables/table1_*.md, table1.csv")

    outliers, normality = step_screening(df)
    typer.echo("[3/5] screening -> tables/outliers_iqr.csv, tables/normality.csv")
    typer.echo(outliers.to_string(index=False))
    typer.echo(normality.to_string(index=False))

    step_figures(df)
    typer.echo("[4/5] figures -> figures/{png,svg,pdf}/fig1_corr_matrix, fig2_distributions_by_diabetes")

    df = step_gof_and_transform(df)
    new_cols = [c for c in df.columns if c.startswith("creatinine_")]
    typer.echo(f"[5/5] gof + transform -> fig3_gof_creatinine_*, fig4_data_doctor_*; new column(s): {new_cols}")


if __name__ == "__main__":
    app()
