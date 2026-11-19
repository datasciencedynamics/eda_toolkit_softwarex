<p align="center">
  <a href="https://github.com/datasciencedynamics/eda_toolkit">
    <img src="https://raw.githubusercontent.com/datasciencedynamics/eda_toolkit/main/assets/eda_toolkit_logo.svg" width="300" alt="eda_toolkit">
  </a>
</p>

<h1 align="center">EDA Toolkit: SoftwareX Companion</h1>

<p align="center">
  <a href="https://github.com/datasciencedynamics/eda_toolkit"><img src="https://img.shields.io/badge/library-eda__toolkit-blue" alt="eda_toolkit"></a>
  <a href="https://pypi.org/project/eda_toolkit/"><img src="https://img.shields.io/pypi/v/eda_toolkit.svg" alt="PyPI"></a>
  <a href="LICENSE.md"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT"></a>
</p>

Companion repository for the SoftwareX paper

> Shpaner L, Gil O. `eda_toolkit`: A Python Library for Reproducible Exploratory Data Analysis. *SoftwareX* (submitted, 2026).

A single `make all` downloads the public NHANES August 2021–August 2023 files from the CDC, builds the analysis cohort, and regenerates every table and figure in the paper's illustrative example with [`eda_toolkit`](https://github.com/datasciencedynamics/eda_toolkit). No data or outputs are stored in this repository; everything is rebuilt from the source files.

## Contents

- [Quick start](#quick-start)
- [What the pipeline does](#what-the-pipeline-does)
- [Outputs and the paper](#outputs-and-the-paper)
- [Data](#data)
- [Repository layout](#repository-layout)
- [Make targets](#make-targets)
- [Requirements](#requirements)
- [Citation](#citation)
- [Authors and license](#authors-and-license)

## Quick start

```bash
git clone https://github.com/datasciencedynamics/eda_toolkit_softwarex.git
cd eda_toolkit_softwarex

# activate a Python 3.8+ environment first
make venv && source etk_sx_venv/bin/activate
make requirements
make all
```

The full run, from CDC download to the last figure, takes under two minutes on a laptop. Results land in `outputs/`.

## What the pipeline does

| Step | Script | What it does | Output |
|---|---|---|---|
| 1 | `src/data_gen.py` | Downloads six NHANES component files (XPORT) and saves each as Parquet. Flags: `--csv` for a CSV copy, `--force` to re-download. | `data/raw/` |
| 2 | `src/preprocessing.py` | Merges components on `SEQN`, keeps adults aged 20 and over with a known self-reported diabetes status, recodes categorical variables to readable labels. | `data/processed/nhanes_adults.parquet` |
| 3 | `src/eda.py` | Runs the analysis in the paper: profile, stratified Table 1, outlier and normality screening, correlation matrix, distributions by group, goodness-of-fit plots, Box-Cox transform. | `outputs/tables/`, `outputs/figures/{png,svg,pdf}/` |

Step 3 is a sequence of `eda_toolkit` calls (`dataframe_profiler`, `generate_table1`, `detect_outliers`, `normality_tests`, `flex_corr_matrix`, `plot_distributions`, `distribution_gof_plots`, `data_doctor`). Reading `src/eda.py` top to bottom is the quickest way to see how the paper's example was produced.

## Outputs and the paper

| Paper item | File under `outputs/` |
|---|---|
| Table 1, characteristics by diabetes status | `tables/table1_continuous.md`, `tables/table1_categorical.md`, `tables/table1.csv` |
| Outlier and normality screening | `tables/outliers_iqr.csv`, `tables/normality.csv` |
| Column profile | `tables/profile.csv` |
| Fig. 1, Spearman correlation matrix with FDR-adjusted stars | `figures/{png,svg,pdf}/fig1_corr_matrix` |
| Fig. 2, HbA1c, BMI, and systolic BP by diabetes status | `figures/{png,svg,pdf}/fig2_distributions_by_diabetes` |
| Fig. 3, creatinine QQ plots, normal and lognormal fits | `figures/{png,svg,pdf}/fig3_gof_creatinine_{norm,lognorm}` |
| Fig. 4, creatinine after Box-Cox | `figures/{png,svg,pdf}/fig4_data_doctor_creatinine_boxcox` |

Every figure is written as PNG, SVG, and PDF by the same `eda_toolkit` call that draws it; the PDFs are the ones placed in the manuscript.

## Data

Public-use files from the National Center for Health Statistics, NHANES August 2021–August 2023 cycle (file suffix `_L`):

| Component | File | Variables used |
|---|---|---|
| Demographics | `DEMO_L` | age, sex, race and ethnicity, income-to-poverty ratio |
| Body measures | `BMX_L` | BMI, waist circumference |
| Blood pressure (oscillometric) | `BPXO_L` | first systolic and diastolic readings |
| Glycohemoglobin | `GHB_L` | HbA1c |
| Standard biochemistry | `BIOPRO_L` | creatinine, albumin, total cholesterol |
| Diabetes questionnaire | `DIQ_L` | self-reported diabetes (DIQ010) |

The cohort is adults aged 20 and over with a known answer to DIQ010: 7,806 participants (1,070 with diabetes, 6,466 without, 270 borderline). Survey weights are deliberately not applied; the example illustrates the software workflow and makes no epidemiological claim.

## Repository layout

```
eda_toolkit_softwarex/
├── Makefile
├── requirements.txt
├── src/
│   ├── core/
│   │   └── nhanes.py        # download, read, and merge helpers
│   ├── data_gen.py          # step 1
│   ├── preprocessing.py     # step 2
│   └── eda.py               # step 3
├── data/                    # gitignored, created by make
│   ├── raw/
│   └── processed/
└── outputs/                 # gitignored, created by make
    ├── tables/
    └── figures/{png,svg,pdf}/
```

## Make targets

| Target | Action |
|---|---|
| `make venv` | Create the `etk_sx_venv` virtual environment |
| `make requirements` | Install `requirements.txt` into it |
| `make data_gen` | Step 1 only |
| `make preprocessing` | Step 2 only |
| `make eda` | Step 3 only |
| `make all` | Steps 1 through 3 |
| `make clean_data` | Remove `data/` |
| `make clean_outputs` | Remove `outputs/` |
| `make clean` | Both of the above |
| `make help` | List targets |

## Requirements

Python 3.8 or later, `eda_toolkit` 0.0.31 or later, pandas, pyarrow, requests, typer. Exact floors are in `requirements.txt`. Internet access is needed once, for the CDC download in step 1.

## Citation

If you use this repository or the library, please cite the paper and the software:

```bibtex
@article{shpaner2026edatoolkit,
  author  = {Shpaner, Leonid and Gil, Oscar},
  title   = {eda\_toolkit: A Python Library for Reproducible Exploratory Data Analysis},
  journal = {SoftwareX},
  year    = {2026},
  note    = {submitted}
}

@software{shpaner_2026_13162633,
  author    = {Shpaner, Leonid and Gil, Oscar},
  title     = {EDA Toolkit},
  version   = {0.0.31},
  publisher = {Zenodo},
  year      = {2026},
  doi       = {10.5281/zenodo.13162633},
  url       = {https://doi.org/10.5281/zenodo.13162633}
}
```

## Authors and license

Leonid Shpaner and Oscar Gil, [Data Science Dynamics](https://datasciencedynamics.com). Released under the MIT License; see `LICENSE.md`.
