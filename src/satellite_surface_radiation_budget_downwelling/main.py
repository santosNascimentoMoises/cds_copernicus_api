import os
import cdsapi
import numpy as np

# make data output patch
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "data_output")
print(BASE_DIR)
os.makedirs(OUTPUT_PATH, exist_ok=True)

# config to API
DATASET = "satellite-surface-radiation-budget"
PRODUCT_FAMILY = "clara_a3"
ORIGIN = "eumetsat"
VARIABLES = [
    "surface_downwelling_shortwave_flux",
    "surface_downwelling_longwave_flux",
]
TIME_AGGREGATION = "monthly_mean"
CLIMATE_DATA_RECORD_TYPE = "thematic_climate_data_record"
AREA = [10, -56.5, -8, -30]  # [N, W, S, E]

INITIAL_YEAR = 2006
LAST_YEAR = 2021
YEARS = np.arange(INITIAL_YEAR, LAST_YEAR)

MONTHS = [
    "01", "02", "03",
    "04", "05", "06",
    "07", "08", "09",
    "10", "11", "12"
    ]

def build_request(variable,year):
    return {
        "product_family": PRODUCT_FAMILY,
        "origin": ORIGIN,
        "variable": [variable],
        "climate_data_record_type": CLIMATE_DATA_RECORD_TYPE,
        "time_aggregation": TIME_AGGREGATION,
        "year": [str(year)],
        "month": MONTHS,
        "area": AREA,
        "data_format": "netcdf",
    }

def main():
    client = cdsapi.Client()
    for var in VARIABLES:
        for year in YEARS:
            print(f"downloading data {var} {year}")
            request = build_request(var, year)
            target = os.path.join(OUTPUT_PATH, f"{var}_{year}.zip")
            client.retrieve(DATASET, request, target)

if __name__ == "__main__":
    main()
