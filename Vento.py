import os
import glob 
import imageio
import matplotlib
matplotlib.use("Agg")

from netCDF4 import Dataset
import matplotlib.pyplot as plt
import cartopy.crs as crs
import cartopy.feature as cfeature
import numpy as np
from cartopy.feature import NaturalEarthFeature
from datetime import datetime

from wrf import (
    to_np, getvar, get_cartopy,
    cartopy_xlim, cartopy_ylim,
    latlon_coords, smooth2d, interplevel
)

# ==========================================================
# CONFIGURAÇÕES GERAIS
# ==========================================================
base_output_dir = "VENTO_SUPERFICIE_ALTURA"
os.makedirs(base_output_dir, exist_ok=True)

gif_fps = 1
domains = ["d01", "d02", "d03"]

pressure_levels = {
    "surface": None,
    "925hPa": 925,
    "850hPa": 850,
    "700hPa": 700,
    "500hPa": 500,
    "300hPa": 300,
    "250hPa": 250,
    "200hPa": 200
}

wind_skip = 7
interval_dam = 3.0  

# ==========================================================
# LOOP POR DOMÍNIO
# ==========================================================
for dom in domains:

    print(f"\n=== Processando domínio {dom} ===")

    # Busca arquivos ---
    files = glob.glob(f"wrfout_{dom}*")
    if not files:
        print(f"Arquivo wrfout para {dom} não encontrado. Pulando domínio.")
        continue

    # Ordena e pega o primeiro encontrado
    wrf_file = sorted(files)[0]
    print(f"Arquivo encontrado: {wrf_file}")
    # ---------------------------------------------------

    ncfile = Dataset(wrf_file)
    ntimes = len(ncfile.dimensions["Time"])

    start_time_val = getvar(ncfile, "times", timeidx=0).values
    start_time_str = str(start_time_val)[:19]
    start_time_dt = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S")
    start_time_label = start_time_dt.strftime("%d/%m/%Y %H:%M UTC")

    # ======================================================
    # LOOP POR NÍVEL
    # ======================================================
    for level_label, level_value in pressure_levels.items():

        print(f"\n--- Nível {level_label} ---")

        level_dir = os.path.join(base_output_dir, dom, level_label)
        os.makedirs(level_dir, exist_ok=True)

        # ==================================================
        # LOOP TEMPORAL
        # ==================================================
        for t in range(ntimes):

            print(f"Domínio {dom} | {level_label} | Tempo {t}/{ntimes-1}")

            # --------------------------------------------------
            # TEMPO
            # --------------------------------------------------
            time_val = getvar(ncfile, "times", timeidx=t).values
            time_str = str(time_val)
            time_dt = datetime.strptime(time_str[:19], "%Y-%m-%dT%H:%M:%S")       
            time_dt = time_dt.replace(minute=0, second=0, microsecond=0)  
            
            time_label_file = time_dt.strftime("%Y-%m-%d_%H")
            valid_time_label = time_dt.strftime("%d/%m/%Y %H:%M UTC")

            # --------------------------------------------------
            # VARIÁVEIS
            # --------------------------------------------------
            pressure = getvar(ncfile, "pressure", timeidx=t)

            if level_label == "surface":

                u = getvar(ncfile, "U10", timeidx=t)
                v = getvar(ncfile, "V10", timeidx=t)
                u = u * 1.94384 
                v = v * 1.94384

                slp = getvar(ncfile, "slp", timeidx=t)
                slp_smooth = smooth2d(slp, 3, cenweight=4)

                contour_levels = np.arange(960, 1040, 2)
                field_contour = slp_smooth
                ref_var = slp

            else:
                u3d = getvar(ncfile, "ua", timeidx=t)
                v3d = getvar(ncfile, "va", timeidx=t)
                z3d = getvar(ncfile, "z", timeidx=t)  

                u = interplevel(u3d, pressure, level_value)
                v = interplevel(v3d, pressure, level_value)
                u = u * 1.94384 
                v = v * 1.94384

                z_level = interplevel(z3d, pressure, level_value)
                z_dam = z_level / 10.0  

                z_dam_smooth = smooth2d(z_dam, 3, cenweight=4)

                zmin = np.nanmin(to_np(z_dam_smooth))
                zmax = np.nanmax(to_np(z_dam_smooth))

                zmin = np.floor(zmin / interval_dam) * interval_dam
                zmax = np.ceil(zmax / interval_dam) * interval_dam

                contour_levels = np.arange(
                    zmin, zmax + interval_dam, interval_dam
                )

                field_contour = z_dam_smooth
                ref_var = u

            # --------------------------------------------------
            # COORDENADAS
            # --------------------------------------------------
            lats, lons = latlon_coords(ref_var)
            cart_proj = get_cartopy(ref_var)

            # ==================================================
            # FIGURA
            # ==================================================
            fig = plt.figure(figsize=(12, 6))
            ax = plt.axes(projection=cart_proj)

            ax.set_xlim(cartopy_xlim(ref_var))
            ax.set_ylim(cartopy_ylim(ref_var))

            states = NaturalEarthFeature(
                category="cultural",
                name="admin_1_states_provinces_lines",
                scale="50m",
                facecolor="none"
            )

            ax.add_feature(states, linewidth=0.8, edgecolor="gray")
            ax.add_feature(cfeature.BORDERS, linewidth=0.8)
            ax.coastlines(resolution="50m", linewidth=1.2)

            # -----------------------------
            # ISÓPLETAS
            # -----------------------------
            cs = ax.contour(
                to_np(lons), to_np(lats),
                to_np(field_contour),
                levels=contour_levels,
                colors="black",
                linewidths=1.0,
                transform=crs.PlateCarree()
            )
            ax.clabel(cs, fontsize=8)

            # -----------------------------
            # BARBELAS DE VENTO
            # -----------------------------
            ax.barbs(
                to_np(lons[::wind_skip, ::wind_skip]),
                to_np(lats[::wind_skip, ::wind_skip]),
                to_np(u[::wind_skip, ::wind_skip]),
                to_np(v[::wind_skip, ::wind_skip]),
                length=5,
                linewidth=0.8,
                transform=crs.PlateCarree(),
                zorder=10
            )

            ax.gridlines(draw_labels=False, linestyle="dotted")

            if level_label == "surface":
                title_var = "Pressão ao Nível do Mar (hPa)"
            else:
                title_var = "Altura Geopotencial (dam)"

            # TÍTULO 
            plt.title(
                f"{title_var} e Vento — {level_label}\n"
                f"Domínio {dom.upper()} | WRF 4.7.1 \n"
                f"Início: {start_time_label} | Válido: {valid_time_label}"
            )

            outfile = os.path.join(
                level_dir, f"WIND_{dom}_{level_label}_{time_label_file}.png"
            )
            plt.savefig(outfile, dpi=300, bbox_inches="tight")
            plt.close(fig) 

        # ==================================================
        # GIF
        # ==================================================
        png_files = sorted(
            f for f in os.listdir(level_dir) if f.endswith(".png")
        )

        if png_files:
            gif_path = os.path.join(
                level_dir, f"WIND_{dom}_{level_label}.gif"
            )
            with imageio.get_writer(gif_path, mode="I", fps=gif_fps) as writer:
                for png in png_files:
                    writer.append_data(
                        imageio.imread(os.path.join(level_dir, png))
                    )
            print(f"GIF salvo em: {gif_path}")

    ncfile.close()

print("\nProcessamento de vento, pressão de superfície e altura geopotencial finalizado.")
