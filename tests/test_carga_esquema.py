"""Carga y esquema: ruta inexistente, CSV vacío, columna ausente, fecha corrupta, cabecera ausente."""
import pytest

from data.pipeline import PipelineError, load_and_validate
from conftest import escribir_acc


def test_01_ruta_inexistente(tmp_path):
    with pytest.raises(PipelineError, match="No existe la carpeta"):
        load_and_validate(tmp_path / "no_existe", escribir_salidas=False)


def test_02_csv_vacio(tmp_path):
    carpeta = escribir_acc(tmp_path / "x", pedidos="")
    with pytest.raises(PipelineError) as e:
        load_and_validate(carpeta, escribir_salidas=False)
    assert any(i["regla"] == "01_fichero_vacio" for i in e.value.issues)


def test_03_columna_ausente_bloquea_y_no_publica(tmp_path):
    carpeta = escribir_acc(tmp_path / "x", modelos="id_modelo,nombre\nM1,Uno\n")
    with pytest.raises(PipelineError) as e:
        load_and_validate(carpeta, escribir_salidas=False)
    assert any(i["regla"].startswith("01_columnas_ausentes:precio") for i in e.value.issues)


def test_04_fecha_corrupta_se_excluye_y_se_registra(tmp_path):
    ped = ("id_pedido,tipo,estado,descuento,fecha,id_linea_Linea de pedido,id_modelo_Modelo,id_trabajador_Trabajador,id_cliente_Clientes\n"
           "P1,Tienda,Entregado,f,2026-01-10,L1,M1,T1,C1\nP2,Online,Entregado,f,31/02/2026,L2,M2,T1,C2\n")
    lin = "\nL1,42,2,B,N,B,A,100\nL2,40,1,N,R,B,A,80\n"
    s = load_and_validate(escribir_acc(tmp_path / "x", pedidos=ped, lineas=lin), escribir_salidas=False)
    assert s["valid_rows"]["pedidos"] == 1 and s["valid_rows"]["lineas"] == 1
    assert "04_fecha_nula_o_imposible" in set(s["issues"]["regla"])


def test_05_cabecera_ausente_se_infiere_con_advertencia(acc):
    s = load_and_validate(acc, escribir_salidas=False)
    inc = s["issues"]
    assert (inc["regla"] == "01_cabecera_ausente_inferida").sum() == 2
    assert s["valid_rows"]["clientes"] == 3 and s["valid_rows"]["lineas"] == 4   # no se pierde la primera fila


def test_06_no_se_modifican_los_csv_de_entrada(acc):
    antes = {p.name: p.read_bytes() for p in acc.iterdir()}
    load_and_validate(acc, escribir_salidas=False)
    assert antes == {p.name: p.read_bytes() for p in acc.iterdir()}
