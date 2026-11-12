# Informe ejecutivo · Sneaker Factory

**Origen de los datos: ACC · REAL** · Generado: 12/11/2026 08:35 · Semilla: 42

> Este informe separa **observaciones** (qué pasa), **interpretaciones** (por qué podría pasar) y **propuestas** (qué hacer). Ninguna interpretación es una afirmación causal.

**Resumen:** ingresos de venta 176,060.88 €; 6,371 unidades; 1,852 pedidos de venta sobre 3,680 pedidos de actividad; ticket medio 95.07 €. Estados que reconocen ingreso: entregado, enviado.

## Decisión Concentrar la capacidad de fabricación en los modelos clase A
*Prioridad 1 · Alta · Origen: ACC · REAL*

- **Observación:** 7 modelos (clase A) reúnen el 80.8 % de los ingresos; el top-20 % de modelos aporta el 76.1 %.
- **Interpretación:** La demanda está muy concentrada; una rotura en esos modelos penaliza más que en la cola.
- **Propuesta:** Asegurar materia prima y cadencia para los modelos A y revisar la utilidad de mantener la cola larga.
- **Evidencia:** Tabla Modelos ABC (modelos_abc.csv) y figura 03_pareto_abc.png
- **Impacto esperado:** Menos roturas en los modelos que más facturan
- **Limitación / riesgo:** Periodo corto; la clasificación puede cambiar con más meses.

## Decisión Reponer los modelos con menor cobertura
*Prioridad 2 · Alta · Origen: ACC · REAL*

- **Observación:** 3 modelos con stock ≤ 10 o cobertura < 4 semanas; el más ajustado: Zapatillas Aero Motion (65 uds).
- **Interpretación:** La cobertura usa la demanda de 28 días; el stock es una instantánea, no un histórico.
- **Propuesta:** Lanzar reposición de los modelos señalados y repetir el cálculo tras la siguiente exportación.
- **Evidencia:** Tabla stock_cobertura.csv y figura 10_stock_vs_demanda.png
- **Impacto esperado:** Evitar ventas perdidas
- **Limitación / riesgo:** ACC exporta stock por modelo (no por talla): no se detectan roturas de talla concretas.

## Decisión Revisar la cartera de pedidos pendientes
*Prioridad 3 · Media · Origen: ACC · REAL*

- **Observación:** 1,828 pedidos (49.7 % de la actividad) siguen pendientes o en preparación y no cuentan como venta.
- **Interpretación:** Pueden ser pedidos recientes o un flujo de estados que no se actualiza; los datos no lo distinguen.
- **Propuesta:** Contrastar con Acceso a Datos si los estados se actualizan; si no, los ingresos reales están infravalorados.
- **Evidencia:** KPI pedidos_pendientes y reconciliación SQL (auditoria_reconciliacion.csv)
- **Impacto esperado:** Ingresos reconocidos más fiables
- **Limitación / riesgo:** No se conoce la antigüedad esperada de un pedido pendiente.

## Decisión Tratar los canales con criterio, no por el ticket
*Prioridad 4 · Media · Origen: ACC · REAL*

- **Observación:** Online aporta el 53.4 % de los ingresos. Contraste H1 sobre el ticket: Evidencia insuficiente: el IC 95 % incluye 0.
- **Interpretación:** Una diferencia en el ticket medio no demuestra que un canal sea mejor; el canal no se asignó al azar.
- **Propuesta:** No cambiar el reparto de esfuerzo entre canales hasta tener más meses y repetir el contraste.
- **Evidencia:** hipotesis.csv y figura 05_boxplot_importe_por_tipo.png
- **Impacto esperado:** Evita decisiones sobre diferencias no concluyentes
- **Limitación / riesgo:** Los datos reales de ACC no contienen pedidos Custom: la comparación Custom/estándar no es calculable.

## Decisión Reactivar clientes en riesgo o dormidos
*Prioridad 5 · Media · Origen: ACC · REAL*

- **Observación:** 102 clientes en RFM 'En riesgo' o 'Dormido'; 356 clientes sin compras válidas.
- **Interpretación:** Pueden haber dejado de comprar o tener pedidos aún no entregados; RFM usa solo ventas válidas.
- **Propuesta:** Campaña de reactivación acotada a 'En riesgo' y medir la respuesta con la siguiente exportación.
- **Evidencia:** rfm.csv, figura 07_dispersion_rfm.png y kmeans_perfil.csv
- **Impacto esperado:** Recuperar ingresos recurrentes
- **Limitación / riesgo:** El nombre de un clúster no es una categoría comercial; con pocos meses la recencia es poco discriminante.

## Qué NO puede afirmarse
Los datos no permiten afirmar causalidad (canal, día o modelo no se asignaron al azar), ni extrapolar más allá del periodo exportado; con pocos meses tampoco puede hablarse de estacionalidad.
