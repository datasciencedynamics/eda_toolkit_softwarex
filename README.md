# eda_toolkit_softwarex

Companion repository for the SoftwareX paper on [`eda_toolkit`](https://github.com/datasciencedynamics/eda_toolkit).
It reproduces every table and figure in the paper's illustrative example from
public NHANES 2017-2018 data.

## Pipeline

| Step | Script | Output |
|---|---|---|
| 1 | `src/data_gen.py` | raw NHANES components in `data/raw/` (Parquet) |
| 2 | `src/preprocessing.py` | `data/processed/nhanes_adults.parquet` |
| 3 | `src/eda.py` | tables in `outputs/tables/`, figures in `outputs/figures/` |

`data/` is gitignored; everything in it is downloaded from CDC on first run.

## Quick start

```bash
# activate a Python 3.10+ environment first
make venv && source etk_sx_venv/bin/activate
make requirements
make all
```

Run `make help` to list targets.

## Data

NHANES 2017-2018 public-use files from the National Center for Health
Statistics: DEMO_J, BMX_J, BPX_J, GHB_J, BIOPRO_J, DIQ_J. Adults aged 20 and
over with a known self-reported diabetes status (DIQ010) are retained.

## Authors

Leonid Shpaner and Oscar Gil, Data Science Dynamics.

## License

MIT
