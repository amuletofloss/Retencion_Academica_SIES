# Seguridad

## Alcance

El repositorio contiene datos abiertos derivados. `MRUN` es un identificador enmascarado publicado por SIES, no un RUT real. Aun así, debe tratarse como identificador técnico: no se muestra en visuales, no se combina con fuentes privadas y no se intenta reidentificar personas.

## Reporte responsable

No publique credenciales ni evidencia sensible en un issue. Use **Private vulnerability reporting** en la pestaña Security del repositorio.

## Controles obligatorios

- No versionar `.env`, tokens, secretos, conexiones personales ni identificadores internos no autorizados.
- Usar GitHub Environments y secretos del repositorio para automatización.
- Aplicar mínimo privilegio al service principal de despliegue.
- Revisar cambios en `expressions.tmdl`, roles y workflows por un propietario independiente.
- Rotar de inmediato una credencial expuesta y eliminarla del historial mediante un procedimiento autorizado.
- Verificar que `datos_fuente/` permanezca excluida y que cada archivo derivado tenga trazabilidad.

## RLS y OLS

El modelo actual no define RLS ni OLS. Es una decisión acorde con su conjunto de datos abiertos y alcance público, no una garantía general de seguridad. Si se incorporan datos internos, la publicación queda bloqueada hasta diseñar roles, pruebas positivas/negativas y un ADR de seguridad. Consulte [docs/06-seguridad.md](docs/06-seguridad.md).
