# highRES Dashboard

Status: Proof of concept done. Dashboard runs end-to-end via Snakemake or directly with streamlit command.

## Whats done

- Streamlit dashboard in `dashboard/app.py`
- Loads results from a scenario's `results.gdx` using `data_loader.py`
- `app.py` renders the different components like sidebar and different charts
- The code for rendering the UI-components like the different plots live in the ui folder

## How to run this branch

1. Clone the fork and check out the branch:

```bash
git clone https://github.com/gjermundmyrvang/highRES-Europe-WF-dashboard.git
cd highRES-Europe-WF-dashboard
git checkout feature/results-dashboard
```

2. You also need to manually add or generate the `intermediate_data/` and `shared_input/` folder (not included in the repo ~7GB).

3. Build and activate dashboard environment:

```bash
mamba env create -f dashboard/environment.yml
```

```bash
mamba activate highres-dashboard
```

### 3. Run the dashboard

From the project root, start the Streamlit dashboard:

```bash
streamlit run dashboard/app.py
```

---

### 4. Switching scenarios

By default, `data_loader.py` loads the pre-installed **dummy scenario** located at:

```
work_test/BASE_2010_nuts2
```

To use other scenarios, there are two options:

#### Option 1: Load a custom scenario folder manually

- Prepare a folder containing scenario(s) `.gdx` files
- Make sure the folder is accessible from the project
- Open the running Streamlit dashboard
- Enter or select the path to that folder in the sidebar
- Switch the dropdown to the **added** folder so its `.gdx` files are loaded

#### Option 2: Run a full new scenario

Update or set your configuration in `config/config_ci.yaml`, then run:

```bash
snakemake -c all --configfile config/config_ci.yaml
```

This will:

- execute the full pipeline
- generate `results.gdx`
- automatically open the Streamlit dashboard in your browser

Stop the dashboard with `Ctrl + C`.

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
