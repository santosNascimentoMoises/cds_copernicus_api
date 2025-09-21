import pandas as pd
import cdsapi

client = cdsapi.Client()

dataset = 'reanalysis-era5-pressure-levels'
request = {
  'product_type': ['reanalysis'],
  'variable': ['geopotential'],
  'year': ['2024'],
  'month': ['03'],
  'day': ['01'],
  'time': ['13:00'],
  'pressure_level': ['1000'],
  'data_format': 'netcdf',
}
target = 'download.netcdf'

client.retrieve(dataset, request, target)

import cdsapi

dataset = "satellite-surface-radiation-budget"
request = {
    "product_family": "clara_a3",
    "origin": "eumetsat",
    "variable": [
        "surface_downwelling_shortwave_flux",
        "surface_downwelling_longwave_flux"
    ],
    "time_aggregation": "monthly_mean",
    "year": ["2006", "2007"],
    "month": [
        "01", "02", "03",
        "04", "05", "06",
        "07", "08", "09",
        "10", "11", "12"
    ],
    "area": [10, -56.5, -8, -30]
}

client = cdsapi.Client()
client.retrieve(dataset, request).download()
