from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR.parent / "database" / "csv"
OUTPUT_DIR = BASE_DIR / "outputs"
LOG_DIR = BASE_DIR / "logs"

# El contrato se normaliza a estos nombres internos y sus ficheros reales.
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

ALIASES = {
    "clientes": {
        "id_cliente": ["id_cliente", "cliente_id", "id"],
        "dni": ["dni", "nif", "identificacion"],
        "nombre": ["nombre", "alias", "nombre_cliente"],
        "direccion": ["direccion", "dir_cliente"],
        "telefono": ["telefono", "tlf_cliente", "movil"],
        "email": ["email", "correo", "mail"],
    },
    "modelos": {
        "id_modelo": ["id_modelo", "modelo_id", "id"],
        "id_producto": ["id_producto", "producto_id", "id_producto_Productos"],
        "modelo": ["modelo", "nombre", "nombre_modelo"],
        "precio": ["precio", "price"],
        "stock": ["stock", "inventario", "cantidad_disponible"],
    },
    "pedidos": {
        "id_pedido": ["id_pedido", "pedido_id", "id"],
        "fecha": ["fecha", "fecha_pedido", "created_at"],
        "estado": ["estado", "status"],
        "tipo": ["tipo", "tipo_pedido", "personalizacion"],
        "descuento": ["descuento", "rebaja", "discount"],
        "id_linea": ["id_linea", "linea_id"],
        "id_modelo": ["id_modelo", "modelo_id"],
        "id_trabajador": ["id_trabajador", "trabajador_id"],
        "id_cliente": ["id_cliente", "cliente_id"],
    },
    "lineas": {
        "id_linea": ["id_linea", "linea_id"],
        "id_pedido": ["id_pedido", "pedido_id"],
        "id_modelo": ["id_modelo", "modelo_id"],
        "talla": ["talla", "size"],
        "cantidad": ["cantidad", "unidades", "pares"],
        "precio_total": ["precio_total", "precio", "precio_par"],
        "color": ["color", "color_modelo"],
        "color_panel": ["color_panel", "panel_color"],
        "color_suela": ["color_suela", "suela_color"],
        "color_cordones": ["color_cordones", "cordones_color"],
    },
    "almacen": {
        "id_almacen": ["id_almacen", "almacen_id", "id"],
        "direccion": ["direccion", "dir_almacen"],
    },
    "fabrica": {
        "id_fabrica": ["id_fabrica", "fabrica_id", "id"],
        "direccion": ["direccion", "dir_fabrica"],
    },
    "productos": {
        "id_producto": ["id_producto", "producto_id", "id"],
        "tipo": ["tipo", "categoría", "tipo_producto"],
    },
    "sucursal": {
        "id_sucursal": ["id_sucursal", "sucursal_id", "id"],
        "direccion": ["direccion", "dir_sucursal"],
        "id_almacen": ["id_almacen", "almacen_id"],
    },
    "trabajador": {
        "id_trabajador": ["id_trabajador", "trabajador_id", "id"],
        "puesto": ["puesto", "cargo", "rol"],
        "nombre": ["nombre", "nombre_trabajador"],
        "id_sucursal": ["id_sucursal", "sucursal_id"],
    },
    "many": {
        "id_fabrica": ["id_fabrica", "fabrica_id"],
        "id_almacen": ["id_almacen", "almacen_id"],
    },
}

# Ajustar según el catálogo acordado con ACC.
SALES_STATES = [
    "entregado",
    "enviado",
]

CANCEL_STATES = [
    "cancelado",
    "cancelada",
]

PENDING_STATES = [
    "pendiente",
    "en preparacion",
    "en preparación",
]
CUSTOM_VALUES = ["custom", "personalizado", "personalizada"]
STANDARD_VALUES = ["estandar", "estándar", "standard"]
LOW_STOCK_THRESHOLD = 10
CURRENCY = "€"
CSV_ENCODING = "utf-8-sig"
CSV_SEPARATOR = ","
DECIMAL = "."

# Tallas permitidas: dejar vacío para no imponer un catálogo que ACC no haya acordado.
VALID_SIZES = []
AUTO_REFRESH_SECONDS = 60
RANDOM_SEED = 42