# ADR-0004 · Universo IP+CFT flexible

- Estado: Aceptado
- Fecha: 2026-09-11
- Decisores: `responsables de negocio`, `responsables del modelo`, `responsables de negocio ECS`

## Contexto

Limitar el análisis a una sola modalidad reduce la observación de oferta flexible. La jornada A Distancia es pequeña frente a otras modalidades, pero representa una forma relevante de provisión. IP y CFT amplían el universo pertinente a educación técnico-profesional.

## Opciones consideradas

1. **Solo No Presencial:** simple, pero excluye Semipresencial y casos A Distancia.
2. **IP+CFT con unión flexible:** incluye No Presencial, Semipresencial o jornada A Distancia, deduplicando trayectorias.
3. **Toda educación superior:** diluye el foco técnico-profesional y modifica el objetivo.

## Decisión

Usar carreras de pregrado IP+CFT cuya modalidad de origen sea No Presencial o Semipresencial, o cuya jornada de origen sea A Distancia. Conservar segmentos pequeños y deduplicar la unión antes de medir.

## Consecuencias

### Positivas

- Mayor cobertura de trayectorias flexibles.
- Comparabilidad entre modalidad y jornada.
- ECS se analiza dentro de un universo más representativo.

### Negativas y riesgos

- “Modalidad” y “jornada” no son dimensiones equivalentes; la regla OR debe explicarse.
- Los segmentos pequeños pueden producir tasas volátiles.
- Cambios de clasificación SIES requieren rematerialización.

## Validación

- `Programas` conserva `ModalidadOrigen`, `JornadaOrigen` y `AmbitoFlexible`.
- Los controles verifican deduplicación por trayectoria.

## Revisión

Revisar ante cambios del catálogo SIES o si negocio solicita universidades/postgrado.
