# 08 · Estándares del repositorio

## Principios

1. Reproducibilidad antes que conveniencia local.
2. Un concepto tiene una definición canónica.
3. Código ejecutable, datos y documentación cambian juntos.
4. Todo resultado publicado tiene fuente, corte, unidad y denominador.
5. Los hechos, inferencias y recomendaciones se distinguen explícitamente.

## Nomenclatura

| Objeto | Convención | Ejemplo |
|---|---|---|
| Proyecto PBIP | PascalCase con guion bajo, estable | `Retencion_Academica_SIES` |
| Tabla | Sustantivo plural/PascalCase | `Programas`, `Cohortes` |
| Columna | PascalCase, sin abreviaturas ambiguas | `AnioDesdeIngreso` |
| Medida de conteo | prefijo `N ` | `N Institucion` |
| Medida de tasa | prefijo `Tasa ` | `Tasa Carrera` |
| Medida específica ECS | prefijo `ECS ` | `ECS Tasa Carrera` |
| Rama | tipo/descripción-kebab | `fix/multiseleccion-cohorte` |
| Commit | Conventional Commit | `docs(modelo): actualiza relaciones` |
| ADR | número de cuatro dígitos y slug | `0005-parametro-ruta-datos.md` |

`Anio` sin tilde se conserva en nombres técnicos para portabilidad. En texto de negocio se escribe “año”.

## Descripciones obligatorias

Cada tabla, columna visible y medida debe documentar:

- definición de negocio;
- unidad/granularidad;
- fuente;
- filtros implícitos o defaults;
- propietario;
- advertencia cuando corresponda.

Estado actual: [FALTA] incorporar descripciones TMDL a tablas, columnas y medidas. La documentación externa no reemplaza el metadato en el modelo.

## Formato

- Tasa: `0.0%`.
- Conteo: `#,##0`.
- Texto: `@` cuando aplique.
- Cultura: `es-CL`.
- CSV: UTF-8, delimitador `;`, finales de línea LF en Git.
- Markdown/YAML/JSON/TMDL: UTF-8 y LF.
- DAX: multilínea, sangría de cuatro espacios, variables descriptivas.

## Capas y dependencias

- `datos/` no depende del PBIP.
- El modelo consume `datos/` mediante `Ruta datos`.
- El reporte consume el modelo semántico.
- Las medidas reutilizan medidas base; los visuales no recrean cálculos de negocio.
- Los scripts son la única vía aprobada para regeneraciones masivas.

## Revisión de código

| Área modificada | Revisor mínimo | Pregunta central |
|---|---|---|
| Datos/script Python | `responsables de datos` | ¿se conserva linaje y granularidad? |
| TMDL/DAX | `responsables del modelo` | ¿el contexto de filtro produce la definición acordada? |
| PBIR/reporte | `responsables del reporte` | ¿el usuario interpreta bien filtros y unidades? |
| ECS | `responsables de negocio ECS` | ¿clasificación y lectura son válidas? |
| Workflow/seguridad | `responsables de DevOps` y `canal privado de seguridad` | ¿hay mínimo privilegio y controles? |
| Documentación | `responsables de documentación` | ¿describe el estado real sin contradicción? |

Los placeholders deben reemplazarse por cuentas/equipos de GitHub con permisos de escritura para que CODEOWNERS sea operativo.

## Política de cambios

- **PATCH:** corrección que no cambia definición ni universo.
- **MINOR:** nueva página, desglose o medida compatible.
- **MAJOR:** cambio de universo, granularidad, definición de indicador o ruptura de compatibilidad.
- Cambios metodológicos requieren ADR, comparación antes/después y comunicación ejecutiva.
- No sobrescribir silenciosamente resultados históricos.

## Documentación

- Los documentos numerados son canónicos.
- `METODOLOGIA.md`, `DICCIONARIO_DATOS.md` y `MEDIDAS_DAX.md` son accesos de compatibilidad y apuntan a los canónicos.
- Cada afirmación cuantitativa incluye cohorte/horizonte/corte.
- Mermaid se usa para arquitectura, relaciones y flujos, no como decoración.
- Enlaces relativos deben funcionar desde GitHub.

## Estado de campos técnicos

Se deben ocultar claves y banderas que no sean aptas para autoservicio. `MRUN`, `TrayectoriaID`, `ProgramaID` e `InstitucionID` ya están ocultas. Se recomienda ocultar banderas 0/1 y exponer solo medidas certificadas después de confirmar que ningún visual depende de su visibilidad.

## Convenciones organizacionales pendientes

No se proporcionaron estándares formales de la organización. Hasta recibirlos, estas reglas son la convención recomendada del repositorio y pueden ser sustituidas mediante un ADR aprobado.
