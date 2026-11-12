"""Figuras PNG reproducibles (Matplotlib) generadas a partir de los DataFrames en ejecución."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data.config import CURRENCY

COL = {"azul": "#1f4e79", "rojo": "#b03a2e", "gris": "#7f8c8d", "verde": "#2e7d32"}


def _cierra(fig, ruta, titulo, origen, periodo, lectura):
    fig.suptitle(titulo, fontsize=12, fontweight="bold")
    fig.text(0.01, 0.01, f"Origen: {origen} · Periodo: {periodo}\nLectura: {lectura}", fontsize=7.5, color="#444", va="bottom")
    fig.tight_layout(rect=(0, 0.10, 1, 0.95))
    fig.savefig(ruta, dpi=130)
    plt.close(fig)
    return ruta


def generar_figuras(a, out_dir, origen, periodo):
    """Devuelve la lista de PNG creados (mínimo 8 si hay datos suficientes)."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    l, p = a["lineas_enriquecidas"], a["pedidos_unicos"]
    pv = p[p["es_venta"]]
    ventas, abc, rfm = a["ventas_periodo"], a["modelos_abc"], a["rfm"]
    creadas = []

    if len(ventas):                                                              # 1 serie temporal
        fig, ax = plt.subplots(figsize=(8, 4.8))
        ax.plot(ventas["mes"], ventas["ingresos"].astype(float), marker="o", color=COL["azul"], label="Ingresos")
        ax.plot(ventas["mes"], ventas["media_3_meses_previos"], ls="--", color=COL["gris"], label="Media 3 meses previos")
        ax.set_ylabel(f"Ingresos ({CURRENCY})"); ax.set_xlabel("Mes"); ax.legend(); ax.tick_params(axis="x", rotation=45)
        mx = ventas.loc[ventas["ingresos"].astype(float).idxmax(), "mes"]
        creadas.append(_cierra(fig, out / "01_serie_ingresos_mensuales.png", "Ingresos mensuales de venta", origen, periodo,
                                f"El mes de mayor ingreso es {mx}; el primer mes puede estar incompleto."))
    if len(abc):                                                                 # 2 ranking
        top = abc.head(10).iloc[::-1]
        fig, ax = plt.subplots(figsize=(8, 4.8))
        ax.barh(top["modelo"], top["ingresos"].astype(float), color=COL["azul"], label="Ingresos")
        ax.set_xlabel(f"Ingresos ({CURRENCY})"); ax.legend()
        creadas.append(_cierra(fig, out / "02_ranking_modelos.png", "Top 10 modelos por ingresos", origen, periodo,
                                f"{top.iloc[-1]['modelo']} lidera con el {top.iloc[-1]['peso_pct']:.1f} % de los ingresos."))
        fig, ax = plt.subplots(figsize=(8, 4.8))                                 # 3 Pareto
        ax.bar(range(len(abc)), abc["ingresos"].astype(float), color=COL["azul"], label="Ingresos por modelo")
        ax.set_ylabel(f"Ingresos ({CURRENCY})"); ax.set_xlabel("Modelos (orden por ingresos)")
        ax2 = ax.twinx(); ax2.plot(range(len(abc)), abc["acumulado_pct"], color=COL["rojo"], marker="o", ms=3, label="% acumulado")
        ax2.axhline(80, ls=":", color=COL["gris"]); ax2.set_ylabel("% acumulado de ingresos"); ax2.set_ylim(0, 105)
        h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); ax.legend(h1 + h2, l1 + l2, loc="center right")
        nA = int((abc["clase_abc"] == "A").sum())
        creadas.append(_cierra(fig, out / "03_pareto_abc.png", "Pareto de modelos (clasificación ABC)", origen, periodo,
                                f"{nA} modelos clase A reúnen el 80 % de los ingresos; el resto aporta la cola."))
    if len(pv):                                                                  # 4 histograma
        fig, ax = plt.subplots(figsize=(8, 4.8))
        ax.hist(pv["importe"].astype(float), bins=25, color=COL["azul"], label="Pedidos de venta")
        med = float(pv["importe"].astype(float).median()); ax.axvline(med, color=COL["rojo"], ls="--", label=f"Mediana {med:.1f} {CURRENCY}")
        ax.set_xlabel(f"Importe del pedido ({CURRENCY})"); ax.set_ylabel("Nº de pedidos"); ax.legend()
        creadas.append(_cierra(fig, out / "04_histograma_importe_pedido.png", "Distribución del importe por pedido", origen, periodo,
                                f"Distribución asimétrica: media {pv['importe'].astype(float).mean():.1f} {CURRENCY} > mediana {med:.1f} {CURRENCY}."))
        g = [(k, d["importe"].astype(float).values) for k, d in pv.groupby(pv["segmento"] if pv["segmento"].nunique() > 1 else pv["tipo"].astype(str))]
        fig, ax = plt.subplots(figsize=(8, 4.8))                                 # 5 boxplot
        try:
            ax.boxplot([v for _, v in g], tick_labels=[k for k, _ in g])
        except TypeError:                      # matplotlib < 3.9
            ax.boxplot([v for _, v in g], labels=[k for k, _ in g])
        ax.set_ylabel(f"Importe del pedido ({CURRENCY})"); ax.set_xlabel("Segmento / tipo de pedido")
        ax.plot([], [], color="orange", label="Mediana"); ax.legend()
        creadas.append(_cierra(fig, out / "05_boxplot_importe_por_tipo.png", "Importe por pedido según tipo", origen, periodo,
                                "La caja marca el rango intercuartílico; los puntos son pedidos atípicos (no se eliminan)."))
    m = a["matriz_modelo_talla"]
    if len(m):                                                                   # 6 mapa de calor
        fig, ax = plt.subplots(figsize=(8, 6))
        im = ax.imshow(m.values.astype(float), aspect="auto", cmap="Blues")
        ax.set_xticks(range(m.shape[1])); ax.set_xticklabels(m.columns, fontsize=7); ax.set_yticks(range(m.shape[0])); ax.set_yticklabels(m.index, fontsize=7)
        ax.set_xlabel("Talla"); ax.set_ylabel("Modelo"); fig.colorbar(im, label="Unidades vendidas")
        creadas.append(_cierra(fig, out / "06_mapa_calor_modelo_talla.png", "Unidades vendidas por modelo y talla", origen, periodo,
                                f"La talla más vendida en conjunto es la {m.sum().idxmax()}; compara filas por proporción, no solo por volumen."))
    r = rfm[rfm["segmento_rfm"] != "Sin compras válidas"]
    if len(r):                                                                   # 7 dispersión
        fig, ax = plt.subplots(figsize=(8, 4.8))
        for seg, d in r.groupby("segmento_rfm"):
            ax.scatter(d["recency_dias"].astype(float), d["monetary"].astype(float), s=14, alpha=.65, label=seg)
        ax.set_xlabel("Recencia (días desde la última compra)"); ax.set_ylabel(f"Gasto total ({CURRENCY})"); ax.legend(fontsize=7)
        creadas.append(_cierra(fig, out / "07_dispersion_rfm.png", "Clientes: recencia frente a gasto", origen, periodo,
                                "Los clientes de arriba a la izquierda (recientes y de alto gasto) son los más valiosos."))
    ce = a["custom_estandar"]
    if len(ce):                                                                  # 8 comparativa
        fig, ax = plt.subplots(figsize=(8, 4.8)); x = np.arange(len(ce)); w = .38
        ax.bar(x - w / 2, ce["cuota_ingresos_pct"], w, label="Cuota de ingresos (%)", color=COL["azul"])
        ax.bar(x + w / 2, ce["tasa_cancelacion_pct"], w, label="Tasa de cancelación (% pedidos)", color=COL["rojo"])
        ax.set_xticks(x); ax.set_xticklabels(ce["segmento"]); ax.set_ylabel("Porcentaje"); ax.set_xlabel("Segmento"); ax.legend()
        creadas.append(_cierra(fig, out / "08_comparativa_segmentos.png", "Comparativa por segmento", origen, periodo,
                                "La cuota de ingresos (euros) y la tasa de cancelación (pedidos) usan denominadores distintos."))
    co = a["cohortes"]
    if len(co):                                                                  # 9 cohortes
        fig, ax = plt.subplots(figsize=(8, 4.8)); im = ax.imshow(co.values.astype(float), cmap="Greens", vmin=0, vmax=100)
        ax.set_xticks(range(co.shape[1])); ax.set_xticklabels(co.columns); ax.set_yticks(range(co.shape[0])); ax.set_yticklabels(co.index)
        ax.set_xlabel("Meses desde la primera compra"); ax.set_ylabel("Cohorte (mes de primera compra)"); fig.colorbar(im, label="% de clientes que compran")
        aviso = " Muestra pequeña: interpretar con cautela." if co.attrs.get("muestra_insuficiente") else ""
        creadas.append(_cierra(fig, out / "09_retencion_cohortes.png", "Retención por cohorte de compra", origen, periodo,
                                "Cada fila es la cohorte de clientes según su primer mes de compra." + aviso))
    s = a["stock_cobertura"]
    if len(s):                                                                   # 10 stock vs demanda
        s2 = s.sort_values("stock_disponible", ascending=False).head(12)
        fig, ax = plt.subplots(figsize=(8, 4.8)); x = np.arange(len(s2)); w = .38
        ax.bar(x - w / 2, s2["stock_disponible"].astype(float), w, label="Stock (instantánea)", color=COL["azul"])
        ax.bar(x + w / 2, s2["demanda_28_dias"].astype(float), w, label="Demanda 28 días", color=COL["verde"])
        ax.set_xticks(x); ax.set_xticklabels(s2["id_modelo"], rotation=45); ax.set_ylabel("Unidades"); ax.set_xlabel("Modelo"); ax.legend()
        creadas.append(_cierra(fig, out / "10_stock_vs_demanda.png", "Stock frente a demanda reciente", origen, periodo,
                                "El stock es una fotografía, no una serie histórica; la cobertura solo existe si hubo demanda."))
    return creadas
