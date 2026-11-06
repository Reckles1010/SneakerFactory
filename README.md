# 👟 MERCURY

> **Sneakers for what´s next**

---


## 📌 Índice

- Sobre el proyecto.
- Objetivos.
- Asignaturas.
- Tecnologías utilizadas.
- Estructura del repositorio.
- Identidad de marca.
- Instalación y ejecución.

---


## 👟 Sobre el proyecto

Este proyecto forma parte del segundo curso del ciclo formativo de **Desarrollo de Aplicaciones Multiplataforma (DAM)**.

Consiste en desarrollar una solución tecnológica para **Mercury**, una empresa ficticia dedicada al diseño y comercialización de zapatillas y relacionados.

El proyecto combina programación, bases de datos, diseño web y herramientas de desarrollo para construir una aplicación que permita presentar los productos y gestionar la información de la empresa.


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
| CSS3 | Diseño y presentación visual. |
| JavaScript | Interactividad de la interfaz. |
| SQL | Consultas y manipulación de datos. |
| PostgreSQL | Almacenamiento y gestión de la información. |
| Git | Control de versiones del código. |
| GitHub | Alojamiento del repositorio y colaboración. |
| IntelliJ IDEA | Desarrollo del código Java. |
| Visual Studio Code | Desarrollo de la interfaz web. |

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
│        └── 📄 style.css
│   ├── 📁 js/
│        └── 📄 scripts.js
│   └── 📁 views/
│       ├── 📄 adminUsuarios.html
│       ├── 📄 carrito.html
│       ├── 📄 catalogo.html
│       ├── 📄 historia.html
│       ├── 📄 inicio.html
│       ├── 📄 login.html
│       └── 📄 registro.html
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
└── 📄 📄 README.md
```


## 🎨 Identidad de marca

| Elemento | Descripción |
|---|---|
| Nombre | Mercury |
| Actividad | Diseño y comercialización de zapatillas. |
| Colores corporativos | Blanco y Negro. |
| Tipografía | 'Inter', -apple-system, BlinkMacSystemFont, sans-serif. |
| Eslogan | «Sneakers for what´s next». |
| Público objetivo | Personas interesadas en el deporte, la moda y el calzado urbano. |


## 🚀 Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone (https://github.com/Reckles1010/SneakerFactory.git)
```

### 2. Acceder al proyecto

```bash
cd SneakerFactory
```

### 3. Configurar la base de datos

- Crear la base de datos en PostgreSQL.
- Ejecutar los scripts SQL de la carpeta `database/`.
- Comprobar que las tablas y relaciones se han creado correctamente.

### 4. Abrir el proyecto

Abrir los archivos con el entorno de desarrollo correspondiente:

- **IntelliJ IDEA:** para el backend Java.
- **Visual Studio Code:** para el frontend web.

### 5. Ejecutar la aplicación

Configurar los parámetros de conexión a la base de datos y ejecutar los componentes siguiendo las instrucciones del proyecto.

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
python -m streamlit run .\data\app_dashboard.py
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

El ticket medio se calcula sobre pedidos únicos, no sobre líneas. Los pedidos cancelados/pedientes permanecen en actividad, pero no se suman a ventas válidas.

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

| Integrante | Responsabilidades |
|---|---|
| Carlos Corchado | Responsabilidades |
| Berta Díaz | Responsabilidades |
| Alberto Ordiales | Responsabilidades |


---


 **Proyecto académico · 2.º DAM · Curso 2026–2027**

