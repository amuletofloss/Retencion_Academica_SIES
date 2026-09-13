# 00 · Introducción a PBIP y alcance del proyecto

## Qué es PBIP

Power BI Project (PBIP) guarda la definición de un informe y su modelo semántico como carpetas y archivos de texto. A diferencia de un `.pbix`, que concentra los artefactos en un único archivo binario, PBIP permite revisar diferencias, resolver cambios por objeto y automatizar controles en Git.

Microsoft documenta PBIP como una característica en versión preliminar. El soporte y el esquema pueden cambiar; por eso la versión de Power BI Desktop debe quedar registrada en cada release. Referencia: [Power BI Desktop projects (PBIP)](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview), consultada el 2026-09-11.

## PBIP frente a PBIX

| Aspecto | PBIP | PBIX |
|---|---|---|
| Unidad principal | Archivo `.pbip` más carpetas enlazadas | Archivo único `.pbix` |
| Revisión en Git | Texto estructurado, apto para diff | Limitada por formato contenedor |
| Modelo semántico | TMDL en `.SemanticModel/definition/` | Interno al archivo |
| Reporte | PBIR/JSON en `.Report/definition/` | Interno al archivo |
| Automatización | Adecuado para validación y despliegue por código | Requiere herramientas o conversiones adicionales |
| Riesgo principal | Formato preliminar y archivos generados que no deben editarse sin conocimiento | Conflictos opacos y cambios binarios |

## Ventajas aplicadas aquí

- Un único PBIP enlaza de forma explícita reporte y modelo.
- El DAX, las relaciones, Power Query y las páginas se pueden auditar sin abrir Desktop.
- Los datos derivados y hashes permiten reproducir y conciliar cifras.
- Los cambios pueden pasar por pull request y validaciones automáticas.
- Las decisiones de alcance se conservan como ADR.

## Limitaciones verificadas

- La versión disponible y verificada es Power BI Desktop 2.157.1354.0 (August 2026).
- La validación automatizada no sustituye abrir, actualizar y revisar visualmente el informe.
- El despliegue a Fabric/Power BI Service no está configurado.
- El repositorio no contiene credenciales, tenant, capacidades ni workspaces.
- PBIP representa definiciones; la caché local y el estado de Desktop se excluyen de Git.
- La edición manual de definiciones de reporte puede romper el esquema. Los cambios deben validarse en Desktop.

## Alcance funcional

El análisis sigue cohortes de matrícula de origen IP+CFT y observa continuidad en años posteriores. El universo flexible incluye registros de carreras de pregrado que cumplen al menos una condición:

- `ModalidadOrigen = No Presencial`;
- `ModalidadOrigen = Semipresencial`;
- `JornadaOrigen = A Distancia`.

La unión se deduplica por trayectoria. Las modalidades o jornadas de menor tamaño permanecen visibles: no se eliminan por su volumen.

Los tres indicadores principales son carrera de origen, institución jurídica de origen y cualquier institución de educación superior. La página ECS aplica la misma lógica al subconjunto de carreras definido por `GrupoECS` y permite analizar movilidad interna.

## Alcance técnico

Incluye:

- modelo semántico TMDL;
- relaciones y 21 medidas DAX;
- consultas M y parámetro `Ruta datos`;
- definición PBIR del reporte con siete páginas;
- cultura `es-CL`;
- CSV analíticos, manifiestos y hashes;
- scripts de reconstrucción y pruebas;
- documentación, ADR y gobierno GitHub.

No incluye actualmente:

- roles RLS u OLS;
- grupos de cálculo;
- una tabla calendario o inteligencia de tiempo calendario;
- incremental refresh o agregaciones administradas;
- pipeline CD operativo;
- archivos fuente brutos SIES dentro del repositorio;
- datos privados o RUT real.

## Fuentes de verdad

| Pregunta | Fuente prioritaria |
|---|---|
| ¿Qué ejecuta el modelo? | `.SemanticModel/definition/*.tmdl` |
| ¿Qué presenta el informe? | `.Report/definition/` |
| ¿Cómo se derivan los datos? | `scripts/materializar_datos.py` y `datos/fuentes.json` |
| ¿Qué resultado se espera? | `datos/resultados_control.csv` y tests |
| ¿Por qué se eligió una solución? | `docs/10-adr/` |
| ¿Cuál es el alcance explicado? | esta documentación canónica |

## Criterio de credibilidad

Una persona externa debe poder tomar los CSV versionados, aplicar la lógica documentada y obtener los mismos numeradores y tasas. La trazabilidad depende de conservar `MRUN` enmascarado, `TrayectoriaID`, claves de programa, cohortes, banderas y manifiestos. Ocultar `MRUN` en la experiencia de reporte no equivale a retirarlo del conjunto reproducible.
