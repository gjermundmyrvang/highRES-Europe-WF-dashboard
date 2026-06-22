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

2. Install the extra dependencies:

```bash
pip install streamlit plotly
```

3. You also need to manually add or generate the `intermediate_data/` and `shared_input/` folder (not included in the repo ~7GB).

4. Activate enviornment `mamba activate highres`

5. Run the app (two ways):

#### 5.1 Run model then load dashboard:

The dashboard is now part of `rule all`. Just run the normal command:

```bash
snakemake -c all --configfile config/config_ci.yaml
```

This runs the full pipeline (if needed) and once `results.gdx` exists, opens
the dashboard in your browser. Ctrl+C to stop.

---

#### 5.2 Run dashboard directly

You can also run the dashboard standalone for development. Requires you have a 'work' folder with at least one scenario with a `results.gdx` file:

```bash
streamlit run dashboard/app.py
```

(run from project root, not from `dashboard/`)

## Things to fix/improve

- Path to `intermediate_data/.../europe_onshore.geojson` is hardcoded relative
  to project root. Will break if run from elsewhere.

## Next up

- Keep working with key data, but bring in more dimensions, make it more useful
- Think about displays that makes sense to different stakeholders
- Test with complete scenario (one year) --> change from gdxpd to gams-api?
