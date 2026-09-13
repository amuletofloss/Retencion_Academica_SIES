# 01 · Estructura del PBIP

## Árbol real

```text
retencion-academica-sies/
├── Retencion_Academica_SIES.pbip
├── Retencion_Academica_SIES.Report/
│   ├── definition.pbir
│   └── definition/
│       ├── report.json
│       ├── version.json
│       └── pages/
│           ├── pages.json
│           └── <pagina>/
│               ├── page.json
│               └── visuals/<visual>/visual.json
├── Retencion_Academica_SIES.SemanticModel/
│   ├── definition.pbism
│   └── definition/
│       ├── database.tmdl
│       ├── expressions.tmdl
│       ├── model.tmdl
│       ├── relationships.tmdl
│       ├── cultures/es-CL.tmdl
│       └── tables/*.tmdl
├── datos/
├── scripts/
├── tests/
├── docs/
└── .github/
```

## Función de cada componente

| Ruta | Función | ¿Editar manualmente? |
|---|---|---|
| `*.pbip` | Descriptor que enlaza reporte y modelo | Solo con conocimiento del esquema |
| `*.Report/definition.pbir` | Referencia del reporte al modelo semántico | Preferir Desktop |
| `*.Report/definition/` | Definición PBIR: páginas, visuales, tema y configuración | Solo cambios controlados y validados |
| `*.SemanticModel/definition.pbism` | Descriptor de la definición semántica | Preferir herramientas compatibles |
| `database.tmdl` | Propiedades de base del modelo | Controlado |
| `model.tmdl` | Modelo, cultura y referencias de objetos | Controlado |
| `expressions.tmdl` | Expresiones compartidas y parámetros M | Sí, con prueba de actualización |
| `relationships.tmdl` | Relaciones del modelo | Sí, con prueba de cardinalidad y filtro |
| `tables/*.tmdl` | Tablas, columnas, medidas y particiones | Sí, con auditoría DAX/M |
| `cultures/*.tmdl` | Metadatos de cultura y traducción | Sí, cuidando sincronización |
| `datos/` | Entradas analíticas reproducibles | Solo mediante proceso trazable |
| `scripts/` | Materialización y generación determinista | Sí, con tests |
| `tests/` | Contratos de reproducibilidad | Sí; no reducir cobertura sin justificación |
| `.github/` | Gobierno y automatización | Revisión independiente obligatoria |

El formato TMDL representa objetos tabulares en texto y utiliza indentación significativa. Referencia: [TMDL overview](https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview), consultada el 2026-09-11. La estructura PBIR del reporte se describe en [Power BI enhanced report format](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report), consultada el 2026-09-11.

## Archivos presentes y ausentes

| Objeto esperado | Estado | Evidencia |
|---|---|---|
| `.pbip` | [OK] uno | `Retencion_Academica_SIES.pbip` |
| `.Report` | [OK] | `Retencion_Academica_SIES.Report/` |
| `.SemanticModel` | [OK] | `Retencion_Academica_SIES.SemanticModel/` |
| tablas TMDL | [OK] cuatro | `definition/tables/` |
| relaciones TMDL | [OK] tres | `definition/relationships.tmdl` |
| expresiones M | [OK] | `definition/expressions.tmdl` y particiones |
| cultura | [OK] `es-CL` | `definition/cultures/es-CL.tmdl` |
| roles | [NO APLICA] | no existe `definition/roles/` |
| calculation groups | [NO APLICA] | no existe `definition/calculationGroups/` |
| `.platform` | [FALTA] no versionado | se generará o configurará al integrar con Fabric/Git, si corresponde |

La ausencia de `.platform` no impide abrir localmente el PBIP; sí deja pendiente verificar metadatos específicos de Fabric cuando se configure integración Git.

## Ejemplo TMDL mínimo

```tmdl
table Cohortes

    column 'Cohorte'
        dataType: int64
        sourceColumn: Cohorte

    partition Cohortes = m
        mode: import
        source =
            let
                Fuente = Csv.Document(...)
            in
                Fuente
```

El ejemplo ilustra la forma, pero la definición real en `definition/tables/Cohortes.tmdl` es la autoridad.

## Archivos generados y conflictos

- No versionar `.pbi/`, cachés `.abf`, locks o configuración local.
- No resolver un conflicto TMDL aceptando automáticamente un archivo completo: revisar por objeto y volver a abrir el PBIP.
- Los identificadores de página/visual deben ser únicos. El generador actual tiene un riesgo conocido de colisiones en tres segmentadores.
- Si Desktop reescribe masivamente archivos, separar el cambio funcional del cambio de formato cuando sea posible.
- Tras un merge, ejecutar tests y una apertura/actualización en Desktop.

## Qué debe versionarse

Se versionan el `.pbip`, las carpetas `.Report` y `.SemanticModel`, los datos analíticos necesarios, scripts, pruebas, documentos y automatización. No se versionan fuentes brutas descargadas, estado local, secretos ni resultados temporales.

Git LFS no está configurado porque ningún archivo actual supera 100 MiB. La política y los límites deben revisarse antes de agregar binarios grandes; GitHub explica el mecanismo en [About Git Large File Storage](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage).
