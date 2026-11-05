from pathlib import Path
import pandas as pd
from datetime import datetime
import re as r
import sys


def verArchivo(ruta):
    try:
        return pd.read_csv(ruta, dtype=str, encoding="utf-8-sig")
    except:
        return None



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

cabeceras = {
    "Almacenes": ['id_almacen', 'direccion'],
    "Clientes": ['id_cliente', 'dni', 'nombre', 'direccion', 'telefono'],
    "Fábricas": ['id_fabrica', 'direccion'],
    "Líneas": ['id_linea', 'talla', 'colorBase', 'colorPanel', 'colorSuela', 'colorCordones'],
    "Fábricas y almacenes": ['id_fabrica_Fabrica', 'id_almacen_Almacen'],
    "Modelos": ['id_modelo', 'nombre', 'precio', 'stock', 'id_producto_Productos'],
    "Pedidos": ['id_pedido', 'tipo', 'estado', 'descuento', 'fecha', 'id_linea_Linea de pedido', 'id_modelo_Modelo', 'id_trabajador_Trabajador', 'id_cliente_Clientes'],
    "Productos": ['id_producto', 'tipo'],
    "Sucursales": ['id_sucursal', 'direccion', 'id_almacen_Almacen'],
    "Trabajadores": ['id_trabajador','puesto','nombre','id_sucursal_Sucursal'],
}

claves = {
    "Almacenes": ['id_almacen'],
    "Clientes": ['id_cliente'],
    "Fábricas": ['id_fabrica'],
    "Líneas": ['id_linea'],
    "Fábricas y almacenes": ['id_fabrica_Fabrica', "id_almacen_Almacen"],
    "Modelos": ['id_modelo'],
    "Pedidos": ['id_pedido'],
    "Productos": ['id_producto'],
    "Sucursales": ['id_sucursal'],
    "Trabajadores": ['id_trabajador'],
}

relaciones = {
    "Modelos": {"id_producto_Productos": ("Productos", "id_producto")},
    "Sucursales": {"id_almacen_Almacen": ("Almacenes", "id_almacen")},
    "Trabajadores": {"id_sucursal_Sucursal": ("Sucursales", "id_sucursal")},
    "Pedidos": {
        "id_cliente_Clientes": ("Clientes", "id_cliente"),
        "id_trabajador_Trabajador": ("Trabajadores", "id_trabajador"),
        "id_modelo_Modelo": ("Modelos", "id_modelo"),
        "id_linea_Linea de pedido": ("Líneas", "id_linea")
    },
    "Fábricas y almacenes": {
        "id_fabrica_Fabrica": ("Fábricas", "id_fabrica"),
        "id_almacen_Almacen": ("Almacenes", "id_almacen")
    }
}

columnasNull = {
    "Clientes": ["dni", "nombre", "telefono"]
}



def mostrarTablas():
    errores = []
    for nombre, data in tablas.items():
        print(f"\n--- {nombre} ---")

        if data is None:
            errores.append({"tabla": nombre, "error": " no tiene contenido", "gravedad": "alta"})
            continue
        elif len(data.columns) == 0:
            errores.append({"tabla": nombre, "error": " no tiene columnas", "gravedad": "alta"})
            continue
        elif nombre in cabeceras and list(data.columns) != cabeceras[nombre]:
            errores.append({"tabla": nombre, "error": " cabecera incorrecta", "gravedad": "alta"})
            continue
        elif data.empty:
            errores.append({"tabla": nombre, "error": " sin registros", "gravedad": "media"})
            continue
        elif data.duplicated(subset=claves[nombre]).any():
            filas = data.index[
                data.duplicated(subset=claves[nombre], keep=False)
            ].tolist()

            errores.append({
                "tabla": nombre,
                "error": f" IDs duplicados en filas: {filas}",
                "gravedad": "alta"
            })

            continue
        else:
            print("Columnas:", data.columns.tolist())
            print("Número de filas:", len(data))

    return errores


def mostrarResumen(errores):
    print(f"\n--- Resumen general [{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}]---")

    if not errores: 
        print("Todas las tablas están bien")
    else:
        for error in errores:
            print(f"{error["tabla"]}:{error["error"]}")


def comprobarFK():
    errores = []

    for nombreTabla, foreignKeys in relaciones.items():
        for columnaFK, (tablaReferencia, columnaPK) in foreignKeys.items():

            
            tabla = tablas[nombreTabla]
            referencia = tablas[tablaReferencia]

            if tabla is None or referencia is None:
                continue

            if columnaFK not in tabla.columns:
                errores.append({
                                    "tabla": nombreTabla,
                                    "error": f" falta la columna propia {columnaFK}: ",
                                    "gravedad": "alta"
                                })
                continue

            if columnaPK not in referencia.columns:
                errores.append({
                                    "tabla": nombreTabla,
                                    "error": f" falta la columna ajena {columnaPK}: ",
                                    "gravedad": "alta"
                                })
                continue

            idsValidos = set(tablas[tablaReferencia][columnaPK].dropna())
            valoresFK = tablas[nombreTabla][columnaFK].dropna()
            valoresFK = valoresFK[valoresFK.str.strip() != ""]

            invalidos = valoresFK[~valoresFK.isin(idsValidos)]

            if not invalidos.empty:
                errores.append({
                    "tabla": nombreTabla,
                    "error": f" claves foráneas inválidas en {columnaFK}: "
                             f"{invalidos.tolist()}",
                    "gravedad": "alta"
                })

    return errores


def comprobarModelos():
    errores = []

    if modelos is None:
        errores.append({"tabla": "Modelos",
                        "error": f" no se puede validar el archivo",
                        "gravedad": "alta"})
        return errores

    for fila in modelos.itertuples(index=False):
        try:
            if int(fila.stock) <= 0:
                errores.append({"tabla": "Modelos",
                                "error": f" stock insuficiente en modelo {fila.id_modelo}",
                                "gravedad": "alta"})
        except (ValueError, TypeError):
            errores.append({"tabla": "Modelos",
                                "error": f" stock no numerico en modelo {fila.id_modelo}",
                                "gravedad": "alta"})
        try:
            if float(fila.precio) <= 0:
                errores.append({"tabla": "Modelos",
                                "error": f" precio inexistente en modelo {fila.id_modelo}",
                                "gravedad": "alta"})
        except (ValueError, TypeError, AttributeError):
                errores.append({"tabla": "Modelos",
                                "error": f" precio no numero en modelo {fila.id_modelo}",
                                "gravedad": "alta"})
    return errores


def comprobarPedidos():
    errores=[]
    fechaActual = datetime.now().date()

    if pedidos is None or not set(cabeceras["Pedidos"]).issubset(pedidos.columns):
        return errores


    for fila in pedidos.itertuples(index=False):

        if pd.isna(fila.fecha) or not isinstance(fila.fecha, str):
            errores.append({"tabla": "Pedidos",
                                    "error": f" fecha vacía en pedido {fila.id_pedido}",
                                    "gravedad": "alta"})
            continue

        try:
            fecha = datetime.strptime(str(fila.fecha).strip(), "%Y-%m-%d").date()
        except ValueError:
            errores.append({"tabla": "Pedidos",
                                    "error": f" fecha incorrecta en pedido {fila.id_pedido}",
                                    "gravedad": "alta"})
            continue

        if fecha > fechaActual:
            errores.append({"tabla": "Pedidos",
                                    "error": f" fecha futura en pedido {fila.id_pedido}",
                                    "gravedad": "alta"})


        if str(fila.estado).strip() not in ["Entregado", "Enviado", "Pendiente", "En preparacion"]:
            errores.append({"tabla": "Pedidos",
                                    "error": f" estado erroneo en pedido {fila.id_pedido}",
                                    "gravedad": "alta"})

        if str(fila.tipo).strip() not in ["Tienda", "Online"]:
            errores.append({"tabla": "Pedidos",
                                    "error": f" tipo erroneo en pedido {fila.id_pedido}",
                                    "gravedad": "alta"})

    
    return errores


def comprobarLineas():
    errores = []

    if lineas is None:
        errores.append({
            "tabla": "Líneas",
            "error": "No se puede validar el archivo",
            "gravedad": "alta"
        })
        return errores

    if not set(cabeceras["Líneas"]).issubset(lineas.columns):
        return errores

    for fila in lineas.itertuples(index=False):
        try:
            talla = float(fila.talla)

            if talla <= 0:
                errores.append({
                    "tabla": "Líneas",
                    "error": (
                        f"Talla no positiva en la línea "
                        f"{fila.id_linea}: {fila.talla}"
                    ),
                    "gravedad": "alta"
                })

        except (ValueError, TypeError):
            errores.append({
                "tabla": "Líneas",
                "error": (
                    f"Talla no numérica en la línea "
                    f"{fila.id_linea}: {fila.talla}"
                ),
                "gravedad": "alta"
            })

    return errores


def comprobarNulos():
    errores = []

    for nombreTabla, data in tablas.items():
        if data is None:
            continue

        if not set(cabeceras[nombreTabla]).issubset(data.columns):
            continue

        permitidas = columnasNull.get(nombreTabla, [])

        for columna in data.columns:
            if columna in permitidas:
                continue

            vacios = (data[columna].isna() | data[columna].astype(str).str.strip().eq(""))

            for indice in data.index[vacios]:
                errores.append({
                    "tabla": nombreTabla,
                    "error": (
                        f" valor obligatorio ausente en "
                        f"{columna}, fila {indice + 2}"
                    ),
                    "gravedad": "alta"
                })

    return errores


def comprobarRelaciones11():
    errores = []

    relaciones11 = {
        "Sucursales": ["id_almacen_Almacen"],
        "Pedidos": ["id_linea_Linea de pedido"]
    }

    for nombreTabla, columnas in relaciones11.items():
        data = tablas[nombreTabla]

        if data is None:
            continue

        for columna in columnas:
            if columna not in data.columns:
                continue

            valores = data[columna]
            valores = valores[valores.notna() & valores.astype(str).str.strip().ne("")]

            duplicados = valores[valores.duplicated(keep=False)]

            if not duplicados.empty:
                errores.append({
                    "tabla": nombreTabla,
                    "error": (
                        f" valores duplicados en la relación "
                        f"{columna}: "
                        f"{duplicados.unique().tolist()}"
                    ),
                    "gravedad": "alta"
                })
    return errores



errores = mostrarTablas()
errores.extend(comprobarNulos())
errores.extend(comprobarFK())
errores.extend(comprobarModelos())
errores.extend(comprobarPedidos())
errores.extend(comprobarLineas())
errores.extend(comprobarRelaciones11())

nombre = datetime.now().strftime("incidencias_%Y-%m-%d_%H-%M-%S.txt")
stdoutTrue = sys.stdout
ruta = Path(__file__).parent / "../../docs" / nombre

with open(ruta, "w", encoding="utf-8") as archivo:
    sys.stdout = archivo
    mostrarResumen(errores)
    sys.stdout = stdoutTrue
