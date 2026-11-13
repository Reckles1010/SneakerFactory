"""Generador de histórico SINTÉTICO (separado de los datos reales de ACC).

Hipótesis de simulación (no reflejan demanda real):
  * 18 meses consecutivos, crecimiento suave (+1,5 % mensual) con estacionalidad por modelo.
  * Los clientes siguen una distribución Pareto (pocos compran mucho).
  * Un 20 % de los pedidos son Custom (recargo del 15 %), a veces pedidos de equipo con muchas líneas.
  * Estados: los pedidos antiguos están entregados o cancelados; solo los recientes pueden estar pendientes.
Semilla fija: misma semilla -> mismos ficheros.
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from data.config import RANDOM_SEED, SYNTH_DIR, SYNTH_FILES

# Catálogo idéntico al de la base de datos (Modelo.csv): mismos id_modelo, nombres y precios.
# (id_modelo, nombre, categoría = tipo de Productos.csv, precio, pico estacional (mes), popularidad)
# Pico estacional y popularidad son hipótesis de simulación (no existen en la BD).
MODELOS = [
    ("M1", "Zapatillas Breeze Urban", "Zapatillas", 59.99, 6, 1.6),
    ("M2", "Zapatillas Nebula Run", "Zapatillas", 84.99, 4, 1.4),
    ("M3", "Zapatillas Vertex Street", "Zapatillas", 69.50, 9, 1.2),
    ("M4", "Zapatillas Cobalt Flex", "Zapatillas", 74.99, 10, 1.5),
    ("M5", "Calcetines Cloud Smooth", "Calcetines", 3.99, 10, 1.3),
    ("M6", "Calcetines Route Sport", "Calcetines", 4.50, 4, 1.2),
    ("M7", "Calcetines Grid Color", "Calcetines", 2.99, 6, 1.0),
    ("M8", "Cordones Boreal Warm", "Cordones", 9.99, 12, 0.7),
    ("M9", "Cordones Active Pulse", "Cordones", 14.50, 4, 0.8),
    ("M10", "Cordones Mount Soft", "Cordones", 19.99, 5, 0.6),
    ("M11", "Gorra Horizon Classic", "Gorras", 16.99, 7, 0.9),
    ("M12", "Gorra Prisma Street", "Gorras", 21.50, 7, 0.8),
    ("M13", "Zapatillas Aero Motion", "Zapatillas", 64.99, 3, 1.3),
    ("M14", "Zapatillas Urban Force", "Zapatillas", 72.50, 9, 1.1),
    ("M15", "Zapatillas Speed Runner", "Zapatillas", 89.99, 4, 1.2),
    ("M16", "Zapatillas Street Comfort", "Zapatillas", 54.99, 9, 1.1),
    ("M17", "Calcetines Comfort Plus", "Calcetines", 5.99, 11, 1.1),
    ("M18", "Calcetines Running Pro", "Calcetines", 6.50, 4, 1.0),
    ("M19", "Calcetines Cotton Basic", "Calcetines", 3.50, 9, 1.4),
    ("M20", "Calcetines Sport Fresh", "Calcetines", 4.99, 7, 1.0),
    ("M21", "Cordones Winter Shield", "Cordones", 12.99, 12, 0.6),
    ("M22", "Cordones Sport Grip", "Cordones", 16.50, 3, 0.7),
    ("M23", "Cordones Thermal Comfort", "Cordones", 18.99, 1, 0.5),
    ("M24", "Cordones Outdoor Flex", "Cordones", 21.99, 5, 0.5),
    ("M25", "Gorra Urban Style", "Gorras", 18.99, 6, 1.0),
    ("M26", "Gorra Sport Vision", "Gorras", 22.50, 7, 0.9),
    ("M27", "Gorra Classic Cotton", "Gorras", 14.99, 8, 0.8),
    ("M28", "Gorra Active Street", "Gorras", 19.50, 7, 0.8),
]
IDX_ZAPATILLAS = [i for i, m in enumerate(MODELOS) if m[2] == "Zapatillas"]
TALLAS = [str(t) for t in range(37, 47)]          # solo calzado
TALLA_UNICA = "Única"                              # calcetines, cordones y gorras
P_TALLA = np.array([2, 4, 7, 11, 15, 17, 15, 11, 6, 3], dtype=float)


def _tallas(i):
    """Tallas disponibles del modelo i: numeración para zapatillas, 'Única' para accesorios."""
    return TALLAS if MODELOS[i][2] == "Zapatillas" else [TALLA_UNICA]


def generar(seed=RANDOM_SEED, n_pedidos=900, n_clientes=40, meses=18, inicio="2025-01-01", out_dir=SYNTH_DIR,
            con_incidencias=False):
    rng = np.random.default_rng(seed)
    ini = pd.Timestamp(inicio)
    periodos = pd.period_range(ini, periods=meses, freq="M")
    mo = pd.DataFrame([{"id_modelo": idm, "modelo": n, "categoria": c, "precio": p} for idm, n, c, p, _, _ in MODELOS])
    cl = pd.DataFrame({"id_cliente": [f"C{i+1}" for i in range(n_clientes)]})
    peso_cli = rng.pareto(1.6, n_clientes) + 1
    peso_cli /= peso_cli.sum()
    # pedidos por mes: tendencia creciente
    w_mes = np.array([1.015 ** i for i in range(meses)])
    por_mes = rng.multinomial(n_pedidos, w_mes / w_mes.sum())
    ped, lin = [], []
    n_lin = 0
    hoy_fin = periodos[-1].end_time
    for per, n in zip(periodos, por_mes):
        # demanda del modelo en el mes: popularidad × estacionalidad (pico ±)
        est = np.array([m[5] * (1 + 0.6 * np.cos(2 * np.pi * (per.month - m[4]) / 12)) for m in MODELOS])
        est /= est.sum()
        for _ in range(n):
            pid = f"P{len(ped)+1:04d}"
            dia = int(rng.integers(0, per.days_in_month))
            fecha = per.start_time + pd.Timedelta(days=dia)
            custom = rng.random() < 0.20
            antig = (hoy_fin - fecha).days
            if antig > 60:
                estado = rng.choice(["Entregado", "Cancelado"], p=[0.93, 0.07])
            elif antig > 15:
                estado = rng.choice(["Entregado", "Enviado", "Cancelado"], p=[0.7, 0.22, 0.08])
            else:
                estado = rng.choice(["Pendiente", "En preparacion", "Enviado", "Cancelado"], p=[0.4, 0.3, 0.22, 0.08])
            ped.append({"id_pedido": pid, "fecha": fecha.date().isoformat(), "id_cliente": cl["id_cliente"][rng.choice(n_clientes, p=peso_cli)],
                        "estado": estado, "tipo": "Custom" if custom else "Estándar"})
            equipo = custom and rng.random() < 0.15
            k = int(rng.integers(6, 11)) if equipo else int(rng.choice([1, 2, 3, 4], p=[.25, .40, .25, .10]))
            for _ in range(k):
                i = int(rng.choice(len(MODELOS), p=est))
                n_lin += 1
                precio = round(MODELOS[i][3] * (1.15 if custom else 1.0), 2)
                lin.append({"id_linea": f"L{n_lin:05d}", "id_pedido": pid, "id_modelo": MODELOS[i][0],
                            "talla": rng.choice(TALLAS, p=P_TALLA / P_TALLA.sum()) if i in IDX_ZAPATILLAS else TALLA_UNICA,
                            "cantidad": int(rng.integers(2, 7)) if equipo else int(rng.choice([1, 1, 1, 2, 3])),
                            "precio_unitario": precio})
    pe, li = pd.DataFrame(ped), pd.DataFrame(lin)
    corte = hoy_fin.date().isoformat()
    st = pd.DataFrame([{"id_modelo": MODELOS[i][0], "talla": t, "stock_disponible": int(rng.integers(0, 40)), "fecha_corte": corte}
                        for i in range(len(MODELOS)) for t in _tallas(i)])
    tablas = {"clientes": cl, "modelos": mo, "pedidos": pe, "lineas": li, "stock": st}
    if con_incidencias:
        tablas = _inyectar_incidencias(tablas)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for k, df in tablas.items():
        df.to_csv(out_dir / SYNTH_FILES[k], index=False, encoding="utf-8-sig")
    meta = {"origen": "SINTÉTICO", "semilla": seed, "generado_en": datetime.now().astimezone().isoformat(timespec="seconds"),
            "pedidos": len(pe), "lineas": len(li), "clientes": n_clientes, "modelos": len(mo), "meses": meses,
            "con_incidencias_deliberadas": con_incidencias,
            "aviso": "Datos simulados: NO son ventas reales ni evidencia de demanda real de clientes."}
    (out_dir / "metadatos_sinteticos.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return tablas


def _inyectar_incidencias(t):
    """Copia con fallos deliberados para probar las reglas de validación."""
    t = {k: v.copy() for k, v in t.items()}
    pe, li, st = t["pedidos"], t["lineas"], t["stock"]
    li["precio_unitario"] = li["precio_unitario"].astype(object)
    pe.loc[0, "id_cliente"] = "C999"                                 
    pe.loc[1, "fecha"] = "31/02/2025"                                 # fecha imposible
    t["pedidos"] = pd.concat([pe, pe.iloc[[2]]], ignore_index=True)   # duplicado exacto
    li.loc[0, "cantidad"] = -3                                        # cantidad negativa
    li.loc[1, "precio_unitario"] = "abc"                              # precio no numérico
    li.loc[2, "talla"] = "99"                                         # talla inválida
    t["pedidos"].loc[3, "estado"] = "Devuelto"                        # estado fuera de catálogo
    st.loc[0, "stock_disponible"] = -5                                # stock negativo
    return t


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Generador de histórico sintético")
    ap.add_argument("--semilla", type=int, default=RANDOM_SEED)
    ap.add_argument("--salida", default=str(SYNTH_DIR))
    ap.add_argument("--con-incidencias", action="store_true")
    a = ap.parse_args()
    t = generar(a.semilla, out_dir=a.salida, con_incidencias=a.con_incidencias)
    print(f"Sintético generado en {a.salida}: {len(t['pedidos'])} pedidos, {len(t['lineas'])} líneas")