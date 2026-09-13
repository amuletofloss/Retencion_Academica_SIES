# ADR-0003 · Versionar datos derivados y excluir fuentes brutas

- Estado: Aceptado
- Fecha: 2026-09-11
- Decisores: `responsables de datos`, `mantenedores del repositorio`

## Contexto

El PBIP debe actualizarse después de clonar y producir los mismos resultados sin depender de archivos privados. Las fuentes oficiales abarcan 29 archivos y pueden ser voluminosas; el análisis usa un subconjunto transformado.

## Opciones consideradas

1. **No versionar datos:** repo liviano, pero el PBIP no sería autónomo ni inmediatamente reproducible.
2. **Versionar fuentes completas:** máxima copia local, pero duplica publicación, tamaño y responsabilidad.
3. **Versionar derivados suficientes más manifiestos/hashes:** equilibrio entre reproducibilidad, trazabilidad y tamaño.

## Decisión

Versionar `seguimiento_*.csv.gz`, dimensiones, resultados de control, `fuentes.json` y hashes. Excluir `datos_fuente/` y permitir reconstrucción mediante script.

## Consecuencias

### Positivas

- Un clon contiene todo lo necesario para recalcular el PBIP.
- Cada derivado es auditable contra fuente y hash.
- El repositorio permanece bajo los límites actuales sin Git LFS.

### Negativas y riesgos

- Los commits de datos comprimidos producen diffs binarios.
- Cada nuevo corte incrementa el tamaño histórico de Git.
- Las condiciones de reutilización deben mantenerse documentadas.

## Validación

- Ningún archivo versionado supera 100 MiB.
- `datos/resultados_control.csv` coincide con las medidas del corte de control.
- `LICENCIA_DATOS.md` identifica procedencia y alcance.

## Revisión

Revisar al superar umbrales de tamaño, cambiar licencias o adoptar almacenamiento de artefactos/LFS.
