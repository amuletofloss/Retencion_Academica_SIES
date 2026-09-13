# Retención académica SIES · IP+CFT

Proyecto Power BI Project (PBIP) reproducible para analizar continuidad académica en carreras de pregrado de Institutos Profesionales (IP) y Centros de Formación Técnica (CFT), con foco en oferta no presencial, semipresencial o con jornada a distancia.

El repositorio contiene un único proyecto, `Retencion_Academica_SIES.pbip`, su reporte, modelo semántico, datos analíticos, transformación reproducible, pruebas y documentación de gobierno.

## Indicadores

Para una cohorte y año observado, el modelo calcula sobre trayectorias observables:

1. **Retención académica:** continúa en la carrera de origen.
2. **Retención institucional:** continúa en la institución jurídica de origen.
3. **Retención en educación superior:** registra matrícula en cualquier institución de educación superior.

`MRUN` es el identificador enmascarado publicado por SIES; no es el RUT real. Las fuentes y el proyecto no contienen ni requieren una columna `RUT`. Se incluye `MRUN` en los CSV analíticos para que terceros puedan reproducir los conteos distintos y las vinculaciones longitudinales.

## Alcance

| Incluido | No incluido |
|---|---|
| Matrícula SIES 2011–2025 | Cohortes posteriores a 2025 |
| Titulados SIES 2011–2024 | Certificación oficial del indicador por SIES |
| IP y CFT, carreras de pregrado | Universidades y postgrado |
| No Presencial, Semipresencial o jornada A Distancia | Seguimiento fuera de las bases públicas utilizadas |
| Modelo semántico, DAX, reporte y datos derivados | RLS/OLS activo o despliegue automático a producción |
| Página específica para la Escuela de Comercio y Servicios (ECS) | Identificación mediante RUT real |

La metodología es una reconstrucción analítica propia. Consulte [modelo semántico y metodología](docs/02-modelo-semantico.md) antes de interpretar resultados.

## Estructura principal

```text
Retencion_Academica_SIES.pbip
Retencion_Academica_SIES.Report/
Retencion_Academica_SIES.SemanticModel/
datos/
scripts/
tests/
docs/
.github/
```

La anatomía completa y el rol de cada archivo están en [docs/01-estructura-pbip.md](docs/01-estructura-pbip.md). El índice de documentación está en [docs/README.md](docs/README.md).

## Requisitos

- Git.
- Power BI Desktop con soporte PBIP/TMDL. Versión disponible y verificada: **2.157.1354.0 (August 2026)**.
- Python 3.12 y dependencias de `requirements.txt` para reconstrucción y pruebas.
- Node.js 22 para validar o regenerar la definición del proyecto.
- Aproximadamente 100 MB libres para el clon y archivos temporales de actualización.

## Clonar y abrir

1. Use el botón **Code** de GitHub para copiar la URL HTTPS y clone o descargue el repositorio.
2. Desde la carpeta descargada, ejecute `python scripts/configurar_ruta_datos.py`.
3. Abra `Retencion_Academica_SIES.pbip` y ejecute **Actualizar**.

Si los datos están en otro lugar, entregue esa carpeta como argumento al configurador. `Folder.Files` y `File.Contents` requieren una ruta absoluta existente.

Consulte la guía detallada [Configurar Ruta datos](CONFIGURAR_RUTA_DATOS.md), incluida la configuración manual y la solución de errores.

## Desplegar

El repositorio no ejecuta despliegues automáticos todavía. La arquitectura propuesta separa DEV, TEST y PROD y requiere confirmar workspaces, capacidad, tenant e identidad de servicio antes de habilitar CD. Consulte el [plan ALM/DevOps y de publicación](docs/07-alm-devops.md); no coloque esos secretos o identificadores sensibles en los archivos TMDL ni en el workflow.

## Recalcular y validar

Descargue Matrícula 2011–2025 y Titulados 2011–2024 desde el [portal de Datos Abiertos del Centro de Estudios Mineduc](https://centroestudios.mineduc.cl/datos-abiertos/) y mantenga la estructura documentada en [docs/04-power-query.md](docs/04-power-query.md).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\materializar_datos.py --source-root datos_fuente --output datos
python scripts\auditar_numeros.py
python scripts\generar_entregables_iplacex.py
node --check scripts/construir_pbip.mjs
node --check scripts/visuales.mjs
pytest -q
```

También se admite como `--source-root` una carpeta `artifacts` con particiones Parquet `silver/source=matricula|titulados/year=AAAA/data.parquet`.

## Resultados de control

Para la cohorte 2024 observada en 2025, el universo completo contiene 41.056 trayectorias:

| Indicador | Numerador | Tasa |
|---|---:|---:|
| Retención académica | 26.470 | 64,5 % |
| Retención institucional | 27.111 | 66,0 % |
| Retención en educación superior | 29.383 | 71,6 % |

Las cifras se generan desde los CSV incluidos y se concilian con `datos/resultados_control.csv`.

## Estado conocido

- [OK] Versión 3.1.0 con un solo PBIP, 7 páginas y 73 visuales únicos.
- [OK] Auditoría numérica: 4.955 de 4.955 controles aprobados y 120 celdas cohorte–horizonte conciliadas.
- [OK] Cohorte y horizonte son de selección única y las medidas rechazan contextos ambiguos.
- [OK] Procedencia IPLACEX auditada en [AUDITORIA_NUMERICA_COMPLETA.md](AUDITORIA_NUMERICA_COMPLETA.md) y en el PDF V2.
- [FALTA] Confirmar responsables GitHub y destino de despliegue.

No se debe declarar una versión liberada como validada hasta completar el checklist de [docs/11-checklists.md](docs/11-checklists.md).

## Gobierno y contribución

- [CONTRIBUTING.md](CONTRIBUTING.md): ramas, commits, revisión y definición de terminado.
- [SECURITY.md](SECURITY.md): manejo de datos, secretos y reporte de vulnerabilidades.
- [LICENCIA_DATOS.md](LICENCIA_DATOS.md): procedencia y condiciones de los datos derivados.
- [INFORME_VICERRECTOR_ECS.md](INFORME_VICERRECTOR_ECS.md): lectura ejecutiva para la ECS.
- [docs/10-adr/](docs/10-adr/): decisiones de arquitectura.

No se requiere Git LFS en el estado actual: ningún archivo versionado supera 100 MiB. Esta decisión debe revisarse si cambia el tamaño o la política de datos.

## Licencia

El código y la documentación se distribuyen bajo la licencia incluida en [LICENSE](LICENSE). Los datos conservan su procedencia y condiciones descritas en [LICENCIA_DATOS.md](LICENCIA_DATOS.md).
