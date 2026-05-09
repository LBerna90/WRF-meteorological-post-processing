#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import numpy as np
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from netCDF4 import Dataset
from wrf import getvar, interplevel, to_np, ll_to_xy, ALL_TIMES
from metpy.plots import SkewT
from metpy.units import units
from datetime import datetime

# ==========================================================
# CONFIGURAÇÕES
# ==========================================================
lat_pt = 
lon_pt = 
base_output_dir = "skew-t"


# IDENTIFICAÇÃO DE DOMÍNIOS
all_wrf_files = glob.glob("wrfout_*")

if not all_wrf_files:
    print("Nenhum arquivo wrfout encontrado.")
    exit()

# Extrai os domínios únicos (ex: d01, d02, d03)
found_domains = sorted(list(set([f.split('_')[1] for f in all_wrf_files if '_' in f])))
print(f"Domínios encontrados: {found_domains}")

# ==========================================================
# LOOP POR DOMÍNIO
# ==========================================================
for dom in found_domains:
    print(f"\n=== Processando domínio {dom} ===")

    dom_files = glob.glob(f"wrfout_{dom}*")
    if not dom_files:
        continue
    
    wrfout_file = sorted(dom_files)[0]
    print(f"Arquivo selecionado: {wrfout_file}")

    dom_output_dir = os.path.join(base_output_dir, dom)
    os.makedirs(dom_output_dir, exist_ok=True)

    try:
        ncfile = Dataset(wrfout_file)

        i_pt, j_pt = ll_to_xy(ncfile, lat_pt, lon_pt)
        i_pt, j_pt = int(i_pt), int(j_pt)

        pressure = getvar(ncfile, "pressure", timeidx=ALL_TIMES) * units.hPa
        temperature = getvar(ncfile, "tc", timeidx=ALL_TIMES) * units.degC
        dewpoint = getvar(ncfile, "td", timeidx=ALL_TIMES) * units.degC
        u_wind = getvar(ncfile, "ua", timeidx=ALL_TIMES) * units("m/s")
        v_wind = getvar(ncfile, "va", timeidx=ALL_TIMES) * units("m/s")
        times = getvar(ncfile, "times", timeidx=ALL_TIMES)

        start_time_val = times[0].values
        start_time_fmt = np.datetime64(start_time_val).astype("datetime64[s]").astype(datetime)
        start_time_label = start_time_fmt.strftime("%d/%m/%Y %H:%M UTC")

        # ======================================================
        # LOOP TEMPORAL
        # ======================================================
        for t in range(len(times)):

            p = pressure[t, :, j_pt, i_pt]
            T = temperature[t, :, j_pt, i_pt]
            Td = dewpoint[t, :, j_pt, i_pt]
            u = u_wind[t, :, j_pt, i_pt]
            v = v_wind[t, :, j_pt, i_pt]

            mask = np.isfinite(p)
            p = p[mask]
            T = T[mask]
            Td = Td[mask]
            u = u[mask]
            v = v[mask]

            time_val = times[t].values
            time_fmt = np.datetime64(time_val).astype("datetime64[s]").astype(datetime)
            time_fmt = time_dt.replace(minute=0, second=0, microsecond=0)

            valid_time_label = time_fmt.strftime("%d/%m/%Y %H:%M UTC")

            # ======================================================
            # CRIA FIGURA SKEW-T
            # ======================================================
            fig = plt.figure(figsize=(9, 9))
            skew = SkewT(fig, rotation=45)

            skew.plot(p, T, "r", linewidth=2, label="Temperatura")
            skew.plot(p, Td, "g", linewidth=2, label="Ponto de Orvalho")
            skew.plot_barbs(p, u, v)

            skew.ax.set_ylim(1000, 100)
            skew.ax.set_xlim(-40, 40)

            skew.plot_dry_adiabats(alpha=0.3)
            skew.plot_moist_adiabats(alpha=0.3)
            skew.plot_mixing_lines(alpha=0.3)

            # --- TÍTULO ALTERADO ---
            plt.title(
                f"Skew-T | Lat {lat_pt:.2f}, Lon {lon_pt:.2f} | Domínio {dom.upper()} | WRF 4.7.1\n"
                f"Início: {start_time_label} | Válido: {valid_time_label}",
                loc="left"
            )

            plt.legend(loc="upper right")

            # ======================================================
            # SALVA FIGURA
            # ======================================================
            outname = f"skewt_{dom}_{time_fmt:%Y%m%d_%H%M}.png"
            plt.savefig(os.path.join(dom_output_dir, outname), dpi=150, bbox_inches="tight")
            plt.close(fig) 

        ncfile.close()
        print(f"✔ Skew-Ts para o domínio {dom} gerados com sucesso.")

    except Exception as e:
        print(f"Erro ao processar domínio {dom}: {e}")
        print("Possível causa: O ponto geográfico está fora da área deste domínio.")

print("\nProcessamento de todos os domínios finalizado.")
