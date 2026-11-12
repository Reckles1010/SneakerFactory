"""Ingesta, control de esquema, validación (12 reglas) e integración relacional.

No depende de Streamlit. Dos orígenes con el MISMO motor de validación:
    - load_and_validate(): CSV reales de ACC (origen "ACC · REAL")
    - load_synthetic():    histórico simulado del generador (origen "SINTÉTICO")
Los ficheros de entrada se abren solo en lectura: nunca se sobrescriben.
"""
import hashlib
import time
from datetime import datetime
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd

from data.config import (
    ALIASES, CSV_ENCODING, CSV_SEPARATOR, CUSTOM_VALUES, FALLBACK_COLUMNS, FILES, INPUT_DIR,
    OUTPUT_DIR, REQUIRED, SALES_STATES, STATE_CATALOG, SYNTH_DIR, SYNTH_FILES, VALID_SIZES,
)

ORIGEN_REAL = "ACC · REAL"
ORIGEN_SINTETICO = "SINTÉTICO"
MAX_POR_REGLA = 50          # incidencias detalladas por (tabla, regla); el resto se resume


class PipelineError(Exception):
    """Fallo bloqueante: no se publica ningún cálculo parcial."""

    def __init__(self, message, issues=None):
        super().__init__(message)
        self.issues = issues or []


class Incidencias:
    """Registro de incidencias: tabla, registro, regla, gravedad y tratamiento."""

    def __init__(self):
        self.rows, self.count, self.rechazadas = [], {}, {}

    def add(self, tabla, registro, regla, gravedad, tratamiento, detalle=""):
        k = (tabla, regla, gravedad)
        self.count[k] = self.count.get(k, 0) + 1
        if self.count[k] <= MAX_POR_REGLA:
            self.rows.append({"tabla": tabla, "registro": registro, "regla": regla,
                            "gravedad": gravedad, "tratamiento": tratamiento, "detalle": detalle})

    def flag(self, tabla, df, mask, key, regla, gravedad, tratamiento, detalle=""):
        """Registra una incidencia por cada fila de df donde mask es True; devuelve mask."""
        mask = mask.fillna(False).astype(bool)
        for v in df.loc[mask, key].astype(str).head(MAX_POR_REGLA + 1):
            self.add(tabla, v, regla, gravedad, tratamiento, detalle)
        extra = int(mask.sum()) - min(int(mask.sum()), MAX_POR_REGLA + 1)
        if extra > 0:
            k = (tabla, regla, gravedad)
            self.count[k] += extra
        return mask

    def rechazar(self, tabla, n):
        self.rechazadas[tabla] = self.rechazadas.get(tabla, 0) + int(n)

    def bloqueante(self):
        return any(g == "BLOQUEANTE" for (_, _, g) in self.count)

    def frame(self):
        rows = list(self.rows)
        for (t, r, g), n in self.count.items():
            if n > MAX_POR_REGLA:
                rows.append({"tabla": t, "registro": "(resumen)", "regla": r, "gravedad": g,
                            "tratamiento": "Ver resumen", "detalle": f"{n} registros afectados en total"})
        cols = ["tabla", "registro", "regla", "gravedad", "tratamiento", "detalle"]
        return pd.DataFrame(rows, columns=cols)


# lectura
def _norm(txt):
    return str(txt).strip().lower()


def _renombrar(df, tabla):
    df = df.copy()
    df.columns = [_norm(c) for c in df.columns]
    ren = {}
    for canon, alts in ALIASES.get(tabla, {}).items():
        for a in alts:
            if _norm(a) in df.columns and canon not in ren.values():
                ren[_norm(a)] = canon
                break
    return df.rename(columns=ren)


def _leer_csv(payload, **kw):
    return pd.read_csv(BytesIO(payload), sep=CSV_SEPARATOR, encoding=CSV_ENCODING, dtype=str,
                       skipinitialspace=True, skip_blank_lines=True, **kw)


def _leer_tabla(payload, tabla, nombre, iss):
    if not payload.strip():
        iss.add(tabla, nombre, "01_fichero_vacio", "BLOQUEANTE", "Rechazo del snapshot")
        return None
    try:
        df = _renombrar(_leer_csv(payload), tabla)
    except Exception as exc:                       # CSV ilegible / delimitador inválido
        iss.add(tabla, nombre, "01_fichero_ilegible", "BLOQUEANTE", "Rechazo del snapshot", str(exc))
        return None
    falta = [c for c in REQUIRED.get(tabla, []) if c not in df.columns]
    fb = FALLBACK_COLUMNS.get(tabla)
    if falta and fb:
        try:                                       # exportación sin fila de cabecera
            sin_cab = _leer_csv(payload, header=None)
        except Exception:
            sin_cab = None
        if sin_cab is not None and sin_cab.shape[1] == len(fb):
            sin_cab.columns = fb
            iss.add(tabla, nombre, "01_cabecera_ausente_inferida", "ADVERTENCIA",
                    "Se asignan nombres por posición",
                    "El CSV no trae cabecera; pedir a ACC que exporte los nombres de columna")
            return _renombrar(sin_cab, tabla)
    for c in falta:
        iss.add(tabla, nombre, f"01_columnas_ausentes:{c}", "BLOQUEANTE", "Rechazo del snapshot")
    return df


def _estandarizar_ids(df):
    for c in df.columns:
        if c.startswith("id_"):
            df[c] = df[c].astype("string").str.strip()
    return df


# tipado
def _fechas(s):
    out = pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")
    resto = out.isna() & s.notna()
    if resto.any():
        try:
            out[resto] = pd.to_datetime(s[resto], dayfirst=True, errors="coerce", format="mixed")
        except Exception:
            pass
    return out


def _num(s):
    return pd.to_numeric(s.astype("string").str.replace(",", ".", regex=False), errors="coerce")


def _bool(s):
    m = {"t": True, "true": True, "1": True, "si": True, "sí": True,
        "f": False, "false": False, "0": False, "no": False}
    return s.astype("string").str.strip().str.lower().map(m).astype("boolean")


def tipar_contrato(c):
    """Conversión explícita de tipos. Un valor no convertible queda nulo y lo detectan las reglas."""
    c = {k: v.copy() for k, v in c.items()}
    p, li, st = c["pedidos"], c["lineas"], c["stock"]
    p["fecha"] = _fechas(p["fecha"].astype("string"))
    if "descuento" in p:
        p["descuento"] = _bool(p["descuento"])
    li["cantidad"] = _num(li["cantidad"])
    if "precio_unitario" in li:
        li["precio_unitario"] = _num(li["precio_unitario"])
    else:
        tot = _num(li["precio_total"])
        li["precio_unitario"] = (tot / li["cantidad"].where(li["cantidad"] > 0)).round(4)
    li["talla"] = li["talla"].astype("string").str.strip()
    c["modelos"]["precio"] = _num(c["modelos"]["precio"])
    st["stock_disponible"] = _num(st["stock_disponible"])
    st["fecha_corte"] = _fechas(st["fecha_corte"].astype("string")) if "fecha_corte" in st else pd.NaT
    st["talla"] = st["talla"].astype("string").str.strip() if "talla" in st else pd.NA
    return c


# Reglas 01-12
def validar_contrato(c, iss, hoy=None):
    """Aplica las doce comprobaciones. Devuelve las tablas válidas y el resumen de calidad."""
    hoy = pd.Timestamp(hoy or datetime.now().date())
    recibidas = {k: len(v) for k, v in c.items()}
    c = {k: v.copy() for k, v in c.items()}
    claves = {"clientes": "id_cliente", "modelos": "id_modelo", "pedidos": "id_pedido", "lineas": "id_linea"}

    for t in claves:                                                     # 01 vacío
        if c[t].empty:
            iss.add(t, t, "01_fichero_vacio", "BLOQUEANTE", "Rechazo del snapshot")

    for t, k in claves.items():                                          # 02 IDs
        df = c[t]
        iss.flag(t, df, df[k].isna(), k, "02_id_nulo", "BLOQUEANTE", "Rechazo del snapshot")
        dup = df[k].notna() & df[k].duplicated(keep=False)
        if dup.any():
            distintos = df[dup].drop_duplicates().groupby(k).size()
            conflict = df[k].isin(distintos[distintos > 1].index)
            iss.flag(t, df, dup & conflict, k, "02_id_duplicado_conflictivo", "BLOQUEANTE",
                    "Rechazo del snapshot", "Mismo ID con contenido distinto")
            exacto = dup & ~conflict & df.duplicated(keep="first")
            iss.flag(t, df, exacto, k, "02_fila_duplicada_exacta", "RECUPERABLE",
                    "Se conserva una copia", "Fila idéntica repetida")
            iss.rechazar(t, exacto.sum())
            c[t] = df[~exacto]

    cl, mo, pe, li, st = c["clientes"], c["modelos"], c["pedidos"], c["lineas"], c["stock"]

    # 09 ausencia de cliente o modelo / 03 claves huérfanas
    iss.flag("pedidos", pe, pe["id_cliente"].isna(), "id_pedido", "09_ausencia_cliente", "BLOQUEANTE", "Rechazo del snapshot")
    if "id_modelo" in pe:      # en el esquema real ACC el modelo viene en el pedido (1 pedido = 1 línea)
        iss.flag("pedidos", pe, pe["id_modelo"].isna(), "id_pedido", "09_ausencia_modelo", "BLOQUEANTE", "Rechazo del snapshot")
        iss.flag("pedidos", pe, pe["id_modelo"].notna() & ~pe["id_modelo"].isin(mo["id_modelo"]),
                "id_pedido", "03_huerfana_modelo", "BLOQUEANTE", "Rechazo del snapshot", "Modelo inexistente")
    iss.flag("lineas", li, li["id_modelo"].isna(), "id_linea", "09_ausencia_modelo", "BLOQUEANTE", "Rechazo del snapshot")
    iss.flag("pedidos", pe, pe["id_cliente"].notna() & ~pe["id_cliente"].isin(cl["id_cliente"]),
            "id_pedido", "03_huerfana_cliente", "BLOQUEANTE", "Rechazo del snapshot", "Cliente inexistente")
    iss.flag("lineas", li, ~li["id_pedido"].isin(pe["id_pedido"]),
            "id_linea", "03_huerfana_pedido", "BLOQUEANTE", "Rechazo del snapshot", "Línea sin pedido")
    iss.flag("lineas", li, li["id_modelo"].notna() & ~li["id_modelo"].isin(mo["id_modelo"]),
            "id_linea", "03_huerfana_modelo", "BLOQUEANTE", "Rechazo del snapshot", "Modelo inexistente")

    # 04 fecha nula o imposible / 12 fecha futura
    f_nula = iss.flag("pedidos", pe, pe["fecha"].isna(), "id_pedido", "04_fecha_nula_o_imposible",
                    "RECUPERABLE", "Se excluye el pedido y sus líneas")
    f_fut = iss.flag("pedidos", pe, pe["fecha"] > hoy, "id_pedido", "12_fecha_futura",
                    "RECUPERABLE", "Se excluye el pedido y sus líneas", "Fecha posterior a hoy")
    # 07 estado fuera de catálogo
    est = pe["estado"].astype("string").str.strip().str.lower()
    iss.flag("pedidos", pe, ~est.isin(STATE_CATALOG), "id_pedido", "07_estado_fuera_catalogo",
            "ADVERTENCIA", "Se conserva como actividad; no cuenta como venta")
    # 05 cantidad / 06 precio / 08 talla / 10 duplicidad de líneas
    q_mal = iss.flag("lineas", li, li["cantidad"].isna() | (li["cantidad"] <= 0), "id_linea",
                    "05_cantidad_nula_cero_o_negativa", "RECUPERABLE", "Se excluye la línea")
    p_mal = iss.flag("lineas", li, li["precio_unitario"].isna() | (li["precio_unitario"] < 0), "id_linea",
                    "06_precio_no_numerico_o_negativo", "RECUPERABLE", "Se excluye la línea")
    if VALID_SIZES:
        iss.flag("lineas", li, ~li["talla"].isin(VALID_SIZES), "id_linea", "08_talla_no_valida",
                "ADVERTENCIA", "Se conserva marcada fuera de contrato")
    clave = ["id_pedido", "id_modelo", "talla", "cantidad", "precio_unitario"]
    iss.flag("lineas", li, li.duplicated(clave, keep="first"), "id_linea", "10_linea_posible_duplicado",
            "ADVERTENCIA", "Se conserva; verificar con ACC", "Misma clave pedido-modelo-talla-cantidad-precio")
    # 12 incoherencia comercial: precio de línea frente a catálogo
    cat = li["id_modelo"].map(mo.drop_duplicates("id_modelo").set_index("id_modelo")["precio"])
    es_custom = li["id_pedido"].map(pe.drop_duplicates("id_pedido").set_index("id_pedido")["tipo"]
                                    .astype("string").str.lower()).isin(CUSTOM_VALUES)   # el Custom lleva recargo legítimo
    dif = (((li["precio_unitario"] - cat).abs() / cat.replace(0, np.nan)) > 0.01) & ~es_custom.fillna(False)
    iss.flag("lineas", li, dif, "id_linea", "12_precio_distinto_catalogo", "ADVERTENCIA",
            "Se conserva el precio de la línea", "Difiere >1 % del precio del catálogo")
    sin_linea = ~pe["id_pedido"].isin(li["id_pedido"])
    iss.flag("pedidos", pe, sin_linea, "id_pedido", "12_pedido_sin_lineas", "ADVERTENCIA",
            "Se conserva como actividad sin importe")
    # 11 stock
    neg = iss.flag("stock", st, st["stock_disponible"].isna() | (st["stock_disponible"] < 0), "id_modelo",
                "11_stock_negativo_o_nulo", "RECUPERABLE", "Se excluye la fila de stock")
    kk = ["id_modelo", "talla"]
    dup_st = st.duplicated(kk, keep="last") & st["id_modelo"].notna()
    iss.flag("stock", st, dup_st, "id_modelo", "11_stock_duplicado_modelo_talla", "ADVERTENCIA",
            "Se conserva la fila más reciente")

    # tratamiento: exclusiones
    malos_ped = pe.loc[f_nula | f_fut, "id_pedido"]
    pe_ok = pe[~(f_nula | f_fut)]
    li_mask = q_mal | p_mal | li["id_pedido"].isin(malos_ped)
    iss.rechazar("pedidos", len(pe) - len(pe_ok))
    iss.rechazar("lineas", int(li_mask.sum()))
    st_ok = st[~neg & ~dup_st]
    iss.rechazar("stock", len(st) - len(st_ok))
    out = {"clientes": cl, "modelos": mo, "pedidos": pe_ok, "lineas": li[~li_mask], "stock": st_ok}

    freq = pd.DataFrame(
        [(g, t, n) for (t, _, g), n in iss.count.items()], columns=["gravedad", "tabla", "n"])
    filas = []
    for t in out:
        rec = recibidas[t]
        val = len(out[t])
        sub = freq[freq["tabla"] == t].groupby("gravedad")["n"].sum()
        filas.append({"tabla": t, "filas_recibidas": rec, "filas_validas": val,
                    "filas_rechazadas": rec - val,
                      "pct_calidad": round(100 * val / rec, 2) if rec else 0.0,
                    "nulos_totales": int(out[t].isna().sum().sum()),
                    "inc_bloqueantes": int(sub.get("BLOQUEANTE", 0)),
                    "inc_recuperables": int(sub.get("RECUPERABLE", 0)),
                    "inc_advertencias": int(sub.get("ADVERTENCIA", 0))})
    return out, pd.DataFrame(filas)


# integración
def _merge_seguro(izq, der, on, how, validate, nombre):
    """Merge con cardinalidad declarada, sin multiplicar filas ni perder claves en silencio."""
    n = len(izq)
    m = izq.merge(der, on=on, how=how, validate=validate, indicator=True)
    if len(m) != n:
        raise PipelineError(f"El cruce {nombre} altera el número de filas ({n} → {len(m)})")
    if (m["_merge"] != "both").any():
        raise PipelineError(f"El cruce {nombre} deja {(m['_merge'] != 'both').sum()} claves sin resolver")
    return m.drop(columns="_merge")


def enriquecer(c, origen):
    """Vista a nivel de línea (df_lineas_enriquecidas) con variables derivadas."""
    pe, li, mo = c["pedidos"], c["lineas"], c["modelos"]
    cols_p = ["id_pedido", "fecha", "id_cliente", "estado", "tipo"] + [x for x in ("descuento", "id_trabajador") if x in pe]
    x = _merge_seguro(li[["id_linea", "id_pedido", "id_modelo", "talla", "cantidad", "precio_unitario"]],
                    pe[cols_p], "id_pedido", "left", "many_to_one", "líneas×pedidos")
    cols_m = ["id_modelo", "modelo", "precio"] + (["categoria"] if "categoria" in mo else [])
    x = _merge_seguro(x, mo[cols_m].rename(columns={"precio": "precio_catalogo"}), "id_modelo", "left",
                    "many_to_one", "líneas×modelos")
    x["estado"] = x["estado"].astype("string").str.strip()
    x["estado_normalizado"] = x["estado"].str.lower()
    x["tipo"] = x["tipo"].astype("string").str.strip()
    x["tipo_normalizado"] = x["tipo"].str.lower()
    x["segmento"] = np.where(x["tipo_normalizado"].isin(CUSTOM_VALUES), "Custom", "Estándar")
    x["es_venta"] = x["estado_normalizado"].isin(SALES_STATES)
    x["cantidad"] = x["cantidad"].astype("int64")                       # validado: sin nulos y > 0
    x["precio_unitario"] = x["precio_unitario"].astype("float64")
    x["precio_catalogo"] = x["precio_catalogo"].astype("float64")
    x["importe_linea"] = (x["cantidad"] * x["precio_unitario"]).round(2)
    x["anio"] = x["fecha"].dt.year
    x["mes"] = x["fecha"].dt.strftime("%Y-%m")
    x["trimestre"] = x["fecha"].dt.year.astype(str) + "-T" + x["fecha"].dt.quarter.astype(str)
    x["dia_semana"] = x["fecha"].dt.dayofweek
    x["antiguedad_dias"] = (x["fecha"].max() - x["fecha"]).dt.days
    if "descuento" in x:
        x["con_descuento"] = x["descuento"].fillna(False).astype(bool)
    x = x.sort_values(["fecha", "id_pedido", "id_linea"]).reset_index(drop=True)
    x.attrs.update({"origen": origen, "funcion": "pipeline.enriquecer", "filas_origen": len(li),
                    "fecha_corte": str(x["fecha"].max().date()) if len(x) else None, "filtros": {}})
    return x


# ACC real
def _desde_acc(raw, iss):
    """Adapta las 10 tablas de ACC al contrato (clientes, modelos, pedidos, lineas, stock)."""
    cl = raw["clientes"][["id_cliente"]].copy()                  # sin datos personales
    pr = raw["productos"]
    mo = raw["modelos"].copy()
    if "id_producto" in mo.columns:
        sin = mo["id_producto"].notna() & ~mo["id_producto"].isin(pr["id_producto"])
        iss.flag("modelos", mo, sin, "id_modelo", "03_huerfana_producto", "ADVERTENCIA", "Categoría desconocida")
        mo = mo.merge(pr.rename(columns={"tipo": "categoria"})[["id_producto", "categoria"]]
                    .drop_duplicates("id_producto"), on="id_producto", how="left")
    st = pd.DataFrame({"id_modelo": mo["id_modelo"], "talla": pd.NA,
                    "stock_disponible": mo.get("stock"), "fecha_corte": pd.NA})
    pe = raw["pedidos"].copy()
    cols = [c for c in ("id_pedido", "fecha", "id_cliente", "estado", "tipo", "descuento",
                        "id_trabajador", "id_linea", "id_modelo") if c in pe]
    pe = pe[cols]
    li = raw["lineas"].copy()
    compartida = pe["id_linea"].notna() & pe["id_linea"].duplicated(keep=False)
    iss.flag("pedidos", pe, compartida, "id_pedido", "10_linea_compartida_por_varios_pedidos",
            "BLOQUEANTE", "Rechazo del snapshot")
    uno = pe.drop_duplicates("id_linea").set_index("id_linea")
    li["id_pedido"] = li["id_linea"].map(uno["id_pedido"])
    li["id_modelo"] = li["id_linea"].map(uno["id_modelo"])
    li = li[["id_linea", "id_pedido", "id_modelo", "talla", "cantidad", "precio_total"]]
    pe = pe.drop(columns=["id_linea", "id_modelo"]).assign(id_modelo=pe["id_modelo"].values)
    # integridad de las tablas auxiliares
    for t, k, fk, ref, rk in (("many", "id_fabrica", "id_fabrica", "fabrica", "id_fabrica"),
                            ("many", "id_almacen", "id_almacen", "almacen", "id_almacen"),
                            ("sucursal", "id_sucursal", "id_almacen", "almacen", "id_almacen"),
                            ("trabajador", "id_trabajador", "id_sucursal", "sucursal", "id_sucursal")):
        df = raw[t]
        if fk in df:
            iss.flag(t, df, df[fk].notna() & ~df[fk].isin(raw[ref][rk]), k, f"03_huerfana_{fk}",
                    "ADVERTENCIA", "Se conserva; tabla auxiliar")
    return {"clientes": cl, "modelos": mo, "pedidos": pe, "lineas": li, "stock": st}


def _manifest(rutas, payloads, tablas):
    filas = []
    ahora = datetime.now().astimezone().isoformat(timespec="seconds")
    for t, p in rutas.items():
        df = tablas.get(t)
        filas.append({"tabla": t, "fichero": p.name, "fecha_analisis": ahora,
                    "filas": 0 if df is None else len(df), "columnas": 0 if df is None else df.shape[1],
                    "bytes": len(payloads[t]), "sha1": hashlib.sha1(payloads[t]).hexdigest()[:12]})
    return pd.DataFrame(filas)


def _guardar_calidad(iss_df, calidad, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    iss_df.to_csv(out_dir / "incidencias.csv", index=False, encoding="utf-8-sig")
    if calidad is not None:
        calidad.to_csv(out_dir / "resumen_calidad.csv", index=False, encoding="utf-8-sig")


def _publicar(c, iss, raw_aux, origen, rutas, payloads, tablas_manifest, t0, escribir, out_dir):
    c = tipar_contrato(c)
    c, calidad = validar_contrato(c, iss)
    st_ = c["stock"]
    c["stock"] = st_.assign(stock_disponible=st_["stock_disponible"].astype("float64").pipe(
        lambda v: v.astype("int64") if (v.dropna() % 1 == 0).all() and not v.isna().any() else v))
    iss_df = iss.frame()
    if iss.bloqueante():
        if escribir:
            _guardar_calidad(iss_df, calidad, out_dir)
        bl = iss_df[iss_df["gravedad"] == "BLOQUEANTE"]
        raise PipelineError("Esquema o contenido incompleto. No se publica el snapshot. "
                            f"Reglas bloqueantes: {', '.join(sorted(bl['regla'].unique())[:6])}",
                            iss_df.to_dict("records"))
    lineas = enriquecer(c, origen)
    if escribir:
        _guardar_calidad(iss_df, calidad, out_dir)
    firma = hashlib.sha1("".join(hashlib.sha1(p).hexdigest() for p in payloads.values()).encode()).hexdigest()
    tablas = {**raw_aux, **c}
    return {"origin": origen, "tables": tablas, "lineas": lineas, "issues": iss_df, "quality": calidad,
            "manifest": _manifest(rutas, payloads, tablas_manifest),
            "valid_rows": {k: len(v) for k, v in c.items()}, "signature": firma,
            "checked_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "processing_seconds": time.perf_counter() - t0,
            "fecha_corte": lineas["fecha"].max() if len(lineas) else pd.NaT}


def _leer_referencia_sql(input_dir):
    """Opcional: reconciliacion_acc.csv (metrica,valor_sql) con los resultados de las consultas SQL de ACC."""
    ruta = Path(input_dir) / "reconciliacion_acc.csv"
    try:
        ref = pd.read_csv(ruta) if ruta.exists() else None
        return ref if ref is not None and {"metrica", "valor_sql"} <= set(ref.columns) else None
    except Exception:
        return None


def load_and_validate(input_dir=INPUT_DIR, escribir_salidas=True, out_dir=OUTPUT_DIR):
    """Carga los CSV reales de ACC, valida y devuelve un snapshot coherente."""
    t0 = time.perf_counter()
    input_dir = Path(input_dir)
    iss = Incidencias()
    if not input_dir.is_dir():
        raise PipelineError(f"No existe la carpeta de entrada: {input_dir}")
    rutas, payloads, raw = {}, {}, {}
    for t, nombre in FILES.items():
        ruta = input_dir / nombre
        if not ruta.exists():
            iss.add(t, nombre, "01_fichero_ausente", "BLOQUEANTE", "Rechazo del snapshot")
            continue
        rutas[t], payloads[t] = ruta, ruta.read_bytes()
    if iss.bloqueante():
        raise PipelineError("Faltan ficheros de la exportación: "
                            + ", ".join(FILES[r["tabla"]] for r in iss.rows), iss.frame().to_dict("records"))
    for t in rutas:
        df = _leer_tabla(payloads[t], t, rutas[t].name, iss)
        if df is not None:
            raw[t] = _estandarizar_ids(df)
    if iss.bloqueante():
        df = iss.frame()
        raise PipelineError("Esquema o contenido incompleto. No se publica el snapshot.", df.to_dict("records"))
    contrato = _desde_acc(raw, iss)
    aux = {t: raw[t] for t in ("productos", "almacen", "fabrica", "sucursal", "trabajador", "many")}
    snap = _publicar(contrato, iss, aux, ORIGEN_REAL, rutas, payloads, raw, t0, escribir_salidas, out_dir)
    snap["referencia_sql"] = _leer_referencia_sql(input_dir)
    return snap


def load_synthetic(input_dir=SYNTH_DIR, escribir_salidas=False, out_dir=None):
    """Carga el histórico sintético (formato del contrato) con las mismas reglas de validación."""
    t0 = time.perf_counter()
    input_dir = Path(input_dir)
    iss = Incidencias()
    rutas, payloads, raw = {}, {}, {}
    for t, nombre in SYNTH_FILES.items():
        ruta = input_dir / nombre
        if not ruta.exists():
            iss.add(t, nombre, "01_fichero_ausente", "BLOQUEANTE", "Rechazo del snapshot")
            continue
        rutas[t], payloads[t] = ruta, ruta.read_bytes()
    if iss.bloqueante():
        raise PipelineError("Faltan ficheros del conjunto sintético", iss.frame().to_dict("records"))
    for t in rutas:
        df = _leer_csv(payloads[t]) if payloads[t].strip() else pd.DataFrame()
        df.columns = [_norm(x) for x in df.columns]
        raw[t] = _estandarizar_ids(df)
    return _publicar(raw, iss, {}, ORIGEN_SINTETICO, rutas, payloads, raw, t0, escribir_salidas,
                    out_dir or OUTPUT_DIR / "sintetico")

