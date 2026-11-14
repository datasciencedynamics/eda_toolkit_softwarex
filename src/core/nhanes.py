"""Reusable helpers for pulling and labeling NHANES August 2021-August 2023 data.

Nothing here filters or engineers features; that belongs in preprocessing.py.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Dict, Iterable

import pandas as pd
import requests

CYCLE = "2021-2023"
CYCLE_START = "2021"
SUFFIX = "L"

# CDC moved the public-use files in 2025. Newest location first; the legacy
# path is kept as a fallback.
BASE_URLS = [
    f"https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/{CYCLE_START}/DataFiles/",
    f"https://wwwn.cdc.gov/Nchs/Nhanes/{CYCLE}/",
]
BASE_URL = BASE_URLS[0]

# NHANES component files used in the paper, keyed by component name
COMPONENTS: Dict[str, str] = {
    "DEMO": "Demographics",
    "BMX": "Body measures",
    "BPXO": "Blood pressure (oscillometric)",
    "GHB": "Glycohemoglobin (HbA1c)",
    "BIOPRO": "Standard biochemistry profile",
    "DIQ": "Diabetes questionnaire",
}

# NHANES variable -> readable column name
RENAME: Dict[str, str] = {
    "RIDAGEYR": "age",
    "RIAGENDR": "sex",
    "RIDRETH3": "race_ethnicity",
    "INDFMPIR": "income_poverty_ratio",
    "BMXBMI": "bmi",
    "BMXWAIST": "waist_cm",
    "BPXOSY1": "systolic_bp",
    "BPXODI1": "diastolic_bp",
    "LBXGH": "hba1c",
    "LBXSCR": "creatinine",
    "LBXSAL": "albumin",
    "LBXSCH": "total_cholesterol",
    "DIQ010": "diabetes",
}

# Code books for categorical recodes
SEX = {1: "Male", 2: "Female"}
RACE_ETHNICITY = {
    1: "Mexican American",
    2: "Other Hispanic",
    3: "Non-Hispanic White",
    4: "Non-Hispanic Black",
    6: "Non-Hispanic Asian",
    7: "Other / Multiracial",
}
# DIQ010: 1 yes, 2 no, 3 borderline, 7 refused, 9 don't know
DIABETES = {1: "Yes", 2: "No", 3: "Borderline"}


def component_filename(component: str) -> str:
    """'DEMO' -> 'DEMO_L.XPT'."""
    return f"{component}_{SUFFIX}.XPT"


def component_urls(component: str) -> list:
    """Candidate download URLs for a component, newest CDC layout first."""
    name = component_filename(component)
    return [base + name for base in BASE_URLS] + [
        base + name.replace(".XPT", ".xpt") for base in BASE_URLS
    ]


def component_url(component: str) -> str:
    return component_urls(component)[0]


def _looks_like_xpt(content: bytes) -> bool:
    return content[:20].startswith(b"HEADER RECORD")


def download_xpt(component: str, timeout: int = 120) -> pd.DataFrame:
    """Download one NHANES XPT file from CDC and return it as a DataFrame.

    Tries each candidate URL in turn and verifies the payload is a SAS
    transport file before parsing, so an HTML error page fails loudly.
    """
    headers = {"User-Agent": "Mozilla/5.0 (eda_toolkit_softwarex; research use)"}
    errors = []
    for url in component_urls(component):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
        except requests.RequestException as exc:
            errors.append(f"{url}: {exc}")
            continue
        if response.status_code != 200:
            errors.append(f"{url}: HTTP {response.status_code}")
            continue
        if not _looks_like_xpt(response.content):
            ctype = response.headers.get("Content-Type", "unknown")
            errors.append(f"{url}: not an XPT payload (Content-Type: {ctype})")
            continue
        with tempfile.NamedTemporaryFile(suffix=".XPT") as tmp:
            tmp.write(response.content)
            tmp.flush()
            return pd.read_sas(tmp.name, format="xport")
    raise RuntimeError(
        f"Could not download {component_filename(component)} from CDC:\n  "
        + "\n  ".join(errors)
    )


def read_components(raw_dir: Path, components: Iterable[str]) -> Dict[str, pd.DataFrame]:
    """Read previously saved raw Parquet files, keyed by component name."""
    return {c: pd.read_parquet(raw_dir / f"{c}_{SUFFIX}.parquet") for c in components}


def merge_on_seqn(frames: Dict[str, pd.DataFrame], base: str = "DEMO") -> pd.DataFrame:
    """Left-join every component onto the base component by respondent id."""
    df = frames[base]
    for name, frame in frames.items():
        if name == base:
            continue
        df = df.merge(frame, on="SEQN", how="left")
    return df
