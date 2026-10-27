from pathlib import Path
import tkinter as tk


rutaAlmacen = Path(__file__).parent / "../../database/csv/Almacen.csv"
rutaClientes = Path(__file__).parent / "../../database/csv/Clientes.csv"
rutaFabrica = Path(__file__).parent / "../../database/csv/Fabrica.csv"
rutaLineas = Path(__file__).parent / "../../database/csv/Linea de pedido.csv"
rutaFabricaAlmacenes = Path(__file__).parent / "../../database/csv/many_Fabrica_has_many_Almacen.csv"
rutaModelos = Path(__file__).parent / "../../database/csv/Modelo.csv"
rutaPedidos = Path(__file__).parent / "../../database/csv/Pedido.csv"
rutaProductos = Path(__file__).parent / "../../database/csv/Productos.csv"
rutaSucursal = Path(__file__).parent / "../../database/csv/Sucursal.csv"
rutaTrabajadores = Path(__file__).parent / "../../database/csv/Trabajador.csv"



def verArchivo(texto, ruta):
    contenido=""
    with open (ruta, "r", encoding="utf-8") as archivo:
        contenido += archivo.read()
    escribir(texto, contenido)


def escribir(tabla, contenido):
    for fila in tabla.get_children():
        tabla.delete(fila)

    for fila in contenido:
        tabla.insert("", "end", values=fila)


