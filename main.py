"""Ejecución por consola: modo real/sintético, directorios y acciones (misma lógica que el dashboard)."""
import argparse
import sys
from pathlib import Path

import pandas as pd

from data.analiticas import build_analytics
from data.config import INPUT_DIR, OUTPUT_DIR, RANDOM_SEED, SYNTH_DIR
from data.generador_datos import generar
from data.informes import generar_todo
from data.pipeline import PipelineError, load_and_validate, load_synthetic
from data.segmentacion import kmeans_clientes

ACCIONES = ["calidad", "descriptivo", "segmentacion", "informe", "todo", "generar"]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Sneaker Factory · análisis reproducible")
    ap.add_argument("--modo", choices=["real", "sintetico"], default="real")
    ap.add_argument("--accion", choices=ACCIONES, default="todo")
    ap.add_argument("--entrada", default=None, help="Carpeta de entrada (por defecto: la de config.py según el modo)")
    ap.add_argument("--salida", default=None, help="Carpeta de salida (por defecto outputs/<modo>)")
    ap.add_argument("--semilla", type=int, default=RANDOM_SEED)
    a = ap.parse_args(argv)
    real = a.modo == "real"
    entrada = Path(a.entrada) if a.entrada else (INPUT_DIR if real else SYNTH_DIR)
    salida = Path(a.salida) if a.salida else OUTPUT_DIR / a.modo
    print(f"ORIGEN: {'ACC · REAL' if real else 'SINTÉTICO (simulado, no son ventas reales)'} · entrada={entrada} · salida={salida}")
    if a.accion == "generar" or (not real and not (entrada / "pedidos.csv").exists()):
        generar(a.semilla, out_dir=entrada)
        print(f"Histórico sintético generado en {entrada} (semilla {a.semilla})")
        if a.accion == "generar":
            return 0
    try:
        snap = load_and_validate(entrada, out_dir=salida) if real else load_synthetic(entrada, escribir_salidas=True, out_dir=salida)
    except PipelineError as exc:
        print(f"DATOS INVÁLIDOS: {exc}")
        for r in exc.issues[:15]:
            print("  -", r["tabla"], r["registro"], r["regla"], r["gravedad"])
        return 2
    ac = a.accion
    if ac in ("calidad", "todo"):
        print("\n== Calidad por tabla =="); print(snap["quality"].to_string(index=False))
        print(f"Incidencias: {len(snap['issues'])} (ver {salida / 'incidencias.csv'})")
    an = build_analytics(snap)
    if ac in ("descriptivo", "todo"):
        print("\n== KPIs =="); print(an["kpis_tabla"][["kpi", "valor"]].to_string(index=False))
    if ac in ("segmentacion", "todo"):
        km = kmeans_clientes(an["rfm"])
        print("\n== Segmentación ==", km["estado"], km.get("motivo", ""))
        if km["estado"] == "CALCULADO":
            print(km["comparacion_k"].round(3).to_string(index=False)); print(km["perfil"].round(1).to_string(index=False))
    if ac in ("informe", "todo"):
        r = generar_todo(snap, out_dir=salida)
        print(f"\nInformes generados en {r['carpeta']}: {r['csv']} CSV, {r['figuras']} figuras PNG, informe_tecnico.md, informe_ejecutivo.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
