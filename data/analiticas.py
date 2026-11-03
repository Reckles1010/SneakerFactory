"""Funciones pandas puras para vistas analíticas; ninguna depende de Streamlit."""
import pandas as pd
import numpy as np
from data.config import SALES_STATES, CANCEL_STATES, CUSTOM_VALUES

def _sales_mask(df):
    return df["estado_normalizado"].isin([x.lower() for x in SALES_STATES])

def filter_lines(df, start=None, end=None, models=None, sizes=None, types=None, states=None):
    out = df.copy()
    if start: out = out[out["fecha"] >= pd.Timestamp(start)]
    if end: out = out[out["fecha"] < pd.Timestamp(end) + pd.Timedelta(days=1)]
    if models: out = out[out["modelo"].astype(str).isin(models)]
    if sizes: out = out[out["talla"].astype(str).isin(sizes)]
    if types: out = out[out["tipo"].astype(str).isin(types)]
    if states: out = out[out["estado"].astype(str).isin(states)]
    return out

def pedidos_unicos(lineas):
    return (lineas.groupby(["id_pedido","fecha","id_cliente","estado","tipo"], dropna=False)
            .agg(pares=("cantidad","sum"), importe=("importe_linea","sum"),
                 numero_lineas=("id_pedido","size"), modelos=("id_modelo","nunique"))
            .reset_index().assign(ticket=lambda x: np.where(x["numero_lineas"] > 0, x["importe"], np.nan)))

def ventas_por_periodo(lineas):
    d = lineas[_sales_mask(lineas)].copy()
    out = d.groupby("mes", as_index=False).agg(ingresos=("importe_linea","sum"), pares=("cantidad","sum"), pedidos=("id_pedido","nunique"))
    out["ticket_medio"] = out["ingresos"] / out["pedidos"].replace(0, np.nan)
    out = out.sort_values("mes")
    out["variacion_ingresos_pct"] = out["ingresos"].pct_change() * 100
    out["media_3_meses_previos"] = out["ingresos"].shift(1).rolling(3, min_periods=1).mean()
    return out

def modelos_abc(lineas):
    d = lineas[_sales_mask(lineas)]
    x = d.groupby(["id_modelo","modelo"], as_index=False).agg(ingresos=("importe_linea","sum"), unidades=("cantidad","sum"))
    x = x.sort_values("ingresos", ascending=False)
    total = x["ingresos"].sum()
    x["peso_pct"] = x["ingresos"] / total * 100 if total else 0
    x["acumulado_pct"] = x["peso_pct"].cumsum()
    x["clase_abc"] = np.select([x["acumulado_pct"] <= 80, x["acumulado_pct"] <= 95], ["A","B"], default="C")
    return x

def matriz_modelo_talla(lineas):
    d = lineas[_sales_mask(lineas)]
    units = d.pivot_table(index="modelo", columns="talla", values="cantidad", aggfunc="sum", fill_value=0)
    proportions = units.div(units.sum(axis=1).replace(0, np.nan), axis=0) * 100
    return units, proportions

def custom_vs_estandar(pedidos):
    x = pedidos.copy()
    x["segmento"] = np.where(x["tipo"].astype(str).str.lower().isin(CUSTOM_VALUES), "Custom", "Estándar")
    return x.groupby("segmento", as_index=False).agg(pedidos=("id_pedido","nunique"), pares=("pares","sum"), ingresos=("importe","sum"),
            ticket_medio=("ticket","mean"), cancelados=("estado", lambda s: s.astype(str).str.lower().isin(["cancelado","cancelada"]).sum()))

def clientes_rfm(lineas, clientes, cutoff=None):
    d = lineas[_sales_mask(lineas)].copy()
    if cutoff is None:
        cutoff = d["fecha"].max() if not d.empty else pd.Timestamp.today()
    cutoff = pd.Timestamp(cutoff)
    valid_orders = d[["id_cliente","id_pedido"]].drop_duplicates()
    r = d.groupby("id_cliente").agg(ultima_compra=("fecha","max"), monetary=("importe_linea","sum"), pares=("cantidad","sum")).reset_index()
    f = valid_orders.groupby("id_cliente").agg(frequency=("id_pedido","nunique")).reset_index()
    r = r.merge(f, on="id_cliente", how="left", validate="one_to_one")
    r["recency_dias"] = (cutoff - r["ultima_compra"]).dt.days
    r["segmento_rfm"] = np.select([r["recency_dias"] <= 30, r["frequency"] >= 3, r["frequency"] == 1],
                                   ["Reciente","Recurrente","Primera compra"], default="En riesgo")
    out = clientes[["id_cliente"]].drop_duplicates().merge(r, on="id_cliente", how="left", validate="one_to_one")
    out["segmento_rfm"] = out["segmento_rfm"].fillna("Sin compras válidas")
    return out

def cohortes(lineas):
    d = lineas[_sales_mask(lineas)].copy()
    if d.empty: return pd.DataFrame()
    d["periodo"] = d["fecha"].dt.to_period("M")
    first = d.groupby("id_cliente")["periodo"].min().rename("cohorte")
    d = d.join(first, on="id_cliente")
    d["edad_cohorte"] = (d["periodo"].dt.year-d["cohorte"].dt.year)*12 + d["periodo"].dt.month-d["cohorte"].dt.month
    counts = d.groupby(["cohorte","edad_cohorte"])["id_cliente"].nunique().unstack(fill_value=0)
    return counts.div(counts.iloc[:,0].replace(0,np.nan), axis=0) * 100

def stock_cobertura(stock, lineas, threshold=10, cutoff=None):
    d = lineas[_sales_mask(lineas)].copy()
    if cutoff is None: cutoff = d["fecha"].max() if not d.empty else pd.Timestamp.today()
    cutoff = pd.Timestamp(cutoff)
    recent = d[d["fecha"] >= cutoff - pd.Timedelta(days=28)].groupby(["id_modelo","talla"], as_index=False).agg(demanda_28_dias=("cantidad","sum"))
    s = stock.copy()
    if "fecha_corte" in s.columns and s["fecha_corte"].notna().any():
        s = s.sort_values("fecha_corte").drop_duplicates(["id_modelo","talla"], keep="last")
    x = s.merge(recent, on=["id_modelo","talla"], how="left", validate="one_to_one")
    x["demanda_28_dias"] = x["demanda_28_dias"].fillna(0)
    x["cobertura_semanas"] = np.where(x["demanda_28_dias"] > 0, x["stock_disponible"] / (x["demanda_28_dias"]/4), np.nan)
    x["alerta"] = np.where(x["stock_disponible"] <= threshold, "Stock bajo", "Correcto")
    x["cobertura_estado"] = np.where(x["demanda_28_dias"] > 0, "Calculada", "N/D")
    return x

def calidad_dataframe(snapshot):
    tables = snapshot["tables"]
    rows = []
    for name, df in tables.items():
        rows.append({"tabla":name, "filas_recibidas":len(df), "filas_validas":len(df), "filas_rechazadas":0,
                     "nulos_totales":int(df.isna().sum().sum()), "columnas":len(df.columns)})
    return pd.DataFrame(rows)

def anomalias_iqr(lineas):
    d = lineas[_sales_mask(lineas)].copy()
    if d.empty: return d
    q1 = d.groupby("id_modelo")["precio_unitario"].transform("quantile", 0.25)
    q3 = d.groupby("id_modelo")["precio_unitario"].transform("quantile", 0.75)
    iqr = q3-q1
    d["anomalia_precio_iqr"] = (d["precio_unitario"] < q1-1.5*iqr) | (d["precio_unitario"] > q3+1.5*iqr)
    return d[d["anomalia_precio_iqr"]]

def build_analytics(snapshot, filters=None):
    filters = filters or {}
    l = filter_lines(snapshot["lineas"], **filters)
    p = pedidos_unicos(l)
    sales = l[_sales_mask(l)]
    abc = modelos_abc(l)
    units, proportions = matriz_modelo_talla(l)
    return {
        "lineas_enriquecidas": l,
        "pedidos_unicos": p,
        "ventas_periodo": ventas_por_periodo(l),
        "modelos_abc": abc,
        "matriz_modelo_talla": units,
        "proporcion_tallas": proportions,
        "custom_estandar": custom_vs_estandar(p),
        "rfm": clientes_rfm(l, snapshot["tables"]["clientes"]),
        "cohortes": cohortes(l),
        "stock_cobertura": stock_cobertura(snapshot["tables"]["stock"], l),
        "calidad": calidad_dataframe(snapshot),
        "anomalias": anomalias_iqr(l),
        "kpis": {
            "pedidos_actividad": int(p["id_pedido"].nunique()),
            "pedidos_venta": int(p[p["estado"].astype(str).str.lower().isin(["confirmado","entregado"])]["id_pedido"].nunique()),
            "pares": float(sales["cantidad"].sum()),
            "ingresos": float(sales["importe_linea"].sum()),
            "ticket": float(p[p["estado"].astype(str).str.lower().isin(["confirmado","entregado"])]["importe"].mean()) if not p.empty else 0.0,
            "custom_pct": float(p["tipo"].astype(str).str.lower().isin(["custom","personalizado","personalizada"]).mean()*100) if not p.empty else 0.0,
        }
    }
