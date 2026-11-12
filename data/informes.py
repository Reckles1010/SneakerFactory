"""Salidas reproducibles: CSV con linaje, figuras PNG, informe técnico y ejecutivo."""
from datetime import datetime
from pathlib import Path

import pandas as pd

from data.analiticas import build_analytics
from data.config import CURRENCY, LOW_STOCK_THRESHOLD, OUTPUT_DIR, RANDOM_SEED, SALES_STATES
from data.figuras import generar_figuras
from data.segmentacion import kmeans_clientes


def _csv(df, ruta, origen, ahora, filtros, indice=False):
    d = df.reset_index() if indice else df.copy()
    d.insert(0, "filtros", str(filtros or "ninguno"))
    d.insert(0, "generado_en", ahora)
    d.insert(0, "origen", origen)
    d.to_csv(ruta, index=False, encoding="utf-8-sig")
    return {"fichero": ruta.name, "origen": origen, "generado_en": ahora, "filtros": str(filtros or "ninguno"), "filas": len(d)}


def _pct(x):
    return f"{x:.1f} %"


def informe_ejecutivo(a, snap, km, origen):
    k, abc, stock, rfm, ce = a["kpis"], a["modelos_abc"], a["stock_cobertura"], a["rfm"], a["custom_estandar"]
    nA = int((abc["clase_abc"] == "A").sum())
    pesoA = abc.loc[abc["clase_abc"] == "A", "peso_pct"].sum()
    baja = stock[(stock["alerta"] == "Stock bajo") | (stock["cobertura_semanas"] < 4)].sort_values("cobertura_semanas")
    pend = k["pedidos_pendientes"] / max(1, k["pedidos_actividad"]) * 100
    riesgo = int(rfm["segmento_rfm"].isin(["En riesgo", "Dormido"]).sum())
    sin = int((rfm["segmento_rfm"] == "Sin compras válidas").sum())
    tickets = ", ".join(f"{r['segmento']}: {r['ticket_medio']:.2f} {CURRENCY}" for _, r in ce.iterrows() if pd.notna(r["ticket_medio"]))
    top_canal = ce.sort_values("cuota_ingresos_pct", ascending=False).iloc[0] if len(ce) else None
    L = [f"# Informe ejecutivo · Sneaker Factory", "",
            f"**Origen de los datos: {origen}** · Generado: {datetime.now().astimezone():%d/%m/%Y %H:%M} · Semilla: {RANDOM_SEED}", "",
         "> Este informe separa **observaciones** (qué pasa), **interpretaciones** (por qué podría pasar) y **propuestas** (qué hacer). "
            "Ninguna interpretación es una afirmación causal.", "",
            f"**Resumen:** ingresos de venta {k['ingresos']:,.2f} {CURRENCY}; {k['pares']:,.0f} unidades; {k['pedidos_venta']:,} pedidos de venta "
            f"sobre {k['pedidos_actividad']:,} pedidos de actividad; ticket medio {k['ticket']:,.2f} {CURRENCY}. "
            f"Estados que reconocen ingreso: {', '.join(SALES_STATES)}.", ""]
    dec = [
        ("Concentrar la capacidad de fabricación en los modelos clase A", "1 · Alta",
            f"{nA} modelos (clase A) reúnen el {_pct(pesoA)} de los ingresos; el top-20 % de modelos aporta el {_pct(k['pareto_top20_modelos_pct'])}.",
            "La demanda está muy concentrada; una rotura en esos modelos penaliza más que en la cola.",
            "Asegurar materia prima y cadencia para los modelos A y revisar la utilidad de mantener la cola larga.",
            "Tabla Modelos ABC (modelos_abc.csv) y figura 03_pareto_abc.png", "Menos roturas en los modelos que más facturan",
            "Periodo corto; la clasificación puede cambiar con más meses."),
        ("Reponer los modelos con menor cobertura", "2 · Alta",
            (f"{len(baja)} modelos con stock ≤ {LOW_STOCK_THRESHOLD} o cobertura < 4 semanas; el más ajustado: "
            f"{baja.iloc[0]['modelo']} ({baja.iloc[0]['stock_disponible']} uds)." if len(baja) else
            f"Ningún modelo está bajo el umbral de {LOW_STOCK_THRESHOLD} unidades ni con cobertura < 4 semanas."),
            "La cobertura usa la demanda de 28 días; el stock es una instantánea, no un histórico.",
            "Lanzar reposición de los modelos señalados y repetir el cálculo tras la siguiente exportación.",
            "Tabla stock_cobertura.csv y figura 10_stock_vs_demanda.png", "Evitar ventas perdidas",
            "ACC exporta stock por modelo (no por talla): no se detectan roturas de talla concretas."),
        ("Revisar la cartera de pedidos pendientes", "3 · Media",
            f"{k['pedidos_pendientes']:,} pedidos ({_pct(pend)} de la actividad) siguen pendientes o en preparación y no cuentan como venta.",
            "Pueden ser pedidos recientes o un flujo de estados que no se actualiza; los datos no lo distinguen.",
            "Contrastar con Acceso a Datos si los estados se actualizan; si no, los ingresos reales están infravalorados.",
            "KPI pedidos_pendientes y reconciliación SQL (auditoria_reconciliacion.csv)", "Ingresos reconocidos más fiables",
            "No se conoce la antigüedad esperada de un pedido pendiente."),
        ("Tratar los canales con criterio, no por el ticket", "4 · Media",
            (f"{top_canal['segmento']} aporta el {_pct(top_canal['cuota_ingresos_pct'])} de los ingresos. " if top_canal is not None else "") +
            f"Ticket medio por tipo de pedido: {tickets}.",
            "Una diferencia en el ticket medio no demuestra que un canal sea mejor; el canal no se asignó al azar.",
            "No cambiar el reparto de esfuerzo entre canales hasta tener más meses y repetir la comparación.",
            "custom_vs_estandar.csv y figura 05_boxplot_importe_por_tipo.png", "Evita decisiones sobre diferencias no contrastadas",
            "Los datos reales de ACC no contienen pedidos Custom: la comparación Custom/estándar no es calculable."),
        ("Reactivar clientes en riesgo o dormidos", "5 · Media",
            f"{riesgo:,} clientes en RFM 'En riesgo' o 'Dormido'; {sin:,} clientes sin compras válidas.",
            "Pueden haber dejado de comprar o tener pedidos aún no entregados; RFM usa solo ventas válidas.",
            "Campaña de reactivación acotada a 'En riesgo' y medir la respuesta con la siguiente exportación.",
            "rfm.csv, figura 07_dispersion_rfm.png y kmeans_perfil.csv", "Recuperar ingresos recurrentes",
            "El nombre de un clúster no es una categoría comercial; con pocos meses la recencia es poco discriminante."),
    ]
    for i, (t, prio, obs, interp, prop, ev, imp, lim) in enumerate(dec, 1):
        L += [f"## Decisión {t}", f"*Prioridad {prio} · Origen: {origen}*", "",
              f"- **Observación:** {obs}", f"- **Interpretación:** {interp}", f"- **Propuesta:** {prop}",
              f"- **Evidencia:** {ev}", f"- **Impacto esperado:** {imp}", f"- **Limitación / riesgo:** {lim}", ""]
    L += ["## Qué NO puede afirmarse", "Una diferencia observada entre canales o periodos no demuestra causalidad; "
            "con pocos meses de datos tampoco puede hablarse de estacionalidad. No se ha realizado contraste estadístico formal.", ""]
    return "\n".join(L)


def informe_tecnico(a, snap, km, origen, filtros):
    q, kp = snap["quality"], a["kpis_tabla"]
    L = [f"# Informe técnico · Sneaker Factory", "", f"**Origen: {origen}** · Generado: {datetime.now().astimezone():%d/%m/%Y %H:%M} · Filtros: {filtros or 'ninguno'} · Semilla: {RANDOM_SEED}", "",
            "## 1. Método y datos", "Flujo: CSV → validación de esquema y 12 reglas → limpieza trazable → cruces con `validate=` e `indicator=` "
            "→ DataFrames analíticos → estadística, segmentación y predicción. Los CSV de entrada nunca se modifican.", "",
            "## 2. Calidad por tabla", q.to_markdown(index=False), "",
            "### Incidencias por regla", (snap["issues"].groupby(["regla", "gravedad"]).size().rename("registros").reset_index().to_markdown(index=False)
                                        if len(snap["issues"]) else "Sin incidencias."), "",
            "## 3. KPIs, fórmulas y denominadores", kp.to_markdown(index=False), "",
            "## 4. Descriptivo del importe por pedido de venta"]
    pv = a["pedidos_unicos"]; pv = pv[pv["es_venta"]]
    if len(pv):
        L += [pv.groupby("tipo")["importe"].describe().round(2).reset_index().to_markdown(index=False),
                "La mediana representa mejor el pedido típico que la media porque la distribución es asimétrica.", ""]
    L += ["## 5. Segmentación"]
    if km["estado"] == "CALCULADO":
        L += [f"RFM por cuartiles (R, F, M de 1 a 4). KMeans con variables escaladas; k elegido = {km['k_elegido']} por silhouette.",
                km["comparacion_k"].round(3).to_markdown(index=False), km["perfil"].round(2).to_markdown(index=False),
                "Cruce clúster × segmento RFM:", km["cruce_rfm"].to_markdown(), km["nota"], ""]
    else:
        L += [km["motivo"], ""]
    L += ["## 6. Sesgos y limitaciones",
            "- Periodo corto y una sola exportación: no hay estacionalidad demostrable.",
            "- El stock es una instantánea y ACC lo exporta por modelo, no por talla.",
            "- `descuento` llega como booleano: el importe es bruto, sin descuentos ni IVA; no se calcula margen (no hay costes).",
            "- Los datos sintéticos no representan clientes reales y nunca se mezclan con los reales.", ""]
    return "\n".join(L)


def generar_todo(snapshot, out_dir=None, filtros=None, origen=None):
    """Genera CSV (≥10), PNG (≥8) e informes. """
    origen = origen or snapshot["origin"]
    sub = "real" if origen.startswith("ACC") else "sintetico"
    out = Path(out_dir or OUTPUT_DIR / sub)
    out.mkdir(parents=True, exist_ok=True)
    ahora = datetime.now().astimezone().isoformat(timespec="seconds")
    a = build_analytics(snapshot, filtros)
    km = kmeans_clientes(a["rfm"])
    man = []
    c = lambda df, n, **kw: man.append(_csv(df, out / n, origen, ahora, filtros, **kw))
    c(snapshot["quality"], "resumen_calidad.csv"); c(snapshot["issues"], "incidencias.csv")
    c(a["kpis_tabla"], "kpis.csv"); c(a["pedidos_unicos"], "pedidos_unicos.csv"); c(a["ventas_periodo"], "evolucion_mensual.csv")
    c(a["ventas_trimestre"], "evolucion_trimestral.csv"); c(a["modelos_abc"], "modelos_abc.csv")
    c(a["matriz_modelo_talla"], "matriz_modelo_talla.csv", indice=True); c(a["rfm"], "rfm.csv")
    c(a["cohortes"], "cohortes.csv", indice=True); c(a["stock_cobertura"], "stock_cobertura.csv")
    c(a["reconciliacion"], "auditoria_reconciliacion.csv"); c(a["anomalias"].drop(columns=["id_cliente"], errors="ignore"), "anomalias_iqr.csv")
    c(a["custom_estandar"], "custom_vs_estandar.csv"); c(a["nulos_columna"], "nulos_por_columna.csv")
    if km["estado"] == "CALCULADO":
        c(km["perfil"], "kmeans_perfil.csv"); c(km["comparacion_k"], "kmeans_comparacion_k.csv")
    l = a["lineas_enriquecidas"]
    periodo = f"{l['fecha'].min():%Y-%m-%d} – {l['fecha'].max():%Y-%m-%d}" if len(l) else "sin datos"
    figs = generar_figuras(a, out / "figuras", origen, periodo)
    (out / "informe_ejecutivo.md").write_text(informe_ejecutivo(a, snapshot, km, origen), encoding="utf-8")
    (out / "informe_tecnico.md").write_text(informe_tecnico(a, snapshot, km, origen, filtros), encoding="utf-8")
    pd.DataFrame(man).to_csv(out / "manifiesto_salidas.csv", index=False, encoding="utf-8-sig")
    return {"carpeta": out, "csv": len(man), "figuras": len(figs), "analytics": a, "kmeans": km}
