import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data.config import FILES, SYNTH_FILES  # noqa: E402


def escribir_acc(carpeta: Path, **cambios):
    """Escribe un mini export ACC (Clientes y Linea_pedido SIN cabecera, como en la realidad)."""
    d = {
        "almacen": "id_almacen,direccion\nA1,Calle 1\n",
        "fabrica": "id_fabrica,direccion\nF1,Poligono 1\n",
        "many": "id_fabrica_Fabrica,id_almacen_Almacen\nF1,A1\n",
        "productos": "id_producto,tipo\nP1,Zapatillas\n",
        "sucursal": "id_sucursal,direccion,id_almacen_Almacen\nS1,Av 1,A1\n",
        "trabajador": "id_trabajador,puesto,nombre,id_sucursal_Sucursal\nT1,Vendedor,Ana,S1\n",
        "modelos": "id_modelo,nombre,precio,stock,id_producto_Productos\nM1,Zapa Uno,50,100,P1\nM2,Zapa Dos,80,5,P1\n",
        "clientes": "C1,,,Calle A,,\nC2,111,Luis,Calle B,600,l@x.es\nC3,,,Calle C,,\n",
        "pedidos": ("id_pedido,tipo,estado,descuento,fecha,id_linea_Linea de pedido,id_modelo_Modelo,id_trabajador_Trabajador,id_cliente_Clientes\n"
                    "P1,Tienda,Entregado,f,2026-01-10,L1,M1,T1,C1\n"
                    "P2,Online,Cancelado,f,2026-01-12,L2,M2,T1,C2\n"
                    "P3,Online,Pendiente,f,2026-02-01,L3,M1,T1,C2\n"
                    "P4,Tienda,Enviado,t,2026-02-03,L4,M2,T1,C1\n"),
        "lineas": "\nL1,42,2,Blanco,Negro,Blanco,Azul,100\nL2,40,1,Negro,Rojo,Blanco,Azul,80\nL3,41,1,Negro,Rojo,Blanco,Azul,50\nL4,43,3,Negro,Rojo,Blanco,Azul,240\n",
    }
    d.update(cambios)
    carpeta.mkdir(parents=True, exist_ok=True)
    for k, nombre in FILES.items():
        if d.get(k) is not None:
            (carpeta / nombre).write_text(d[k], encoding="utf-8")
    return carpeta


def escribir_contrato(carpeta: Path, **tablas):
    """Escribe el conjunto del contrato (formato sintético) con pedidos multilínea."""
    base = {
        "clientes": pd.DataFrame({"id_cliente": ["C1", "C2"]}),
        "modelos": pd.DataFrame({"id_modelo": ["M1", "M2"], "modelo": ["Uno", "Dos"], "categoria": ["Urbana", "Urbana"], "precio": [50.0, 80.0]}),
        "pedidos": pd.DataFrame({"id_pedido": ["P1", "P2", "P3"], "fecha": ["2026-01-05", "2026-01-20", "2026-02-02"],
                                 "id_cliente": ["C1", "C1", "C2"], "estado": ["Entregado", "Cancelado", "Pendiente"],
                                 "tipo": ["Custom", "Estándar", "Estándar"]}),
        "lineas": pd.DataFrame({"id_linea": ["L1", "L2", "L3", "L4", "L5"], "id_pedido": ["P1", "P1", "P1", "P2", "P3"],
                                "id_modelo": ["M1", "M1", "M2", "M2", "M1"], "talla": ["40", "41", "42", "42", "40"],
                                "cantidad": [15, 15, 10, 2, 1], "precio_unitario": [50.0, 50.0, 80.0, 80.0, 50.0]}),
        "stock": pd.DataFrame({"id_modelo": ["M1", "M2"], "talla": ["40", "42"], "stock_disponible": [20, 3], "fecha_corte": ["2026-02-10"] * 2}),
    }
    base.update(tablas)
    carpeta.mkdir(parents=True, exist_ok=True)
    for k, nombre in SYNTH_FILES.items():
        base[k].to_csv(carpeta / nombre, index=False, encoding="utf-8-sig")
    return carpeta


@pytest.fixture
def acc(tmp_path):
    return escribir_acc(tmp_path / "acc")


@pytest.fixture
def contrato(tmp_path):
    return escribir_contrato(tmp_path / "c")
