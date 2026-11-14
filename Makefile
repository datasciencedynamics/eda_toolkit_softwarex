################################################################################
# GLOBALS                                                                      #
################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROJECT_NAME = eda_toolkit_softwarex
PYTHON_INTERPRETER = python
VENV_NAME = etk_sx_venv

ifeq (,$(shell which conda))
	HAS_CONDA=False
else
	HAS_CONDA=True
endif

################################################################################
# ENVIRONMENT                                                                  #
################################################################################

## Create a virtual environment (activate your conda env first, e.g. conda_312)
venv:
	$(PYTHON_INTERPRETER) -m venv $(VENV_NAME)
	@echo "Activate with: source $(VENV_NAME)/bin/activate"

## Install Python dependencies into the active environment
requirements:
	$(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

################################################################################
# PIPELINE                                                                     #
################################################################################

## Download raw NHANES 2017-2018 components to data/raw (Parquet)
data_gen:
	cd src && $(PYTHON_INTERPRETER) data_gen.py

## Build the adults analysis table in data/processed
preprocessing:
	cd src && $(PYTHON_INTERPRETER) preprocessing.py

## Run the EDA and write tables and figures to outputs/
eda:
	cd src && $(PYTHON_INTERPRETER) eda.py

## Run the whole pipeline: data_gen -> preprocessing -> eda
all: data_gen preprocessing eda

################################################################################
# HOUSEKEEPING                                                                 #
################################################################################

## Remove downloaded and derived data
clean_data:
	rm -rf $(PROJECT_DIR)/data/raw $(PROJECT_DIR)/data/processed

## Remove generated tables and figures
clean_outputs:
	find $(PROJECT_DIR)/outputs -type f ! -name '.gitkeep' -delete

## Remove data and outputs
clean: clean_data clean_outputs

################################################################################
# SELF-DOCUMENTING HELP                                                        #
################################################################################

.DEFAULT_GOAL := help

## Show this help
help:
	@echo "$(PROJECT_NAME)"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@awk '/^## /{desc=substr($$0,4); next} /^[a-zA-Z_]+:/{if(desc){sub(":","",$$1); printf "  %-16s %s\n", $$1, desc; desc=""}}' $(MAKEFILE_LIST)

.PHONY: venv requirements data_gen preprocessing eda all clean_data clean_outputs clean help
