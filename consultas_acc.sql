-- Consultas SQL de reconciliación para Acceso a Datos (PostgreSQL).
-- Ejecútalas sobre la misma base que se exportó a CSV y guarda los resultados en
--   database/csv/reconciliacion_acc.csv   con columnas:  metrica,valor_sql
-- El dashboard (pestaña Calidad y auditoría) y outputs/<modo>/auditoria_reconciliacion.csv los compararán con pandas.
-- Adapta los nombres de tabla/columna si en PostgreSQL difieren de las cabeceras del CSV.
-- Estados que reconocen ingreso (config.py: SALES_STATES): Entregado, Enviado.

-- 1) metrica = pedidos_unicos
SELECT COUNT(DISTINCT id_pedido) AS valor_sql FROM "Pedido";

-- 2) metrica = pedidos_venta
SELECT COUNT(DISTINCT id_pedido) AS valor_sql FROM "Pedido" WHERE LOWER(estado) IN ('entregado', 'enviado');

-- 3) metrica = pares_vendidos  y  4) metrica = ingresos_ventas
SELECT SUM(l.cantidad) AS pares_vendidos, ROUND(SUM(l.precio_total), 2) AS ingresos_ventas
FROM "Pedido" p JOIN "Linea de pedido" l ON l.id_linea = p."id_linea_Linea de pedido"
WHERE LOWER(p.estado) IN ('entregado', 'enviado');

-- 5) metrica = clientes_unicos   (clientes con al menos un pedido, de cualquier estado)
SELECT COUNT(DISTINCT "id_cliente_Clientes") AS valor_sql FROM "Pedido";

-- 6) metrica = ingresos_mes_AAAA-MM   (cambia el mes por el último mes de tus datos, p. ej. 2026-10)
SELECT ROUND(SUM(l.precio_total), 2) AS valor_sql
FROM "Pedido" p JOIN "Linea de pedido" l ON l.id_linea = p."id_linea_Linea de pedido"
WHERE LOWER(p.estado) IN ('entregado', 'enviado') AND TO_CHAR(p.fecha, 'YYYY-MM') = '2026-10';

-- 7) matriz talla x modelo (Caso N): compara con matriz_modelo_talla.csv
SELECT m.nombre AS modelo, l.talla, SUM(l.cantidad) AS unidades
FROM "Pedido" p JOIN "Linea de pedido" l ON l.id_linea = p."id_linea_Linea de pedido"
JOIN "Modelo" m ON m.id_modelo = p."id_modelo_Modelo"
WHERE LOWER(p.estado) IN ('entregado', 'enviado') GROUP BY m.nombre, l.talla ORDER BY 1, 2;
