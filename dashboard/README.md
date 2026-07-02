# highRES Dashboard

Status: Proof of concept done. Dashboard runs end-to-end via Snakemake or directly with streamlit command.

## Whats done

- Streamlit dashboard in `dashboard/app.py`
- Loads results from a scenario's `results.gdx` using `data_loader.py`
- `app.py` renders the different components like sidebar and different charts
- The code for rendering the UI-components like the different plots live in the ui folder

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

**4. Configure the dashboard** (optional):

Edit `dashboard/dashboard_config.yaml` to point to your results folder and GeoJSON path:

```yaml
results_path: work # folder containing scenario subfolders with results.gdx
geojson_path: intermediate_data/region/shapes/europe_onshore.geojson
```

**5. Run the dashboard** from the project root:

```bash
streamlit run dashboard/app.py
```

---

### 4. Switching scenarios

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

## Things to fix/improve

- Path to `intermediate_data/.../europe_onshore.geojson` is hardcoded relative
  to project root. Will break if run from elsewhere.

## Questions for further work

- gen_cap2area --> is this the values for mapping GW to Km2?
- Structure of dashboard, a tool where you manually add scenarios to a designated folder or either manually + new step in snakefile so result gdx scenarios also automatically gets moved inside this folder
- Visualizing costs, what tables are important and what makes sense to show?
- Visualizing transmissions, both total and hourly, best structure for this?
- Splitview with multiple scenarios, relevant feature?
- EN-Roads scenario playground, relevant future feature?
