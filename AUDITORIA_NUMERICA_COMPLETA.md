# Auditoría numérica completa · versión 3.1.0

Fecha: 12 de septiembre de 2026
Corte: matrícula 2025 / titulados 2024
Resultado: **4.955 controles aprobados, 0 fallidos**

## Objetivo

Verificar desde los datos analíticos materializados que el PBIP, sus controles, sus dimensiones y los entregables de procedencia de IPLACEX expresen los mismos números. La unidad central es la trayectoria deduplicada `MRUN–carrera–institución–cohorte`.

## Cobertura

- 15 archivos longitudinales de seguimiento, cohortes 2011–2025.
- 1.634.184 observaciones, 307.477 trayectorias y 283.350 personas enmascaradas.
- 120 combinaciones válidas de cohorte y horizonte.
- Cuatro conteos: base, retención en carrera, retención institucional y continuidad en educación superior.
- Nueve dimensiones: tipo de institución, institución, carrera, nivel, área, modalidad de origen, jornada de origen, ámbito flexible y grupo ECS.
- 18 archivos analíticos verificados mediante SHA-256.

## Método de conciliación

Para cada celda cohorte–horizonte se recalcularon los cuatro conteos con `DISTINCT TrayectoriaID` directamente desde los CSV comprimidos y se compararon con `datos/resultados_control.csv`. Después se repitió la conciliación agrupando por cada dimensión. También se controló en todas las celdas la relación:

`retención en carrera ≤ retención institucional ≤ continuidad en educación superior ≤ base`

Se añadieron controles certificados para el total nacional, ECS e IPLACEX, junto con la conciliación excluyente:

`sin matrícula previa + con matrícula previa = total de primer año IPLACEX`

## Resultados principales

| Control | Resultado |
|---|---:|
| Controles ejecutados | 4.955 |
| Aprobados | 4.955 |
| Fallidos | 0 |
| Celdas cohorte–horizonte | 120 |
| Dimensiones conciliadas | 9 |
| Problemas de conciliación IPLACEX | 0 |

### Procedencia IPLACEX

| Período | Total primer año | Sin matrícula previa | Con matrícula previa | Previa en otra IES | Previa online en otra IES |
|---|---:|---:|---:|---:|---:|
| 2012–2025 | 61.905 | 29.751 | 32.154 | 31.448 | 6.618 |
| 2024–2025 | 27.874 | — | — | 15.664 | 3.469 |

El hallazgo ejecutivo correcto es que, en 2024–2025, **56,2 %** de las trayectorias de primer año tenía antecedentes en alguna otra IES, mientras sólo **12,4 %** tenía antecedentes online en otra IES. Por tanto, no corresponde afirmar que la mayoría llegó desde competidores online.

## Cambios aplicados al PBIP

- Se eliminaron los valores silenciosos predeterminados de las medidas.
- Las nueve medidas de resultado sólo se evalúan con una única cohorte y un único horizonte.
- Se agregó la medida `Estado selección` para orientar al usuario.
- Cohorte y horizonte operan como segmentadores de selección única.
- Se corrigieron tres colisiones de identificadores; el reporte contiene 73 visuales únicos.
- La ruta de datos quedó parametrizada y materializada como una ruta absoluta existente para la copia local.

## Evidencia y repetición

- Detalle: `auditoria/evidencia/evidencia_numerica.csv`.
- Resumen: `auditoria/evidencia/resumen_auditoria.json`.
- Ejecutor: `scripts/auditar_numeros.py`.
- Procedencia IPLACEX: `datos/iplacex_procedencia_cohortes.csv`.

```powershell
python scripts/auditar_numeros.py
pytest -q
```

## Límite de la conclusión

La historia previa indica que el MRUN apareció en años anteriores de SIES. No identifica necesariamente la matrícula inmediatamente anterior, no mide una transferencia directa y no demuestra causalidad comercial. La revisión estática y numérica no sustituye la actualización interactiva final y la inspección visual en Power BI Desktop antes de publicar.
