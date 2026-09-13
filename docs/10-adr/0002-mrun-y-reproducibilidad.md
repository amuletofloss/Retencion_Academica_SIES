# ADR-0002 · Conservar MRUN en los CSV reproducibles

- Estado: Aceptado
- Fecha: 2026-09-11
- Decisores: `responsables de datos`, `responsables del modelo`

## Contexto

SIES publica `MRUN` como identificador enmascarado. No es el RUT real. La vinculación longitudinal y los conteos distintos por persona necesitan ese identificador. Eliminarlo de los archivos publicados impediría a terceros reconstruir las medidas de personas y cuestionaría la credibilidad del resultado.

## Opciones consideradas

1. **Eliminar MRUN:** reduce detalle, pero impide reproducibilidad completa.
2. **Publicar solo agregados:** hace imposible auditar DAX desde la misma base.
3. **Conservar MRUN enmascarado y ocultarlo en el informe:** conserva reproducibilidad sin presentarlo como atributo de análisis.

## Decisión

Incluir `MRUN` como texto en `seguimiento_*.csv.gz`, usarlo solo en medidas documentadas y mantenerlo oculto en el modelo. No crear ni solicitar una columna `RUT`.

## Consecuencias

### Positivas

- Reproducción independiente de `DISTINCTCOUNT(MRUN)`.
- Trazabilidad longitudinal congruente con las fuentes abiertas.
- Definición explícita que evita confundir MRUN con RUT.

### Negativas y riesgos

- Un usuario puede extraer el campo desde los CSV aunque esté oculto en Power BI.
- Debe prohibirse la reidentificación o combinación con fuentes privadas.

## Validación

- Tests verifican presencia de `MRUN` y ausencia de una columna `RUT`.
- La medida `Definicion MRUN` comunica la definición correcta.
- `MRUN` está marcado `isHidden` en TMDL.

## Revisión

Revisar si cambian las condiciones de publicación de SIES o la clasificación institucional de los datos.
