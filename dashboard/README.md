# highRES Dashboard

Status: Proof of concept done. Dashboard runs end-to-end via Snakemake or directly with streamlit command.

## Dashboard structure

```
└── 📁dashboard
    └── 📁data
        ├── country_names.py
        ├── loader.py
        ├── transformer.py
    └── 📁plots
        ├── capacity_map.py
        ├── plot_capacity_pie.py
        ├── technology_bar.py
        ├── tot_trans_flow.py
    └── 📁test_logs
        ├── test_1.txt
        ├── test_2.txt
    └── 📁ui
        └── 📁charts
            ├── tot_trans_flow.py
            ├── total_capacity.py
            ├── zone_capacity_v2.py
            ├── zone_capacity.py
        ├── sidebar.py
    ├── __init__.py
    ├── app.py
    ├── data_loader.py
    ├── README.md
```

## Whats done

- Streamlit dashboard in `dashboard/app.py`
- Loads results from a scenario's `results.gdx` using `data_loader.py`
- `app.py` renders the different components like sidebar and different charts
- The code for the actual plots (graphs) live in the plots folder
- The code for rendering the UI-components like the different plots live in the ui folder

## How to run it

The dashboard is now part of `rule all`. Just run the normal command:

```bash
snakemake -c all --configfile config/config_ci.yaml
```

This runs the full pipeline (if needed) and once `results.gdx` exists, opens
the dashboard in your browser. Ctrl+C to stop.

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
