import tkinter as tk
from tkinter import ttk
from pathlib import Path
from ..services.csv_reader import * 

def funcion(event, combo, texto):
    tabla = combo.get()

    match tabla:
        case "Almacen":
            verArchivo(texto, rutaAlmacen)
        case "Clientes":
            verArchivo(texto, rutaClientes)
        case "Fabricas":
            verArchivo(texto, rutaFabrica)
        case "Lineas de pedidos":
            verArchivo(texto, rutaLineas)
        case "Fabricas y Almacenes":
            verArchivo(texto, rutaFabricaAlmacenes)
        case "Modelos":
            verArchivo(texto, rutaModelos)
        case "Pedidos":
            verArchivo(texto, rutaPedidos)
        case "Productos":
            verArchivo(texto, rutaProductos)
        case "Sucursales":
            verArchivo(texto, rutaSucursal)
        case "Trabajadores":
            verArchivo(texto, rutaTrabajadores)



def crearInterfaz():
    window = tk.Tk()
    window.title("Mercury DataBases Analyzer")
    window.geometry("700x400")

    box = tk.Frame(window)
    box.pack(fill="x")


    combo = ttk.Combobox(box, state="readonly", values=[
            "Almacen",
            "Clientes", 
            "Fabricas",
            "Lineas de pedidos",
            "Fabricas y Almacenes",
            "Modelos",
            "Pedidos",
            "Productos",
            "Sucursales", 
            "Trabajadores", 
    ])

    combo.grid(row=0, column=0)
    combo.bind("<<ComboboxSelected>>", lambda event: funcion(event, combo, texto))

    tk.Label(box, text = "Ver gráfico").grid(row=0, column=1)
    tk.Label(box, text = "Generar informe").grid(row=0, column=2)
    tk.Label(box, text = "⟳").grid(row=0, column=3)


    frame_tabla = tk.Frame(window)
    frame_tabla.pack(fill="both", expand=True)

    texto = ttk.Treeview(frame_tabla, show="headings")
    texto.pack(side="left", fill="both", expand=True)


    window.mainloop()


def crearTablaClientes(window):
    columnas = ("cod-cliente", "dni", "nombre", "direccion", "ubicación", "telefono")

    tabla = ttk.Treeview(window, columns=columnas, show="headings")

    tabla.heading("cod-cliente", text="ID")
    tabla.heading("dni", text="dni")
    tabla.heading("nombre", text="nombre")
    tabla.heading("direccion", text="direccion")
    tabla.heading("ubicacion", text="ubicacion")
    tabla.heading("telefono", text="telefono")

    tabla.column("cod-cliente", width=50)
    tabla.column("dni", width=50)
    tabla.column("nombre", width=50)
    tabla.column("direccion", width=50)