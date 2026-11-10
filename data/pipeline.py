
"""Ingesta, validación y snapshot coherente de los CSV reales de ACC."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
from io import BytesIO
import json
import time

import pandas as pd

try:
    from .config import (
        FILES,
        INPUT_DIR,
        CSV_ENCODING,
        CSV_SEPARATOR,
        DECIMAL,
        LOG_DIR,
        OUTPUT_DIR,
        VALID_SIZES,
        SALES_STATES,
        CANCEL_STATES,
        PENDING_STATES,
    )
except ImportError:
    from data.config import (
        FILES,
        INPUT_DIR,
        CSV_ENCODING,
        CSV_SEPARATOR,
        DECIMAL,
        LOG_DIR,
        OUTPUT_DIR,
        VALID_SIZES,
        SALES_STATES,
        CANCEL_STATES,
        PENDING_STATES,
    )


class PipelineError(Exception):
    """Error de lectura, estructura o validación del snapshot."""

    def __init__(self, message, issues=None):
        super().__init__(message)
        self.issues = issues or []


# Columnas obligatorias según las exportaciones reales de ACC.
REQUIRED = {
    "clientes": ["id_cliente"],
    "modelos": ["id_modelo", "nombre", "precio", "stock"],
    "pedidos": [
        "id_pedido",
        "fecha",
        "id_cliente_Clientes",
        "id_modelo_Modelo",
        "id_linea_Linea de pedido",
        "estado",
        "tipo",
    ],
    "lineas": ["id_linea", "talla"],
    "productos": ["id_producto", "tipo"],
    "trabajador": ["id_trabajador"],
    "sucursal": ["id_sucursal"],
    "almacen": ["id_almacen"],
    "fabrica": ["id_fabrica"],
    "many": ["id_fabrica_Fabrica", "id_almacen_Almacen"],
}


# Normalización de encabezados reales de ACC.
ALIASES = {
    "clientes": {
        "id_cliente": ["id_cliente"],
        "dni": ["dni"],
        "nombre": ["nombre"],
        "direccion": ["direccion"],
        "telefono": ["telefono"],
    },
    "modelos": {
        "id_modelo": ["id_modelo"],
        "nombre": ["nombre", "modelo"],
        "precio": ["precio"],
        "stock": ["stock"],
        "id_producto_Productos": [
            "id_producto_Productos",
            "id_producto",
        ],
    },
    "pedidos": {
        "id_pedido": ["id_pedido"],
        "tipo": ["tipo"],
        "estado": ["estado"],
        "descuento": ["descuento"],
        "fecha": ["fecha"],
        "id_linea_Linea de pedido": [
            "id_linea_Linea de pedido",
            "id_linea",
        ],
        "id_modelo_Modelo": [
            "id_modelo_Modelo",
            "id_modelo",
        ],
        "id_trabajador_Trabajador": [
            "id_trabajador_Trabajador",
            "id_trabajador",
        ],
        "id_cliente_Clientes": [
            "id_cliente_Clientes",
            "id_cliente",
        ],
    },
    "lineas": {
        "id_linea": ["id_linea"],
        "talla": ["talla"],
        "colorBase": ["colorBase", "color_base"],
        "colorPanel": ["colorPanel", "color_panel"],
        "colorSuela": ["colorSuela", "color_suela"],
        "colorCordones": ["colorCordones", "color_cordones"],
    },
    "productos": {
        "id_producto": ["id_producto"],
        "tipo": ["tipo"],
    },
    "trabajador": {
        "id_trabajador": ["id_trabajador"],
        "puesto": ["puesto"],
        "nombre": ["nombre"],
        "id_sucursal_Sucursal": [
            "id_sucursal_Sucursal",
            "id_sucursal",
        ],
    },
    "sucursal": {
        "id_sucursal": ["id_sucursal"],
        "direccion": ["direccion"],
        "id_almacen_Almacen": [
            "id_almacen_Almacen",
            "id_almacen",
        ],
    },
    "almacen": {
        "id_almacen": ["id_almacen"],
        "direccion": ["direccion"],
    },
    "fabrica": {
        "id_fabrica": ["id_fabrica"],
        "direccion": ["direccion"],
    },
    "many": {
        "id_fabrica_Fabrica": [
            "id_fabrica_Fabrica",
            "id_fabrica",
        ],
        "id_almacen_Almacen": [
            "id_almacen_Almacen",
            "id_almacen",
        ],
    },
}


def _normalise_columns(df, table):
    """Normaliza encabezados sin perder las columnas originales."""

    rename = {}

    lower = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for canonical, alternatives in ALIASES.get(table, {}).items():
        for candidate in alternatives:
            original = lower.get(candidate.strip().lower())

            if original is not None:
                rename[original] = canonical
                break

    return df.rename(columns=rename)


def _read_snapshot(input_dir: Path):
    """Lee todos los CSV y comprueba que no cambian durante la lectura."""

    paths = {
        key: input_dir / filename
        for key, filename in FILES.items()
    }

    missing = [
        path.name
        for path in paths.values()
        if not path.is_file()
    ]

    if missing:
        raise PipelineError(
            "Faltan CSV obligatorios: " + ", ".join(missing)
        )

    for _ in range(2):

        before = {
            key: (
                path.stat().st_size,
                path.stat().st_mtime_ns,
            )
            for key, path in paths.items()
        }

        payloads = {
            key: path.read_bytes()
            for key, path in paths.items()
        }

        after = {
            key: (
                path.stat().st_size,
                path.stat().st_mtime_ns,
            )
            for key, path in paths.items()
        }

        if before == after:
            return paths, payloads, after

    raise PipelineError(
        "La exportación ha cambiado durante la lectura. "
        "Vuelve a intentarlo cuando ACC termine de exportar."
    )


def _write_issues(issues):
    """Guarda las incidencias de validación."""

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    columns = [
        "tabla",
        "registro",
        "regla",
        "gravedad",
        "tratamiento",
    ]

    pd.DataFrame(
        issues,
        columns=columns,
    ).to_csv(
        OUTPUT_DIR / "incidencias.csv",
        index=False,
        encoding="utf-8-sig",
    )

    event = {
        "at": datetime.now().astimezone().isoformat(),
        "event": "validacion",
        "issues": len(issues),
    }

    with (LOG_DIR / "refrescos.jsonl").open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(event, ensure_ascii=False) + "\n"
        )


def load_and_validate(input_dir: Path = INPUT_DIR):
    """
    Carga las diez exportaciones reales de ACC.

    Devuelve:
        tables: DataFrames originales normalizados.
        raw: DataFrames originales sin normalizar.
        lineas: pedidos enriquecidos con clientes, modelos y líneas.
        issues: incidencias.
        manifest: manifiesto de los archivos.
    """

    started = time.perf_counter()
    checked_at = datetime.now().astimezone()

    paths, payloads, signatures = _read_snapshot(
        Path(input_dir)
    )

    raw = {}
    tables = {}
    issues = []
    manifest = []

    def issue(
        table,
        record,
        rule,
        severity="BLOQUEANTE",
        treatment="Rechazo del snapshot",
    ):
        issues.append({
            "tabla": table,
            "registro": str(record),
            "regla": rule,
            "gravedad": severity,
            "tratamiento": treatment,
        })

    # ---------------------------------------------------------
    # 1. LECTURA DE CSV
    # ---------------------------------------------------------

    for table, path in paths.items():

        data = payloads[table]

        if not data.strip():
            issue(
                table,
                "",
                "01_fichero_vacio",
            )
            continue

        try:
            df = pd.read_csv(
                BytesIO(data),
                encoding=CSV_ENCODING,
                sep=CSV_SEPARATOR,
                decimal=DECIMAL,
                dtype=str,
                keep_default_na=True,
            )

        except Exception as exc:
            raise PipelineError(
                f"No se pudo leer {path.name}: {exc}",
                issues,
            )

        if df.empty or len(df.columns) == 0:
            issue(
                table,
                "",
                "01_sin_datos_o_cabeceras",
            )

        # Elimina espacios en encabezados.
        df.columns = [
            str(column).strip()
            for column in df.columns
        ]

        raw[table] = df.copy()

        df = _normalise_columns(df, table)

        # Validación de columnas obligatorias.
        for column in REQUIRED.get(table, []):

            if column not in df.columns:
                issue(
                    table,
                    "",
                    f"01_columnas_ausentes:{column}",
                )

        tables[table] = df

        manifest.append({
            "tabla": table,
            "fichero": path.name,
            "filas": len(df),
            "columnas": len(df.columns),
            "bytes": len(data),
            "mtime_ns": signatures[table][1],
        })

    # No continuar si faltan columnas obligatorias.
    blocking = [
        item
        for item in issues
        if item["gravedad"] == "BLOQUEANTE"
    ]

    if blocking:
        _write_issues(issues)

        raise PipelineError(
            "Esquema o contenido incompleto. "
            "No se publica el snapshot.",
            issues,
        )

    # ---------------------------------------------------------
    # 2. ACCESO A TABLAS
    # ---------------------------------------------------------

    c = tables["clientes"]
    m = tables["modelos"]
    p = tables["pedidos"]
    l = tables["lineas"]

    productos = tables["productos"]
    trabajadores = tables["trabajador"]
    sucursales = tables["sucursal"]
    almacenes = tables["almacen"]
    fabricas = tables["fabrica"]
    many = tables["many"]

    # ---------------------------------------------------------
    # 3. LIMPIEZA DE IDENTIFICADORES
    # ---------------------------------------------------------

    id_columns = {
        "clientes": ["id_cliente"],
        "modelos": ["id_modelo", "id_producto_Productos"],
        "pedidos": [
            "id_pedido",
            "id_cliente_Clientes",
            "id_modelo_Modelo",
            "id_linea_Linea de pedido",
            "id_trabajador_Trabajador",
        ],
        "lineas": ["id_linea"],
        "productos": ["id_producto"],
        "trabajador": [
            "id_trabajador",
            "id_sucursal_Sucursal",
        ],
        "sucursal": [
            "id_sucursal",
            "id_almacen_Almacen",
        ],
        "almacen": ["id_almacen"],
        "fabrica": ["id_fabrica"],
        "many": [
            "id_fabrica_Fabrica",
            "id_almacen_Almacen",
        ],
    }

    for table, columns in id_columns.items():

        df = tables[table]

        for column in columns:

            if column in df.columns:
                df[column] = (
                    df[column]
                    .astype("string")
                    .str.strip()
                )

                df[column] = df[column].replace(
                    "",
                    pd.NA,
                )

    # ---------------------------------------------------------
    # 4. CONVERSIÓN DE FECHAS Y NÚMEROS
    # ---------------------------------------------------------

    p["fecha"] = pd.to_datetime(
        p["fecha"],
        errors="coerce",
        dayfirst=True,
    )

    m["precio"] = pd.to_numeric(
        m["precio"],
        errors="coerce",
    )

    m["stock"] = pd.to_numeric(
        m["stock"],
        errors="coerce",
    )

    if "descuento" in p.columns:

        p["descuento"] = pd.to_numeric(
            p["descuento"],
            errors="coerce",
        )

    # ---------------------------------------------------------
    # 5. IDENTIFICADORES DUPLICADOS
    # ---------------------------------------------------------

    unique_keys = [
        ("clientes", c, "id_cliente"),
        ("modelos", m, "id_modelo"),
        ("pedidos", p, "id_pedido"),
        ("lineas", l, "id_linea"),
        ("productos", productos, "id_producto"),
        ("trabajador", trabajadores, "id_trabajador"),
        ("sucursal", sucursales, "id_sucursal"),
        ("almacen", almacenes, "id_almacen"),
        ("fabrica", fabricas, "id_fabrica"),
    ]

    for table, df, key in unique_keys:

        duplicate = (
            df[key].isna()
            | df[key].duplicated(keep=False)
        )

        for index in df.index[duplicate]:

            issue(
                table,
                index,
                f"02_id_duplicado_o_nulo:{key}",
            )

    # ---------------------------------------------------------
    # 6. VALIDACIÓN DE DATOS
    # ---------------------------------------------------------

    for index in p.index[p["fecha"].isna()]:

        issue(
            "pedidos",
            index,
            "04_fecha_nula_o_invalida",
        )

    for index in p.index[
        p["id_cliente_Clientes"].isna()
    ]:

        issue(
            "pedidos",
            index,
            "09_cliente_ausente",
        )

    for index in m.index[
        m["precio"].isna() | (m["precio"] < 0)
    ]:

        issue(
            "modelos",
            index,
            "06_precio_no_numerico_o_negativo",
        )

    for index in m.index[
        m["stock"].isna() | (m["stock"] < 0)
    ]:

        issue(
            "modelos",
            index,
            "11_stock_negativo_o_no_numerico",
        )

    # Las tallas son obligatorias.
    for index in l.index[l["talla"].isna()]:

        issue(
            "lineas",
            index,
            "08_talla_ausente",
        )

    # Solo validar catálogo si ACC ha acordado uno.
    if VALID_SIZES:

        invalid_sizes = ~l["talla"].astype(
            str
        ).isin(VALID_SIZES)

        for index in l.index[invalid_sizes]:

            issue(
                "lineas",
                index,
                "08_talla_fuera_catalogo",
                "RECUPERABLE",
                "Revisar catálogo de tallas",
            )

    # ---------------------------------------------------------
    # 7. VALIDACIÓN DE ESTADOS
    # ---------------------------------------------------------

    known_states = (
        set(SALES_STATES)
        | set(CANCEL_STATES)
        | set(PENDING_STATES)
    )

    known_states = {
        str(state).lower().strip()
        for state in (
            list(SALES_STATES)
            + list(CANCEL_STATES)
            + list(PENDING_STATES)
        )
    }

    invalid_states = ~p["estado"].astype(
        str
    ).str.lower().str.strip().isin(known_states)

    for index in p.index[invalid_states]:

        issue(
            "pedidos",
            index,
            "07_estado_fuera_catalogo",
        )

    # ---------------------------------------------------------
    # 8. VALIDACIÓN DE RELACIONES
    # ---------------------------------------------------------

    def check_foreign_key(
        source_table,
        source_df,
        source_column,
        target_table,
        target_df,
        target_column,
    ):

        source_values = set(
            source_df[source_column].dropna()
        )

        target_values = set(
            target_df[target_column].dropna()
        )

        missing = source_values - target_values

        for value in missing:

            issue(
                source_table,
                value,
                f"03_referencia_huerfana:{source_column}",
            )

    # Pedidos -> clientes.
    check_foreign_key(
        "pedidos",
        p,
        "id_cliente_Clientes",
        "clientes",
        c,
        "id_cliente",
    )

    # Pedidos -> modelos.
    check_foreign_key(
        "pedidos",
        p,
        "id_modelo_Modelo",
        "modelos",
        m,
        "id_modelo",
    )

    # Pedidos -> líneas.
    check_foreign_key(
        "pedidos",
        p,
        "id_linea_Linea de pedido",
        "lineas",
        l,
        "id_linea",
    )

    # Modelos -> productos.
    check_foreign_key(
        "modelos",
        m,
        "id_producto_Productos",
        "productos",
        productos,
        "id_producto",
    )

    # Trabajadores -> sucursales.
    check_foreign_key(
        "trabajador",
        trabajadores,
        "id_sucursal_Sucursal",
        "sucursal",
        sucursales,
        "id_sucursal",
    )

    # Sucursales -> almacenes.
    check_foreign_key(
        "sucursal",
        sucursales,
        "id_almacen_Almacen",
        "almacen",
        almacenes,
        "id_almacen",
    )

    # Fábricas y almacenes.
    check_foreign_key(
        "many",
        many,
        "id_fabrica_Fabrica",
        "fabrica",
        fabricas,
        "id_fabrica",
    )

    check_foreign_key(
        "many",
        many,
        "id_almacen_Almacen",
        "almacen",
        almacenes,
        "id_almacen",
    )

    # ---------------------------------------------------------
    # 9. RESULTADO DE LAS VALIDACIONES
    # ---------------------------------------------------------

    blocking = [
        item
        for item in issues
        if item["gravedad"] == "BLOQUEANTE"
    ]

    _write_issues(issues)

    if blocking:

        raise PipelineError(
            f"Se detectaron {len(blocking)} incidencias "
            "bloqueantes. No se publica el snapshot.",
            issues,
        )

    # ---------------------------------------------------------
    # 10. CONSTRUCCIÓN DE LA TABLA ANALÍTICA
    # ---------------------------------------------------------

    # Cada pedido referencia directamente:
    # - Un cliente.
    # - Un modelo.
    # - Una línea de pedido.

    lineas = p.merge(
        c,
        left_on="id_cliente_Clientes",
        right_on="id_cliente",
        how="left",
        validate="many_to_one",
        suffixes=("", "_cliente"),
    )

    lineas = lineas.merge(
        m,
        left_on="id_modelo_Modelo",
        right_on="id_modelo",
        how="left",
        validate="many_to_one",
        suffixes=("", "_modelo"),
    )

    lineas = lineas.merge(
        l,
        left_on="id_linea_Linea de pedido",
        right_on="id_linea",
        how="left",
        validate="many_to_one",
        suffixes=("", "_linea"),
    )

    lineas = lineas.merge(
        productos,
        left_on="id_producto_Productos",
        right_on="id_producto",
        how="left",
        validate="many_to_one",
        suffixes=("", "_producto"),
    )

    # ---------------------------------------------------------
    # 11. CAMPOS ANALÍTICOS
    # ---------------------------------------------------------

    lineas["mes"] = (
        lineas["fecha"]
        .dt.to_period("M")
        .astype("string")
    )

    lineas["estado_normalizado"] = (
        lineas["estado"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    lineas["tipo_normalizado"] = (
        lineas["tipo"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    # El precio procede del catálogo de modelos.
    # No se inventa cantidad ni precio unitario.
    lineas["precio_unitario"] = lineas["precio"]

    # Cada registro representa un pedido, no necesariamente
    # una unidad vendida.
    lineas["importe_bruto"] = lineas["precio"]

    if "descuento" in lineas.columns:

        descuento = lineas["descuento"].fillna(0)

        lineas["importe_neto"] = (
            lineas["importe_bruto"]
            * (1 - descuento / 100)
        )

    else:

        lineas["importe_neto"] = (
            lineas["importe_bruto"]
        )

    # Alias para facilitar el uso en el dashboard.
    lineas["modelo"] = lineas["nombre"]

    lineas["stock_disponible"] = lineas["stock"]

    # No se crea una cantidad ficticia.
    lineas["cantidad"] = pd.NA

    # ---------------------------------------------------------
    # 12. TABLA DE STOCK
    # ---------------------------------------------------------

    stock = m[
        [
            "id_modelo",
            "nombre",
            "stock",
            "precio",
        ]
    ].copy()

    stock = stock.rename(
        columns={
            "nombre": "modelo",
            "stock": "stock_disponible",
        }
    )

    stock["talla"] = pd.NA

    # ---------------------------------------------------------
    # 13. RESUMEN Y MANIFIESTO
    # ---------------------------------------------------------

    elapsed = time.perf_counter() - started

    result = {
        "tables": tables,
        "raw": raw,
        "lineas": lineas,
        "stock": stock,
        "issues": pd.DataFrame(
            issues,
            columns=[
                "tabla",
                "registro",
                "regla",
                "gravedad",
                "tratamiento",
            ],
        ),
        "manifest": pd.DataFrame(manifest),
        "checked_at": checked_at.isoformat(),
        "processing_seconds": elapsed,
        "signature": json.dumps(
            signatures,
            sort_keys=True,
        ),
        "valid_rows": {
            key: len(value)
            for key, value in tables.items()
        },
    }

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    result["manifest"].to_csv(
        OUTPUT_DIR / "manifiesto_origen.csv",
        index=False,
        encoding="utf-8-sig",
    )

    return result
