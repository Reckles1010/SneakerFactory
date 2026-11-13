"""Configuración central: rutas relativas, catálogos de negocio y reglas.

Todo lo que pueda cambiar (estados de venta, tallas válidas, umbrales, separador CSV)
vive aquí y no en el código de cálculo.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

# Entrada REAL (exportaciones de Acceso a Datos). Se puede cambiar con la variable de entorno.
INPUT_DIR = Path(os.getenv("SNEAKER_INPUT_DIR", ROOT_DIR / "database" / "csv"))
# Histórico SINTÉTICO (nunca se mezcla con INPUT_DIR).
SYNTH_DIR = Path(os.getenv("SNEAKER_SYNTH_DIR", ROOT_DIR / "datos_sinteticos"))
OUTPUT_DIR = BASE_DIR / "outputs"
LOG_DIR = BASE_DIR / "logs"

# Ficheros reales exportados por ACC.
FILES = {
    "almacen": "Almacen.csv",
    "clientes": "Clientes.csv",
    "fabrica": "Fabrica.csv",
    "lineas": "Linea_pedido.csv",
    "many": "many_Fabrica_has_many_Almacen.csv",
    "modelos": "Modelo.csv",
    "pedidos": "Pedido.csv",
    "productos": "Productos.csv",
    "sucursal": "Sucursal.csv",
    "trabajador": "Trabajador.csv",
}

# Ficheros del conjunto sintético.
SYNTH_FILES = {
    "clientes": "clientes.csv",
    "modelos": "modelos.csv",
    "pedidos": "pedidos.csv",
    "lineas": "lineas_pedido.csv",
    "stock": "stock.csv",
}

# Columnas obligatorias tras normalizar nombres.
REQUIRED = {
    "clientes": ["id_cliente"],
    "modelos": ["id_modelo", "modelo", "precio"],
    "pedidos": ["id_pedido", "fecha", "estado", "tipo", "id_linea", "id_modelo", "id_cliente"],
    "lineas": ["id_linea", "talla", "cantidad", "precio_total"],
    "almacen": ["id_almacen"],
    "fabrica": ["id_fabrica"],
    "productos": ["id_producto"],
    "sucursal": ["id_sucursal"],
    "trabajador": ["id_trabajador"],
    "many": ["id_fabrica", "id_almacen"],
}

ALIASES = {
    "clientes": {
        "id_cliente": ["id_cliente", "cliente_id", "id"],
        "dni": ["dni", "nif"], "nombre": ["nombre", "alias"],
        "direccion": ["direccion"], "telefono": ["telefono", "movil"],
        "email": ["email", "correo", "mail"],
    },
    "modelos": {
        "id_modelo": ["id_modelo", "modelo_id", "id"],
        "id_producto": ["id_producto", "id_producto_productos"],
        "modelo": ["modelo", "nombre", "nombre_modelo"],
        "precio": ["precio", "price"],
        "stock": ["stock", "stock_disponible"],
    },
    "pedidos": {
        "id_pedido": ["id_pedido", "pedido_id", "id"],
        "fecha": ["fecha", "fecha_pedido"],
        "estado": ["estado", "status"],
        "tipo": ["tipo", "tipo_pedido"],
        "descuento": ["descuento", "discount"],
        "id_linea": ["id_linea", "id_linea_linea de pedido", "id_linea_linea_pedido"],
        "id_modelo": ["id_modelo", "id_modelo_modelo"],
        "id_trabajador": ["id_trabajador", "id_trabajador_trabajador"],
        "id_cliente": ["id_cliente", "id_cliente_clientes"],
    },
    "lineas": {
        "id_linea": ["id_linea", "linea_id"],
        "talla": ["talla", "size"],
        "cantidad": ["cantidad", "unidades", "pares"],
        "color": ["color", "colorbase", "color_base"],
        "color_panel": ["color_panel", "colorpanel"],
        "color_suela": ["color_suela", "colorsuela"],
        "color_cordones": ["color_cordones", "colorcordones"],
        "precio_total": ["precio_total", "importe"],
    },
    "almacen": {"id_almacen": ["id_almacen"], "direccion": ["direccion"]},
    "fabrica": {"id_fabrica": ["id_fabrica"], "direccion": ["direccion"]},
    "productos": {"id_producto": ["id_producto"], "tipo": ["tipo", "categoria"]},
    "sucursal": {"id_sucursal": ["id_sucursal"], "direccion": ["direccion"],
                    "id_almacen": ["id_almacen", "id_almacen_almacen"]},
    "trabajador": {"id_trabajador": ["id_trabajador"], "puesto": ["puesto"], "nombre": ["nombre"],
                    "id_sucursal": ["id_sucursal", "id_sucursal_sucursal"]},
    "many": {"id_fabrica": ["id_fabrica", "id_fabrica_fabrica"],
                "id_almacen": ["id_almacen", "id_almacen_almacen"]},
}

# Si ACC exporta SIN fila de cabecera,
# se asignan estos nombres por posición. Se registra como ADVERTENCIA en las incidencias.
FALLBACK_COLUMNS = {
    "clientes": ["id_cliente", "dni", "nombre", "direccion", "telefono", "email"],
    "lineas": ["id_linea", "talla", "cantidad", "color", "color_panel",
                "color_suela", "color_cordones", "precio_total"],
}

# --- Reglas de negocio ---
SALES_STATES = ["entregado", "enviado", "en preparación", "pendiente", "cancelado"]            # estados que reconocen ingreso
CANCEL_STATES = ["cancelado", "cancelada"]
PENDING_STATES = ["pendiente", "en preparacion", "en preparación"]
STATE_CATALOG = SALES_STATES + CANCEL_STATES + PENDING_STATES + ["confirmado"]
CUSTOM_VALUES = ["custom", "personalizado", "personalizada"]
STANDARD_VALUES = ["estandar", "estándar", "standard"]
VALID_SIZES = [str(n) for n in range(35, 49)] + ["Única"]  # calzado EU 35-48 + talla única (accesorios)
LOW_STOCK_THRESHOLD = 10
COVERAGE_WINDOW_DAYS = 28
CURRENCY = "€"

CSV_ENCODING = "utf-8-sig"
CSV_SEPARATOR = ","
DECIMAL = "."

AUTO_REFRESH_SECONDS = 60
RANDOM_SEED = 42
BOOTSTRAP_ITERATIONS = 2000
TEST_MONTHS = 3          # meses finales reservados para evaluar el predictor