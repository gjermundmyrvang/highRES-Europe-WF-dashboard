# highRES Dashboard

Status: Milestone 1 done. Dashboard runs end-to-end via Snakemake.

## What works

- Streamlit dashboard in `dashboard/app.py`
- Loads results from a scenario's `results.gdx` using `data_loader.py`
- Shows:
  - KPI numbers (total/new/existing capacity)
  - Stacked bar chart of capacity by technology (total/new/existing toggle)
  - Choropleth map of total capacity per zone (uses geojson shapes in `intermediate_data/`)

## How to run it

The dashboard is now part of `rule all`. Just run the normal command:

```bash
snakemake -c all --configfile config/config_ci.yaml
```

This runs the full pipeline (if needed) and once `results.gdx` exists, opens
the dashboard in your browser. Ctrl+C to stop.

(`dashboard.done` was added as an input to `rule all`, using the same `expand(...)`
pattern as the existing target --> no path-matching issues since it's all built
internally by Snakemake.)

You can also run the dashboard standalone for development:

```bash
streamlit run dashboard/app.py -- --results-path '..path to scenario folder'
```

(run from project root, not from `dashboard/`)

## Known issues / things to fix later

- Path to `intermediate_data/.../europe_onshore.geojson` is hardcoded relative
  to project root. Will break if run from elsewhere.

## Next up (Milestone 2)

- Scenario selector with multiple scenarios
- Technology filter
- Scenario comparison view
