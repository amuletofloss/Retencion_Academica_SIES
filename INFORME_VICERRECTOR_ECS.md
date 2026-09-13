# Informe ejecutivo para la Vicerrectoría ECS

## Propósito

Este proyecto permite observar la continuidad anual de estudiantes de pregrado en formatos No Presencial, Semipresencial o con jornada A Distancia, comparando el sistema IP+CFT con la Escuela de Comercio de Santiago.

El informe utiliza matrícula SIES 2011–2025 y titulados SIES 2011–2024. Los cálculos se reconstruyen desde datos abiertos y no corresponden a una cifra oficial certificada por SIES.

## Tres preguntas distintas

- **Retención académica:** ¿la trayectoria continúa en la carrera de origen?
- **Retención institucional:** ¿continúa en la misma institución jurídica?
- **Retención en educación superior:** ¿continúa en algún lugar del sistema?

Esta separación evita calificar como pérdida total a quienes cambian de carrera o institución. También distingue movilidad dentro de ECS: el paso entre el IP 171 y el CFT 426 se informa, pero no se presenta como permanencia en la misma institución.

## Resultado más reciente

Para la cohorte 2024 observada en 2025:

| Ámbito | Trayectorias | Académica | Institucional | Educación superior |
|---|---:|---:|---:|---:|
| IP+CFT nacional | 41.056 | 64,5 % | 66,0 % | 71,6 % |
| ECS: IP 171 + CFT 426 | 1.697 | 67,0 % | 68,1 % | 74,6 % |
| Resto IP+CFT | 39.359 | 64,4 % | 66,0 % | 71,4 % |

En esta observación, ECS se ubica por encima del resto del universo en los tres indicadores descriptivos. La diferencia es de aproximadamente 2,6 puntos porcentuales en retención académica, 2,1 en retención institucional y 3,1 en permanencia en educación superior.

No debe interpretarse como una comparación causal: la mezcla de carreras, el tamaño, la modalidad, el perfil de ingreso y la expansión de oferta pueden explicar parte de las diferencias.

## Comportamiento que requiere seguimiento

La base ECS del primer seguimiento pasó de 468 trayectorias en la cohorte 2023 a 1.697 en 2024. Este cambio de escala es relevante para gestión, pero también significa que los porcentajes de ambos años representan composiciones distintas. Conviene revisar los resultados por IP/CFT, carrera, modalidad y jornada antes de atribuir el movimiento a una intervención institucional.

La brecha entre retención institucional y permanencia en educación superior muestra trayectorias que continúan estudiando fuera de su institución de origen. Para ECS, en 2024–2025, 1.266 trayectorias permanecen en educación superior y 1.155 en la misma institución: la diferencia de 111 trayectorias merece un análisis de destino y oportunidad de recuperación, sin asumir una causa de salida.

## Recomendaciones

1. Usar la página ECS como tablero regular de cohortes, separando siempre IP 171 y CFT 426.
2. Priorizar carreras con una brecha amplia entre permanencia en educación superior y retención institucional.
3. Analizar la expansión de la cohorte 2024 por programa y formato antes de compararla con cohortes pequeñas.
4. Complementar SIES con registros académicos y de plataforma para estudiar causas; la ausencia de matrícula anual no demuestra abandono ni falta de conexión.
5. Mantener la publicación reproducible: conservar los CSV analíticos, medidas DAX, hashes de fuentes y resultados de las pruebas con cada actualización.

## Garantía de trazabilidad

El repositorio incluye los registros analíticos con `MRUN`, identificador enmascarado oficial, y no utiliza un campo `RUT`. Cualquier revisor puede descomprimir los CSV, aplicar las medidas documentadas y conciliar los resultados con `datos/resultados_control.csv`.
