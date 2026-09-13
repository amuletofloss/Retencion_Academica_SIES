## Propósito

<!-- Explique el problema y el resultado esperado. -->

## Tipo de cambio

- [ ] Datos o Power Query
- [ ] Modelo/relaciones
- [ ] DAX
- [ ] Reporte/PBIR
- [ ] Documentación
- [ ] CI/CD o seguridad
- [ ] Release

## Impacto y riesgo

<!-- Indique universo, granularidad, medidas, páginas y usuarios afectados. -->

## Evidencia

<!-- Incluya pruebas, conciliación antes/después y capturas cuando correspondan. -->

- Corte de datos: `[CORTE]`
- Resultado de `pytest -q`: `[RESULTADO]`
- Resultado de validación en Desktop: `[RESULTADO_Y_VERSION]`
- Issue relacionado: `[ISSUE]`

## Checklist

- [ ] No contiene rutas personales, secretos ni fuentes brutas.
- [ ] MRUN conserva su definición de identificador enmascarado; no se agregó RUT.
- [ ] Actualicé documentación, ADR y changelog cuando corresponde.
- [ ] Probé selección sin filtro, única y múltiple si cambié DAX/filtros.
- [ ] Concilié resultados si cambié datos, universo o medidas.
- [ ] Revisé accesibilidad e interacciones si cambié el reporte.
- [ ] Solicité revisión de los propietarios correspondientes.
- [ ] La CI finaliza correctamente.

## Plan de reversión

<!-- Explique cómo revertir sin perder datos ni trazabilidad. -->
