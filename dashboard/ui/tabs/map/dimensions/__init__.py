from . import capacity, cost, storage

# To add a new dimension: create a new module in this folder exposing
# LABEL (str) and render_controls(data, selected) -> MapDimensionResult,
# then register it here. Nothing else in render.py needs to change.
DIMENSIONS = {
    "capacity": capacity,
    "cost": cost,
    "storage": storage,
}
