# Diccionario de datos · Contrato ACC

Los nombres siguientes son nombres canónicos internos adaptados a los ficheros reales de la base de datos. Confirmar con ACC los tipos, formatos y valores permitidos antes de la entrega final.

| Tabla | Campo canónico | Significado | Tipo | Unidad / regla |
|---|---|---|---|---|
| clientes | id_cliente | Identificador de cliente | texto | Clave única, no magnitud |
| clientes | nombre | Nombre o alias | texto | Dato personal; evitar mostrarlo/descargarlo |
| modelos | id_modelo | Identificador de modelo | texto | Clave única |
| modelos | modelo | Nombre comercial | texto | Etiqueta |
| modelos | categoria | Categoría del modelo | texto | Clasificación |
| pedidos | id_pedido | Identificador de pedido | texto | Clave única |
| pedidos | fecha | Fecha del pedido | fecha | Formato a confirmar con ACC |
| pedidos | id_cliente | Cliente comprador | texto | FK clientes |
| pedidos | estado | Estado operativo | categoría | Catálogo acordado |
| pedidos | tipo | Estándar o Custom | categoría | Catálogo acordado |
| linea | id_linea | Identificador de línea | texto | Único si ACC lo exporta |
| linea | id_pedido | Pedido asociado | texto | FK pedidos |
| linea | id_modelo | Modelo vendido | texto | FK modelos |
| linea | talla | Talla | texto | Catálogo acordado |
| linea | cantidad | Pares | numérico | > 0 |
| linea | precio_unitario | Precio por par | decimal | >= 0, moneda a confirmar |
| stock | id_modelo | Modelo | texto | FK modelos (desde Almacen.csv) |
| stock | talla | Talla | texto | Variante |
| stock | stock_disponible | Stock disponible | numérico | >= 0, snapshot |
| stock | fecha_corte | Fecha del snapshot | fecha | Opcional; confirmar con ACC |
| almacen | id_almacen | Identificador de almacén | texto | Clave única |
| almacen | nombre | Nombre del almacén | texto | Etiqueta |
| fabrica | id_fabrica | Identificador de fábrica | texto | Clave única |
| fabrica | nombre | Nombre de la fábrica | texto | Etiqueta |
| productos | id_producto | Identificador de producto | texto | Clave única |
| productos | nombre | Nombre del producto | texto | Etiqueta |
| sucursal | id_sucursal | Identificador de sucursal | texto | Clave única |
| sucursal | nombre | Nombre de la sucursal | texto | Etiqueta |
| trabajador | id_trabajador | Identificador de trabajador | texto | Clave única |
| trabajador | nombre | Nombre del trabajador | texto | Dato personal |
| many | id_fabrica | Fábrica asociada | texto | FK fábrica |
| many | id_almacen | Almacén asociado | texto | FK almacén (relación N:M) |

## Formato CSV
Configuración inicial: UTF-8-SIG, coma como delimitador, punto decimal. Debe verificarse con los ficheros reales. Los IDs se conservan como texto.