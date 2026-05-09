import os
import glob 
import imageio
import matplotlib
matplotlib.use("Agg")

from netCDF4 import Dataset
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
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
# CONFIGURAÇÕES
# ==========================================================
base_output_dir = "VENTO_CORES_ALTURA"
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

interval_dam = 3.0 
wind_levels = np.arange(0, 45, 2)

wind_bounds = [0, 5, 10, 15, 20,
               25, 30, 35, 40,
               45, 55, 65, 70,
               80, 100, 
               120, 140, 160, 180, 200]

wind_colors = [
    "#08306b", "#08519c", "#2171b5", "#6baed6",
    "#238b45", "#41ab5d", "#feb24c", "#fd8d3c",
    "#f03b20", "#e31a1c", "#bd0026", "#800026",
    "#7a0177", "#6a00a8",
    "#4b0082", "#3b006b", "#2b005a", "#1b0049", "#0b0038"
]

wind_cmap = ListedColormap(wind_colors)
wind_norm = BoundaryNorm(wind_bounds, wind_cmap.N)

# ==========================================================
# LOOP POR DOMÍNIO
# ==========================================================
for dom in domains:

    print(f"\n=== Processando domínio {dom} ===")

    files = glob.glob(f"wrfout_{dom}*")
    if not files:
        print(f"Arquivo wrfout para {dom} não encontrado. Pulando domínio.")
        continue

    wrf_file = sorted(files)[0]
    print(f"Arquivo encontrado: {wrf_file}")

    ncfile = Dataset(wrf_file)
    ntimes = len(ncfile.dimensions["Time"])

    start_time_val = getvar(ncfile, "times", timeidx=0).values
    start_time_str = str(start_time_val)
    start_time_dt = datetime.strptime(start_time_str[:19], "%Y-%m-%dT%H:%M:%S")
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

            time_val = getvar(ncfile, "times", timeidx=t).values
            time_str = str(time_val)
            time_dt = datetime.strptime(time_str[:19], "%Y-%m-%dT%H:%M:%S")
            time_dt = time_dt.replace(minute=0, second=0, microsecond=0)
            
            time_label_file = time_dt.strftime("%Y-%m-%d_%H")
            valid_time_label = time_dt.strftime("%d/%m/%Y %H:%M UTC")

            pressure = getvar(ncfile, "pressure", timeidx=t)

            if level_label == "surface":
                u = getvar(ncfile, "U10", timeidx=t)
                v = getvar(ncfile, "V10", timeidx=t)
                u = u * 3.6 
                v = v * 3.6

                slp = getvar(ncfile, "slp", timeidx=t)
                field_contour = smooth2d(slp, 3, cenweight=4)
                contour_levels = np.arange(960, 1040, 2)
            else:
                u3d = getvar(ncfile, "ua", timeidx=t)
                v3d = getvar(ncfile, "va", timeidx=t)
                z3d = getvar(ncfile, "z", timeidx=t)

                u = interplevel(u3d, pressure, level_value)
                v = interplevel(v3d, pressure, level_value)
                u = u * 3.6 
                v = v * 3.6

                z = interplevel(z3d, pressure, level_value) / 10.0
                field_contour = smooth2d(z, 3, cenweight=4)

                zmin = np.floor(np.nanmin(to_np(field_contour)) / interval_dam) * interval_dam
                zmax = np.ceil(np.nanmax(to_np(field_contour)) / interval_dam) * interval_dam
                contour_levels = np.arange(zmin, zmax + interval_dam, interval_dam)

            wspd = np.sqrt(u**2 + v**2)
            lats, lons = latlon_coords(wspd)
            cart_proj = get_cartopy(wspd)

            fig = plt.figure(figsize=(12, 6))
            ax = plt.axes(projection=cart_proj)

            ax.set_xlim(cartopy_xlim(wspd))
            ax.set_ylim(cartopy_ylim(wspd))

            states = NaturalEarthFeature(
                category="cultural",
                name="admin_1_states_provinces_lines",
                scale="50m",
                facecolor="none"
            )

            ax.add_feature(states, linewidth=0.8, edgecolor="gray")
            ax.add_feature(cfeature.BORDERS, linewidth=0.8)
            ax.coastlines(resolution="50m", linewidth=1.2)

            cf = ax.contourf(
                to_np(lons), to_np(lats),
                to_np(wspd),
                levels=wind_bounds,
                cmap=wind_cmap,
                norm=wind_norm,
                extend="max",
                transform=crs.PlateCarree()
            )

            cbar = plt.colorbar(
                cf,
                ax=ax,
                pad=0.02,
                ticks=[0, 20, 40, 70, 100, 140, 180, 200]
            )
            cbar.set_label("Velocidade do vento (km h⁻¹)")

            cs = ax.contour(
                to_np(lons), to_np(lats),
                to_np(field_contour),
                levels=contour_levels,
                colors="black",
                linewidths=1.0,
                transform=crs.PlateCarree()
            )
            ax.clabel(cs, fontsize=8)

            ax.gridlines(draw_labels=False, linestyle="dotted")

            if level_label == "surface":
                title_var = "Pressão ao Nível do Mar (hPa)"
            else:
                title_var = "Altura Geopotencial (dam)"

            plt.title(
                f"{title_var} e Velocidade do Vento \n" f"WRF 4.7.1 | Domínio {dom.upper()} | {level_label}\n"
                f"Início: {start_time_label} | Válido: {valid_time_label}"
            )

            outfile = os.path.join(
                level_dir, f"WINDSPD_{dom}_{level_label}_{time_label_file}.png"
            )
            plt.savefig(outfile, dpi=300, bbox_inches="tight")
            plt.close(fig) 

        # ==================================================
        # GIF
        # ==================================================
        png_files = sorted(f for f in os.listdir(level_dir) if f.endswith(".png"))

        if png_files:
            gif_path = os.path.join(level_dir, f"WINDSPD_{dom}_{level_label}.gif")
            with imageio.get_writer(gif_path, mode="I", fps=gif_fps) as writer:
                for png in png_files:
                    writer.append_data(
                        imageio.imread(os.path.join(level_dir, png))
                    )
            print(f"GIF salvo em: {gif_path}")

    ncfile.close()

print("\nProcessamento finalizado")
