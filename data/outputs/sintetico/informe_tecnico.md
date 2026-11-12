# Informe técnico · Sneaker Factory

**Origen: SINTÉTICO** · Generado: 12/11/2026 08:35 · Filtros: ninguno · Semilla: 42

## 1. Método y datos
Flujo: CSV → validación de esquema y 12 reglas → limpieza trazable → cruces con `validate=` e `indicator=` → DataFrames analíticos → estadística, segmentación y predicción. Los CSV de entrada nunca se modifican.

## 2. Calidad por tabla
| tabla    |   filas_recibidas |   filas_validas |   filas_rechazadas |   pct_calidad |   nulos_totales |   inc_bloqueantes |   inc_recuperables |   inc_advertencias |
|:---------|------------------:|----------------:|-------------------:|--------------:|----------------:|------------------:|-------------------:|-------------------:|
| clientes |                40 |              40 |                  0 |           100 |               0 |                 0 |                  0 |                  0 |
| modelos  |                12 |              12 |                  0 |           100 |               0 |                 0 |                  0 |                  0 |
| pedidos  |               900 |             900 |                  0 |           100 |               0 |                 0 |                  0 |                  0 |
| lineas   |              2147 |            2147 |                  0 |           100 |               0 |                 0 |                  0 |                 12 |
| stock    |               120 |             120 |                  0 |           100 |               0 |                 0 |                  0 |                  0 |

### Incidencias por regla
| regla                      | gravedad    |   registros |
|:---------------------------|:------------|------------:|
| 10_linea_posible_duplicado | ADVERTENCIA |          12 |

## 3. KPIs, fórmulas y denominadores
| kpi                      |        valor | formula                                                                        | denominador                     |
|:-------------------------|-------------:|:-------------------------------------------------------------------------------|:--------------------------------|
| pedidos_actividad        |    900       | Nº de id_pedido distintos (todos los estados)                                  | Todos los pedidos del filtro    |
| pedidos_venta            |    817       | id_pedido distintos con estado Entregado/Enviado (SALES_STATES)                | Pedidos del filtro              |
| pedidos_pendientes       |     28       | id_pedido distintos en estado pendiente / en preparación                       | Pedidos del filtro              |
| pedidos_cancelados       |     55       | id_pedido distintos cancelados                                                 | Pedidos del filtro              |
| pares                    |   3637       | Σ cantidad de líneas de pedidos de venta (unidades)                            | Líneas de venta                 |
| ingresos                 | 302977       | Σ cantidad × precio_unitario de líneas de venta (bruto, sin IVA ni descuentos) | Líneas de venta                 |
| ticket                   |    370.841   | ingresos / pedidos_venta                                                       | Pedidos de venta (nunca líneas) |
| pares_por_pedido         |      4.45165 | pares / pedidos_venta                                                          | Pedidos de venta                |
| tasa_cancelacion_pct     |      6.11111 | pedidos_cancelados / pedidos_actividad × 100                                   | Pedidos del filtro              |
| custom_pct               |     21.3333  | pedidos Custom / pedidos_actividad × 100 (N/D si no hay Custom)                | Pedidos del filtro              |
| clientes_activos         |     40       | id_cliente distintos con alguna venta                                          | Clientes con ventas             |
| modelos_vendidos         |     12       | id_modelo distintos con alguna venta                                           | Modelos con ventas              |
| talla_mas_vendida        |     42       | talla con mayor Σ cantidad                                                     | Líneas de venta                 |
| pareto_top20_modelos_pct |     36.2847  | ingresos del 20 % de modelos con más ingresos / ingresos                       | Ingresos de venta               |
| variacion_ultimo_mes_pct |    -51.8052  | (ingresos mes − ingresos mes previo) / ingresos mes previo × 100               | Meses con ventas                |

## 4. Descriptivo del importe por pedido de venta
| tipo     |   n |   media |   mediana |   moda |   desv_tipica |    p25 |    p75 |     p90 |    iqr |   minimo |   maximo |
|:---------|----:|--------:|----------:|-------:|--------------:|-------:|-------:|--------:|-------:|---------:|---------:|
| Custom   | 170 |  732.23 |    339.21 |  91.99 |        991.41 | 191.17 | 561.99 | 2566.52 | 370.83 |    68.99 |  4438.52 |
| Estándar | 647 |  275.88 |    259.97 | 139.98 |        156    | 154.98 | 369.95 |  504.94 | 214.97 |    49.99 |   784.91 |
La mediana representa mejor el pedido típico que la media porque la distribución es asimétrica.

## 5. Hipótesis (formuladas antes de calcular) e incertidumbre
- **H1**: El ticket de los pedidos de venta de un tipo de pedido (primer valor alfabético) difiere del otro tipo.
- **H2**: Tres modelos concentran más del 50 % de los ingresos de venta.
- **H3**: Se vende más (ingresos diarios) en fin de semana que entre semana.

| hipotesis   | comparacion                                                |   n_a |   n_b |   diferencia |   ic95_inf |   ic95_sup | conclusion                                                                      |
|:------------|:-----------------------------------------------------------|------:|------:|-------------:|-----------:|-----------:|:--------------------------------------------------------------------------------|
| H1          | Custom − Estándar (mediana de importe por pedido, €)       |   170 |   647 |        79.24 |      46.25 |     130.99 | Diferencia observada (mayor) con IC 95 % que excluye 0; no demuestra causalidad |
| H2          | Peso top-3 modelos = 36.3 %                                |    12 |   nan |       -13.72 |     nan    |     nan    | No se cumple                                                                    |
| H3          | Fin de semana − laborable (mediana de ingresos diarios, €) |   117 |   302 |       -83    |    -155.86 |      45.49 | Evidencia insuficiente: el IC 95 % incluye 0                                    |

Bootstrap con semilla 42. Los datos no permiten afirmar causalidad (canal, día o modelo no se asignaron al azar), ni extrapolar más allá del periodo exportado; con pocos meses tampoco puede hablarse de estacionalidad.

## 6. Segmentación
RFM por cuartiles (R, F, M de 1 a 4). KMeans con variables escaladas; k elegido = 2 por silhouette.
|   k |   silhouette |   inercia |
|----:|-------------:|----------:|
|   2 |        0.642 |    59.002 |
|   3 |        0.528 |    31.274 |
|   4 |        0.509 |    21.791 |
|   5 |        0.355 |    16.843 |
|   cluster |   clientes |   recency_media |   frecuencia_media |   monetary_medio |   monetary_mediana |   proporcion_pct | nombre                         |
|----------:|-----------:|----------------:|-------------------:|-----------------:|-------------------:|-----------------:|:-------------------------------|
|         0 |         36 |           37.67 |              16.56 |          6006.34 |            6049.53 |               90 | Inactivos o de baja frecuencia |
|         1 |          4 |           21.5  |              55.25 |         21687.2  |           20401    |               10 | Alto valor y frecuente         |
Cruce clúster × segmento RFM:
| nombre                         |   Campeón |   Dormido |   En riesgo |   Fiel |   Reciente |
|:-------------------------------|----------:|----------:|------------:|-------:|-----------:|
| Alto valor y frecuente         |         3 |         0 |           0 |      1 |          0 |
| Inactivos o de baja frecuencia |         5 |         7 |           4 |     11 |          9 |
Un clúster es un grupo matemático de recency/frecuencia/gasto escalados; no equivale automáticamente a una categoría comercial. Se nombra por el perfil medio y se compara con las reglas RFM.

## 7. Predicción de demanda
Origen de la evaluación: **SINTÉTICO**.
Meses de entrenamiento: 2025-02 … 2026-03; meses de prueba: 2026-04, 2026-05, 2026-06 (separación temporal, sin barajar).
| modelo_predictivo       |   MAE |   RMSE |
|:------------------------|------:|-------:|
| Baseline (mes anterior) |  8.67 |  12.48 |
| RandomForest            |  9.01 |  11.16 |
| Ridge                   |  8.32 |  10.32 |
Baseline: MAE 8.67. RandomForest: MAE 9.01 (+3.9 % frente al baseline); Ridge: MAE 8.32 (−4.0 % frente al baseline). El mejor modelo (Ridge) supera al baseline en los últimos 3 meses reservados.
Errores más relevantes:
| id_modelo   | mes     |   real |   baseline_mes_anterior |   random_forest |   ridge |   error_abs |
|:------------|:--------|-------:|------------------------:|----------------:|--------:|------------:|
| M1          | 2026-05 |     57 |                      32 |            21.8 |    27.2 |        35.2 |
| M11         | 2026-06 |      5 |                      19 |            23.7 |    21.1 |        18.7 |
| M2          | 2026-05 |     44 |                      24 |            26.8 |    21.5 |        17.2 |
| M8          | 2026-06 |     12 |                      22 |            29.1 |    16.2 |        17.1 |
| M9          | 2026-05 |     26 |                       7 |             9.4 |    12.1 |        16.6 |

## 8. Sesgos y limitaciones
- Periodo corto y una sola exportación: no hay estacionalidad demostrable.
- El stock es una instantánea y ACC lo exporta por modelo, no por talla.
- `descuento` llega como booleano: el importe es bruto, sin descuentos ni IVA; no se calcula margen (no hay costes).
- Los datos sintéticos no representan clientes reales y nunca se mezclan con los reales.
