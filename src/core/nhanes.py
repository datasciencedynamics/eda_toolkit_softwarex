"""Reusable helpers for pulling and labeling NHANES 2017-2018 data.

Nothing here filters or engineers features; that belongs in preprocessing.py.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Dict, Iterable

import pandas as pd
import requests

CYCLE = "2017-2018"
SUFFIX = "J"
BASE_URL = f"https://wwwn.cdc.gov/Nchs/Nhanes/{CYCLE}/"

# NHANES component files used in the paper, keyed by component name
COMPONENTS: Dict[str, str] = {
    "DEMO": "Demographics",
    "BMX": "Body measures",
    "BPX": "Blood pressure",
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
    "BPXSY1": "systolic_bp",
    "BPXDI1": "diastolic_bp",
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
    """'DEMO' -> 'DEMO_J.XPT'."""
    return f"{component}_{SUFFIX}.XPT"


def component_url(component: str) -> str:
    return BASE_URL + component_filename(component)


def download_xpt(component: str, timeout: int = 120) -> pd.DataFrame:
    """Download one NHANES XPT file from CDC and return it as a DataFrame."""
    url = component_url(component)
    headers = {"User-Agent": "eda_toolkit_softwarex/0.1 (research use)"}
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".XPT") as tmp:
        tmp.write(response.content)
        tmp.flush()
        return pd.read_sas(tmp.name, format="xport")


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
