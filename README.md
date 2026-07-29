# highRES-model

[![Documentation Status](https://readthedocs.org/projects/highres-europe-wf/badge/?version=latest)](https://highres-europe-wf.readthedocs.io/en/latest/?badge=latest)

Welcome to the repository for the European version of the high temporal and spatial resolution electricity system model (highRES). The model is used to plan least-cost electricity systems for Europe and specifically designed to analyse the effects of high shares of variable renewables and explore integration/flexibility options. It does this by comparing and trading off potential options to integrate renewables into the system including the extension of the transmission grid, interconnection with other countries, building flexible generation (e.g. gas power stations), renewable curtailment and energy storage.

highRES is written in GAMS and its objective is to minimise power system investment and operational costs to meet hourly demand, subject to a number of system constraints. The transmission grid is represented using a linear transport model. To realistically model variable renewable supply, the model uses spatially and temporally-detailed renewable generation time series that are based on weather data.

## About This Fork

This is a fork of the official highRES repository that additionally
includes a results dashboard for exploring model outputs (costs,
capacity, utilization, and more).

- To run the model itself, follow the instructions below, same as the
  official repo.
- To use the results dashboard, see [`dashboard/README.md`](dashboard/README.md)
  for setup and usage instructions.

The dashboard reads GDX result files produced by the model and includes
example scenarios, so it can be explored immediately after cloning, no
model run required.

## Getting started

To run the full workflow, three datapackages are needed:

1. Resources (3.2 MB compressed, 6.4 MB uncompressed)
2. Weatherdata (4.3 GB)
3. Geodata (260 MB compressed, 518 MB uncompressed)

The datapackages can be downloaded from [Zenodo](https://doi.org/10.5281/zenodo.14223617).

## Windows

1. Clone the repository
   - To also get the submodule, go into the cloned folder and run these two commands
     ```
     git submodule init
     git submodule update
     ```
2. Install snakemake
   - Download miniforge windows exe <https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe>
   - Install Miniforge
   - Open Miniforge Prompt from the start menu
   - Install the environment from the provided yaml file `mamba env create -f workflow/envs/highres_environment.yaml`
3. Activate the snakemake environment `mamba activate highres`
4. Navigate to the repository in your snakemake conda environment shell
5. Get the required input files
   ```
   zenodo_get 10.5281/zenodo.14223617
   ```
6. Extract the required input files
   ```
   unzip resources.zip
   unzip weatherdata.zip
   unzip geodata.zip
   ```
7. Create a folder for shared input and move the geodata and weatherdata to that folder
   ```
   mkdir shared_input
   mv geodata shared_input
   mv weatherdata shared_input
   ```
8. Make sure GAMS is installed and licensed and that gamspath is set correctly in the config file
9. Run `snakemake -c all --configfile config/config_ci.yaml`. Specify your own config file by changing the file name

## Documentation

[Documentation](https://highres-europe-wf.readthedocs.io/en/latest/)
