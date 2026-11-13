# 👟 MERCURY

> **Pisa fuera del Molde**

---


## 📌 Índice

- Sobre el proyecto.
- Objetivos.
- Asignaturas.
- Tecnologías utilizadas.
- Estructura del repositorio.
- Identidad de marca.
- Instalación y ejecución.
- Aplicación web MERCURY.
- Dashboard operacional.
- Equipo de desarrollo.

---


## 👟 Sobre el proyecto

Este proyecto forma parte del segundo curso del ciclo formativo de **Desarrollo de Aplicaciones Multiplataforma (DAM)**.

Consiste en desarrollar una solución tecnológica para **Mercury**, una empresa ficticia dedicada al diseño y comercialización de zapatillas y relacionados.

El proyecto combina programación, bases de datos, diseño web y herramientas de desarrollo para construir una aplicación que permita presentar los productos, vender online (incluida la personalización de zapatillas y calcetines) y gestionar la información de la empresa.


## 🎯 Objetivos

- Crear una identidad de marca propia.
- Desarrollar una aplicación funcional.
- Diseñar e implementar una base de datos.
- Crear una interfaz web atractiva y adaptable.
- Aplicar buenas prácticas de programación.
- Utilizar Git y GitHub para gestionar las versiones.
- Organizar y documentar el trabajo en equipo.


## 📚 Asignaturas

| Asignatura | Aplicación en el proyecto |
|---|---|
| Acceso a Datos | Conexión con la base de datos y operaciones CRUD. |
| Desarrollo de Interfaces | Diseño e implementación de la interfaz gráfica. |
| Python | Desarrollo de la lógica y funcionalidades de la aplicación. |
| Sistemas de Gestión Empresarial | Gestión de procesos y funcionalidades empresariales. |
| Programación de Servicios y Procesos | Ejecución y gestión de procesos y tareas. |


## 🛠️ Tecnologías utilizadas

### 💻 Lenguajes de programación

![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![SQL](https://img.shields.io/badge/SQL-4479A1?style=for-the-badge&logo=databricks&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

### 🌐 Servidor web

![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)
![Express](https://img.shields.io/badge/Express-000000?style=for-the-badge&logo=express&logoColor=white)

### 🗄️ Bases de datos

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)

### 🔧 Herramientas de desarrollo

![IntelliJ IDEA](https://img.shields.io/badge/IntelliJ_IDEA-000000?style=for-the-badge&logo=intellijidea&logoColor=white)
![Visual Studio Code](https://img.shields.io/badge/VS_Code-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![pgAdmin](https://img.shields.io/badge/pgAdmin-326690?style=for-the-badge&logo=pgadmin&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)

### 📋 Función de cada tecnología

| Tecnología | Uso en el proyecto |
|---|---|
| Java | Desarrollo de la lógica de la aplicación. |
| HTML5 | Estructura de las páginas web. |
| CSS3 | Diseño y presentación visual (con adaptación a distintos tamaños de pantalla). |
| JavaScript | Interactividad de la interfaz: catálogo, carrito, personalizador, registro e inicio de sesión. |
| Node.js + Express | Servidor de la web: sirve las páginas y expone la API REST. |
| SQL | Consultas y manipulación de datos. |
| PostgreSQL | Almacenamiento y gestión de la información. |
| Git | Control de versiones del código. |
| GitHub | Alojamiento del repositorio y colaboración. |
| IntelliJ IDEA | Desarrollo del código Java. |
| Visual Studio Code | Desarrollo de la interfaz web y del servidor. |

### 📋 Dependencias del servidor web (Node.js)

| Paquete | Uso en el proyecto |
|---|---|
| express | Servidor HTTP y definición de las rutas de la API. |
| pg | Conexión con PostgreSQL mediante un pool de conexiones. |
| bcrypt | Cifrado de las contraseñas de los clientes. |
| dotenv | Carga de la configuración desde el archivo `.env`. |

### 📋 Dependencias del dashboard (Python)

| Tecnología | Uso en el proyecto |
|---|---|
| streamlit | Desarrollo de la interfaz web y la lógica de la aplicación. |
| pandas | Consultas, análisis y manipulación de datos. |
| numpy | Soporte para operaciones numéricas y estructuras de datos eficientes. |
| matplotlib | Generación de gráficos y visualización interactiva de datos. |
| scikit-learn | Modelado y algoritmos de aprendizaje automático. |
| plotly | Generación de gráficos interactivos y visualización avanzada de datos. |
| pytest | Definición y ejecución de pruebas unitarias y de calidad del código. |
| sqlalchemy | Capa de abstracción y mapeo objeto-relacional para la base de datos. |
| psycopg2-binary | Conector de base de datos PostgreSQL para Python. |
| python-dotenv | Gestión segura de variables de entorno y configuración. |


## 📂 Estructura del repositorio

```text
📦 SneakerFactory
│
├── 📁 .venv/
│   ├── 📁 etc/
│   ├── 📁 Include/
│   ├── 📁 Lib/
│   ├── 📁 Scripts/
│   ├── 📁 share/
│   ├── 📄 .gitignore
│   └── 📄 pyvenv.cfg
│
├── 📁 database/
│   ├── 📁 csv/
│       ├── 📄 Almacen.csv
│       ├── 📄 Clientes.csv
│       ├── 📄 Fabrica.csv
│       ├── 📄 Linea_pedido.csv
│       ├── 📄 many_Fabrica_has_many_Almacen.csv
│       ├── 📄 Modelo.csv
│       ├── 📄 Pedido.csv
│       ├── 📄 Productos.csv
│       ├── 📄 Sucursal.csv
│       └── 📄 Trabajador.csv
│   ├── 📁 diagrams/
│       └── 📄 Modelo E-R.dbm
│   └── 📁 sql/
│       ├── 📄 DDL.sql
│       └── 📄 DML.sql
│
├── 📁 backend/
│   ├── 📁 controllers/
│   ├── 📁 middlewares/
│   ├── 📁 models/
│   ├── 📁 routes/
│   ├── 📁 scripts/
│   ├── 📁 services/
│   └── 📁 utils/
│
├── 📁 frontend/
│   ├── 📁 assets/
│       ├── 📄 LogoM.png
│       ├── 📄 LogotipoFondoBlanco.png
│       └── 📄 SinFondo.png
│   ├── 📁 css/
│        └── 📄 styles.css
│   ├── 📁 js/
│        └── 📄 script.js
│   ├── 📁 views/
│       ├── 📄 adminUsuarios.html
│       ├── 📄 carrito.html
│       ├── 📄 catalogo.html
│       ├── 📄 historia.html
│       ├── 📄 inicio.html
│       ├── 📄 login.html
│       └── 📄 registro.html
│   ├── 📄 server.js
│   ├── 📄 package.json
│   └── 📄 .env            (no se sube al repositorio)
│
├── 📁 data/
│   ├── 📁 __pycache__/
│   ├── 📁 datos_sinteticos/
│   ├── 📁 entrada_acc/
│   ├── 📁 logs/
│    │   └── 📄 refrescos.jsonl
│   ├── 📁 outputs/
│       ├── 📄 incidencias.csv
│       └── 📄 manifiesto_origen.csv
│   ├── 📄 __init__.py
│   ├── 📄 analiticas.py
│   ├── 📄 app_dashboard.py
│   ├── 📄 config.py
│   ├── 📄 diccionario_datos.md
│   ├── 📄 main.py
│   ├── 📄 pipeline.py
│   ├── 📄 requirements.txt
│   └── 📄 visualizaciones.py
│
├── 📁 docs/
│   ├── 📄 incidencias_2026-10-28_20-58-17.txt
│   └── 📄 incidencias_2026-10-28_21-01-19.txt
│
├── 📁 tests/
└── 📄 README.md
```


## 🎨 Identidad de marca

| Elemento | Descripción |
|---|---|
| Nombre | Mercury |
| Actividad | Diseño y comercialización de zapatillas. |
| Colores corporativos | Blanco, Negro y Turquesa. |
| Tipografía | 'Inter', -apple-system, BlinkMacSystemFont, sans-serif. |
| Eslogan | «Pisa fuera del Molde». |
| Público objetivo | Personas interesadas en el deporte, la moda y el calzado urbano. |


## 🚀 Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/Reckles1010/SneakerFactory.git
```

### 2. Acceder al proyecto

```bash
cd SneakerFactory
```

### 3. Configurar la base de datos

- Crear la base de datos `Mercury` en PostgreSQL.
- Ejecutar los scripts SQL de la carpeta `database/sql/` (`DDL.sql` y `DML.sql`).
- Comprobar que las tablas y relaciones se han creado correctamente.

### 4. Abrir el proyecto

Abrir los archivos con el entorno de desarrollo correspondiente:

- **IntelliJ IDEA:** para el backend Java.
- **Visual Studio Code:** para el frontend web, el servidor Node.js y Python.

### 5. Ejecutar la aplicación

- Web y servidor: seguir los pasos de la sección **Aplicación web MERCURY**.
- Dashboard: seguir los pasos de la sección **Dashboard operacional**.


## 🛒 Aplicación web MERCURY

Tienda online de Mercury. Un único servidor Node.js + Express sirve las páginas y la API, y se conecta a la base de datos PostgreSQL del proyecto.

### Funcionalidades

| Página | Función |
|---|---|
| Inicio | Presentación de la marca. |
| Catálogo | Productos por categoría (zapatillas, calcetines, cordones y gorras), filtros y ventana emergente con selección de talla. |
| Personalización | Personalizador de zapatillas, calcetines y conjuntos: diseño, color por zonas, talla y precio. |
| Registro e inicio de sesión | Alta de clientes con contraseña cifrada y acceso a la cuenta. |
| Carrito | Gestión de productos y formulario de compra con datos del destinatario (incluido DNI/NIE), dirección de envío y método de pago. |
| Administración de usuarios | Página de gestión de usuarios y roles. |

### Instalación del servidor

Requisitos: **Node.js 18 o superior** y PostgreSQL con la base de datos `Mercury` creada.

```bash
cd frontend
npm install express pg bcrypt dotenv
```

Crear el archivo `.env` en la misma carpeta que `server.js`:

```dotenv
# SERVIDOR NODE.JS
PORT=3001

# POSTGRESQL - MERCURY
DB_HOST=localhost
DB_PORT=5432
DB_NAME=Mercury
DB_USER=postgres
DB_PASSWORD=tu_contraseña
```

> ⚠️ El archivo `.env` contiene credenciales. No debe subirse a GitHub: añadir `.env` al `.gitignore`.

Arrancar el servidor:

```bash
node server.js
```

La web queda disponible en `http://localhost:3001`. Al arrancar, la consola indica si PostgreSQL está conectado.

### Base de datos y tablas que usa la web

La web trabaja directamente sobre las tablas del modelo de datos de Mercury:

| Operación de la web | Tabla | Qué se guarda |
|---|---|---|
| Registro e inicio de sesión | `Clientes` | Id de cliente generado, nombre completo, correo y contraseña cifrada (`password_hash`). |
| Datos de la compra | `Clientes` | DNI/NIE del cliente. |
| Pedido | `Pedido` | Id de pedido, tipo (estándar o personalizado), estado, fecha, cliente, modelo, línea de pedido, dirección de envío y notas de entrega. |
| Registro del pedido | `Linea de pedido` | Talla, cantidad, colores del diseño personalizado (base, panel, suela y cordones) y precio total de la línea. |
| Catálogo | `Modelo` | Consulta de id, nombre, precio y stock de los productos. |

Cada producto del carrito genera una línea de pedido y un pedido asociado. Todo el proceso se ejecuta en una **transacción**: si algo falla, no se guarda nada. El precio total de una compra es la suma del `PrecioTotal` de sus líneas.

Al arrancar, el servidor adapta las tablas existentes de forma automática, sin borrar datos:

- Hace opcional la dirección de `Clientes` (el registro web no la pide).
- Añade las columnas `direccion_envio` y `notas` a `Pedido`, si no existen.
- Crea un índice único sobre el correo de `Clientes`, para evitar cuentas duplicadas.

### API REST

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/auth/register` | Registra un cliente nuevo. |
| POST | `/api/auth/login` | Inicia sesión y devuelve los datos del cliente. |
| POST | `/api/pedidos` | Registra un pedido con sus líneas (requiere cliente registrado y DNI/NIE válido). |
| GET | `/api/productos` | Lista los modelos con su precio y stock. |
| GET | `/api/estado-db` | Comprueba la conexión con PostgreSQL. |

### Validaciones y seguridad

- Las contraseñas se cifran con **bcrypt** y requieren un mínimo de 8 caracteres.
- El correo se normaliza a minúsculas y no puede repetirse.
- El **DNI/NIE** se valida en el navegador y en el servidor, incluida la letra de control.
- Todas las consultas a la base de datos usan parámetros, lo que evita la inyección SQL.
- Los datos de la tarjeta se piden en el formulario, pero **no se envían ni se almacenan** en el servidor.
- Las credenciales de la base de datos se leen del archivo `.env`.
- 

## Dashboard operacional

### 1. Instalación
Recomendado: Python 3.11 o superior.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Exportaciones ACC
Copia los cinco CSV reales en `entrada_acc/`:
- `clientes.csv`
- `modelos.csv`
- `pedidos.csv`
- `lineas_pedido.csv`
- `stock.csv`

Los nombres son el contrato inicial orientativo. Ajusta `FILES` y `ALIASES` en `config.py` al diccionario de equivalencias acordado con Acceso a Datos. No inventes columnas ni cambies los CSV originales.

Formato inicial configurado: UTF-8-SIG, delimitador coma, decimal punto. Modifica `CSV_SEPARATOR`, `CSV_ENCODING` y `DECIMAL` según la exportación real de ACC.

### 3. Ejecución
```bash
python main.py --modo real
python -m streamlit run .\frontend\data\app_dashboard.py   
```

### 4. Actualización
El dashboard utiliza `st.fragment(run_every="60s")`. En cada ciclo vuelve a leer los cinco ficheros, valida, reconstruye los merges y recalcula los DataFrames. También existe el botón **Actualizar ahora**. Los filtros se conservan mediante claves de sesión.

La aplicación toma una instantánea coherente: captura los bytes de todos los CSV y verifica que tamaño y fecha de modificación no cambian durante la lectura. Si detecta una exportación en curso, aborta ese ciclo. Un cambio en PostgreSQL no llega al dashboard hasta que ACC exporta de nuevo los CSV.

### 5. Reglas que deben acordarse con ACC
Antes de la defensa, confirmar en `config.py`:
- Estados que cuentan como venta: `SALES_STATES`.
- Estados cancelados y pendientes.
- Valores de tipo Custom.
- Catálogo de tallas, si existe.
- Separador, decimal, codificación y formato de fecha.
- Moneda y criterio de reconocimiento del ingreso.

El ticket medio se calcula sobre pedidos únicos, no sobre líneas. Los pedidos cancelados/pendientes permanecen en actividad, pero no se suman a ventas válidas.

### 6. Seguridad de publicación
Si falta un CSV, falta una columna obligatoria, hay claves huérfanas, IDs duplicados, cantidades/precios inválidos o estados no acordados, el pipeline aborta. No publica cálculos parciales. Si existía una ejecución íntegra anterior, queda visible como **DESACTUALIZADO** con su hora original.

### 7. Salidas
- `outputs/manifiesto_origen.csv`
- `outputs/incidencias.csv`
- `logs/refrescos.jsonl`

El panel ofrece descargas CSV de DataFrames analíticos. Los logs no contienen credenciales.

### 8. Limitaciones de esta primera integración
Este paquete implementa el esqueleto modular, el refresco REAL, validación relacional, seis pestañas y DataFrames operativos iniciales. El contrato real de ACC debe ajustarse con una muestra de sus cinco CSV. La conciliación SQL necesita las tres cifras exportadas/consultadas por el equipo de ACC; no se deben inventar. El módulo de ML sintético y las ocho figuras PNG de memoria técnica deben incorporarse como fase separada y claramente etiquetada.


---


## 👥 Equipo de desarrollo

| Integrante |
|---|
| Carlos Corchado | 
| Berta Díaz | 
| Alberto Ordiales | 


---


 **Proyecto académico · 2.º DAM · Curso 2026–2027**
