import glob
import numpy as np
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from matplotlib.colors import ListedColormap, BoundaryNorm
from netCDF4 import Dataset
from wrf import getvar, to_np, ll_to_xy, ALL_TIMES
from datetime import timedelta

# ==============================
# CONFIGURAÇÕES
# ==============================
lat_ponto = 
lon_ponto = 

# =========================================================================
# IDENTIFICAÇÃO DE DOMÍNIOS
# =========================================================================
all_wrf_files = glob.glob("wrfout_*")

if not all_wrf_files:
    print("Nenhum arquivo wrfout encontrado")
    exit()

found_domains = sorted(list(set([f.split('_')[1] for f in all_wrf_files if '_' in f])))
print(f"Domínios encontrados na pasta: {found_domains}")

# ==============================
# LOOP POR DOMÍNIO
# ==============================
for dom in found_domains:
    print(f"\n=== Processando domínio {dom} ===")

    dom_files = glob.glob(f"wrfout_{dom}*")
    if not dom_files:
        continue
    
    wrfout_path = sorted(dom_files)[0]
    saida_figura = f"secao_vertical_superficie_real_isotermas_precip_{dom}.png"
    print(f"Arquivo selecionado: {wrfout_path}")

    try:
        ncfile = Dataset(wrfout_path)
        ix, iy = ll_to_xy(ncfile, lat_ponto, lon_ponto)
        ix, iy = int(ix), int(iy)

        # VARIÁVEIS 3D
        temp  = getvar(ncfile, "tk", timeidx=ALL_TIMES)
        ua    = getvar(ncfile, "ua", timeidx=ALL_TIMES)
        va    = getvar(ncfile, "va", timeidx=ALL_TIMES)
        pres  = getvar(ncfile, "pressure", timeidx=ALL_TIMES)
        z     = getvar(ncfile, "z", timeidx=ALL_TIMES)
        times = getvar(ncfile, "times", timeidx=ALL_TIMES)

        # VARIÁVEIS DE SUPERFÍCIE
        t2   = getvar(ncfile, "T2",  timeidx=ALL_TIMES) - 273.15
        td2  = getvar(ncfile, "td2", timeidx=ALL_TIMES)
        rh2  = getvar(ncfile, "rh2", timeidx=ALL_TIMES)
        psfc = getvar(ncfile, "PSFC", timeidx=ALL_TIMES) / 100.0
        u10 = getvar(ncfile, "U10", timeidx=ALL_TIMES)
        v10 = getvar(ncfile, "V10", timeidx=ALL_TIMES)

        # PRECIPITAÇÃO
        rain_conv  = getvar(ncfile, "RAINC",  timeidx=ALL_TIMES)
        rain_nconv = getvar(ncfile, "RAINNC", timeidx=ALL_TIMES)

        # TEMPO UTC → LOCAL
        tempo_utc = to_np(times).astype("datetime64[s]").astype(object)
        tempo_dt  = np.array([t - timedelta(hours=3) for t in tempo_utc])

        # EXTRAÇÃO NO PONTO (3D)
        temp_p = to_np(temp[:, :, iy, ix]) - 273.15
        ua_p   = to_np(ua[:, :, iy, ix]) * 1.94384
        va_p   = to_np(va[:, :, iy, ix]) * 1.94384
        pres_p = to_np(pres[:, :, iy, ix])
        z_p    = to_np(z[:, :, iy, ix])

        mask = np.nanmax(pres_p, axis=0) >= 500.0
        temp_p = temp_p[:, mask]
        ua_p   = ua_p[:, mask]
        va_p   = va_p[:, mask]
        pres_p = pres_p[:, mask]
        z_p    = z_p[:, mask]

        pres_mean = np.nanmean(pres_p, axis=0)
        z_mean    = np.nanmean(z_p, axis=0)

        # NÍVEIS DE PRESSÃO
        psfc_p = to_np(psfc[:, iy, ix])
        p_sfc  = int(np.round(np.nanmean(psfc_p), -1))
        p_levels = list(range(p_sfc, 499, -100))

        z_levels = []
        for p in p_levels:
            idx = np.abs(pres_mean - p).argmin()
            z_levels.append(z_mean[idx])

        # SUPERFÍCIE
        t2_p  = to_np(t2[:, iy, ix])
        td2_p = to_np(td2[:, iy, ix])
        rh2_p = to_np(rh2[:, iy, ix])
        wspd10 = np.sqrt(to_np(u10[:, iy, ix])**2 + to_np(v10[:, iy, ix])**2) * 3.6

        valid = np.isfinite(t2_p)
        tempo_dt_v = tempo_dt[valid]
        t2_p       = t2_p[valid]
        td2_p      = td2_p[valid]
        rh2_p      = rh2_p[valid]
        wspd10     = wspd10[valid]

        # Precipitação horária
        rain_total  = to_np(rain_conv[:, iy, ix]) + to_np(rain_nconv[:, iy, ix])
        rain_hourly = np.diff(rain_total, prepend=0)
        rain_hourly[rain_hourly < 0] = 0
        rain_hourly = rain_hourly[valid]

        # COLORMAP
        temp_bounds = np.array([-30, -26, -22, -18, -14, -12, -8, -4, 0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 50])
        colors = []
        colors.extend(plt.cm.Purples(np.linspace(0.45, 0.9, 5)))
        colors.extend(plt.cm.Blues(np.linspace(0.45, 0.9, 3)))
        colors.extend(plt.cm.Greens(np.linspace(0.45, 0.9, 5)))
        colors.extend(plt.cm.YlOrBr(np.linspace(0.35, 0.7, 3)))
        colors.extend(plt.cm.Reds(np.linspace(0.45, 0.9, 5)))
        cmap = ListedColormap(colors)
        norm = BoundaryNorm(temp_bounds, cmap.N)

        # FIGURA
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(
            4, 1, figsize=(15, 18), sharex=True,
            gridspec_kw={"height_ratios": [3, 1, 1, 1]}
        )
        fig.subplots_adjust(hspace=0.17)

        # PAINEL 1: Secção Vertical
        cf = ax1.contourf(tempo_dt, z_mean, temp_p[:len(tempo_dt_v)].T, levels=temp_bounds, cmap=cmap, norm=norm, extend="both")
        cs = ax1.contour(tempo_dt, z_mean, temp_p[:len(tempo_dt_v)].T, levels=temp_bounds[temp_bounds != 0], colors="black", linewidths=0.6)
        ax1.clabel(cs, fmt="%d °C", fontsize=11)
        
        cs0 = ax1.contour(tempo_dt, z_mean, temp_p[:len(tempo_dt_v)].T, levels=[0], colors="black", linewidths=2.4)
        labels0 = ax1.clabel(cs0, fmt="0 °C", fontsize=13)
        for txt in labels0: txt.set_fontweight("bold")

        nt, nz = temp_p.shape
        ax1.barbs(tempo_dt[::max(1, nt // 24)], z_mean[::max(1, nz // 20)], 
                  ua_p[:len(tempo_dt_v):max(1, nt // 24), ::max(1, nz // 20)].T, 
                  va_p[:len(tempo_dt_v):max(1, nt // 24), ::max(1, nz // 20)].T, length=5.5, linewidth=1.0)

        ax1.set_ylim(min(z_levels), max(z_levels))
        ax1.set_yticks(z_levels)
        ax1.set_yticklabels([f"{int(z)}" for z in z_levels])
        ax1.set_ylabel("Altitude (m)")
        ax1_p = ax1.twinx()
        ax1_p.set_ylim(ax1.get_ylim())
        ax1_p.set_yticks(z_levels)
        ax1_p.set_yticklabels([f"{p}" for p in p_levels])
        ax1_p.set_ylabel("Pressão (hPa)")

        # PAINEL 2: Temp / Orvalho / RH
        ax2.plot(tempo_dt_v, t2_p,  color="red", lw=2)
        ax2.plot(tempo_dt_v, td2_p, color="#8B0000", lw=2)
        ax2.text(-0.05, 0.55, "Temperatura (°C)", transform=ax2.transAxes, rotation=90, va="center", ha="center", color="red", fontsize=10)
        ax2.text(-0.07, 0.55, "Ponto de orvalho (°C)", transform=ax2.transAxes, rotation=90, va="center", ha="center", color="#8B0000", fontsize=10)
        ax2.tick_params(axis="y", labelcolor="red")
        ax2_rh = ax2.twinx()
        ax2_rh.plot(tempo_dt_v, rh2_p, color="blue", lw=2)
        ax2_rh.set_ylabel("Umidade relativa (%)", color="blue")
        ax2_rh.set_ylim(0, 100)
        ax2.grid(True, linestyle="--", linewidth=1.0, alpha=0.8)

        # PAINEL 3: Precipitação
        ax3.bar(tempo_dt_v, rain_hourly, width=0.03, color="dodgerblue", edgecolor="blue")
        ax3.set_ylabel("Precipitação (mm/h)")
        ax3.grid(True, linestyle="--", alpha=0.8)

        # PAINEL 4: Vento e Pressão
        ax4.plot(tempo_dt_v, wspd10, color="green", lw=2)
        ax4.set_ylabel("Vento 10 m (km/h)", color="green")
        ax4.tick_params(axis="y", labelcolor="green")
        ax4_p = ax4.twinx()
        ax4_p.plot(tempo_dt_v, to_np(psfc[:, iy, ix])[valid], color="blue", lw=2)
        ax4_p.set_ylabel("Pressão em superfície (hPa)", color="blue")
        ax4_p.tick_params(axis="y", labelcolor="blue")
        ax4.grid(True, linestyle="--", alpha=0.8)

        # Formatação de Eixos X
        locator = mdates.HourLocator(byhour=[0, 6, 12, 18])
        def format_time(x, pos=None):
            dt = mdates.num2date(x).replace(tzinfo=None)
            return dt.strftime("00:00\n%d/%m") if dt.hour == 0 else dt.strftime("%H:%M")

        for ax in (ax1, ax2, ax3, ax4):
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(FuncFormatter(format_time))

        ax1.set_xlim(tempo_dt_v[0], tempo_dt_v[-1])
        ax1.set_title(f"Seção Vertical – Temperatura, Vento e Pressão\nInterlagos (RS) | WRF 4.7.1 | Domínio {dom.upper()} | Horário Local")
        ax4.set_xlabel("Tempo (Hora Local)")

        plt.savefig(saida_figura, dpi=300)
        plt.close(fig)
        ncfile.close()
        print(f"Figura salva com sucesso: {saida_figura}")

    except Exception as e:
        print(f"Erro ao processar domínio {dom}: {e}")

print("\nProcessamento finalizado para todos os domínios.")
