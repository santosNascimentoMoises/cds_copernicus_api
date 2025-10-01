import xarray as xr

# opem file
ds = xr.open_dataset('download.netcdf')

print(ds)
