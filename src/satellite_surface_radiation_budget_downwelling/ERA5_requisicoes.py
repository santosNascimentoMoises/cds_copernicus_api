import os
import numpy as np
import cdsapi
from concurrent.futures import ThreadPoolExecutor

# diretórios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "data_output")
os.makedirs(OUTPUT_PATH, exist_ok=True)

# config ERA5
DATASET = "reanalysis-era5-single-levels"
VARIABLES = ["mean_surface_net_long_wave_radiation_flux"]

POINTS = {
    'A':[5.00001,-50.00001,5,-50],
    'B':[0.00001,-45.00001,0,-45],
    'C':[5.00001,-35.00001,5,-35],
    'D':[0.00001,-45.00001,0,-45],
    'E':[0.00001,-35.00001,0,-35],
    'F':[-2.5,-35.00001,-2.500001,-35],
}

MONTHS = [f"{m:02d}" for m in range(1, 13)]
DAYS = [f"{d:02d}" for d in range(1, 32)]
HOURS = [f"{h:02d}:00" for h in range(24)]

DATA_FORMAT = "grib"
DOWNLOAD_FORMAT = "zip"
PRODUCT_TYPE = "reanalysis"

DECADES = [
    list(range(2006, 2017)),
    list(range(2017, 2021))
]

def build_request(variable, area, years):
    return {
        "product_type": [PRODUCT_TYPE],
        "variable": [variable],
        "year": [str(y) for y in years],
        "month": MONTHS,
        "day": DAYS,
        "time": HOURS,
        "area": area,
        "data_format": DATA_FORMAT,
        "download_format": DOWNLOAD_FORMAT
    }

def retrieve_data(var, point_name, decade_years, area):
    client = cdsapi.Client()
    request = build_request(var, area, decade_years)
    target = os.path.join(
        OUTPUT_PATH,
        f"{var}_{point_name}_{decade_years[0]}-{decade_years[-1]}.zip"
    )
    print(f"→ Iniciando download {var} {point_name} ({decade_years[0]}–{decade_years[-1]})")
    client.retrieve(DATASET, request, target)
    print(f"✔ Download finalizado: {target}")

def main():
    with ThreadPoolExecutor(max_workers=1000) as executor:  # ajuste o paralelismo conforme sua rede
        futures = []
        for var in VARIABLES:
            for point_name, area in POINTS.items():
                for decade_years in DECADES:
                    futures.append(
                        executor.submit(retrieve_data, var, point_name, decade_years, area)
                    )
        # opcional: aguardar finalização
        for f in futures:
            f.result()

if __name__ == "__main__":
    main()
