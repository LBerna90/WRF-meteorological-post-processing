import os
import glob
import imageio.v2 as imageio
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
    to_np, getvar, smooth2d, get_cartopy,
    cartopy_xlim, cartopy_ylim, latlon_coords
)

# ==========================================================
# CONFIGURAÇÕES GERAIS
# ==========================================================
base_output_dir = "PNMM"
os.makedirs(base_output_dir, exist_ok=True)

gif_fps = 2
levels = np.arange(980, 1040, 2)
domains = ["d01", "d02", "d03"]

# ==========================================================
# LOOP POR DOMÍNIO
# ==========================================================
for dom in domains:
    print(f"\n=== Processando domínio {dom} ===")

    files = glob.glob(f"wrfout_{dom}*")
    if not files:
        print(f"Nenhum arquivo wrfout encontrado para {dom}")
        continue
    
    wrf_file = sorted(files)[0]
    print(f"Arquivo encontrado: {wrf_file}")

    dom_output_dir = os.path.join(base_output_dir, dom)
    os.makedirs(dom_output_dir, exist_ok=True)

    ncfile = Dataset(wrf_file)
    ntimes = len(ncfile.dimensions["Time"])

 
# ------------------------------------------------------
    temp_slp = getvar(ncfile, "slp", timeidx=0)
    lats, lons = latlon_coords(temp_slp)
    cart_proj = get_cartopy(temp_slp)
    
    lons_np = to_np(lons)
    lats_np = to_np(lats)

    xlim = cartopy_xlim(temp_slp)
    ylim = cartopy_ylim(temp_slp)


    start_time_str = str(temp_slp.Time.values)
    start_time_dt = datetime.strptime(start_time_str[:19], "%Y-%m-%dT%H:%M:%S")
    start_time_label = start_time_dt.strftime("%d/%m/%Y %H:%M UTC")

    states_feature = NaturalEarthFeature(
        category="cultural",
        name="admin_1_states_provinces_lines",
        scale="50m",
        facecolor="none"
    )

    fig = plt.figure(figsize=(12, 6))
    ax = plt.axes(projection=cart_proj)

    # ======================================================
    # LOOP NO TEMPO
    # ======================================================
    for t in range(ntimes):
        print(f"Domínio {dom} | Tempo {t+1}/{ntimes}")

        slp = getvar(ncfile, "slp", timeidx=t)
        smooth_slp = smooth2d(slp, 3, cenweight=4)
        smooth_slp_np = to_np(smooth_slp)

        # Processamento de data para o rótulo (Data Válida)
        time_str = str(slp.Time.values)
        time_dt = datetime.strptime(time_str[:19], "%Y-%m-%dT%H:%M:%S")
        time_dt = time_dt.replace(minute=0, second=0, microsecond=0)
        valid_time_label = time_dt.strftime("%d/%m/%Y %H:%M UTC")
        time_label_file = time_dt.strftime("%Y-%m-%d_%H")

        ax.clear()
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        ax.add_feature(states_feature, linewidth=0.8, edgecolor="gray")
        ax.add_feature(cfeature.BORDERS, linewidth=0.8, edgecolor="black")
        ax.coastlines(resolution="50m", linewidth=1.0)

        cs = ax.contour(
            lons_np, lats_np, smooth_slp_np,
            levels=levels, colors="black", linewidths=0.8,
            linestyles="dashed", transform=crs.PlateCarree()
        )

        cf = ax.contourf(
            lons_np, lats_np, smooth_slp_np,
            levels=levels, cmap="jet", transform=crs.PlateCarree()
        )

        ax.clabel(cs, fmt="%d", fontsize=8)

        if t == 0:
            cbar = plt.colorbar(cf, ax=ax, shrink=0.95, label="hPa")
        
        gl = ax.gridlines(draw_labels=True, linestyle="dotted")
        gl.right_labels = False
        gl.top_labels = False
        gl.x_inline = False

        
        plt.title(
            f"Pressão Nível Médio do Mar (hPa) WRF 4.7.1 Domínio {dom.upper()}\n"f"Início: {start_time_label} Válido: {valid_time_label}"
        )

        outfile = os.path.join(dom_output_dir, f"PNMM_{dom}_{time_label_file}.png")
        plt.savefig(outfile, dpi=300, bbox_inches="tight")

    plt.close(fig)

    # ======================================================
    # GIF DO DOMÍNIO
    # ======================================================
    print(f"Criando GIF do domínio {dom}...")
    png_files = sorted([
        os.path.join(dom_output_dir, f)
        for f in os.listdir(dom_output_dir)
        if f.endswith(".png")
    ])

    if png_files:
        gif_path = os.path.join(dom_output_dir, f"PNMM_{dom}.gif")
        with imageio.get_writer(gif_path, mode="I", fps=gif_fps) as writer:
            for png in png_files:
                writer.append_data(imageio.imread(png))
        print(f"GIF salva em: {gif_path}")

    ncfile.close()

print("\nProcessamento finalizado para todos os domínios.")
