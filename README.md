<p align="left">
  <a href="https://github.com/datasciencedynamics/eda_toolkit">
    <img src="https://raw.githubusercontent.com/datasciencedynamics/eda_toolkit/main/assets/eda_toolkit_logo.svg" width="300" alt="eda_toolkit">
  </a>
</p>

# eda_toolkit_softwarex

Companion repository for the SoftwareX paper on [`eda_toolkit`](https://github.com/datasciencedynamics/eda_toolkit).
It reproduces every table and figure in the paper's illustrative example from
public NHANES August 2021-August 2023 data.

## Pipeline

| Step | Script | Output |
|---|---|---|
| 1 | `src/data_gen.py` | raw NHANES components in `data/raw/` (Parquet) |
| 2 | `src/preprocessing.py` | `data/processed/nhanes_adults.parquet` |
| 3 | `src/eda.py` | tables in `outputs/tables/`, figures in `outputs/figures/{png,svg,pdf}/` |

`data/` and `outputs/` are gitignored; `make all` regenerates both from CDC downloads.

## Quick start

```bash
# activate a Python 3.8+ environment first
make venv && source etk_sx_venv/bin/activate
make requirements
make all
```

Run `make help` to list targets. Requires `eda_toolkit` 0.0.31 or later.

## Outputs and the paper

| Paper item | File under `outputs/` |
|---|---|
| Table 1 (characteristics by diabetes status) | `tables/table1_continuous.md`, `tables/table1_categorical.md`, `tables/table1.csv` |
| Outlier and normality screening | `tables/outliers_iqr.csv`, `tables/normality.csv` |
| Fig. 1 correlation matrix | `figures/{png,svg,pdf}/fig1_corr_matrix` |
| Fig. 2 distributions by diabetes status | `figures/{png,svg,pdf}/fig2_distributions_by_diabetes` |
| Fig. 3 creatinine goodness of fit | `figures/{png,svg,pdf}/fig3_gof_creatinine_{norm,lognorm}` |
| Fig. 4 creatinine after Box-Cox | `figures/{png,svg,pdf}/fig4_data_doctor_creatinine_boxcox` |

## Data

NHANES August 2021-August 2023 public-use files from the National Center for Health
Statistics: DEMO_L, BMX_L, BPXO_L, GHB_L, BIOPRO_L, DIQ_L. Adults aged 20 and
over with a known self-reported diabetes status (DIQ010) are retained.

## Authors

Leonid Shpaner and Oscar Gil, Data Science Dynamics.

## License

MIT
