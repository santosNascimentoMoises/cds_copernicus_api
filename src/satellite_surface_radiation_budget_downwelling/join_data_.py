import zipfile
import xarray as xr
import io
import os
import shutil

def open_and_concat_nc_from_zip(zip_path, concat_dim="time", ext=".nc"):
    """
    Abre um arquivo .zip contendo múltiplos NetCDF
    e concatena em um único xarray.Dataset.
    
    Parâmetros:
    -----------
    zip_path : str
        Caminho para o arquivo zipado.
    concat_dim : str
        Dimensão pela qual concatenar (default="time").
    ext : str
        Extensão alvo (default=".nc").
    """

    datasets = []

    with zipfile.ZipFile(zip_path, "r") as z:
        nc_files = sorted([f for f in z.namelist() if f.endswith(ext)])

        for fname in nc_files:
            try:
                with z.open(fname) as f:
                    file_like = io.BytesIO(f.read())
                    ds = xr.open_dataset(file_like, engine="h5netcdf")
                    datasets.append(ds)
            except Exception as e:
                print(f"[WARN] Falha ao abrir {fname}: {e}")

    if not datasets:
        raise ValueError("Nenhum dataset válido encontrado no zip.")

    # Ordena datasets por valor da coordenada 'time' se existir
    if concat_dim in datasets[0].coords:
        datasets.sort(key=lambda d: d[concat_dim].values[0])

    combined = xr.concat(datasets, dim=concat_dim, data_vars="minimal")

    # Fecha datasets individuais para evitar warnings
    for ds in datasets:
        ds.close()

    return combined

# import zipfile
# import xarray as xr
# import io

# def open_and_concat_nc_from_zip(zip_path, concat_dim="time", ext=".nc"):
#     """Abre todos os NetCDFs dentro de um .zip e concatena no eixo indicado"""
#     datasets = []
#     with zipfile.ZipFile(zip_path, "r") as zf:
#         for name in zf.namelist():
#             if name.endswith(ext):
#                 with zf.open(name) as f:
#                     # mantém o buffer em memória
#                     data = io.BytesIO(f.read())
#                     ds = xr.open_dataset(data, engine="h5netcdf",chunks={})
#                     datasets.append(ds)   # força leitura, não depende mais do BytesIO fechado

#     if not datasets:
#         raise ValueError(f"Nenhum NetCDF {ext} encontrado dentro de {zip_path}")

#     if len(datasets) == 1:
#         return datasets[0]
#     else:
#         return xr.concat(datasets, dim=concat_dim)


# ###
# def open_and_concat_from_zip(zip_path, concat_dim="time"):
#     import zipfile, io, xarray as xr

#     datasets = []

#     with zipfile.ZipFile(zip_path, "r") as zf:
#         for name in zf.namelist():
#             if name.endswith((".nc", ".grib", ".grb")):
#                 with zf.open(name) as f:
#                     print('tomar no cu nc')
#                     data = io.BytesIO(f.read())

#                     # 🔍 escolha o engine com base na extensão
#                     if name.endswith(".nc"):
                        
#                         try:
#                             ds = xr.open_dataset(data, engine="h5netcdf", chunks={})
#                         except Exception as e:
#                             raise RuntimeError(f"Erro ao abrir {name} como NetCDF: {e}")

#                     elif name.endswith((".grib", ".grb")):
#                         print('tomar no cu grib')
#                         try:
#                             ds = xr.open_dataset(data, engine="cfgrib")
#                         except Exception as e:
#                             raise RuntimeError(f"Erro ao abrir {name} como GRIB: {e}")

#                     else:
#                         raise ValueError(f"Extensão não reconhecida: {name}")

#                     datasets.append(ds)

#     if not datasets:
#         raise ValueError(f"Nenhum arquivo válido encontrado em {zip_path}")

#     return xr.concat(datasets, dim=concat_dim) if len(datasets) > 1 else datasets[0]

# ###
# def concat_all_zips(zip_dir, output_path=None, concat_dim="time", ext=".nc", var=None):
#     os.makedirs(zip_dir + "/tmp", exist_ok=True)
#     """
#     Concatena NetCDFs contidos em múltiplos arquivos .zip dentro de um diretório
#     e retorna um único xarray.Dataset.

#     Parâmetros:
#     -----------
#     zip_dir : str
#         Caminho para o diretório contendo os arquivos zipados.
#     output_path : str, opcional
#         Caminho para salvar o NetCDF final. Se None, não salva.
#     concat_dim : str
#         Dimensão pela qual concatenar (default="time").
#     ext : str
#         Extensão alvo dos NetCDFs (default=".nc").
#     var : str, opcional
#         Parte do nome do arquivo zip que deve ser utilizada como filtro.
#         Exemplo: "surface_downwelling_shortwave_flux"
#     """

#     # datasets = []

#     for fname in sorted(os.listdir(zip_dir)):
#         if fname.endswith(".zip"):
#             # 🔑 Se 'var' foi especificado, só processa arquivos cujo nome contém 'var'
#             if var and var not in fname:
#                 continue  

#             zip_path = os.path.join(zip_dir, fname)
#             print(f"[INFO] Processando {zip_path}...")

#             try:
#                 ds = open_and_concat_from_zip(zip_path, concat_dim=concat_dim)
#                 ds.to_netcdf(zip_dir + f"/tmp/{fname}.nc")
#                 # datasets.append(ds)

#             except Exception as e:
#                 print(f"[WARN] Falha ao processar {zip_path}: {e}")

#     combined = xr.open_mfdataset(zip_dir + "/tmp/*.nc", combine="nested", concat_dim="time",join="outer", chunks={})
    
#     if "expver" in combined:
#         combined = combined.drop_vars("expver")

#     # Salva se solicitado
#     if output_path:
#         combined.to_netcdf(output_path,mode="w")
#         print(f"[INFO] Dataset combinado salvo em {output_path}")

#     for f in os.listdir(zip_dir + "/tmp"):
#         os.remove(os.path.join(zip_dir + "/tmp", f))

#     return combined
