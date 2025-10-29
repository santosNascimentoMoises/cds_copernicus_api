import numpy as np

BASE_CONFIG = {
    "DATASET": "satellite-surface-radiation-budget",
    "PRODUCT_FAMILY": "clara_a3",
    "ORIGIN": "eumetsat",
    "TIME_AGGREGATION": "monthly_mean",
    "CLIMATE_DATA_RECORD_TYPE": "thematic_climate_data_record",
    "AREA": [10, -56.5, -8, -30],
    "INITIAL_YEAR": 2006,
    "LAST_YEAR": 2021,
    "YEARS": np.arange(2006, 2021),
    "MONTHS": [f"{m:02d}" for m in range(1, 13)],
}

CONFIG_SATELLITE_SURFACE_RADIATION_BUDGET = {
    "surface_downwelling_shortwave_flux": {
        **BASE_CONFIG,
    },
    "surface_downwelling_longwave_flux": {
        **BASE_CONFIG,
    },
}
