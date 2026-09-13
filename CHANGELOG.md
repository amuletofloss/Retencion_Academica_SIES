# Registro de cambios

Este proyecto sigue [Semantic Versioning](https://semver.org/) para las versiones liberadas y el formato de [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

## [Sin publicar]

### Corregido

- `Ruta datos` se materializa como una ruta absoluta existente; se elimina el error de actualización de las cuatro consultas Power Query.

### Pendiente

- Confirmar propietarios del repositorio.
- Configurar y probar el despliegue a `workspace DEV por definir`, `workspace TEST por definir` y `workspace PROD por definir`.

## [3.1.0] - 2026-09-12

### Corregido

- Las medidas exigen una única cohorte y un único horizonte; se eliminaron los valores silenciosos predeterminados.
- Se corrigieron tres colisiones de identificadores y el reporte quedó en 73 visuales únicos.
- Se sustituyó la ruta personal heredada por un parámetro de datos controlado por el generador.

### Agregado

- Auditoría reproducible de 4.955 controles numéricos, con cero fallas.
- Conciliación de 120 celdas cohorte–horizonte y nueve dimensiones.
- Tabla de procedencia de primer año IPLACEX por cohortes 2012–2025.
- PDF V2 con respaldo de auditoría y comparación explícita con la versión anterior.
- Compatibilidad verificada con Power BI Desktop 2.157.1354.0 (August 2026).

## [3.0.0] - 2026-09-11

### Agregado

- Único PBIP reproducible con modelo semántico TMDL y siete páginas.
- Datos analíticos derivados con `MRUN` enmascarado, manifiesto de fuentes y SHA-256.
- Tres indicadores de retención y página específica para ECS.
- Auditoría exhaustiva del modelo, DAX, rendimiento y gobierno.
- Documentación canónica numerada, ADR, plantillas de GitHub y checklists de liberación.

### Advertencias conocidas

- La reconstrucción constituye una metodología propia; no es un indicador oficial certificado por SIES.
- No hay RLS/OLS activo porque el repositorio publica exclusivamente datos abiertos derivados.
