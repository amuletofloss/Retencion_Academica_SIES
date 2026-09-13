# 09 · Glosario

| Término | Definición en este proyecto |
|---|---|
| ADR | Architecture Decision Record; registro versionado de una decisión técnica o metodológica |
| ALM | Gestión del ciclo de vida de una solución, desde desarrollo hasta operación |
| Ámbito flexible | Criterio que incluye modalidad No Presencial, Semipresencial o jornada A Distancia |
| CFT | Centro de Formación Técnica |
| Cohorte | Año de matrícula de origen de una trayectoria |
| CD | Automatización de entrega o despliegue después de validar cambios |
| CI | Validación automática ejecutada en pushes y pull requests |
| DAX | Lenguaje de expresiones del modelo tabular usado para medidas |
| ECS | Escuela de Comercio y Servicios; subconjunto identificado por `GrupoECS` |
| Educación superior | Cualquier institución de educación superior observable en las bases usadas |
| Hecho | Tabla con observaciones medibles; aquí, `Seguimiento` |
| Horizonte | Año ordinal desde el ingreso; horizonte 2 es el año siguiente |
| IP | Instituto Profesional |
| Jornada A Distancia | Valor de jornada que incorpora un programa al universo flexible |
| MRUN | Identificador enmascarado publicado por SIES; no es RUT real |
| OLS | Object-Level Security; restricción de tablas o columnas del modelo |
| PBIP | Power BI Project: descriptor y carpetas de reporte/modelo versionables |
| PBIR | Formato de definición mejorada de reporte de Power BI |
| Power Query/M | Lenguaje y motor de obtención y transformación de datos |
| Programa de origen | Combinación normalizada de carrera, institución y atributos en la cohorte inicial |
| Retención académica | Continuidad en la carrera de origen |
| Retención institucional | Continuidad en la institución jurídica de origen, aunque cambie de carrera |
| Retención en educación superior | Matrícula posterior en cualquier IES, aunque cambie institución o carrera |
| RLS | Row-Level Security; filtrado de filas según identidad/rol |
| RUT | Rol Único Tributario real; no existe como campo en este proyecto |
| SIES | Servicio de Información de Educación Superior de Chile |
| TMDL | Tabular Model Definition Language; representación textual del modelo semántico |
| Trayectoria | Registro de programa de origen seguido a través de años observados |
| `TrayectoriaID` | Identificador derivado para contar trayectorias, distinto de `MRUN` |
| Universo observable | Trayectorias cuyo horizonte puede evaluarse con el corte de datos disponible |

## Diferencia entre persona y trayectoria

Una persona (`MRUN`) puede tener más de una trayectoria de origen. Los indicadores principales cuentan `TrayectoriaID`; las medidas con “Personas” cuentan `MRUN`. No deben compararse sin declarar la unidad.

## Jerarquía esperada de continuidad

En condiciones normales:

```text
EnCarrera ⊆ EnInstitucion ⊆ EnEducacionSuperior
```

Una violación puede indicar un error de normalización, una definición distinta o un caso excepcional que debe investigarse.
