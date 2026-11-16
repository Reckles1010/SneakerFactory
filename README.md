# MERCURY

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
📁 PSP_PI/
├── 🐍 .venv/                          # Entorno virtual de Python
├── ⚙️ backend/
│   └── 📁 services/
│       └── 📁 PSP_PI/
│           ├── 📂 datos/
│           └── 📂 src/
├── 📊 data/                           # Pipeline analítico en Python
│   ├── 📋 logs/                       # Registros de ejecución
│   ├── 📈 outputs/                    # Resultados generados (figuras, informes)
│   ├── 🐍 __init__.py
│   ├── 🐍 analiticas.py               # Cálculo de métricas e indicadores
│   ├── 🐍 config.py                   # Configuración general
│   ├── 🐍 figuras.py                  # Generación de gráficos
│   ├── 🐍 generador_datos.py          # Generador de datos sintéticos
│   ├── 🐍 informes.py                 # Generación de informes
│   ├── 🐍 pipeline.py                 # Orquestación del flujo de datos
│   ├── 🐍 segmentacion.py             # Segmentación de clientes
│   └── 🐍 visualizaciones.py          # Visualizaciones del dashboard
├── 🗄️ database/
│   ├── 📑 csv/                        # Datos en CSV
│   ├── 🧩 diagrams/                   # Diagramas de la base de datos
│   └── 🛢️ sql/                        # Scripts SQL
├── 🧬 datos_sinteticos/               # Dataset sintético base
│   ├── 📊 clientes.csv
│   ├── 📊 lineas_pedido.csv
│   ├── 🧾 metadatos_sinteticos.json
│   ├── 📊 modelos.csv
│   ├── 📊 pedidos.csv
│   └── 📊 stock.csv
├── 🧬 datos_sinteticos_con_incidencias/   # Dataset sintético con errores inyectados
│   ├── 📊 clientes.csv
│   ├── 📊 lineas_pedido.csv
│   ├── 🧾 metadatos_sinteticos.json
│   ├── 📊 modelos.csv
│   ├── 📊 pedidos.csv
│   └── 📊 stock.csv
├── 📚 docs/                           # Informes de calidad de datos
│   ├── ⚠️ incidencias_<fecha>.csv     # Incidencias detectadas
│   ├── 🧾 manifiesto_<fecha>.json     # Manifiesto de cada generación
│   └── ✅ resumenCalidad_<fecha>.*    # Resumen de calidad
├── 🌐 frontend/                       # Web MERCURY
│   ├── 🖼️ assets/                     # Imágenes y recursos
│   ├── 🎨 css/
│   │   └── 🎨 styles.css
│   ├── ⚡ js/
│   │   └── ⚡ script.js
│   ├── 📦 node_modules/               # Dependencias de Node (no se sube a Git)
│   ├── 🖥️ views/                      # Páginas HTML
│   │   ├── 👥 adminUsuarios.html
│   │   ├── 🛒 carrito.html
│   │   ├── 👟 catalogo.html
│   │   ├── 📖 historia.html
│   │   ├── 🏠 inicio.html
│   │   ├── 🔑 login.html
│   │   └── 📝 registro.html
│   ├── 🔐 .env                        # Variables de entorno
│   ├── 📦 package.json
│   ├── 🔒 package-lock.json
│   └── 🚀 server.js                   # Servidor Node + Express
├── 📕 MemoriaTécnica/
│   └── 📄 MemoriaPsp_Odoo_DI.pdf
├── 🧪 tests/                          # Pruebas automáticas (pytest)
│   ├── 🐍 conftest.py
│   ├── 🧪 test_calculos.py
│   ├── 🧪 test_carga_esquema.py
│   ├── 🧪 test_integridad.py
│   ├── 🧪 test_refresco.py
│   └── 🧪 test_reproducibilidad.py
├── 📈 app_dashboard.py                # Dashboard Streamlit
├── 📘 diccionario_datos.md            # Diccionario de datos
├── ▶️ main.py                         # Punto de entrada del pipeline
├── 📖 README.md
└── 📋 requirements.txt                # Dependencias de Python
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

### Clonar el repositorio

```bash
git clone https://github.com/Reckles1010/SneakerFactory.git
```

### Acceder al proyecto

```bash
cd SneakerFactory
```

### Configurar la base de datos

Este repositorio incluye la base de datos **Mercury**, que usa el servidor de la web (`server.js`, Node + Express + PostgreSQL). La base de datos contiene 12 tablas con su estructura y sus datos.

Se entrega como un script SQL en texto plano (`MercuryDB.sql`) que, al ejecutarlo con `psql`, **crea la base de datos automáticamente** y carga todas las tablas y los datos.

### Requisitos

- PostgreSQL instalado (el proyecto se ha desarrollado con la versión 17). Incluye el programa `psql`.
- pgAdmin 4 (para visualizar la base de datos y el modelo E-R).
- La contraseña del usuario `postgres` de tu instalación.

### 1. Abrir PowerShell

Pulsa la tecla Windows, escribe `powershell` y pulsa Enter.

### 2. Ejecutar el comando

```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -f "C:\DAM\2º DAM\1ºPROYECTO\database\sql\MercuryDB.sql"
```

Hay que adaptar **dos rutas** a tu equipo:

| Parte del comando | Qué es | Qué poner |
|---|---|---|
| `"C:\Program Files\PostgreSQL\17\bin\psql.exe"` | **Primera ruta:** dónde está instalado PostgreSQL | La ruta a `psql.exe` de tu instalación. Cambia `17` por tu versión si es distinta. |
| `"C:\DAM\2º DAM\1ºPROYECTO\database\sql\MercuryDB.sql"` | **Segunda ruta:** dónde está el script SQL descargado | La ruta donde hayas guardado `MercuryDB.sql`. |

**Consejos:**

- Mantén las comillas, porque las rutas tienen espacios.
- Para copiar la ruta del script: clic derecho sobre `MercuryDB.sql` en el Explorador de archivos → **Copiar como ruta de acceso**.
- Para ver qué versión de PostgreSQL tienes instalada, ejecuta:
  ```powershell
  Get-ChildItem "C:\Program Files\PostgreSQL" -Directory
  ```

### 3. Introducir la contraseña

PowerShell pedirá la contraseña del usuario `postgres`. Al escribirla no se ve nada en pantalla; es normal. Pulsa Enter.

Al terminar, `psql` mostrará una serie de mensajes (`CREATE DATABASE`, `CREATE TABLE`, `INSERT`...). Si no aparece ningún mensaje de `ERROR`, la restauración ha sido correcta.

### 4. Abrir la base de datos en pgAdmin

1. Abre pgAdmin y conéctate a tu servidor.
2. Clic derecho sobre **Databases** → **Refresh**.
3. Aparecerá la base de datos **Mercury**. Las tablas están en `Mercury → Schemas → public → Tables`.

### Ver el modelo E-R

No hace falta pgModeler. pgAdmin genera el diagrama directamente:

1. Clic derecho sobre la base de datos **Mercury** → **ERD For Database**.
2. Se muestran las tablas y sus relaciones.
3. Si se incluye el archivo `modelo_er.pgerd`, también se puede abrir desde la herramienta ERD con el icono de abrir archivo.
4. La imagen `modelo_er.png` permite ver el modelo sin abrir pgAdmin.

### Problemas frecuentes

| Error | Causa | Solución |
|---|---|---|
| `El término '...psql.exe' no se reconoce` | La primera ruta es incorrecta (otra versión o carpeta) | Comprueba la versión instalada y corrige la ruta a `psql.exe`. |
| `No such file or directory` | La segunda ruta es incorrecta | Copia la ruta exacta del `.sql` con *Copiar como ruta de acceso*. |
| `password authentication failed` | Contraseña incorrecta | Usa la contraseña del usuario `postgres` de tu instalación. |
| `database "Mercury" already exists` | La base de datos ya existe en tu servidor | Elimínala antes desde pgAdmin (clic derecho → **Delete**) o renómbrala, y vuelve a ejecutar el comando. |


### 5. Abrir el proyecto

Abrir los archivos con el entorno de desarrollo correspondiente:

- **IntelliJ IDEA:** para el backend Java.
- **Visual Studio Code:** para el frontend web, el servidor Node.js y Python.

### 6. Ejecutar la aplicación

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

Arrancar el servidor:

```bash
cd frontend
npm start
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
source .venv\Scripts\Activate.ps1
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
python -m streamlit run .\app_dashboard.py   
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
