
import os
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables del archivo .env
load_dotenv()

# Obtener credenciales
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Crear URL de conexión
DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Crear motor SQLAlchemy
engine = create_engine(DATABASE_URL)


# Comprobar conexión con PostgreSQL
def comprobar_conexion():
    try:
        with engine.connect() as conexion:
            conexion.execute(text("SELECT 1"))

        return True

    except Exception as error:
        print(f"Error de conexión: {error}")
        return False


# Obtener datos de una tabla
def obtener_datos(tabla):

    consulta = f'SELECT * FROM "{tabla}"'

    return pd.read_sql(consulta, engine)
