# 10 · Registros de decisiones de arquitectura

Los ADR explican por qué se tomó una decisión que afecta arquitectura, metodología, seguridad, reproducibilidad o operación. No sustituyen la documentación funcional.

## Estados

- **Propuesto:** requiere aprobación.
- **Aceptado:** decisión vigente.
- **Rechazado:** evaluado y no adoptado.
- **Sustituido:** reemplazado por otro ADR, manteniendo historia.
- **Obsoleto:** ya no aplica sin haber sido sustituido.

## Índice

| ADR | Decisión | Estado |
|---|---|---|
| [0000](0000-plantilla.md) | Plantilla | — |
| [0001](0001-pbip-como-formato-versionable.md) | PBIP como formato versionable | Aceptado |
| [0002](0002-mrun-y-reproducibilidad.md) | Conservar MRUN en CSV reproducibles | Aceptado |
| [0003](0003-datos-derivados-en-github.md) | Versionar datos derivados y excluir fuentes brutas | Aceptado |
| [0004](0004-universo-ip-cft-flexible.md) | Universo IP+CFT flexible | Aceptado |
| [0005](0005-parametro-ruta-datos.md) | Parámetro local para la ruta de datos | Aceptado |

## Crear un ADR

1. Copie la plantilla con el siguiente número correlativo.
2. Describa contexto y restricciones verificables.
3. Compare alternativas reales.
4. Declare consecuencias positivas, negativas y riesgos.
5. Enlace el pull request y la evidencia cuando existan.
6. No cambie retrospectivamente una decisión aceptada; cree otra que la sustituya.
