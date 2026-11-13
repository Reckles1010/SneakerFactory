"""Componentes Streamlit para tablas y gráficos del dashboard (sin lógica de cálculo)."""
import numpy as np
import pandas as pd
import streamlit as st


def _version():
    try:
        return tuple(int(x) for x in st.__version__.split(".")[:2])
    except Exception:
        return (0, 0)


# Streamlit reciente sustituye use_container_width=True por width="stretch".
STRETCH = {"width": "stretch"} if _version() >= (1, 50) else {"use_container_width": True}


def show_df(label, df, key):
    """Muestra la tabla que hay detrás de un gráfico y permite descargarla en CSV UTF-8."""
    with st.expander(f"Ver datos: {label}"):
        st.dataframe(df, hide_index=True, **STRETCH)
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(f"Descargar {label} (CSV)", csv, file_name=f"{key}.csv", mime="text/csv", key=f"download_{key}")


def _grafico(fn, chart, y_label):
    try:
        fn(chart, y_label=y_label, **STRETCH)
    except TypeError:                              # versiones antiguas sin y_label
        fn(chart, **STRETCH)


def line_chart(df, x, y, title, y_label):
    st.markdown(f"**{title}**")
    if df is None or df.empty or x not in df.columns or y not in df.columns:
        st.info("No hay datos suficientes para esta visualización.")
        return
    _grafico(st.line_chart, df.set_index(x)[[y]].astype(float), y_label)


def bar_chart(df, x, y, title, y_label):
    st.markdown(f"**{title}**")
    if df is None or df.empty or x not in df.columns or y not in df.columns:
        st.info("No hay datos suficientes para esta visualización.")
        return
    _grafico(st.bar_chart, df.set_index(x)[[y]].astype(float), y_label)


def heatmap(df, fmt="{:.0f}"):
    """Mapa de calor de una matriz (requiere matplotlib; si falta, muestra la tabla simple)."""
    if df is None or df.empty:
        st.info("No hay datos suficientes para esta visualización.")
        return
    try:
        st.dataframe(df.astype(float).style.background_gradient(cmap="Blues").format(fmt), **STRETCH)
    except Exception:
        st.dataframe(df, **STRETCH)


def histograma(serie, etiqueta, bins=20):
    """Distribución (histograma) calculada con NumPy a partir de una serie numérica."""
    s = pd.to_numeric(serie, errors="coerce").dropna().astype(float)
    if s.empty:
        st.info("No hay datos suficientes para esta visualización.")
        return
    cuentas, bordes = np.histogram(s, bins=bins)
    idx = [f"{bordes[i]:.0f}–{bordes[i+1]:.0f}" for i in range(len(cuentas))]
    st.bar_chart(pd.DataFrame({etiqueta: cuentas}, index=idx), **STRETCH)
