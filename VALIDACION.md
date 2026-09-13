# Validación de la entrega 3.1.0

Fecha de auditoría: 12 de septiembre de 2026.

## Resultado

- Auditoría numérica: **4.955 de 4.955 controles aprobados; 0 fallas**.
- Celdas cohorte–horizonte conciliadas: **120**.
- Dimensiones conciliadas: **9**, cada una para los cuatro conteos centrales.
- Proyecto raíz: exactamente un archivo `.pbip`.
- Páginas: **7**; visuales: **73**, sin identificadores duplicados.
- Medidas: **21**. Las medidas de resultado exigen una única cohorte y un único horizonte.
- Filas longitudinales: **1.634.184**.
- Trayectorias distintas: **307.477**; personas MRUN distintas: **283.350**.
- Duplicados trayectoria–año, MRUN nulos y violaciones de anidamiento: **0**.
- Archivos oficiales trazados: **29**; archivos analíticos con SHA-256: **18**.
- Archivos sobre 100 MiB: **0**.

La evidencia detallada está en `auditoria/evidencia/evidencia_numerica.csv` y el resumen legible por máquina en `auditoria/evidencia/resumen_auditoria.json`.

## Controles certificados

| Ámbito | Cohorte / horizonte | Base | Académica | Institucional | Educación superior |
|---|---|---:|---:|---:|---:|
| IP+CFT | 2024 / año 2 | 41.056 | 26.470 | 27.111 | 29.383 |
| ECS | 2024 / año 2 | 1.697 | 1.137 | 1.155 | 1.266 |

### Procedencia IPLACEX

| Período | Primer año total | Sin matrícula previa | Con matrícula previa | Previa en otra IES | Previa online en otra IES |
|---|---:|---:|---:|---:|---:|
| 2012–2025 | 61.905 | 29.751 | 32.154 | 31.448 | 6.618 |
| 2024–2025 | 27.874 | — | — | 15.664 | 3.469 |

En 2024–2025, el 56,2 % tenía historia en otra IES, pero sólo el 12,4 % tenía historia online en otra IES. Esto describe antecedentes observables y no prueba captación ni causalidad.

## Repetir la validación

```powershell
pip install -r requirements.txt
python scripts/auditar_numeros.py
python scripts/generar_entregables_iplacex.py
node --check scripts/construir_pbip.mjs
node --check scripts/visuales.mjs
pytest -q
```

Se verificó la disponibilidad de Power BI Desktop `2.157.1354.0 (August 2026)`. La auditoría registrada aquí cubre estructura, datos, medidas, referencias y artefactos; la actualización interactiva final en Desktop continúa siendo un control operativo previo a publicación.
