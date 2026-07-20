# highRES Dashboard

This dashboard is designed for users of the highRES model to provide an overview of one or more model results. It's primary objective is to facilitate the communication of key variables from model-generated scenarios to various stakeholders.

## How to run this branch

**1. Clone the fork and check out the branch:**

```bash
git clone https://github.com/gjermundmyrvang/highRES-Europe-WF-dashboard.git
cd highRES-Europe-WF-dashboard
git checkout feature/results-dashboard
```

**2. Add required data folders** (not included in the repo, ~7GB):

- `intermediate_data/` — contains GeoJSON shape files used for map visualizations
- `shared_input/` — shared model input data

**3. Build and activate the dashboard environment:**

```bash
mamba env create -f dashboard/environment.yml
mamba activate highres-dashboard
```

**4. Configure the dashboard**:

Edit `dashboard/dashboard_config.yaml` to point to your results folder, GeoJSON path and GAMS path:

```yaml
results_path: work # defualt folder containing scenario subfolders with results.gdx
geojson_path: intermediate_data/region/shapes/europe_onshore.geojson
gams_path: "path/to/gams"
```

**5. Run the dashboard** from the project root:

```bash
streamlit run dashboard/app.py
```

---

### Switching scenarios

The dashboard supports two folder structures:

**Standard:** each scenario is a subfolder containing `results.gdx` (as created from running the model):

```
work/
└── BASE_2010_nuts2/
    └── results.gdx
```

**Custom:** GDX files named after the scenario (or other names), placed directly in the results folder:

```
custom_folder/
├── BASE_2010_nuts2_high_high.gdx
└── BASE_2010_nuts2_high_medium.gdx
```

Set `results_path` in `dashboard_config.yaml` to point to either structure. You can also add extra scenario folders at runtime via the sidebar ("Add other scenarios").

To generate new scenarios, run the full Snakemake pipeline:

```bash
snakemake -c all --configfile config/config_ci.yaml
```

This executes the full pipeline, generates `results.gdx`, and automatically opens the dashboard. Stop with `Ctrl+C`.
