import xarray as xr
import matplotlib.pyplot as plt

patch = r'/home/moises-ubuntu/UERJ-FILES/demanda_martinho/src/satellite_surface_radiation_budget/data_output'

# Abrir arquivo .nc
# ds = xr.open_dataset(patch + '/mursst.nc')
print(patch + '/surface_downwelling_longwave_flux_2006.nc')
data = patch + '/surface_downwelling_longwave_flux_2006.nc'

import zipfile
import xarray as xr
import io

def open_and_concat_nc_from_zip(zip_path, concat_dim="time"):
    """
    Abre um arquivo .zip contendo múltiplos NetCDF4
    e concatena todos em um único xarray.Dataset.
    """
    datasets = []

    with zipfile.ZipFile(zip_path, "r") as z:
        # pega apenas arquivos .nc
        nc_files = [f for f in z.namelist() if f.endswith(".nc")]
        nc_files.sort()  # garante ordem temporal

        for fname in nc_files:
            with z.open(fname) as f:
                data = f.read()
            file_like = io.BytesIO(data)

            # NetCDF4/HDF5 requer engine="h5netcdf"
            ds = xr.open_dataset(file_like, engine="h5netcdf")
            datasets.append(ds)

    combined = xr.concat(datasets, dim=concat_dim)
    return combined

ds = open_and_concat_nc_from_zip(data)

print(ds)
print(ds.time)

# Inspeção inicial
print(ds)              # Estrutura geral: variáveis, dimensões e atributos
print(ds.variables)    # Lista de variáveis
print(ds.dims)         # Dimensões disponíveis
print(ds.attrs)        # Atributos globais

sst = ds['SDL']
plt.imshow(
        origin="lower",
        cmap="turbo",
        extent=[
            float(sst.longitude.min()),  # min longitude
            float(sst.longitude.max()),  # max longitude
            float(sst.latitude.min()),   # min latitude
            float(sst.latitude.max())    # max latitude
        ],
        aspect="auto"
    )


# sst = ds['sst']
# time = ds['time'][0]

# def plot_imshow_ostia(var,time):
#     frame = sst.isel(time=time)
#     plt.imshow(
#         frame,
#         origin="lower",
#         cmap="turbo",
#         extent=[
#             float(sst.longitude.min()),  # min longitude
#             float(sst.longitude.max()),  # max longitude
#             float(sst.latitude.min()),   # min latitude
#             float(sst.latitude.max())    # max latitude
#         ],
#         aspect="auto"
#     )
#     plt.colorbar(label="SST [C]")
#     plt.xlabel("Longitude")
#     plt.ylabel("Latitude")
#     plt.title(f"MURSST temp em {str(frame['time'].values)[:10]}")
#     plt.savefig(patch +'/output/mursst/'+f"SST em {str(frame['time'].values)[:10]}")
#     plt.close()

# for i in range(len(time)):
#     plot_imshow_ostia(sst, i)