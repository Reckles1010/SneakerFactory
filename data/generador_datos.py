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

MODELOS = [  # (nombre, categoría, precio, pico estacional (mes), popularidad)
    ("Breeze Urban", "Urbana", 59.99, 6, 1.6), ("Nebula Run", "Running", 84.99, 4, 1.4),
    ("Vertex Street", "Urbana", 69.99, 9, 1.2), ("Cobalt Flex", "Running", 79.99, 10, 1.5),
    ("Aero Motion", "Running", 89.99, 3, 1.3), ("Street Comfort", "Urbana", 64.99, 9, 1.1),
    ("Polar Winter", "Invierno", 99.99, 12, 0.9), ("Trail Rock", "Montaña", 109.99, 5, 0.8),
    ("Summer Light", "Verano", 49.99, 7, 1.0), ("Court Classic", "Baloncesto", 94.99, 11, 0.7),
    ("Retro One", "Urbana", 74.99, 1, 1.0), ("Pro Team", "Fútbol sala", 79.99, 2, 0.6)]
TALLAS = [str(t) for t in range(37, 47)]
P_TALLA = np.array([2, 4, 7, 11, 15, 17, 15, 11, 6, 3], dtype=float)


def generar(seed=RANDOM_SEED, n_pedidos=900, n_clientes=40, meses=18, inicio="2025-01-01", out_dir=SYNTH_DIR,
            con_incidencias=False):
    rng = np.random.default_rng(seed)
    ini = pd.Timestamp(inicio)
    periodos = pd.period_range(ini, periods=meses, freq="M")
    mo = pd.DataFrame([{"id_modelo": f"M{i+1}", "modelo": n, "categoria": c, "precio": p} for i, (n, c, p, _, _) in enumerate(MODELOS)])
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
        est = np.array([m[4] * (1 + 0.6 * np.cos(2 * np.pi * (per.month - m[3]) / 12)) for m in MODELOS])
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
                precio = round(MODELOS[i][2] * (1.15 if custom else 1.0), 2)
                lin.append({"id_linea": f"L{n_lin:05d}", "id_pedido": pid, "id_modelo": f"M{i+1}",
                            "talla": rng.choice(TALLAS, p=P_TALLA / P_TALLA.sum()),
                            "cantidad": int(rng.integers(2, 7)) if equipo else int(rng.choice([1, 1, 1, 2, 3])),
                            "precio_unitario": precio})
    pe, li = pd.DataFrame(ped), pd.DataFrame(lin)
    corte = hoy_fin.date().isoformat()
    st = pd.DataFrame([{"id_modelo": f"M{i+1}", "talla": t, "stock_disponible": int(rng.integers(0, 40)), "fecha_corte": corte}
                        for i in range(len(MODELOS)) for t in TALLAS])
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
