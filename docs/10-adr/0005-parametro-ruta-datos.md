# ADR-0005 · Parámetro local para la ruta de datos

- Estado: Aceptado
- Fecha: 2026-09-11
- Decisores: `responsables del modelo`, `responsables de DevOps`

## Contexto

Power Query necesita localizar `datos/`, pero cada clon reside en una ruta distinta. Versionar una ruta absoluta personal rompe portabilidad y expone información del equipo local.

## Opciones consideradas

1. **Ruta absoluta versionada:** funciona solo para un usuario.
2. **Parámetro `Ruta datos`:** cada usuario configura su clon sin cambiar la lógica.
3. **Fuente remota obligatoria:** requiere infraestructura, credenciales y conectividad no disponibles.

## Decisión

Definir `Ruta datos` como parámetro requerido y materializarlo con una ruta absoluta válida. `configurar_ruta_datos.py` cambia sólo esa expresión; el generador completo usa la carpeta `datos` del proyecto y admite `PBIP_DATA_PATH`.

## Consecuencias

### Positivas

- Una sola expresión controla cuatro particiones.
- El PBIP generado queda listo para actualizar en la copia donde se construye.

### Negativas y riesgos

- La ruta debe regenerarse o cambiarse al mover el proyecto.
- La definición generada refleja una ruta específica del entorno.
- El despliegue requiere reglas o parametrización por entorno.

## Validación

- `expressions.tmdl` contiene una ruta absoluta existente.
- La ruta termina en la carpeta analítica `datos`.
- Las cuatro particiones consumen exclusivamente `Ruta datos`.

## Revisión

Sustituir mediante otro ADR si se implementa almacenamiento administrado o parametrización CD por entorno.
