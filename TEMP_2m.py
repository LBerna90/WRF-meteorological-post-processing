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
base_output_dir = "Temperatura_PNMM"
os.makedirs(base_output_dir, exist_ok=True)

gif_fps = 2

# Níveis
slp_levels = np.arange(980, 1040, 2)      # hPa
t_levels   = np.arange(-10, 40, 2)        # °C

domains = ["d01", "d02", "d03"]

# ==========================================================
# LOOP POR DOMÍNIO
# ==========================================================
for dom in domains:

    print(f"\n=== Processando domínio {dom} ===")

    # Busca arquivos
    files = glob.glob(f"wrfout_{dom}*")

    if not files:
        print(f"Arquivo wrfout para {dom} não encontrado. Pulando domínio.")
        continue

    wrf_file = sorted(files)[0]
    print(f"Arquivo encontrado: {wrf_file}")

    dom_output_dir = os.path.join(base_output_dir, dom)
    os.makedirs(dom_output_dir, exist_ok=True)

    ncfile = Dataset(wrf_file)
    ntimes = len(ncfile.dimensions["Time"])

    temp_slp = getvar(ncfile, "slp", timeidx=0)
    start_time_str = str(temp_slp.Time.values)[:19]
    start_time_dt = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S")
    time_dt = time_dt.replace(minute=0, second=0, microsecond=0)
    start_time_label = start_time_dt.strftime("%d/%m/%Y %H:%M UTC")
  

    # Configuração da densidade dos valores por domínio
    if dom == "d01":
        step = 6
        font_size = 6
        min_dist_px = 25
    elif dom == "d02":
        step = 10
        font_size = 5
        min_dist_px = 35
    elif dom == "d03":
        step = 14
        font_size = 4
        min_dist_px = 45

    # ======================================================
    # LOOP NO TEMPO
    # ======================================================
    for t in range(ntimes):

        print(f"Domínio {dom} | Tempo {t+1}/{ntimes}")

        # Variáveis
        slp = getvar(ncfile, "slp", timeidx=t)
        slp = smooth2d(slp, 3, cenweight=4)
        t2 = getvar(ncfile, "T2", timeidx=t) - 273.15  # Kelvin → °C

        lats, lons = latlon_coords(slp)
        cart_proj = get_cartopy(slp)

        # Tratamento de tempo
        time_str = str(slp.Time.values)
        time_dt = datetime.strptime(time_str[:19], "%Y-%m-%dT%H:%M:%S")
        time_dt = time_dt.replace(minute=0, second=0, microsecond=0)
        
        time_label_file = time_dt.strftime("%Y-%m-%d_%H")
        valid_time_label = time_dt.strftime("%d/%m/%Y %H:%M UTC")

        # ==================================================
        # FIGURA
        # ==================================================
        fig = plt.figure(figsize=(12, 6))
        ax = plt.axes(projection=cart_proj)

        ax.set_xlim(cartopy_xlim(slp))
        ax.set_ylim(cartopy_ylim(slp))

        states = NaturalEarthFeature(
            category="cultural",
            name="admin_1_states_provinces_lines",
            scale="50m",
            facecolor="none"
        )
        ax.add_feature(states, linewidth=0.6, edgecolor="black")
        ax.add_feature(cfeature.BORDERS, linewidth=0.6, edgecolor="black")
        ax.coastlines(resolution="50m", linewidth=1.2)

        # Temperatura
        cf = ax.contourf(
            to_np(lons),
            to_np(lats),
            to_np(t2),
            levels=t_levels,
            cmap="turbo",
            extend="both",
            transform=crs.PlateCarree()
        )
        
        # Valores da temperatura nos pontos
        t2_np   = to_np(t2)
        lats_np = to_np(lats)
        lons_np = to_np(lons)

        plotted_points = []
        for i in range(0, t2_np.shape[0], step):
            for j in range(0, t2_np.shape[1], step):
                x_disp, y_disp = ax.transData.transform(
                    crs.PlateCarree().transform_point(
                        lons_np[i, j], lats_np[i, j], crs.PlateCarree()
                    )
                )
                too_close = False
                for xp, yp in plotted_points:
                    if np.hypot(x_disp - xp, y_disp - yp) < min_dist_px:
                        too_close = True
                        break
                if too_close:
                    continue
                ax.text(
                    lons_np[i, j], lats_np[i, j], f"{t2_np[i, j]:.1f}",
                    fontsize=font_size, color="black", ha="center", va="center",
                    transform=crs.PlateCarree(), zorder=5
                )
                plotted_points.append((x_disp, y_disp))

        # Isóbaras (linhas)
        cs = ax.contour(
            to_np(lons), to_np(lats), to_np(slp),
            levels=slp_levels, colors="black", linewidths=1.0,
            linestyles="dashed", transform=crs.PlateCarree()
        )
        ax.clabel(cs, fmt="%d", fontsize=8)

        cbar = plt.colorbar(cf, ax=ax, shrink=0.95)
        cbar.set_label("Temperatura (°C)")

        gl = ax.gridlines(draw_labels=True, linestyle="dotted")
        gl.right_labels = False
        gl.top_labels = False
        gl.x_inline = False

        # Título
        plt.title(
            f"Temperatura a 2 m (°C) e PNMM (hPa)\n"
            f"WRF 4.7.1 | Domínio {dom.upper()} \n"
            f"Início: {start_time_label} | Válido: {valid_time_label}"
        )

        outfile = os.path.join(
            dom_output_dir,
            f"T2_PNMM_{dom}_{time_label_file}.png"
        )
        plt.savefig(outfile, dpi=300, bbox_inches="tight")
        plt.close(fig)

    # ======================================================
    # GIF
    # ======================================================
    print(f"Criando GIF do domínio {dom}...")
    png_files = sorted([
        os.path.join(dom_output_dir, f)
        for f in os.listdir(dom_output_dir)
        if f.endswith(".png")
    ])

    if png_files:
        gif_path = os.path.join(dom_output_dir, f"T2_PNMM_{dom}.gif")
        with imageio.get_writer(gif_path, mode="I", fps=gif_fps) as writer:
            for png in png_files:
                writer.append_data(imageio.imread(png))
        print(f"GIF salva em: {gif_path}")

    ncfile.close()

print("\nProcessamento finalizado para todos os domínios.")
