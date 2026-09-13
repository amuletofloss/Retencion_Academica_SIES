# ADR-0001 · PBIP como formato versionable

- Estado: Aceptado
- Fecha: 2026-09-11
- Decisores: `mantenedores del repositorio`, `responsables del modelo`, `responsables del reporte`

## Contexto

El proyecto debe ser auditable en GitHub, permitir revisar relaciones y DAX, y evitar múltiples PBIP/PBIX divergentes. Un archivo PBIX no ofrece el mismo nivel de diff por objeto.

## Opciones consideradas

1. **PBIX único:** fácil de distribuir, pero opaco para revisión y merge.
2. **PBIP único:** definiciones textuales de reporte y modelo, aptas para Git y automatización.
3. **PBIX y PBIP simultáneos:** aumenta riesgo de dos fuentes de verdad.

## Decisión

Mantener un único `Retencion_Academica_SIES.pbip` como fuente versionada. No versionar un PBIX paralelo como artefacto fuente.

## Consecuencias

### Positivas

- DAX, TMDL, relaciones y PBIR revisables.
- Automatización y gobierno por pull request.
- Menor riesgo de proyectos divergentes.

### Negativas y riesgos

- PBIP permanece sujeto a evolución de formato.
- Conflictos textuales requieren conocimiento del esquema.
- Es obligatorio registrar una versión compatible de Desktop.

## Validación

- Existe exactamente un `.pbip` y las pruebas lo verifican.
- El descriptor enlaza un reporte y un modelo semántico.

## Revisión

Revisar si Microsoft cambia el estado, compatibilidad o estrategia de despliegue de PBIP.
