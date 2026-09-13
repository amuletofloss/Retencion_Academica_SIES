# 11 · Checklists

Estados: `[OK]` validado, `[RIESGO]` requiere revisión, `[FALTA]` no disponible, `[NO APLICA]` fuera del alcance.

## Estado basal del repositorio

| Control | Estado | Observación |
|---|---|---|
| Un único `.pbip` | [OK] | `Retencion_Academica_SIES.pbip` |
| Reporte y modelo enlazados | [OK] | `.Report` y `.SemanticModel` presentes |
| Datos analíticos reproducibles | [OK] | CSV/GZip, manifiesto y hashes |
| MRUN correctamente definido | [OK] | Enmascarado, no RUT; incluido en CSV y oculto en modelo |
| Tres relaciones N:1 | [OK] | activas, unidireccionales |
| Tres indicadores principales | [OK] | carrera, institución, educación superior |
| Hoja ECS | [OK] | página y medidas específicas |
| Multiselección DAX | [OK] | DAX-001 cerrado; contexto único obligatorio |
| 73 visuales esperados | [OK] | REPORT-001 cerrado; 73 identificadores únicos |
| RLS/OLS | [NO APLICA] | datos abiertos actuales |
| Versión Desktop | [OK] | 2.157.1354.0 (August 2026) disponible |
| CD operativo | [FALTA] | workspaces e identidad sin configurar |
| CODEOWNERS operativo | [FALTA] | propietarios pendientes |

## Antes de cada commit

- [ ] El cambio está limitado a una responsabilidad.
- [ ] No hay secretos, tokens ni `.env`; la única ruta local admitida es `Ruta datos`.
- [ ] No se agregó una columna `RUT` ni se redefinió `MRUN`.
- [ ] Los archivos generados provienen del script versionado.
- [ ] Se revisó `git diff`, incluidos cambios automáticos de Desktop.
- [ ] Se actualizó la documentación afectada.
- [ ] Si cambió una decisión transversal, se creó o actualizó un ADR.
- [ ] `pytest -q` finaliza correctamente.
- [ ] Ambos scripts `.mjs` pasan `node --check`.

## Antes de un pull request

- [ ] Se describe problema, solución, impacto y riesgo.
- [ ] Se identifica el corte de datos y si cambian resultados.
- [ ] Se adjunta comparación antes/después para medidas o universo.
- [ ] Se probaron nulos, duplicados, huérfanos y cardinalidades si cambió el modelo.
- [ ] Se probaron sin filtro, selección única y multiselección si cambió DAX.
- [ ] Se revisaron páginas, interacciones y accesibilidad si cambió PBIR.
- [ ] Se agregó prueba de regresión.
- [ ] Se actualizaron `CHANGELOG.md` y manifiestos cuando corresponde.
- [ ] Se solicitó revisión de propietarios adecuados.

## Relaciones

- [ ] La clave del lado uno es única y no nula.
- [ ] La clave del lado muchos no tiene huérfanos inesperados.
- [ ] Los tipos coinciden exactamente.
- [ ] La cardinalidad es N:1 salvo justificación.
- [ ] El filtro es unidireccional dimensión→hecho salvo ADR.
- [ ] No se crearon ciclos o rutas ambiguas.
- [ ] Una relación inactiva tiene medida con `USERELATIONSHIP` y prueba.
- [ ] Una relación N:N usa bridge o tiene justificación explícita.

## DAX

- [ ] La medida tiene definición, formato y carpeta.
- [ ] El denominador corresponde a la unidad declarada.
- [ ] Usa `DIVIDE` para tasas.
- [ ] No confunde ausencia de filtro con multiselección.
- [ ] El contexto de filtro está probado en totales y desgloses.
- [ ] No usa `FILTER`/iteradores sobre grandes tablas sin medición.
- [ ] No elimina filtros con `ALL`/`REMOVEFILTERS` sin justificación.
- [ ] No depende de una relación inactiva sin activarla.
- [ ] No contiene valores hardcodeados repetidos sin política.
- [ ] Coincide con un cálculo independiente sobre CSV.

## Power Query y datos

- [ ] Están presentes los 15 años de matrícula y 14 de titulados del corte actual.
- [ ] `datos/fuentes.json` refleja los archivos realmente usados.
- [ ] Se recalcularon hashes analíticos.
- [ ] Los CSV conservan UTF-8, `;` y esquema documentado.
- [ ] `MRUN` conserva ceros/formato al tratarse como texto.
- [ ] Las banderas solo contienen 0/1.
- [ ] Carrera implica institución e institución implica educación superior, o las excepciones están explicadas.
- [ ] No se versionaron fuentes brutas.

## Reporte

- [ ] El PBIP abre sin reparación.
- [ ] La actualización completa termina correctamente.
- [ ] Existen siete páginas en el orden documentado.
- [ ] Los segmentadores esenciales están presentes y visibles.
- [ ] Títulos muestran contexto y unidad.
- [ ] MRUN y claves técnicas no aparecen en visuales/exportación.
- [ ] La página ECS usa el filtro `GrupoECS = ECS` y resultados conciliados.
- [ ] Se revisaron contraste, texto alternativo y orden de tabulación.
- [ ] Performance Analyzer no muestra regresiones relevantes.

## Seguridad

- [ ] El alcance de datos sigue siendo abierto.
- [ ] Si cambió el alcance, se revaluó RLS/OLS antes de publicar.
- [ ] No existen secretos en archivos ni historial del PR.
- [ ] Los workflows usan versiones confiables y mínimo privilegio.
- [ ] Los entornos de despliegue exigen aprobación.
- [ ] Exportación, drill-through y Analyze in Excel respetan la política.

## Antes de una release

- [ ] Todos los checks de PR están en verde.
- [ ] DAX-001 y REPORT-001 permanecen cerrados y cubiertos por pruebas.
- [ ] Se registró la versión de Power BI Desktop.
- [ ] `pbip.manifest.json` tiene versión y corte correctos.
- [ ] `CHANGELOG.md` contiene la versión y fecha.
- [ ] Los resultados de control coinciden exactamente.
- [ ] Se completó revisión ejecutiva de ECS.
- [ ] El tag sigue `vMAJOR.MINOR.PATCH`.
- [ ] La release enlaza fuentes, metodología, licencia y riesgos.
- [ ] Si hay despliegue, DEV/TEST/PROD y smoke tests finalizaron correctamente.

## Pruebas recomendadas por herramienta

| Herramienta | Prueba | Estado actual |
|---|---|---|
| pytest | estructura, archivos, datos, hashes y documentación | Automatizada |
| Node `--check` | sintaxis de generadores | Automatizada |
| Power BI Desktop | apertura, refresh, visuales e interacciones | Manual requerida |
| DAX Studio | Server Timings, planes y VertiPaq | [FALTA ejecución] |
| Tabular Editor BPA | estándares y metadatos | [FALTA configuración] |
| Performance Analyzer | rendimiento por visual/página | [FALTA ejecución] |

## Aprobación

| Rol | Responsable | Fecha | Estado |
|---|---|---|---|
| Modelo semántico | `responsables del modelo` | `fecha por definir` | Pendiente |
| Datos | `responsables de datos` | `fecha por definir` | Pendiente |
| Reporte | `responsables del reporte` | `fecha por definir` | Pendiente |
| Negocio ECS | `responsables de negocio ECS` | `fecha por definir` | Pendiente |
| DevOps/seguridad | `responsables de DevOps` | `fecha por definir` | Pendiente |
