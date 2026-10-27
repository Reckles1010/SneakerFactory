from pathlib import Path
import pandas as pd
import csv



def verArchivo(ruta):
    data = pd.read_csv(ruta, dtype=str, encoding="utf-8-sig", header=None)
    return data



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


almacenes = verArchivo(rutaAlmacen)
clientes = verArchivo(rutaClientes)
fabricas = verArchivo(rutaFabrica)
lineas = verArchivo(rutaLineas)
almacenesFabricas = verArchivo(rutaFabricaAlmacenes)
modelos = verArchivo(rutaModelos)
pedidos = verArchivo(rutaPedidos)
productos = verArchivo(rutaProductos)
sucursales = verArchivo(rutaSucursal)
trabajadores = verArchivo(rutaTrabajadores)


print(clientes)

tablas = {
    "Almacenes": almacenes,
    "Clientes": clientes,
    "Fábricas": fabricas,
    "Líneas": lineas,
    "Fábricas y almacenes": almacenesFabricas,
    "Modelos": modelos,
    "Pedidos": pedidos,
    "Productos": productos,
    "Sucursales": sucursales,
    "Trabajadores": trabajadores,
}

for nombre, df in tablas.items():
    print(f"\n--- {nombre} ---")
    print("Columnas:", df.columns.tolist())
    print("Número de filas:", len(df))
    print(df.head(3))