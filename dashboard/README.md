# highRES Dashboard

This dashboard is designed for users of the highRES model to provide an overview of one or more model results. It's primary objective is to facilitate the communication of key variables from model-generated scenarios to various stakeholders.

The **highRES Dashboard** is a Streamlit-based web application for visualising and exploring results from the highRES energy system model. It was developed as a summer research project at SINTEF/University of Oslo and is designed to work with results created by the `highRES-Europe-WF` workflow.

The dashboard loads scenario results directly from GDX files produced by the GAMS optimisation model. It is intentionally decoupled from the model run itself, researchers run the model first, then point the dashboard at the results folder.

## 1. Getting Started

### 1.1 Prerequisites

- **GAMS** installed on the machine (required by `gdxpds` to read GDX files)
- `conda` or `mamba` package manager

**Find GAMS path:**
Run this in your terminal and add the path to `gams_path`:

```bash
which gams
```

or

```bash
whereis gams
```

and use the returned path as gams_path.

_Alternatively open `GAMS Studio` and navigate to `Help` then select `GAMS Licensing` and the path will be next to `System Directory:`_

### 1.2 Installation

1. **Clone the fork:**

   ```bash
   git clone https://github.com/gjermundmyrvang/highRES-Europe-WF-dashboard.git
   ```

   ```bash
   cd highRES-Europe-WF-dashboard
   ```

2. **Create and activate the dedicated conda environment:**

   ```bash
   mamba env create -f dashboard/environment.yml
   mamba activate highres-dashboard
   ```

3. **Configure the dashboard** (see [Section 3](#3-configuration) below), then run from the project root:
   ```bash
   streamlit run dashboard/app.py
   ```

---

## 2. Try It Out Immediately (No Model Run Required)

You don't need your own `results.gdx` files to see the dashboard in action.
As long as you've completed the steps above, activated the dashboard
environment, have GAMS installed and licensed, and set `gams_path` in
`dashboard/dashboard_config.yaml`, you can run the dashboard right away:

```bash
streamlit run dashboard/app.py
```

By default, `results_path` in the config points to `dashboard/example_scenarios`,
a set of pre-generated 48h "dummy" scenarios bundled with this repo, along
with a matching `dashboard/shapes/europe_onshore.geojson`. This means a
fresh clone will load and display example results immediately, with no
model run and no real scenario data required.

Once you're ready to explore your own results, update `results_path` in
the config (or add scenario folders at runtime via the sidebar) to point
at your own model output, see Section 3 below.

---

## 3. Configuration

The file `dashboard/dashboard_config.yaml` controls where the dashboard looks for data. Edit this before running:

```yaml
results_path: dashboard/example_scenarios # default folder containing 'dummy' scenarios with just 48h data
geojson_path: dashboard/shapes/europe_onshore.geojson # Can be replaced with custom geojson files
gams_path: /Library/Frameworks/GAMS.framework/... # path to GAMS installation (see instructions below on how to find path)
```

### 3.1 Startup Validation

On startup, `app.py` passes the configuration through `check_user_config()` to ensure all paths exist on disk before executing GDX operations.

In addition, scenario discovery raises explicit `FileNotFoundError` exceptions if the target directory contains no valid model outputs:

- **Path Existence:** `results_path`, `geojson_path`, and `gams_path` are checked for existence.
- **`load_standard_scenarios()`**: Searches for `base_path/*/results.gdx`. Raises `FileNotFoundError` if no nested scenario files are found.
- **`load_custom_scenarios()`**: Searches for `folder_path/*.gdx`. Raises `FileNotFoundError` if no flat GDX files are found.
- **`load_scenarios()`**: Aggregates standard and custom checks. If neither path type yields scenarios, it triggers a clean UI alert in Streamlit (`st.error()`) and halts execution (`st.stop()`), preventing downstream `KeyError` or layout crashes.

### 3.2 Supported scenario folder structures:

- **Standard (model-generated):** `work/scenario_name/results.gdx`
- **Custom (flat):** `custom_folder/scenario_name.gdx`

Users can also add extra scenario folders at runtime via the sidebar without touching the config file.
**NB:** runtime added scenarios currently only works with **Custom (flat):** `custom_folder/scenario_name.gdx`.

### 3.3 Using Regional or Custom Zones

If your GDX file uses sub-national or custom zones (e.g., `NO020` for Innlandet) rather than standard 2-letter country codes, you must update `geojson_path` in `dashboard/dashboard_config.yaml`. Point it to a regional GeoJSON file where the feature properties (`properties.index`) directly match the `z`-values in your GDX file. This ensures map visualizations and land area calculations render correctly.
