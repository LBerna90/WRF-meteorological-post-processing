import os
import glob
import imageio.v2 as imageio
import matplotlib
matplotlib.use("Agg")

import numpy as np
import matplotlib.pyplot as plt

from netCDF4 import Dataset
from datetime import datetime

import cartopy.crs as crs
import cartopy.feature as cfeature
from cartopy.feature import NaturalEarthFeature

from matplotlib.colors import ListedColormap, BoundaryNorm

from wrf import (
    getvar, to_np, latlon_coords,
    get_cartopy, cartopy_xlim, cartopy_ylim,
    smooth2d
)

# ==========================================================
# CONFIGURAÇÕES GERAIS
# ==========================================================
base_output_dir = "PRECIPITAÇÃO"
os.makedirs(base_output_dir, exist_ok=True)

domains = ["d01", "d02", "d03"]
gif_fps = 1

acc_windows = {
    "01h": 1, "03h": 3, "06h": 6, "12h": 12, "24h": 24
}

levels = [0.01, 1, 2, 5, 10, 20, 30, 40, 60, 80, 100, 120, 150, 200, 300]
colors = [
    "#66ff00", "#33cc00", "#009900", "#006600", "#004d00",
    "#08306b", "#08519c", "#2171b5", "#6baed6",
    "#54278f", "#756bb1", "#9e9ac8",
    "#fb6a4a", "#cb181d"
]

cmap = ListedColormap(colors)
norm = BoundaryNorm(levels, ncolors=len(colors), clip=False)

# ==========================================================
# LOOP POR DOMÍNIO
# ==========================================================
for dom in domains:

    print(f"\n=== Processando domínio {dom} ===")

    files = sorted(glob.glob(f"wrfout_{dom}*"))
    if not files:
        print("Nenhum wrfout encontrado.")
        continue

    ncfile = Dataset(files[0])
    ntimes = len(ncfile.dimensions["Time"])

    # ======================================================
    # LEITURA ÚNICA DOS DADOS (CACHE)
    # ======================================================
    print("Carregando dados...")

    all_rainc = np.empty((ntimes,), dtype=object)
    all_rainnc = np.empty((ntimes,), dtype=object)
    all_slp = np.empty((ntimes,), dtype=object)
    all_times_dt = [] 
    all_times_file = []

    slp0 = getvar(ncfile, "slp", timeidx=0)
    
    start_time_str = str(slp0.Time.values)[:19]
    start_time_dt = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S")
    start_time_dt = start_time_dt.replace(minute=0, second=0, microsecond=0)
    start_time_label = start_time_dt.strftime("%d/%m/%Y %H:%M UTC")

    lats, lons = latlon_coords(slp0)
    lats = to_np(lats)
    lons = to_np(lons)

    cart_proj = get_cartopy(slp0)
    xlim = cartopy_xlim(slp0)
    ylim = cartopy_ylim(slp0)

    for t in range(ntimes):
        rainc = getvar(ncfile, "RAINC", timeidx=t)
        rainnc = getvar(ncfile, "RAINNC", timeidx=t)
        slp = getvar(ncfile, "slp", timeidx=t)

        all_rainc[t] = to_np(rainc)
        all_rainnc[t] = to_np(rainnc)
        all_slp[t] = to_np(smooth2d(slp, 3, cenweight=4))

        time_str = str(slp.Time.values)[:19]
        dt_obj = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
        dt_obj = dt_obj.replace(minute=0, second=0, microsecond=0)
        all_times_dt.append(dt_obj)
        all_times_file.append(dt_obj.strftime("%Y-%m-%d_%H"))

    states = NaturalEarthFeature(
        category="cultural",
        name="admin_1_states_provinces_lines",
        scale="50m",
        facecolor="none"
    )

    slp_levels = {
        "low": (np.arange(960, 1009, 2), "red"),
        "mid": (np.arange(1009, 1020, 2), "black"),
        "high": (np.arange(1020, 1060, 2), "blue")
    }

    # ======================================================
    # LOOP POR JANELA DE ACUMULAÇÃO
    # ======================================================
    for label, acc_h in acc_windows.items():

        print(f"--- Acumulado {label} ---")

        outdir = os.path.join(base_output_dir, dom, label)
        os.makedirs(outdir, exist_ok=True)

        fig = plt.figure(figsize=(12, 6))
        ax = plt.axes(projection=cart_proj)

        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        ax.add_feature(states, linewidth=0.8, edgecolor="gray")
        ax.add_feature(cfeature.BORDERS, linewidth=0.8)
        ax.coastlines(resolution="50m", linewidth=1.2)

        gl = ax.gridlines(draw_labels=True, linestyle="dotted")
        gl.right_labels = False
        gl.top_labels = False
        gl.x_inline = False

        cf = None
        cs_list = []
        labels_list = []
        cbar = None

        for t in range(acc_h, ntimes):

            rain = (
                (all_rainc[t] + all_rainnc[t]) -
                (all_rainc[t-acc_h] + all_rainnc[t-acc_h])
            )
            rain = np.maximum(rain, 0.0)

            if cf is not None:
                cf.remove()
                for cs in cs_list:
                    cs.remove()

            cf = ax.contourf(
                lons, lats, rain,
                levels=levels,
                cmap=cmap,
                norm=norm,
                extend="max",
                transform=crs.PlateCarree()
            )

            cs_list = []
            for lvls, color in slp_levels.values():
                cs = ax.contour(
                    lons, lats, all_slp[t],
                    levels=lvls,
                    colors=color,
                    linewidths=1.0,
                    linestyles="dashed",
                    transform=crs.PlateCarree()
                )
                cs_list.append(cs)

            if t % 2 == 0:
                for cs in cs_list:
                    lbls = ax.clabel(cs, fontsize=8)
                    labels_list.extend(lbls)

            if cbar is None:
                cbar = plt.colorbar(
                    cf, ax=ax,
                    shrink=0.95,
                    pad=0.02,
                    label="Precipitação acumulada (mm)"
                )

            valid_time_label = all_times_dt[t].strftime("%d/%m/%Y %H:%M UTC")

            ax.set_title(
                f"Precipitação acumulada em {label}\n"
                f"WRF 4.7.1 | Domínio {dom.upper()}\n"
                f"Início: {start_time_label} | Válido: {valid_time_label}"
            )

            outfile = os.path.join(
                outdir, f"PREC_{dom}_{label}_{all_times_file[t]}.png"
            )

            plt.savefig(outfile, dpi=150, bbox_inches="tight")

        plt.close(fig)

        # ==================================================
        # GIF
        # ==================================================
        pngs = sorted(f for f in os.listdir(outdir) if f.endswith(".png"))
        if pngs:
            gif_path = os.path.join(outdir, f"PREC_{dom}_{label}.gif")
            with imageio.get_writer(gif_path, mode="I", fps=gif_fps) as writer:
                for p in pngs:
                    writer.append_data(
                        imageio.imread(os.path.join(outdir, p))
                    )

    ncfile.close()

print("\nProcessamento finalizado.")
