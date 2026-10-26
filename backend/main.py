import tkinter as tk
from tkinter import ttk
from pathlib import Path

def funcion(event):
    tabla = combo.get()

    if tabla == "Clientes":
        verClientes()

def verClientes():
    with open (ruta, "r", encoding="utf-8") as archivo:
        contenido = archivo.read()

    texto.insert("1.0" ,contenido)


ruta = Path(__file__).parent / "../database/csv/Clientes.csv"

window = tk.Tk()
window.title("Mercury DataBases Analyzer")
window.geometry("700x400")

box = tk.Frame(window)
box.pack(fill="x")


combo = ttk.Combobox(box, text = "Elegir Tabla", state="readonly", values=["Clientes", "Trabajadores", "Productos", "Modelos"])
combo.grid(row=0, column=0)
combo.bind("<<ComboboxSelected>>", funcion)

tk.Label(box, text = "Ver gráfico").grid(row=0, column=1)
tk.Label(box, text = "Generar informe").grid(row=0, column=2)
tk.Label(box, text = "⟳").grid(row=0, column=3)


frame_tabla = tk.Frame(window)
frame_tabla.pack(fill="both", expand=True)

texto = tk.Text(frame_tabla, wrap="none")
texto.pack(side="left", fill="both", expand=True)




texto.config(state="disabled")
window.mainloop()