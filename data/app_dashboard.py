
from datetime import datetime
import time
import json

import streamlit as st
import pandas as pd

from data.config import (
    INPUT_DIR,
    AUTO_REFRESH_SECONDS,
    LOW_STOCK_THRESHOLD,
    CURRENCY,
    LOG_DIR
)

from data.pipeline import load_and_validate, PipelineError
from data.analiticas import build_analytics
from data.visualizaciones import show_df, line_chart, bar_chart

st.set_page_config(
    page_title="MERCURY | Sneaker Factory",
    page_icon="C:\\DAM\\2º DAM\\1ºPROYECTO\\frontend\\assets\\SinFondo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f4f4f5;
    color: #080808;
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #080808;
}

.stAppViewBlockContainer {
    padding-top: 0.8rem !important;
    padding-bottom: 1rem !important;
}

[data-testid="stMainBlockContainer"] {
    padding-top: 0.8rem !important;
}

.block-container {
    padding-top: 0.8rem !important;
}

h1 {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e4e4e7;
    padding: 18px;
    border-radius: 12px;
}

[data-testid="stMetricValue"] {
    color: #080808;
    font-family: 'Space Grotesk', sans-serif;
}

.stButton button,
.stDownloadButton button {
    background: #080808;
    color: white;
    border: 0;
    border-radius: 5px;
}

.stButton button:hover,
.stDownloadButton button:hover {
    background: #179fb5;
    color: white;
}

/* FORZAR VISIBILIDAD DE LA BARRA LATERAL */

section[data-testid="stSidebar"] {
    background: #080808 !important;
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    width: 21rem !important;
    min-width: 21rem !important;
    transform: translateX(0) !important;
    margin-left: 0 !important;
    transition: none !important;
}

/* Texto de la barra lateral */

section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

/* Botón para volver a desplegarla */

button[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
}

.mercury-brand {
    color: #080808;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 25px;
    font-weight: 800;
    letter-spacing: 0.12em;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    line-height: 1.2;
}

.mercury-y {
    position: relative;
}

.mercury-y::after {
    content: "";
    display: inline-block;
    width: 3px;
    height: 27px;
    background-color: #179fb5;
    margin-left: 7px;
    vertical-align: middle;
}

.mercury-sub {
    color: #666666;
    font-size: 12px;
    letter-spacing: 0.12em;
    margin-top: 5px;
    margin-bottom: 15px;
}

.status-ok {
    color: #14804a;
    font-weight: 700;
}

.status-error {
    color: #b42318;
    font-weight: 700;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: transparent;
}

button[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="mercury-brand">
    MERCUR<span class="mercury-y">Y</span>
</div>

<div class="mercury-sub">
    SNEAKER FACTORY
</div>
""", unsafe_allow_html=True)

st.title("Dashboard operacional")

st.caption(
    "Inteligencia de negocio · Exportaciones de Acceso a Datos · "
    "Actualización automática cada 60 segundos"
)

if "last_good_snapshot" not in st.session_state:
    st.session_state.last_good_snapshot = None

if "last_good_analytics" not in st.session_state:
    st.session_state.last_good_analytics = None

if "last_valid_at" not in st.session_state:
    st.session_state.last_valid_at = None

if "last_signature" not in st.session_state:
    st.session_state.last_signature = None

if "last_status" not in st.session_state:
    st.session_state.last_status = "Pendiente de primera comprobación"

if "last_error" not in st.session_state:
    st.session_state.last_error = ""

with st.sidebar:

    st.markdown("## MERCURY")
    st.caption("ACC · REAL")

    st.markdown("---")

    st.markdown("### Filtros transversales")

    reset = st.button(
        "Restablecer filtros",
        use_container_width=True
    )

    if reset:
        for key in [
            "date_range",
            "models_filter",
            "sizes_filter",
            "types_filter",
            "states_filter"
        ]:
            st.session_state.pop(key, None)

    st.caption(
        "Los filtros afectan a KPIs, tablas y gráficos del mismo snapshot."
    )

    st.markdown("---")

    snapshot_sidebar = st.session_state.get("last_good_snapshot")

    if snapshot_sidebar is not None and "lineas" in snapshot_sidebar:

        lineas = snapshot_sidebar["lineas"]

        min_date = (
            lineas["fecha"].min().date()
            if not lineas.empty
            else datetime.now().date()
        )

        max_date = (
            lineas["fecha"].max().date()
            if not lineas.empty
            else datetime.now().date()
        )

        date_range = st.date_input(
            "Periodo",
            value=(min_date, max_date),
            key="date_range"
        )

        models = sorted(
            lineas["modelo"].dropna().astype(str).unique()
        )

        sizes = sorted(
            lineas["talla"].dropna().astype(str).unique()
        )

        types = sorted(
            lineas["tipo"].dropna().astype(str).unique()
        )

        states = sorted(
            lineas["estado"].dropna().astype(str).unique()
        )

        selected_models = st.multiselect(
            "Modelo",
            models,
            key="models_filter"
        )

        selected_sizes = st.multiselect(
            "Talla",
            sizes,
            key="sizes_filter"
        )

        selected_types = st.multiselect(
            "Tipo de pedido",
            types,
            key="types_filter"
        )

        selected_states = st.multiselect(
            "Estado",
            states,
            key="states_filter"
        )

    else:

        date_range = None

        selected_models = None
        selected_sizes = None
        selected_types = None
        selected_states = None

        st.info(
            "Sincroniza los CSV correctamente para habilitar los filtros."
        )


@st.fragment(run_every=f"{AUTO_REFRESH_SECONDS}s")
def dashboard_refresh():

    force = st.button(
        "↻ Actualizar ahora",
        key="refresh_now"
    )

    check_at = datetime.now().astimezone()
    start_time = time.perf_counter()

    try:

        snapshot = load_and_validate(INPUT_DIR)

        analytics = build_analytics(snapshot)

        changed = (
            snapshot["signature"] != st.session_state.last_signature
        )

        st.session_state.last_good_snapshot = snapshot
        st.session_state.last_good_analytics = analytics

        st.session_state.last_signature = snapshot["signature"]

        st.session_state.last_valid_at = (
            datetime.now().astimezone().isoformat()
        )

        st.session_state.last_status = (
            "correcto" if changed else "sin cambios"
        )

        st.session_state.last_error = ""

        elapsed = time.perf_counter() - start_time

        LOG_DIR.mkdir(exist_ok=True, parents=True)

        with (LOG_DIR / "refrescos.jsonl").open(
            "a",
            encoding="utf-8"
        ) as f:

            f.write(
                json.dumps(
                    {
                        "comprobacion": check_at.isoformat(),
                        "origen": "ACC · REAL",
                        "estado": st.session_state.last_status,
                        "filas": snapshot["valid_rows"],
                        "duracion_segundos": elapsed
                    },
                    ensure_ascii=False
                ) + "\n"
            )

    except Exception as exc:

        st.session_state.last_status = (
            "datos inválidos"
            if isinstance(exc, PipelineError)
            else "error de carga"
        )

        st.session_state.last_error = str(exc)

        if isinstance(exc, PipelineError) and exc.issues:
            st.dataframe(
                pd.DataFrame(exc.issues),
                use_container_width=True,
                hide_index=True
            )

    snapshot = st.session_state.last_good_snapshot
    analytics = st.session_state.last_good_analytics

    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Procedencia", "ACC · REAL")

    c2.metric(
        "Estado",
        st.session_state.last_status
    )

    c3.metric(
        "Última comprobación",
        check_at.strftime("%d/%m/%Y %H:%M:%S")
    )

    c4.metric(
        "Última actualización válida",
        st.session_state.last_valid_at or "Sin actualización"
    )

    if st.session_state.last_error:
        st.error(
            f"{st.session_state.last_status.upper()}: "
            f"{st.session_state.last_error}"
        )

    if snapshot is None or analytics is None:

        st.warning(
            f"No hay un snapshot válido que mostrar. "
            f"Coloca los cinco CSV en: `{INPUT_DIR}`. "
            "No se publican cálculos parciales."
        )

        return

    if st.session_state.last_error:

        st.error(
            "DESACTUALIZADO · Se conserva el último snapshot íntegro "
            f"de {st.session_state.last_valid_at}. "
            "Los datos mostrados no son actuales."
        )

    st.caption(
        f"Filas válidas: {sum(snapshot['valid_rows'].values()):,} · "
        f"Procesamiento: {snapshot['processing_seconds']:.3f} s · "
        f"Corte: {snapshot['checked_at']} · "
        f"{st.session_state.last_status}"
    )


    filters = {

        "start": (
            date_range[0]
            if isinstance(date_range, tuple) and len(date_range) == 2
            else None
        ),

        "end": (
            date_range[1]
            if isinstance(date_range, tuple) and len(date_range) == 2
            else None
        ),

        "models": selected_models or None,
        "sizes": selected_sizes or None,
        "types": selected_types or None,
        "states": selected_states or None
    }

    a = build_analytics(snapshot, filters)

    k = a["kpis"]


    tabs = st.tabs([
        "01 · Dirección",
        "02 · Producto y ventas",
        "03 · Clientes",
        "04 · Almacén",
        "05 · Calidad y auditoría",
        "06 · Modelos predictivos"
    ])

    with tabs[0]:

        st.subheader("Resumen ejecutivo")

        cols = st.columns(4)

        cols[0].metric(
            "Ingresos válidos",
            f"{k['ingresos']:,.2f} {CURRENCY}"
        )

        cols[1].metric(
            "Pares vendidos",
            f"{k['pares']:,.0f}"
        )

        cols[2].metric(
            "Pedidos únicos (actividad)",
            f"{k['pedidos_actividad']:,}"
        )

        cols[3].metric(
            "Ticket medio",
            f"{k['ticket']:,.2f} {CURRENCY}"
        )

        st.caption(
            "Ingresos y pares: pedidos confirmados/entregados. "
            "Pedidos únicos: actividad total, incluidos pendientes "
            "y cancelados. Ticket: importe medio por pedido de venta válido."
        )

        line_chart(
            a["ventas_periodo"],
            "mes",
            "ingresos",
            "Evolución mensual de ingresos",
            "Euros (€)"
        )

        show_df(
            "Ventas por periodo",
            a["ventas_periodo"],
            "ventas_por_periodo"
        )

    with tabs[1]:

        st.subheader("Producto y ventas")

        left, right = st.columns(2)

        with left:

            bar_chart(
                a["modelos_abc"].head(10),
                "modelo",
                "ingresos",
                "Top 10 modelos por ingresos",
                "Euros (€)"
            )

        with right:

            st.markdown("**Contribución Custom vs estándar**")

            st.bar_chart(
                a["custom_estandar"].set_index("segmento")[
                    ["ingresos", "pares"]
                ],
                use_container_width=True
            )

        st.markdown("**Matriz modelo × talla · pares vendidos**")

        st.dataframe(
            a["matriz_modelo_talla"],
            use_container_width=True
        )

        st.markdown("**Pareto ABC de modelos**")

        st.dataframe(
            a["modelos_abc"],
            use_container_width=True,
            hide_index=True
        )

        show_df(
            "Modelos ABC",
            a["modelos_abc"],
            "modelos_abc"
        )

        show_df(
            "Comparativa Custom y estándar",
            a["custom_estandar"],
            "custom_estandar"
        )

    with tabs[2]:

        st.subheader("Clientes")

        rfm = a["rfm"]

        st.metric(
            "Clientes en el análisis",
            f"{rfm['id_cliente'].nunique():,}"
        )

        st.bar_chart(
            rfm["segmento_rfm"].value_counts(),
            use_container_width=True
        )

        st.dataframe(
            rfm,
            use_container_width=True,
            hide_index=True
        )

        show_df(
            "Clientes RFM",
            rfm,
            "clientes_rfm"
        )

        cohortes = a["cohortes"]

        if cohortes.empty:

            st.info(
                "Cohortes no calculables: "
                "no hay historial suficiente de ventas válidas."
            )

        else:

            st.dataframe(
                cohortes.style.format("{:.1f}%"),
                use_container_width=True
            )

    with tabs[3]:

        st.subheader("Almacén")

        st.warning(
            "El stock representa una instantánea (snapshot) "
            "de la exportación. No es un histórico de movimientos."
        )

        stock = a["stock_cobertura"]

        low = stock[
            stock["alerta"] == "Stock bajo"
        ]

        x, y = st.columns(2)

        x.metric(
            "Variantes con stock bajo",
            len(low)
        )

        y.metric(
            "Umbral de alerta",
            f"{LOW_STOCK_THRESHOLD} unidades"
        )

        if not low.empty:

            st.error(
                "Hay variantes con stock igual o inferior "
                "al umbral configurado."
            )

        st.dataframe(
            stock,
            use_container_width=True,
            hide_index=True
        )

        bar_chart(
            stock.groupby(
                "id_modelo",
                as_index=False
            )["stock_disponible"].sum(),

            "id_modelo",
            "stock_disponible",
            "Stock disponible por modelo",
            "Pares"
        )

        show_df(
            "Stock y cobertura",
            stock,
            "stock_cobertura"
        )

    with tabs[4]:

        st.subheader("Calidad y auditoría")

        st.dataframe(
            a["calidad"],
            use_container_width=True,
            hide_index=True
        )

        st.metric(
            "Incidencias registradas",
            len(snapshot["issues"])
        )

        if not snapshot["issues"].empty:

            st.dataframe(
                snapshot["issues"],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.success(
                "Sin incidencias bloqueantes en el snapshot publicado."
            )

        st.markdown("**Manifiesto de origen**")

        st.dataframe(
            snapshot["manifest"],
            use_container_width=True,
            hide_index=True
        )

        show_df(
            "Líneas enriquecidas (filtradas)",
            a["lineas_enriquecidas"],
            "lineas_enriquecidas"
        )

        show_df(
            "Pedidos únicos (filtrados)",
            a["pedidos_unicos"],
            "pedidos_unicos"
        )

        show_df(
            "Anomalías IQR",
            a["anomalias"],
            "anomalias_iqr"
        )

    with tabs[5]:

        st.subheader("Modelos predictivos")

        st.info(
            "El predictor se mantiene separado del panel operativo REAL. "
            "El enunciado exige entrenarlo con histórico sintético "
            "identificado, reservar los últimos tres meses y compararlo "
            "con baseline. Esta sección no mostrará predicciones hasta "
            "incorporar y evaluar ese módulo; no se inventan previsiones."
        )

        st.caption(
            "Origen requerido para ML: SINTÉTICO · "
            "Nunca se mezcla con ACC · REAL."
        )

dashboard_refresh()
