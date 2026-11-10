import sys
from pathlib import Path

# Añadir la raíz del proyecto a las rutas de Python
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

from data.conexion import comprobar_conexion

if comprobar_conexion():
    print("Conexión con PostgreSQL correcta")
else:
    print("Error al conectar con PostgreSQL")