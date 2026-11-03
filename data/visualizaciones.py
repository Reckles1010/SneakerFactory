"""Funciones de visualización y exportación para el dashboard."""
import streamlit as st
import pandas as pd

def show_df(label, df, key):
    """Muestra un DataFrame en un expander con opción de descarga CSV."""
    with st.expander(f"Ver datos: {label}"):
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            f"Descargar {label} (CSV)", 
            csv, 
            file_name=f"{key}.csv", 
            mime="text/csv", 
            key=f"download_{key}"
        )

def line_chart(df, x, y, title, y_label):
    """Renderiza un gráfico de líneas controlado."""
    st.markdown(f"**{title}**")
    if df is None or df.empty or x not in df.columns or y not in df.columns:
        st.info("No hay datos suficientes para esta visualización.")
        return
    chart = df.set_index(x)[[y]]
    st.line_chart(chart, y_label=y_label, use_container_width=True)

def bar_chart(df, x, y, title, y_label):
    """Renderiza un gráfico de barras controlado."""
    st.markdown(f"**{title}**")
    if df is None or df.empty or x not in df.columns or y not in df.columns:
        st.info("No hay datos suficientes para esta visualización.")
        return
    st.bar_chart(df.set_index(x)[[y]], y_label=y_label, use_container_width=True)

def build_analytics(snapshot):
    """
    Construye las analíticas y KPIs a partir del snapshot validado del pipeline.
    Integra las tablas principales y secundarias (clientes, modelos, pedidos, lineas, stock, almacenes, etc.).
    """
    tables = snapshot.get("tables", {})
    lineas = snapshot.get("lineas", pd.DataFrame())

    # Extracción segura de dataframes auxiliares para métricas adicionales si se requieren
    clientes = tables.get("clientes", pd.DataFrame())
    modelos = tables.get("modelos", pd.DataFrame())
    pedidos = tables.get("pedidos", pd.DataFrame())
    stock = tables.get("stock", pd.DataFrame())
    almacen = tables.get("almacen", pd.DataFrame())
    sucursal = tables.get("sucursal", pd.DataFrame())

    # Cálculo seguro de KPIs globales operativos
    total_facturado = float(lineas["importe_linea"].sum()) if not lineas.empty and "importe_linea" in lineas.columns else 0.0
    total_pares = int(lineas["cantidad"].sum()) if not lineas.empty and "cantidad" in lineas.columns else 0
    total_pedidos = int(pedidos["id_pedido"].nunique()) if not pedidos.empty and "id_pedido" in pedidos.columns else 0
    total_clientes = int(clientes["id_cliente"].nunique()) if not clientes.empty and "id_cliente" in clientes.columns else 0

    kpis = {
        "facturacion_total": total_facturado,
        "pares_totales": total_pares,
        "pedidos_totales": total_pedidos,
        "clientes_totales": total_clientes,
    }

    # Agrupaciones temporales y analíticas base
    ventas_por_mes = pd.DataFrame(columns=["mes", "importe_linea"])
    if not lineas.empty and "mes" in lineas.columns and "importe_linea" in lineas.columns:
        ventas_por_mes = lineas.groupby("mes", as_index=False)["importe_linea"].sum().sort_values("mes")

    ventas_por_modelo = pd.DataFrame(columns=["modelo", "cantidad"])
    if not lineas.empty and "modelo" in lineas.columns and "cantidad" in lineas.columns:
        ventas_por_modelo = lineas.groupby("modelo", as_index=False)["cantidad"].sum().sort_values("cantidad", ascending=False)

    result = {
        "kpis": kpis,
        "ventas_por_mes": ventas_por_mes,
        "ventas_por_modelo": ventas_por_modelo,
        "lineas": lineas,
        "clientes": clientes,
        "modelos": modelos,
        "pedidos": pedidos,
        "stock": stock,
        "almacen": almacen,
        "sucursal": sucursal,
    }

    return result