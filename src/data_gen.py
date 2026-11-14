"""Fetch raw NHANES 2017-2018 component files and save them unchanged.

Usage:
    python src/data_gen.py            # Parquet only
    python src/data_gen.py --csv      # Parquet plus CSV backup
"""

from __future__ import annotations

from pathlib import Path

import typer

from core.nhanes import COMPONENTS, SUFFIX, download_xpt

app = typer.Typer(add_completion=False)

PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"


@app.command()
def main(
    raw_dir: Path = typer.Option(RAW_DIR, help="Where to save raw files."),
    csv: bool = typer.Option(False, "--csv", help="Also write a CSV copy."),
    force: bool = typer.Option(False, "--force", help="Re-download existing files."),
) -> None:
    """Download each NHANES component and save it as Parquet (optionally CSV)."""
    raw_dir.mkdir(parents=True, exist_ok=True)

    for component, label in COMPONENTS.items():
        stem = f"{component}_{SUFFIX}"
        parquet_path = raw_dir / f"{stem}.parquet"

        if parquet_path.exists() and not force:
            typer.echo(f"[skip] {stem}: already present")
            continue

        typer.echo(f"[fetch] {stem}: {label}")
        df = download_xpt(component)
        df.to_parquet(parquet_path, index=False)
        if csv:
            df.to_csv(raw_dir / f"{stem}.csv", index=False)
        typer.echo(f"        {df.shape[0]:,} rows x {df.shape[1]} cols -> {parquet_path.name}")


if __name__ == "__main__":
    app()
