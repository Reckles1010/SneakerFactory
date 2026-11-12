"""Funciones pandas puras (sin Streamlit). Una sola definición de cada KPI y DataFrame.

Cada DataFrame lleva metadatos en df.attrs: función, origen, fecha de corte, filtros y filas de origen.
"""
import numpy as np
import pandas as pd

from data.config import (CANCEL_STATES, COVERAGE_WINDOW_DAYS, CUSTOM_VALUES, LOW_STOCK_THRESHOLD,
                        PENDING_STATES, SALES_STATES)


def _meta(df, funcion, base, filtros=None):
    df.attrs.update({"funcion": funcion, "origen": base.attrs.get("origen"),
                    "fecha_corte": base.attrs.get("fecha_corte"), "filtros": filtros or {},
                    "filas_origen": base.attrs.get("filas_origen")})
    return df


def _ventas(df):
    return df[df["es_venta"]]


def _f(x):
    return float(x) if pd.notna(x) else 0.0


# filtros combinables
def filter_lines(df, start=None, end=None, models=None, sizes=None, types=None, states=None):
    """Un filtro no aplicado (None o vacío) no restringe nada."""
    out = df
    if start:
        out = out[out["fecha"] >= pd.Timestamp(start)]
    if end:
        out = out[out["fecha"] < pd.Timestamp(end) + pd.Timedelta(days=1)]
    if models:
        out = out[out["modelo"].astype(str).isin(models)]
    if sizes:
        out = out[out["talla"].astype(str).isin(sizes)]
    if types:
        out = out[out["tipo"].astype(str).isin(types)]
    if states:
        out = out[out["estado"].astype(str).isin(states)]
    out = out.copy()
    out.attrs = dict(df.attrs)
    out.attrs["filtros"] = {"start": str(start), "end": str(end), "models": models, "sizes": sizes,
                            "types": types, "states": states}
    return out


# pedidos únicos
def pedidos_unicos(lineas):
    """Una fila por pedido: un pedido con tres líneas cuenta como UN pedido, no como tres."""
    g = (lineas.groupby(["id_pedido", "fecha", "id_cliente", "estado", "tipo", "segmento"], dropna=False)
            .agg(pares=("cantidad", "sum"), importe=("importe_linea", "sum"), numero_lineas=("id_linea", "size"),
                modelos=("id_modelo", "nunique"), es_venta=("es_venta", "max")).reset_index())
    g["pares"], g["importe"] = g["pares"].astype(float), g["importe"].astype(float)
    g["importe_venta"] = np.where(g["es_venta"], g["importe"], 0.0)
    g["ticket"] = np.where(g["es_venta"], g["importe"], np.nan)
    return _meta(g, "analiticas.pedidos_unicos", lineas, lineas.attrs.get("filtros"))


# ventas por periodo
def ventas_por_periodo(lineas):
    d = _ventas(lineas)
    out = d.groupby("mes", as_index=False).agg(ingresos=("importe_linea", "sum"), pares=("cantidad", "sum"),
                                            pedidos=("id_pedido", "nunique")).sort_values("mes")
    out["ticket_medio"] = out["ingresos"] / out["pedidos"].replace(0, np.nan)
    out["variacion_ingresos_pct"] = out["ingresos"].astype(float).pct_change() * 100
    # media de los 3 meses ANTERIORES (shift evita incluir el mes actual)
    out["media_3_meses_previos"] = out["ingresos"].astype(float).shift(1).rolling(3, min_periods=1).mean()
    prev = out.set_index("mes")["ingresos"].astype(float)
    ant = pd.PeriodIndex(out["mes"], freq="M") - 12
    out["variacion_interanual_pct"] = [
        (prev[m] / prev[str(a)] - 1) * 100 if str(a) in prev.index and prev[str(a)] else np.nan
        for m, a in zip(out["mes"], ant)]       # solo si existe el mismo mes del año anterior
    return _meta(out.reset_index(drop=True), "analiticas.ventas_por_periodo", lineas, lineas.attrs.get("filtros"))


def ventas_por_trimestre(lineas):
    d = _ventas(lineas)
    out = d.groupby("trimestre", as_index=False).agg(ingresos=("importe_linea", "sum"), pares=("cantidad", "sum"),
                                                    pedidos=("id_pedido", "nunique")).sort_values("trimestre")
    out["variacion_ingresos_pct"] = out["ingresos"].astype(float).pct_change() * 100
    return _meta(out, "analiticas.ventas_por_trimestre", lineas, lineas.attrs.get("filtros"))


# ABC / Pareto
def modelos_abc(lineas):
    d = _ventas(lineas)
    x = d.groupby(["id_modelo", "modelo"], as_index=False).agg(ingresos=("importe_linea", "sum"),
                                                                unidades=("cantidad", "sum"))
    x = x.sort_values("ingresos", ascending=False).reset_index(drop=True)
    total, tot_u = float(x["ingresos"].sum()), float(x["unidades"].sum())
    x["peso_pct"] = x["ingresos"].astype(float) / total * 100 if total else 0.0
    x["acumulado_pct"] = x["peso_pct"].cumsum()
    x["peso_unidades_pct"] = x["unidades"].astype(float) / tot_u * 100 if tot_u else 0.0
    x["ranking_unidades"] = x["unidades"].rank(ascending=False, method="min")
    # A: hasta el 80 % acumulado (el modelo que cruza el umbral se incluye), B: hasta 95 %, C: resto
    previo = x["acumulado_pct"] - x["peso_pct"]
    x["clase_abc"] = np.select([previo < 80, previo < 95], ["A", "B"], default="C")
    return _meta(x, "analiticas.modelos_abc", lineas, lineas.attrs.get("filtros"))


# matriz modelo × talla
def matriz_modelo_talla(lineas):
    d = _ventas(lineas)
    if d.empty:
        vacio = pd.DataFrame()
        return vacio, vacio
    units = d.pivot_table(index="modelo", columns="talla", values="cantidad", aggfunc="sum", fill_value=0)
    units = units.reindex(sorted(units.columns, key=lambda t: (len(str(t)), str(t))), axis=1)
    prop = units.div(units.sum(axis=1).replace(0, np.nan), axis=0) * 100
    return units, prop


# custom vs estándar
def custom_estandar(pedidos):
    """Compara segmentos. Si ACC no exporta pedidos Custom, compara por tipo de pedido y lo avisa."""
    x = pedidos.copy()
    hay_custom = x["segmento"].eq("Custom").any()
    x["grupo"] = x["segmento"] if hay_custom else x["tipo"].astype(str)
    canc = x["estado"].astype(str).str.lower().isin(CANCEL_STATES)
    x["_canc"], x["_pares_v"] = canc, np.where(x["es_venta"], x["pares"], 0)
    g = x.groupby("grupo", as_index=False).agg(
        pedidos=("id_pedido", "nunique"), cancelados=("_canc", "sum"), pares=("_pares_v", "sum"),
        ingresos=("importe_venta", "sum"), pedidos_venta=("es_venta", "sum"), ticket_medio=("ticket", "mean"))
    g = g.rename(columns={"grupo": "segmento"})
    g["tasa_cancelacion_pct"] = g["cancelados"] / g["pedidos"].replace(0, np.nan) * 100   # sobre pedidos
    g["cuota_ingresos_pct"] = g["ingresos"] / g["ingresos"].sum() * 100 if g["ingresos"].sum() else np.nan  # sobre euros
    g["cuota_pares_pct"] = g["pares"] / g["pares"].sum() * 100 if g["pares"].sum() else np.nan
    g["nota"] = "" if hay_custom else "Custom no existe en la exportación ACC: comparación por tipo de pedido"
    return _meta(g, "analiticas.custom_estandar", pedidos, pedidos.attrs.get("filtros"))


# RFM
def clientes_rfm(lineas, clientes, cutoff=None):
    """Una fila por cliente. R = días desde la última compra válida, F = pedidos únicos válidos,
    M = ventas netas. Puntuación 1-4 por cuartiles (rank 'first' para romper empates)."""
    d = _ventas(lineas)
    corte = pd.Timestamp(cutoff) if cutoff is not None else (d["fecha"].max() if not d.empty else pd.Timestamp.today())
    r = d.groupby("id_cliente").agg(ultima_compra=("fecha", "max"), monetary=("importe_linea", "sum"),
                                    pares=("cantidad", "sum"), frequency=("id_pedido", "nunique")).reset_index()
    r["recency_dias"] = (corte - r["ultima_compra"]).dt.days

    def puntos(s, mayor_mejor):
        rk = s.rank(method="first", ascending=mayor_mejor)
        return pd.qcut(rk, 4, labels=[1, 2, 3, 4]).astype(int) if len(s) >= 4 else pd.Series(2, index=s.index)

    if len(r):
        r["R"], r["F"], r["M"] = (puntos(r["recency_dias"], False), puntos(r["frequency"], True),
                                    puntos(r["monetary"].astype(float), True))
        r["segmento_rfm"] = np.select(
            [(r["R"] >= 3) & (r["F"] >= 3) & (r["M"] >= 3), r["F"] >= 3, r["R"] >= 3, (r["R"] <= 2) & (r["F"] >= 2)],
            ["Campeón", "Fiel", "Reciente", "En riesgo"], default="Dormido")
    if r.empty:
        r = pd.DataFrame(columns=["id_cliente", "ultima_compra", "monetary", "pares", "frequency",
                                "recency_dias", "R", "F", "M", "segmento_rfm"])
    base = clientes[["id_cliente"]].drop_duplicates()
    out = base.merge(r, on="id_cliente", how="left", validate="one_to_one")
    out["segmento_rfm"] = out["segmento_rfm"].fillna("Sin compras válidas")
    out.attrs["fecha_referencia_rfm"] = str(corte.date())
    return _meta(out, "analiticas.clientes_rfm", lineas, lineas.attrs.get("filtros"))


# cohortes
def cohortes(lineas):
    d = _ventas(lineas).copy()
    if d.empty:
        return pd.DataFrame()
    d["periodo"] = d["fecha"].dt.to_period("M")
    primera = d.groupby("id_cliente")["periodo"].min().rename("cohorte")
    d = d.join(primera, on="id_cliente")
    d["edad"] = (d["periodo"].dt.year - d["cohorte"].dt.year) * 12 + d["periodo"].dt.month - d["cohorte"].dt.month
    cnt = d.groupby(["cohorte", "edad"])["id_cliente"].nunique().unstack(fill_value=0)
    ret = cnt.div(cnt.iloc[:, 0].replace(0, np.nan), axis=0) * 100
    ret.index = ret.index.astype(str)
    ret.attrs["muestra_insuficiente"] = bool(cnt.iloc[:, 0].min() < 10 or len(cnt) < 3)
    return ret


# stock y cobertura
def stock_cobertura(stock, lineas, threshold=LOW_STOCK_THRESHOLD, cutoff=None, ventana=COVERAGE_WINDOW_DAYS):
    """Cobertura (semanas) = stock / (demanda de la ventana / 4). Sin demanda: N/D. El stock es una instantánea."""
    d = _ventas(lineas)
    corte = pd.Timestamp(cutoff) if cutoff is not None else (d["fecha"].max() if not d.empty else pd.Timestamp.today())
    s = stock.copy()
    por_talla = "talla" in s and s["talla"].notna().any()
    claves = ["id_modelo", "talla"] if por_talla else ["id_modelo"]
    rec = d[d["fecha"] >= corte - pd.Timedelta(days=ventana)]
    dem = rec.groupby(claves, as_index=False).agg(demanda_28_dias=("cantidad", "sum"))
    if "fecha_corte" in s and s["fecha_corte"].notna().any():
        s = s.sort_values("fecha_corte").drop_duplicates(claves, keep="last")
    if not por_talla:
        s = s.drop(columns=[c for c in ("talla",) if c in s])
    x = s.merge(dem, on=claves, how="left", validate="one_to_one")
    nombres = lineas.drop_duplicates("id_modelo").set_index("id_modelo")["modelo"]
    x.insert(1, "modelo", x["id_modelo"].map(nombres))
    x["demanda_28_dias"] = x["demanda_28_dias"].fillna(0)
    dem_sem = x["demanda_28_dias"].astype(float) / (ventana / 7)
    x["cobertura_semanas"] = np.where(dem_sem > 0, x["stock_disponible"].astype(float) / dem_sem.replace(0, np.nan), np.nan)
    x["cobertura_estado"] = np.where(dem_sem > 0, "Calculada", "N/D")
    x["alerta"] = np.where(x["stock_disponible"] <= threshold, "Stock bajo", "Correcto")
    x["nivel_detalle"] = "modelo-talla" if por_talla else "modelo (ACC no exporta stock por talla)"
    return _meta(x, "analiticas.stock_cobertura", lineas, lineas.attrs.get("filtros"))


# calidad
def calidad_dataframe(snapshot):
    q = snapshot["quality"].copy()
    q["columnas"] = q["tabla"].map(lambda t: snapshot["tables"][t].shape[1])
    return q


def nulos_por_columna(snapshot):
    filas = [{"tabla": t, "columna": c, "nulos": int(df[c].isna().sum()), "filas": len(df)}
            for t in ("clientes", "modelos", "pedidos", "lineas", "stock")
            for df in [snapshot["tables"][t]] for c in df.columns]
    return pd.DataFrame(filas)


# anomalías IQR
def anomalias_iqr(lineas, min_muestra=8):
    """Atípicos por IQR dentro de cada modelo (grupo comparable). Se señalan, nunca se borran."""
    d = _ventas(lineas).copy()
    if d.empty:
        return d
    out = []
    for col in ("precio_unitario", "cantidad"):
        v = d[col].astype(float)
        gr = v.groupby(d["id_modelo"])
        q1, q3 = gr.transform(lambda s: s.quantile(.25)), gr.transform(lambda s: s.quantile(.75))
        n = gr.transform("size")
        iqr = q3 - q1
        flag = (n >= min_muestra) & (iqr > 0) & ((v < q1 - 1.5 * iqr) | (v > q3 + 1.5 * iqr))
        d[f"anomalia_{col}_iqr"] = flag
    res = d[d["anomalia_precio_unitario_iqr"] | d["anomalia_cantidad_iqr"]].copy()
    res["motivo"] = np.where(res["anomalia_precio_unitario_iqr"], "Precio atípico en su modelo", "Cantidad atípica en su modelo")
    return _meta(res, "analiticas.anomalias_iqr", lineas, lineas.attrs.get("filtros"))


# margen
def margen_por_modelo(lineas, tabla_costes=None):
    """Solo si ACC exporta un coste unitario fiable; si no, NO CALCULABLE (nunca se inventa un coste)."""
    if "coste_unitario" not in lineas.columns:
        return pd.DataFrame([{"estado": "NO CALCULABLE", "justificacion": "Coste no disponible: ACC no exporta coste unitario"}])
    d = _ventas(lineas)
    g = d.groupby("modelo").apply(lambda s: pd.Series({
        "precio_medio_ponderado": (s["importe_linea"].sum() / s["cantidad"].sum()),
        "margen_abs": (s["importe_linea"] - s["coste_unitario"] * s["cantidad"]).sum()}))
    return g.reset_index()


# reconciliación SQL
def reconciliacion(lineas, referencia=None, tolerancia=0.01):
    """Compara cifras de pandas con las de las consultas SQL de ACC (ver consultas_acc.sql).
    `referencia`: DataFrame con columnas metrica, valor_sql. Sin él, queda PENDIENTE (no se inventa)."""
    v, p = _ventas(lineas), pedidos_unicos(lineas)
    mes = sorted(lineas["mes"].unique())[-1] if len(lineas) else None
    pandas_vals = {
        "pedidos_unicos": float(p["id_pedido"].nunique()),
        "pedidos_venta": float(v["id_pedido"].nunique()),
        "pares_vendidos": _f(v["cantidad"].sum()),
        "ingresos_ventas": round(_f(v["importe_linea"].sum()), 2),
        "clientes_unicos": float(lineas["id_cliente"].nunique()),
        f"ingresos_mes_{mes}": round(_f(v.loc[v["mes"] == mes, "importe_linea"].sum()), 2),
    }
    df = pd.DataFrame({"metrica": list(pandas_vals), "valor_pandas": list(pandas_vals.values())})
    if referencia is None or referencia.empty:
        df["valor_sql"], df["diferencia"], df["estado"] = np.nan, np.nan, "PENDIENTE (falta resultado SQL de ACC)"
    else:
        df = df.merge(referencia[["metrica", "valor_sql"]], on="metrica", how="left")
        df["diferencia"] = df["valor_pandas"] - df["valor_sql"]
        df["estado"] = np.where(df["valor_sql"].isna(), "PENDIENTE", np.where(df["diferencia"].abs() <= tolerancia, "OK", "DISCREPANCIA"))
    return _meta(df, "analiticas.reconciliacion", lineas, lineas.attrs.get("filtros"))


# KPIs
def kpis_calculo(lineas, pedidos):
    v = _ventas(lineas)
    pv = pedidos[pedidos["es_venta"]]
    est = pedidos["estado"].astype(str).str.lower()
    ing, pares = _f(v["importe_linea"].sum()), _f(v["cantidad"].sum())
    n_venta = int(pv["id_pedido"].nunique())
    abc = modelos_abc(lineas)
    k20 = max(1, int(np.ceil(len(abc) * .2))) if len(abc) else 0
    mens = ventas_por_periodo(lineas)
    talla = v.groupby("talla")["cantidad"].sum()
    hay_custom = pedidos["segmento"].eq("Custom").any()
    return {
        "pedidos_actividad": int(pedidos["id_pedido"].nunique()),
        "pedidos_venta": n_venta,
        "pedidos_pendientes": int(pedidos.loc[est.isin(PENDING_STATES), "id_pedido"].nunique()),
        "pedidos_cancelados": int(pedidos.loc[est.isin(CANCEL_STATES), "id_pedido"].nunique()),
        "pares": pares, "ingresos": ing,
        "ticket": ing / n_venta if n_venta else 0.0,
        "pares_por_pedido": pares / n_venta if n_venta else 0.0,
        "tasa_cancelacion_pct": 100 * pedidos.loc[est.isin(CANCEL_STATES), "id_pedido"].nunique() / max(1, pedidos["id_pedido"].nunique()),
        "custom_pct": float(pedidos["segmento"].eq("Custom").mean() * 100) if hay_custom else float("nan"),
        "clientes_activos": int(v["id_cliente"].nunique()),
        "modelos_vendidos": int(v["id_modelo"].nunique()),
        "top_modelo": abc["modelo"].iloc[0] if len(abc) else "N/D",
        "talla_mas_vendida": str(talla.idxmax()) if len(talla) else "N/D",
        "pareto_top20_modelos_pct": _f(abc["ingresos"].head(k20).sum()) / ing * 100 if ing and k20 else 0.0,
        "variacion_ultimo_mes_pct": _f(mens["variacion_ingresos_pct"].iloc[-1]) if len(mens) > 1 else float("nan"),
    }


KPI_DEFINICIONES = [
    ("pedidos_actividad", "Nº de id_pedido distintos (todos los estados)", "Todos los pedidos del filtro"),
    ("pedidos_venta", "id_pedido distintos con estado Entregado/Enviado (SALES_STATES)", "Pedidos del filtro"),
    ("pedidos_pendientes", "id_pedido distintos en estado pendiente / en preparación", "Pedidos del filtro"),
    ("pedidos_cancelados", "id_pedido distintos cancelados", "Pedidos del filtro"),
    ("pares", "Σ cantidad de líneas de pedidos de venta (unidades)", "Líneas de venta"),
    ("ingresos", "Σ cantidad × precio_unitario de líneas de venta (bruto, sin IVA ni descuentos)", "Líneas de venta"),
    ("ticket", "ingresos / pedidos_venta", "Pedidos de venta (nunca líneas)"),
    ("pares_por_pedido", "pares / pedidos_venta", "Pedidos de venta"),
    ("tasa_cancelacion_pct", "pedidos_cancelados / pedidos_actividad × 100", "Pedidos del filtro"),
    ("custom_pct", "pedidos Custom / pedidos_actividad × 100 (N/D si no hay Custom)", "Pedidos del filtro"),
    ("clientes_activos", "id_cliente distintos con alguna venta", "Clientes con ventas"),
    ("modelos_vendidos", "id_modelo distintos con alguna venta", "Modelos con ventas"),
    ("talla_mas_vendida", "talla con mayor Σ cantidad", "Líneas de venta"),
    ("pareto_top20_modelos_pct", "ingresos del 20 % de modelos con más ingresos / ingresos", "Ingresos de venta"),
    ("variacion_ultimo_mes_pct", "(ingresos mes − ingresos mes previo) / ingresos mes previo × 100", "Meses con ventas"),
]


def kpis_tabla(kpis, lineas):
    return _meta(pd.DataFrame([(n, kpis.get(n), f, d) for n, f, d in KPI_DEFINICIONES],
                                columns=["kpi", "valor", "formula", "denominador"]), "analiticas.kpis_tabla", lineas)


# orquestador
def build_analytics(snapshot, filters=None):
    """Todos los DataFrames y KPIs a partir de UN mismo snapshot y los mismos filtros."""
    l = filter_lines(snapshot["lineas"], **(filters or {}))
    p = pedidos_unicos(l)
    units, prop = matriz_modelo_talla(l)
    kp = kpis_calculo(l, p)
    return {
        "lineas_enriquecidas": l, "pedidos_unicos": p, "ventas_periodo": ventas_por_periodo(l),
        "ventas_trimestre": ventas_por_trimestre(l), "modelos_abc": modelos_abc(l),
        "matriz_modelo_talla": units, "proporcion_tallas": prop, "custom_estandar": custom_estandar(p),
        "rfm": clientes_rfm(l, snapshot["tables"]["clientes"]), "cohortes": cohortes(l),
        "stock_cobertura": stock_cobertura(snapshot["tables"]["stock"], l),
        "calidad": calidad_dataframe(snapshot), "nulos_columna": nulos_por_columna(snapshot),
        "anomalias": anomalias_iqr(l), "margen": margen_por_modelo(l),
        "reconciliacion": reconciliacion(l, snapshot.get("referencia_sql")),
        "kpis": kp, "kpis_tabla": kpis_tabla(kp, l),
    }
