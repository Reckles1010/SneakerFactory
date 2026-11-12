# Diccionario de datos · Contrato ACC

Los nombres canónicos internos se obtienen de las cabeceras reales de las exportaciones de Acceso a Datos mediante `ALIASES` (`data/config.py`).
Los ID se conservan como **texto**; nunca se usan como magnitudes. **Dato personal:** `Clientes.csv` (dni, nombre, dirección, teléfono, email) se descarta al leerlo; solo se conserva `id_cliente`.

## Formato CSV
UTF-8 con BOM opcional (`utf-8-sig`), separador `,`, decimal `.`, fechas ISO `AAAA-MM-DD` (también se acepta `DD/MM/AAAA`), moneda euro (bruto, sin IVA ni descuentos). Valores nulos: celda vacía.
`Clientes.csv` y `Linea_pedido.csv` llegan **sin fila de cabecera**: se asignan los nombres por posición y se registra una ADVERTENCIA (`01_cabecera_ausente_inferida`). Lo correcto es pedir a ACC que exporte las cabeceras.

## Tablas reales de ACC → contrato analítico
| Fichero ACC | Campo ACC | Campo canónico | Tipo | Significado / regla |
|---|---|---|---|---|
| Clientes.csv | col. 1 | id_cliente | texto | Clave única (nombre, dni, dirección, teléfono, email se descartan) |
| Modelo.csv | id_modelo | id_modelo | texto | Clave única |
| Modelo.csv | nombre | modelo | texto | Nombre comercial |
| Modelo.csv | precio | precio | decimal ≥ 0 | Precio de catálogo por unidad |
| Modelo.csv | stock | stock_disponible | entero ≥ 0 | Instantánea por modelo (ACC no exporta talla ni fecha de corte) |
| Modelo.csv | id_producto_Productos | id_producto | texto | FK Productos |
| Productos.csv | tipo | categoria | texto | Zapatillas, Calcetines, Gorras… |
| Pedido.csv | id_pedido | id_pedido | texto | Clave única; en ACC un pedido tiene una línea |
| Pedido.csv | fecha | fecha | fecha | Fecha del pedido; nula o imposible → pedido excluido |
| Pedido.csv | estado | estado | categoría | Entregado, Enviado (ventas); Pendiente, En preparacion (actividad); Cancelado |
| Pedido.csv | tipo | tipo | categoría | Tienda / Online (no existe Custom en los datos reales) |
| Pedido.csv | descuento | descuento | booleano (t/f) | Sin porcentaje: no se aplica ningún descuento al importe |
| Pedido.csv | id_cliente_Clientes / id_modelo_Modelo / id_linea_Linea de pedido / id_trabajador_Trabajador | id_cliente / id_modelo / id_linea / id_trabajador | texto | FK |
| Linea_pedido.csv | col. 1 | id_linea | texto | Clave única |
| Linea_pedido.csv | col. 2 | talla | texto | Contrato: 35–48 |
| Linea_pedido.csv | col. 3 | cantidad | entero > 0 | Unidades (pares en zapatillas) |
| Linea_pedido.csv | col. 4–7 | color, color_panel, color_suela, color_cordones | texto | Personalización |
| Linea_pedido.csv | col. 8 | precio_total | decimal ≥ 0 | = cantidad × precio unitario; `precio_unitario = precio_total / cantidad` |
| Almacen, Fabrica, Sucursal, Trabajador, many_Fabrica_has_many_Almacen | — | id_* | texto | Tablas auxiliares: se validan claves y relaciones (ADVERTENCIA si huérfanas) |

## Campos derivados (≥ 10, nivel línea salvo indicación)
| Familia | Campo | Fórmula |
|---|---|---|
| Calendario | anio, mes, trimestre, dia_semana, antiguedad_dias | de `fecha`; antigüedad = fecha máxima − fecha |
| Economía | importe_linea, ticket (pedido), precio_medio_par | cantidad × precio_unitario; importe del pedido de venta; ingresos / unidades |
| Comportamiento | frequency, recency_dias, segmento_rfm | pedidos únicos de venta; días desde la última compra; reglas RFM |
| Demanda | unidades_modelo_mes, demanda_mes_anterior, media_3_meses_previos | `shift(1)` (sin incluir el mes a predecir) |
| Operaciones | alerta_stock, cobertura_semanas | stock ≤ umbral; stock / (demanda 28 días / 4) |

## Clasificación RFM (puntuación 1–4 por cuartiles, empates con `rank(method="first")`)
Campeón: R≥3, F≥3, M≥3 · Fiel: F≥3 · Reciente: R≥3 · En riesgo: R≤2 y F≥2 · Dormido: resto · Sin compras válidas: sin ventas en el filtro.

## Contrato del conjunto sintético (`datos_sinteticos/`)
clientes(id_cliente) · modelos(id_modelo, modelo, categoria, precio) · pedidos(id_pedido, fecha, id_cliente, estado, tipo) · lineas_pedido(id_linea, id_pedido, id_modelo, talla, cantidad, precio_unitario) · stock(id_modelo, talla, stock_disponible, fecha_corte). Etiquetado siempre como SINTÉTICO.
