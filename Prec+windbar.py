import os
import glob 
import imageio.v2 as imageio
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
    to_np, getvar, smooth2d, get_cartopy,
    cartopy_xlim, cartopy_ylim, latlon_coords
)

# ==========================================================
# CONFIGURAÇÕES GERAIS
# ==========================================================
base_output_dir = "PREC+WINDBAR"
os.makedirs(base_output_dir, exist_ok=True)

gif_fps = 1

domains = ["d01", "d02", "d03"]

acc_windows = {
    "01h": 1,
    "03h": 3,
    "06h": 6,
    "12h": 12,
    "24h": 24
}

levels = [
    0.01, 1, 2, 5, 10, 20,
    30, 40, 60, 80,
    100, 120, 150,
    200, 300
]

colors = [
    "#66ff00", "#33cc00", "#009900", "#006600", "#004d00",
    "#08306b", "#08519c", "#2171b5", "#6baed6",
    "#54278f", "#756bb1", "#9e9ac8",
    "#fb6a4a", "#cb181d"
]

cmap = ListedColormap(colors)
norm = BoundaryNorm(levels, ncolors=len(colors), clip=False)

wind_skip = 7

# ==========================================================
# LOOP POR DOMÍNIO
# ==========================================================
for dom in domains:

    print(f"\n=== Processando domínio {dom} ===")

    files = glob.glob(f"wrfout_{dom}*")
    
    if not files:
        print(f"Nenhum arquivo wrfout encontrado para o domínio {dom}. Pulando...")
        continue
    
    wrf_file = sorted(files)[0]
    print(f"Arquivo encontrado: {wrf_file}")

    ncfile = Dataset(wrf_file)
    ntimes = len(ncfile.dimensions["Time"])

    start_time_val = getvar(ncfile, "times", timeidx=0).values
    start_time_str = str(start_time_val)[:19]
    start_time_dt = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S")
    start_time_label = start_time_dt.strftime("%d/%m/%Y %H:%M UTC")

    # ======================================================
    # LOOP POR JANELA DE ACUMULAÇÃO
    # ======================================================
    for label, acc_h in acc_windows.items():

        print(f"\n--- Acumulado de {label} ---")

        acc_dir = os.path.join(base_output_dir, dom, label)
        os.makedirs(acc_dir, exist_ok=True)

        # ==================================================
        # LOOP TEMPORAL
        # ==================================================
        for t in range(acc_h, ntimes):

            print(f"Domínio {dom} | {label} | Tempo {t}/{ntimes-1}")

            # -----------------------------
            # CHUVA ACUMULADA
            # -----------------------------
            rainc_now = getvar(ncfile, "RAINC", timeidx=t)
            rainnc_now = getvar(ncfile, "RAINNC", timeidx=t)

            rainc_prev = getvar(ncfile, "RAINC", timeidx=t - acc_h)
            rainnc_prev = getvar(ncfile, "RAINNC", timeidx=t - acc_h)

            rain = (rainc_now + rainnc_now) - (rainc_prev + rainnc_prev)
            rain = np.maximum(to_np(rain), 0.0)

            # -----------------------------
            # VENTO 10 m
            # -----------------------------
            u10 = getvar(ncfile, "U10", timeidx=t)
            v10 = getvar(ncfile, "V10", timeidx=t)

            # -----------------------------
            # SLP
            # -----------------------------
            slp = getvar(ncfile, "slp", timeidx=t)
            slp_smooth = smooth2d(slp, 3, cenweight=4)
            slp_np = to_np(slp_smooth)

            # -----------------------------
            # COORDENADAS
            # -----------------------------
            lats, lons = latlon_coords(rainc_now)
            cart_proj = get_cartopy(rainc_now)

            # -----------------------------
            # TEMPO
            # -----------------------------
            time_str = str(rainc_now.Time.values)
            time_dt = datetime.strptime(time_str[:19], "%Y-%m-%dT%H:%M:%S")
            time_dt = time_dt.replace(minute=0, second=0, microsecond=0)
                   
            time_label_file = time_dt.strftime("%Y-%m-%d_%H")
            valid_time_label = time_dt.strftime("%d/%m/%Y %H:%M UTC")

            # ==================================================
            # FIGURA
            # ==================================================
            fig = plt.figure(figsize=(12, 6))
            ax = plt.axes(projection=cart_proj)

            ax.set_xlim(cartopy_xlim(rainc_now))
            ax.set_ylim(cartopy_ylim(rainc_now))

            states = NaturalEarthFeature(
                category="cultural",
                name="admin_1_states_provinces_lines",
                scale="50m",
                facecolor="none"
            )

            ax.add_feature(states, linewidth=0.8)
            ax.add_feature(cfeature.BORDERS, linewidth=0.8)
            ax.coastlines(resolution="50m", linewidth=1.2)

            # -----------------------------
            # CHUVA
            # -----------------------------
            cf = ax.contourf(
                to_np(lons), to_np(lats), rain,
                levels=levels,
                cmap=cmap,
                norm=norm,
                extend="max",
                transform=crs.PlateCarree()
            )

            # -----------------------------
            # ISÓBARAS COLORIDAS
            # -----------------------------
            levels_low = np.arange(960, 1009, 2)
            levels_mid = np.arange(1009, 1018, 2)
            levels_high = np.arange(1018, 1060, 2)

            cs_low = ax.contour(
                to_np(lons), to_np(lats), slp_np,
                levels=levels_low, colors="red", linestyles="dashed",
                linewidths=1.0, transform=crs.PlateCarree()
            )

            cs_mid = ax.contour(
                to_np(lons), to_np(lats), slp_np,
                levels=levels_mid, colors="black", linestyles="dashed",
                linewidths=1.0, transform=crs.PlateCarree()
            )

            cs_high = ax.contour(
                to_np(lons), to_np(lats), slp_np,
                levels=levels_high, colors="blue", linestyles="dashed",
                linewidths=1.0, transform=crs.PlateCarree()
            )

            ax.clabel(cs_low, fontsize=8)
            ax.clabel(cs_mid, fontsize=8)
            ax.clabel(cs_high, fontsize=8)

            # -----------------------------
            # BARBELAS
            # -----------------------------
            ms_to_kt = 1.94384
            u10_kt = u10 * ms_to_kt
            v10_kt = v10 * ms_to_kt
            
            ax.barbs(
                to_np(lons[::wind_skip, ::wind_skip]),
                to_np(lats[::wind_skip, ::wind_skip]),
                to_np(u10_kt[::wind_skip, ::wind_skip]),
                to_np(v10_kt[::wind_skip, ::wind_skip]),
                length=5, linewidth=0.8, transform=crs.PlateCarree(), zorder=10
            )

            # -----------------------------
            # COLORBAR
            # -----------------------------
            plt.colorbar(
                cf, ax=ax, shrink=0.95, pad=0.02,
                label="Precipitação acumulada (mm)"
            )

            ax.gridlines(draw_labels=False, linestyle="dotted")

            plt.title(
                f"Precipitação acumulada em {label}, Vento a 10 m e Pressão NMM\n"
                f"WRF 4.7.1 | Domínio {dom.upper()}\n"
                f"Início: {start_time_label} | Válido: {valid_time_label}"
            )

            outfile = os.path.join(
                acc_dir, f"PREC_{dom}_{label}_{time_label_file}.png"
            )

            plt.savefig(outfile, dpi=300, bbox_inches="tight")
            plt.close(fig)

        # ==================================================
        # GIF
        # ==================================================
        png_files = sorted(
            f for f in os.listdir(acc_dir) if f.endswith(".png")
        )

        if png_files:
            gif_path = os.path.join(acc_dir, f"PREC_{dom}_{label}.gif")
            with imageio.get_writer(gif_path, mode="I", fps=gif_fps) as writer:
                for png in png_files:
                    writer.append_data(
                        imageio.imread(os.path.join(acc_dir, png))
                    )
            print(f"GIF salvo em: {gif_path}")
        else:
            print("Nenhuma imagem para GIF.")

    ncfile.close()

print("\nProcessamento finalizado.")
