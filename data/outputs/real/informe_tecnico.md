# Informe técnico · Sneaker Factory

**Origen: ACC · REAL** · Generado: 12/11/2026 08:35 · Filtros: ninguno · Semilla: 42

## 1. Método y datos
Flujo: CSV → validación de esquema y 12 reglas → limpieza trazable → cruces con `validate=` e `indicator=` → DataFrames analíticos → estadística, segmentación y predicción. Los CSV de entrada nunca se modifican.

## 2. Calidad por tabla
| tabla    |   filas_recibidas |   filas_validas |   filas_rechazadas |   pct_calidad |   nulos_totales |   inc_bloqueantes |   inc_recuperables |   inc_advertencias |
|:---------|------------------:|----------------:|-------------------:|--------------:|----------------:|------------------:|-------------------:|-------------------:|
| clientes |               740 |             740 |                  0 |           100 |               0 |                 0 |                  0 |                  1 |
| modelos  |                28 |              28 |                  0 |           100 |               0 |                 0 |                  0 |                  0 |
| pedidos  |              3680 |            3680 |                  0 |           100 |               0 |                 0 |                  0 |                  0 |
| lineas   |              3680 |            3680 |                  0 |           100 |               0 |                 0 |                  0 |                  1 |
| stock    |                28 |              28 |                  0 |           100 |              56 |                 0 |                  0 |                  0 |

### Incidencias por regla
| regla                        | gravedad    |   registros |
|:-----------------------------|:------------|------------:|
| 01_cabecera_ausente_inferida | ADVERTENCIA |           2 |

## 3. KPIs, fórmulas y denominadores
| kpi                      |        valor | formula                                                                        | denominador                     |
|:-------------------------|-------------:|:-------------------------------------------------------------------------------|:--------------------------------|
| pedidos_actividad        |   3680       | Nº de id_pedido distintos (todos los estados)                                  | Todos los pedidos del filtro    |
| pedidos_venta            |   1852       | id_pedido distintos con estado Entregado/Enviado (SALES_STATES)                | Pedidos del filtro              |
| pedidos_pendientes       |   1828       | id_pedido distintos en estado pendiente / en preparación                       | Pedidos del filtro              |
| pedidos_cancelados       |      0       | id_pedido distintos cancelados                                                 | Pedidos del filtro              |
| pares                    |   6371       | Σ cantidad de líneas de pedidos de venta (unidades)                            | Líneas de venta                 |
| ingresos                 | 176061       | Σ cantidad × precio_unitario de líneas de venta (bruto, sin IVA ni descuentos) | Líneas de venta                 |
| ticket                   |     95.0653  | ingresos / pedidos_venta                                                       | Pedidos de venta (nunca líneas) |
| pares_por_pedido         |      3.44006 | pares / pedidos_venta                                                          | Pedidos de venta                |
| tasa_cancelacion_pct     |      0       | pedidos_cancelados / pedidos_actividad × 100                                   | Pedidos del filtro              |
| custom_pct               |    nan       | pedidos Custom / pedidos_actividad × 100 (N/D si no hay Custom)                | Pedidos del filtro              |
| clientes_activos         |    384       | id_cliente distintos con alguna venta                                          | Clientes con ventas             |
| modelos_vendidos         |     28       | id_modelo distintos con alguna venta                                           | Modelos con ventas              |
| talla_mas_vendida        |     45       | talla con mayor Σ cantidad                                                     | Líneas de venta                 |
| pareto_top20_modelos_pct |     76.0588  | ingresos del 20 % de modelos con más ingresos / ingresos                       | Ingresos de venta               |
| variacion_ultimo_mes_pct |     -5.63589 | (ingresos mes − ingresos mes previo) / ingresos mes previo × 100               | Meses con ventas                |

## 4. Descriptivo del importe por pedido de venta
| tipo   |   n |   media |   mediana |   moda |   desv_tipica |   p25 |    p75 |    p90 |   iqr |   minimo |   maximo |
|:-------|----:|--------:|----------:|-------:|--------------:|------:|-------:|-------:|------:|---------:|---------:|
| Online | 932 |  100.88 |      58   |   7.98 |        109.93 | 23.96 | 119.98 | 259.96 | 96.02 |     2.99 |   389.94 |
| Tienda | 920 |   89.18 |      58.5 |  21.99 |         94.88 | 21.99 | 107.5  | 224.97 | 85.51 |     3.5  |   449.94 |
La mediana representa mejor el pedido típico que la media porque la distribución es asimétrica.

## 5. Hipótesis (formuladas antes de calcular) e incertidumbre
- **H1**: El ticket de los pedidos de venta de un tipo de pedido (primer valor alfabético) difiere del otro tipo.
- **H2**: Tres modelos concentran más del 50 % de los ingresos de venta.
- **H3**: Se vende más (ingresos diarios) en fin de semana que entre semana.

| hipotesis   | comparacion                                                |   n_a |   n_b |   diferencia |   ic95_inf |   ic95_sup | conclusion                                                                      |
|:------------|:-----------------------------------------------------------|------:|------:|-------------:|-----------:|-----------:|:--------------------------------------------------------------------------------|
| H1          | Online − Tienda (mediana de importe por pedido, €)         |   932 |   920 |        -0.5  |     -10.29 |       3.01 | Evidencia insuficiente: el IC 95 % incluye 0                                    |
| H2          | Peso top-3 modelos = 53.4 %                                |    28 |   nan |         3.43 |     nan    |     nan    | Se cumple                                                                       |
| H3          | Fin de semana − laborable (mediana de ingresos diarios, €) |    44 |   110 |      -129.5  |    -217.67 |     -66.72 | Diferencia observada (menor) con IC 95 % que excluye 0; no demuestra causalidad |

Bootstrap con semilla 42. Los datos no permiten afirmar causalidad (canal, día o modelo no se asignaron al azar), ni extrapolar más allá del periodo exportado; con pocos meses tampoco puede hablarse de estacionalidad.

## 6. Segmentación
RFM por cuartiles (R, F, M de 1 a 4). KMeans con variables escaladas; k elegido = 2 por silhouette.
|   k |   silhouette |   inercia |
|----:|-------------:|----------:|
|   2 |        0.594 |   740.111 |
|   3 |        0.373 |   508.931 |
|   4 |        0.392 |   407.559 |
|   5 |        0.37  |   324.147 |
|   cluster |   clientes |   recency_media |   frecuencia_media |   monetary_medio |   monetary_mediana |   proporcion_pct | nombre                         |
|----------:|-----------:|----------------:|-------------------:|-----------------:|-------------------:|-----------------:|:-------------------------------|
|         0 |         32 |           39.38 |               3.12 |           214.7  |             166.38 |             8.33 | Inactivos o de baja frecuencia |
|         1 |        352 |           14.92 |               4.98 |           480.65 |             513.4  |            91.67 | Alto valor y frecuente         |
Cruce clúster × segmento RFM:
| nombre                         |   Campeón |   Dormido |   En riesgo |   Fiel |   Reciente |
|:-------------------------------|----------:|----------:|------------:|-------:|-----------:|
| Alto valor y frecuente         |        52 |        28 |          46 |    140 |         86 |
| Inactivos o de baja frecuencia |         0 |        28 |           0 |      0 |          4 |
Un clúster es un grupo matemático de recency/frecuencia/gasto escalados; no equivale automáticamente a una categoría comercial. Se nombra por el perfil medio y se compara con las reglas RFM.

## 7. Predicción de demanda
Origen de la evaluación: **ACC · REAL**.
Histórico insuficiente: 6 meses (se necesitan al menos 9). No se entrena ni se muestran previsiones; usar el histórico sintético para el laboratorio.

## 8. Sesgos y limitaciones
- Periodo corto y una sola exportación: no hay estacionalidad demostrable.
- El stock es una instantánea y ACC lo exporta por modelo, no por talla.
- `descuento` llega como booleano: el importe es bruto, sin descuentos ni IVA; no se calcula margen (no hay costes).
- Los datos sintéticos no representan clientes reales y nunca se mezclan con los reales.
