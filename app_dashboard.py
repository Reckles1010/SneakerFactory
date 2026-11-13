from datetime import datetime
import time
import json
from pathlib import Path
import streamlit as st
import pandas as pd
try:
    from sklearn.ensemble import IsolationForest
except ImportError:
    IsolationForest = None
from data.config import (
    INPUT_DIR,
    AUTO_REFRESH_SECONDS,
    LOW_STOCK_THRESHOLD,
    CURRENCY,
    LOG_DIR,
)
from data.pipeline import load_and_validate, PipelineError
from data.analiticas import build_analytics
from data.visualizaciones import show_df, line_chart, bar_chart, heatmap, histograma, STRETCH
from data.segmentacion import kmeans_clientes

_ICONO = next((str(p) for p in [Path(__file__).resolve().parent / "frontend" / "assets" / "SinFondo.png"] if p.exists()), "👟")

st.set_page_config(
    page_title="MERCURY · Dashboard operacional",
    page_icon=_ICONO,
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{
    --primary-color: lightblue;
}

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
    font-size: 1.5rem;
}
[data-testid="stMetricValue"] > div {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
}
.stButton button,
.stDownloadButton button {
    background: #179fb5;
    color: white;
    border: 0;
    border-radius: 5px;
}
.stButton button:hover,
.stDownloadButton button:hover {
    background: #179fb5;
    color: white;
}

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
section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
    gap: 0.5rem; /* Reduce la separación general entre elementos de la barra */
    padding-top: 0rem !important;
}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:first-child {
    margin-top: 0rem !important;
    padding-top: 0rem !important;
}
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0px !important;
    min-height: 0px !important;
    visibility: hidden; /* Oculta los elementos por defecto del header si no los usas */
}
/* 2. Forzar al contenedor principal y al sidebar a subir al borde superior (0rem) */
.stAppViewBlockContainer, 
[data-testid="stMainBlockContainer"], 
.block-container {
    padding-top: 0rem !important;
}
/* 3. Subir el contenido interno de la barra lateral arriba del todo */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    padding-top: 0rem !important;
}
button[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    color: red;
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
    color: #179fb5;
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
[data-testid="stMarkdownContainer"] {
    margin-bottom: 0rem;
    padding-bottom: 0rem;
}
/* Color de las etiquetas seleccionadas en los multiselect */
section[data-testid="stSidebar"] [data-testid="stMultiSelect"] span[data-tag] {
    background-color: #179fb5 !important;
    color: #ffffff !important;
    border: 1px solid #179fb5 !important;
    border-radius: 5px !important;
}

/* Texto de las etiquetas */
section[data-testid="stSidebar"] [data-testid="stMultiSelect"] span[data-tag] span {
    color: #ffffff !important;
}

/* Botón de eliminar (X) */
section[data-testid="stSidebar"] [data-testid="stMultiSelect"] span[data-tag] button {
    color: #ffffff !important;
}


/* Texto de la pestaña seleccionada */
.stTabs [data-testid="stTab"][aria-selected="true"] p {
    color: #179fb5 !important;
}

/* Indicador inferior de la pestaña seleccionada */
.stTabs [data-testid="stTab"]:hover {
    color: #179fb5 !important;
}

/* Indicador inferior de la pestaña seleccionada */
.stTabs [data-testid="stTab"][aria-selected="true"] .react-aria-SelectionIndicator {
    background-color: #179fb5 !important;
}

/* Rango comprendido entre las dos fechas */
[role="button"][data-selected="true"]:not([data-selection-start="true"]):not([data-selection-end="true"]) {
    background-color: #d9f3f8 !important;
    color: #080808 !important;
}

[role="button"][data-selected="true"][data-selection-start="true"],
[role="button"][data-selected="true"][data-selection-end="true"] {
    background: #179fb5 !important;
    background-color: #179fb5 !important;
    color: #ffffff !important;
    border-color: #179fb5 !important;
}

/* Evitar que el hover cambie el azul */
[role="button"][data-selected="true"]:hover {
    background-color: #117f91 !important;
    color: #ffffff !important;
}

div[data-testid="stDateInput"] [data-selected="true"],
div[data-testid="stDateInput"] [data-selected="true"]::before,
div[data-testid="stDateInput"] [data-selected="true"]::after {
    background: #179fb5 !important;
    background-color: #179fb5 !important;
    color: #ffffff !important;
    border-color: #179fb5 !important;
    box-shadow: none !important;
}

/* Inicio y final del rango */
div[data-testid="stDateInput"] [data-selection-start="true"],
div[data-testid="stDateInput"] [data-selection-end="true"] {
    background: #179fb5 !important;
    background-color: #179fb5 !important;
    color: #ffffff !important;
}

/* Rango intermedio */
div[data-testid="stDateInput"] [data-selected="true"]:not([data-selection-start="true"]):not([data-selection-end="true"]) {
    background: #d9f3f8 !important;
    background-color: #d9f3f8 !important;
    color: #080808 !important;
}

/* Mantener el día seleccionado siempre en azul */
div[data-testid="stDateInput"] [role="button"][aria-pressed="true"],
div[data-testid="stDateInput"] [role="button"][data-selected="true"],
div[data-testid="stDateInput"] [data-selected="true"] {
    background-color: #179fb5 !important;
    background: #179fb5 !important;
    color: #ffffff !important;
    border-color: #179fb5 !important;
}

/* Mantener el azul al pasar el ratón */
div[data-testid="stDateInput"] [role="button"][aria-pressed="true"]:hover,
div[data-testid="stDateInput"] [role="button"][data-selected="true"]:hover,
div[data-testid="stDateInput"] [data-selected="true"]:hover {
    background-color: #179fb5 !important;
    background: #179fb5 !important;
    color: #ffffff !important;
}

/* Mantener el azul cuando recibe el foco */
div[data-testid="stDateInput"] [role="button"][aria-pressed="true"]:focus,
div[data-testid="stDateInput"] [role="button"][data-selected="true"]:focus,
div[data-testid="stDateInput"] [data-selected="true"]:focus {
    background-color: #179fb5 !important;
    background: #179fb5 !important;
    color: #ffffff !important;
    outline-color: #179fb5 !important;
}

/* FORZAR COLOR AZUL EN EL CALENDARIO MERCURY */

div[data-testid="stDateInput"] button,
div[data-testid="stDateInput"] [role="button"] {
    --primary-color: #179fb5 !important;
    --background-color: #179fb5 !important;
}

/* Fecha seleccionada */
div[data-testid="stDateInput"] [aria-pressed="true"],
div[data-testid="stDateInput"] [data-selected="true"],
div[data-testid="stDateInput"] [data-selection-start="true"],
div[data-testid="stDateInput"] [data-selection-end="true"] {
    background: #179fb5 !important;
    background-color: #179fb5 !important;
    color: white !important;
    border-color: #179fb5 !important;
}

/* Todos los estados interactivos */
div[data-testid="stDateInput"] [aria-pressed="true"]:hover,
div[data-testid="stDateInput"] [aria-pressed="true"]:focus,
div[data-testid="stDateInput"] [aria-pressed="true"]:active,
div[data-testid="stDateInput"] [data-selected="true"]:hover,
div[data-testid="stDateInput"] [data-selected="true"]:focus,
div[data-testid="stDateInput"] [data-selected="true"]:active {
    background: #179fb5 !important;
    background-color: #179fb5 !important;
    color: #ffffff !important;
    border-color: #179fb5 !important;
    box-shadow: none !important;
}

/* Evitar indicadores internos rojos */
div[data-testid="stDateInput"] [data-selected="true"]::before,
div[data-testid="stDateInput"] [data-selected="true"]::after {
    background: #179fb5 !important;
    background-color: #179fb5 !important;
    border-color: #179fb5 !important;
}

/* MERCURY - SELECCIÓN DE RANGOS */

/* Fecha inicial y final del rango */
div[data-testid="stDateInput"] [data-selection-start="true"],
div[data-testid="stDateInput"] [data-selection-end="true"],
div[data-testid="stDateInput"] [data-selection-start="true"]:hover,
div[data-testid="stDateInput"] [data-selection-end="true"]:hover,
div[data-testid="stDateInput"] [data-selection-start="true"]:focus,
div[data-testid="stDateInput"] [data-selection-end="true"]:focus {
    background: #179fb5 !important;
    background-color: #179fb5 !important;
    color: #ffffff !important;
    border-color: #179fb5 !important;
    box-shadow: none !important;
}

/* Texto interno de los extremos */
div[data-testid="stDateInput"] [data-selection-start="true"] *,
div[data-testid="stDateInput"] [data-selection-end="true"] * {
    color: #ffffff !important;
}

/* Días intermedios del rango */
div[data-testid="stDateInput"] [data-selected="true"]:not([data-selection-start="true"]):not([data-selection-end="true"]) {
    background: #d9f3f8 !important;
    background-color: #d9f3f8 !important;
    color: #080808 !important;
    border-color: transparent !important;
}

/* Evitar que el hover vuelva rojo el rango */
div[data-testid="stDateInput"] [data-selected="true"]:not([data-selection-start="true"]):not([data-selection-end="true"]):hover {
    background: #d9f3f8 !important;
    background-color: #d9f3f8 !important;
    color: #080808 !important;
}

.st-emotion-cache-1l9k686[data-selection-start]:not([data-selection-end])::after {
    background-color: #179fb5 !important;
}

.st-emotion-cache-1l9k686[data-selection-end]:not([data-selection-start])::after {
    background-color: #179fb5 !important;
}

/* Al pasar el ratón */
div[data-testid="stDateInput"] [role="spinbutton"]:hover,
div[data-testid="stDateInput"] [role="spinbutton"][data-hovered="true"] {
    color: #179fb5 !important;
    background-color: transparent !important;
}

/* Al seleccionar o editar el día */
div[data-testid="stDateInput"] [role="spinbutton"]:focus,
div[data-testid="stDateInput"] [role="spinbutton"]:focus-visible,
div[data-testid="stDateInput"] [role="spinbutton"][data-focused="true"] {
    color: #179fb5 !important;
    background-color: transparent !important;
}

/* Evitar cambios de color durante la edición */
div[data-testid="stDateInput"] [role="spinbutton"]::selection {
    background-color: #d9f3f8 !important;
    color: #080808 !important;
}

/* Color normal de los números de fecha */
div[data-testid="stDateInput"] [role="spinbutton"] {
    color: rgba(47, 45, 43, 0.7) !important;
    caret-color: #179fb5 !important;
}

/* Iconos SVG de todos los menús de la barra lateral */
section[data-testid="stSidebar"] svg path:not([fill="none"]) {
    fill: rgba(47, 45, 43, 0.7) !important;
}

/* Iconos que utilizan currentColor */
section[data-testid="stSidebar"] svg {
    color: rgba(47, 45, 43, 0.7) !important;
}

/* ANIMACIÓN BOTONES MERCURY */

.stButton button {
    transition:
        transform 0.18s ease,
        box-shadow 0.18s ease,
        background-color 0.18s ease !important;
    transform: scale(1);
}

/* Al pasar el ratón */
.stButton button:hover {
    transform: scale(1.030);
}

/* Al pulsar */
.stButton button:active {
    transform: scale(0.98);
    box-shadow: 0 2px 5px rgba(23, 159, 181, 0.2);
}


/* =================================
   MERCURY · TABLETS
   ================================= */

@media screen and (max-width: 1024px) {

    .stAppViewBlockContainer,
    [data-testid="stMainBlockContainer"],
    .block-container {
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }

    section[data-testid="stSidebar"] {
        width: 17rem !important;
        min-width: 17rem !important;
    }

    [data-testid="stMetric"] {
        padding: 14px !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.3rem !important;
    }

    h1 {
        font-size: 2rem !important;
    }

    h2 {
        font-size: 1.6rem !important;
    }

}



/* =================================
   MERCURY · MÓVILES
   ================================= */

@media screen and (max-width: 600px) {

    .stAppViewBlockContainer,
    [data-testid="stMainBlockContainer"],
    .block-container {
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        padding-top: 0.5rem !important;
    }

    /* Marca */
    .mercury-brand {
        font-size: 21px !important;
    }

    .mercury-y::after {
        height: 22px !important;
    }

    .mercury-sub {
        font-size: 10px !important;
        margin-bottom: 10px !important;
    }

    /* Títulos */
    h1 {
        font-size: 1.65rem !important;
    }

    h2 {
        font-size: 1.35rem !important;
    }

    h3 {
        font-size: 1.15rem !important;
    }

    /* Métricas */
    [data-testid="stMetric"] {
        padding: 10px !important;
        border-radius: 9px !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.7rem !important;
    }

    /* Tablas */
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        max-width: 100% !important;
        overflow-x: auto !important;
    }

    /* Gráficos */
    [data-testid="stVegaLiteChart"],
    [data-testid="stArrowVegaLiteChart"],
    [data-testid="stPlotlyChart"] {
        max-width: 100% !important;
        overflow-x: auto !important;
    }

    /* Pestañas */
    .stTabs [data-testid="stTab"] {
        padding: 6px 9px !important;
        font-size: 0.75rem !important;
    }

    /* Botones */
    .stButton button,
    .stDownloadButton button {
        min-height: 42px !important;
        font-size: 0.85rem !important;
    }

    /* Texto */
    .stCaption {
        font-size: 0.75rem !important;
    }

}


/* =================================
   MERCURY · MÓVILES PEQUEÑOS
   ================================= */

@media screen and (max-width: 380px) {

    .stAppViewBlockContainer,
    [data-testid="stMainBlockContainer"],
    .block-container {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    .mercury-brand {
        font-size: 19px !important;
    }

    h1 {
        font-size: 1.4rem !important;
    }

    [data-testid="stMetric"] {
        padding: 8px !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 0.95rem !important;
    }

    .stTabs [data-testid="stTab"] {
        padding: 5px 6px !important;
        font-size: 0.68rem !important;
    }

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
if st.session_state.last_good_snapshot is None:
    try:                                  # primera carga: los filtros necesitan un snapshot desde el primer pintado
        st.session_state.last_good_snapshot = load_and_validate(INPUT_DIR)
        st.session_state.last_good_analytics = {"signature": st.session_state.last_good_snapshot["signature"]}
        st.session_state.last_valid_at = datetime.now().astimezone().isoformat()
    except Exception:
        pass                              # el fragmento mostrará el error con detalle

def reset_filters():
    st.session_state["date_range"] = (
        st.session_state["default_date_range"]
    )
    st.session_state["models_filter"] = []
    st.session_state["sizes_filter"] = []
    st.session_state["types_filter"] = []
    st.session_state["states_filter"] = []


with st.sidebar:
    st.markdown("## MERCURY")
    st.markdown("---")
    st.markdown("### Filtros transversales")

    st.button(
        "Restablecer filtros",
        on_click=reset_filters,
        **STRETCH
    )

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
        default_date_range = (min_date, max_date)

        st.session_state["default_date_range"] = default_date_range

        if "date_range" not in st.session_state:
            st.session_state["date_range"] = default_date_range

        date_range = st.date_input(
            "Periodo",
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
        "Actualizar ahora",
        key="refresh_now"
    )
    check_at = datetime.now().astimezone()
    start_time = time.perf_counter()
    try:
        snapshot = load_and_validate(INPUT_DIR)
        analytics = {"signature": snapshot["signature"]}   # los DataFrames se calculan una sola vez, con los filtros
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
        LOG_DIR.mkdir(exist_ok=True, parents=True)
        with (LOG_DIR / "refrescos.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"comprobacion": check_at.isoformat(), "origen": "ACC · REAL",
                                "estado": st.session_state.last_status, "error": str(exc)[:300],
                                "duracion_segundos": time.perf_counter() - start_time}, ensure_ascii=False) + "\n")
        if isinstance(exc, PipelineError) and exc.issues:
            st.dataframe(
                pd.DataFrame(exc.issues),
                **STRETCH,
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
    (
        datetime.fromisoformat(
            st.session_state.last_valid_at
        ).astimezone().strftime("%d/%m/%Y %H:%M:%S")
        if st.session_state.last_valid_at
        else "Sin actualización"
    )
)
    if st.session_state.last_error:
        st.error(
            f"{st.session_state.last_status.upper()}: "
            f"{st.session_state.last_error}"
        )
    if snapshot is None or analytics is None:
        st.warning(
            f"No hay un snapshot válido que mostrar. "
            f"Coloca CSV en: `{INPUT_DIR}`. "
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
            f"{k['ingresos']:,.2f} {CURRENCY}",
            delta=(None if pd.isna(k["variacion_ultimo_mes_pct"]) else f"{k['variacion_ultimo_mes_pct']:+.1f} % vs mes previo")
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
        c2 = st.columns(4)
        c2[0].metric("Pedidos de venta", f"{k['pedidos_venta']:,}")
        c2[1].metric("Pares por pedido", f"{k['pares_por_pedido']:,.2f}")
        c2[2].metric("Tasa de cancelación", f"{k['tasa_cancelacion_pct']:.1f} %")
        c2[3].metric("Peso Custom (pedidos)", "N/D" if pd.isna(k["custom_pct"]) else f"{k['custom_pct']:.1f} %")
        st.caption(
            f"Denominadores: ticket = ingresos / {k['pedidos_venta']:,} pedidos de venta; pares por pedido = pares / pedidos de venta; "
            "cancelación = cancelados / pedidos de actividad. Los filtros reducen todos los denominadores. "
            "La variación compara con el mes previo; el último mes puede estar incompleto."
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
                **STRETCH
            )
        st.markdown("**Matriz modelo × talla · pares vendidos**")
        heatmap(a["matriz_modelo_talla"])
        st.markdown("**Pareto ABC de modelos**")
        st.dataframe(
            a["modelos_abc"],
            **STRETCH,
            hide_index=True
        )
        st.markdown("**Ranking acumulado de ingresos (%)**")
        if len(a["modelos_abc"]):
            st.line_chart(a["modelos_abc"].set_index("modelo")[["acumulado_pct"]], **STRETCH)
        st.markdown("**Distribución del importe por pedido de venta (€)**")
        _pv = a["pedidos_unicos"]
        histograma(_pv.loc[_pv["es_venta"], "importe"], "Pedidos")
        if len(a["custom_estandar"]) and a["custom_estandar"]["nota"].iloc[0]:
            st.info(a["custom_estandar"]["nota"].iloc[0])
        show_df(
            "Matriz modelo × talla",
            a["matriz_modelo_talla"].reset_index(),
            "matriz_modelo_talla"
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
            **STRETCH
        )
        st.dataframe(
            rfm,
            **STRETCH,
            hide_index=True
        )
        show_df(
            "Clientes RFM",
            rfm,
            "clientes_rfm"
        )
        cohortes = a["cohortes"]
        if not cohortes.empty and cohortes.attrs.get("muestra_insuficiente"):
            st.warning("Cohortes con muestra pequeña: interpretar con cautela.")
        _r = rfm[rfm["segmento_rfm"] != "Sin compras válidas"]
        if not _r.empty:
            st.markdown("**Recencia (días) frente a gasto (€) por cliente**")
            st.scatter_chart(_r, x="recency_dias", y="monetary", color="segmento_rfm")
        st.markdown("### Segmentación KMeans (variables escaladas)")
        _km = kmeans_clientes(rfm)
        if _km["estado"] != "CALCULADO":
            st.info(_km["motivo"])
        else:
            st.caption(f"k elegido = {_km['k_elegido']} (mayor silhouette). " + _km["nota"])
            st.dataframe(_km["comparacion_k"], hide_index=True, **STRETCH)
            st.dataframe(_km["perfil"], hide_index=True, **STRETCH)
            st.dataframe(_km["cruce_rfm"], **STRETCH)
        if cohortes.empty:
            st.info(
                "Cohortes no calculables: "
                "no hay historial suficiente de ventas válidas."
            )
        else:
            st.dataframe(
                cohortes.style.format("{:.1f}%"),
                **STRETCH
            )
    with tabs[3]:
        st.subheader("Almacén")
        st.warning(
            "El stock representa una instantánea (snapshot) "
            "de la exportación. No es un histórico de movimientos."
        )
        stock = a["stock_cobertura"]
        if len(stock):
            st.caption(f"Nivel de detalle del stock: {stock['nivel_detalle'].iloc[0]}.")
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
            **STRETCH,
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
        for _, _q in a["calidad"].iterrows():
            _ico = "🟢" if _q["pct_calidad"] >= 99 and _q["inc_bloqueantes"] == 0 else ("🟡" if _q["pct_calidad"] >= 90 else "🔴")
            st.write(f"{_ico} **{_q['tabla']}** · {_q['filas_validas']:,}/{_q['filas_recibidas']:,} filas válidas ({_q['pct_calidad']:.1f} %) · "
                     f"{_q['inc_bloqueantes']} bloqueantes · {_q['inc_recuperables']} recuperables · {_q['inc_advertencias']} advertencias")
        st.dataframe(
            a["calidad"],
            **STRETCH,
            hide_index=True
        )
        st.metric(
            "Incidencias registradas",
            len(snapshot["issues"])
        )
        if not snapshot["issues"].empty:
            st.dataframe(
                snapshot["issues"],
                **STRETCH,
                hide_index=True
            )
        else:
            st.success(
                "Sin incidencias bloqueantes en el snapshot publicado."
            )
        st.markdown("**Manifiesto de origen**")
        st.dataframe(
            snapshot["manifest"],
            **STRETCH,
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
        st.markdown("**Reconciliación con las consultas SQL de ACC** (ver `consultas_acc.sql`)")
        st.dataframe(a["reconciliacion"], hide_index=True, **STRETCH)
        show_df("KPIs y definiciones", a["kpis_tabla"], "kpis")
        show_df("Resumen de calidad", a["calidad"], "resumen_calidad")
        show_df(
            "Anomalías IQR",
            a["anomalias"],
            "anomalias_iqr"
        )
        st.markdown("---")
        st.markdown("### Detección de anomalías · Isolation Forest")
        st.caption(
            "Analiza los pedidos únicos del snapshot filtrado. "
            "Este análisis es exploratorio: señala registros inusuales, "
            "pero no demuestra que sean errores ni sustituye las reglas "
            "de calidad del pipeline."
        )
        pedidos_ml = a["pedidos_unicos"].copy()
        if IsolationForest is None:
            st.warning(
                "No está instalada la biblioteca scikit-learn. "
                "Añade `scikit-learn` a requirements.txt e instálala "
                "en tu entorno virtual."
            )
        elif pedidos_ml.empty:
            st.info(
                "No hay pedidos para analizar con los filtros actuales."
            )
        else:
            columnas_numericas = pedidos_ml.select_dtypes(
                include=["number"]
            ).columns.tolist()
            columnas_caracteristicas = [
                columna
                for columna in columnas_numericas
                if not (
                    columna.lower().startswith("id")
                    or columna.lower().endswith("_id")
                    or "codigo" in columna.lower()
                    or "código" in columna.lower()
                    or "telefono" in columna.lower()
                    or "teléfono" in columna.lower()
                    or "postal" in columna.lower()
                )
            ]
            if not columnas_caracteristicas:
                st.warning(
                    "No se han encontrado columnas numéricas adecuadas "
                    "en los pedidos para ejecutar Isolation Forest."
                )
            elif len(pedidos_ml) < 10:
                st.info(
                    "Se necesitan al menos 10 pedidos para realizar "
                    "una detección exploratoria mínimamente útil."
                )
            else:
                contamination = st.slider(
                    "Proporción estimada de anomalías",
                    min_value=0.01,
                    max_value=0.25,
                    value=0.05,
                    step=0.01,
                    help=(
                        "Es una estimación de la proporción de registros "
                        "atípicos que el modelo espera encontrar. "
                        "No es una tasa de errores confirmados."
                    ),
                    key="isolation_contamination"
                )
                X = pedidos_ml[columnas_caracteristicas].copy()
                X = X.replace([float("inf"), float("-inf")], pd.NA)
                columnas_validas = [
                    columna
                    for columna in X.columns
                    if X[columna].nunique(dropna=True) > 1
                ]
                X = X[columnas_validas]
                if X.empty:
                    st.warning(
                        "Las columnas numéricas disponibles no tienen "
                        "variación suficiente para detectar anomalías."
                    )
                else:
                    X = X.apply(
                        lambda columna: columna.fillna(columna.median())
                    )
                    modelo_if = IsolationForest(
                        n_estimators=200,
                        contamination=contamination,
                        random_state=42,
                        n_jobs=-1
                    )
                    etiquetas = modelo_if.fit_predict(X)
                    resultado_if = pedidos_ml.copy()
                    resultado_if["resultado_isolation_forest"] = [
                        "Anomalía" if etiqueta == -1 else "Normal"
                        for etiqueta in etiquetas
                    ]
                    resultado_if["score_anomalia"] = (
                        -modelo_if.decision_function(X)
                    )
                    total_anomalias = int((etiquetas == -1).sum())
                    total_normales = int((etiquetas == 1).sum())
                    metrica_if_1, metrica_if_2, metrica_if_3 = st.columns(3)
                    metrica_if_1.metric(
                        "Pedidos analizados",
                        f"{len(resultado_if):,}"
                    )
                    metrica_if_2.metric(
                        "Anomalías detectadas",
                        f"{total_anomalias:,}"
                    )
                    metrica_if_3.metric(
                        "Pedidos normales",
                        f"{total_normales:,}"
                    )
                    st.markdown("**Distribución de resultados**")
                    st.bar_chart(
                        resultado_if[
                            "resultado_isolation_forest"
                        ].value_counts()
                    )
                    st.markdown("**Pedidos clasificados como anómalos**")
                    anomalos_if = (
                        resultado_if[
                            resultado_if[
                                "resultado_isolation_forest"
                            ] == "Anomalía"
                        ]
                        .sort_values(
                            "score_anomalia",
                            ascending=False
                        )
                    )
                    if anomalos_if.empty:
                        st.success(
                            "Isolation Forest no ha señalado anomalías "
                            "con la configuración actual."
                        )
                    else:
                        st.dataframe(
                            anomalos_if,
                            **STRETCH,
                            hide_index=True
                        )
                    with st.expander(
                        "Ver todos los pedidos analizados"
                    ):
                        st.dataframe(
                            resultado_if.sort_values(
                                "score_anomalia",
                                ascending=False
                            ),
                            **STRETCH,
                            hide_index=True
                        )
                    st.caption(
                        "Variables utilizadas: "
                        + ", ".join(columnas_validas)
                        + ". Un score de anomalía más alto indica "
                        "un registro más atípico según el modelo."
                    )
    with tabs[5]:
        st.subheader("Modelos predictivos")
        st.info(
            "Esta vista queda reservada para el predictor de demanda. Actualmente no hay ningún modelo predictivo "
            "incluido en el proyecto, por lo que no se muestra ninguna previsión."
        )

dashboard_refresh()