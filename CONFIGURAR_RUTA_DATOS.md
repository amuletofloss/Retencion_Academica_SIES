# Configurar `Ruta datos`

Power Query necesita una ruta absoluta para cargar `Seguimiento`, `Programas`, `Cohortes` y `Horizontes`. La copia pública conserva un marcador portable para no publicar la ruta personal del autor.

## Configuración automática recomendada

Abra PowerShell o una terminal en la carpeta del repositorio y ejecute:

```powershell
python scripts/configurar_ruta_datos.py
```

El comando detecta la carpeta `datos` incluida, valida los archivos requeridos y modifica únicamente el parámetro `Ruta datos` del modelo semántico. Después abra `Retencion_Academica_SIES.pbip` y seleccione **Actualizar**.

Si Power BI estaba abierto, ciérrelo antes de ejecutar el comando y vuelva a abrirlo después.

## Usar otra carpeta

Entregue una ruta absoluta como argumento:

```powershell
python scripts/configurar_ruta_datos.py "D:\datos_sies"
```

La carpeta debe contener:

- `programas.csv`;
- `cohortes.csv`;
- `horizontes.csv`;
- al menos un archivo `seguimiento_*.csv.gz`.

## Configuración manual en Power BI

1. Abra el PBIP.
2. Vaya a **Transformar datos > Administrar parámetros**.
3. Seleccione `Ruta datos`.
4. Escriba la ruta absoluta de la carpeta `datos` de su copia.
5. Aplique los cambios y ejecute **Actualizar**.

## Solución de errores

Si aparece “La ruta de acceso debe ser una ruta absoluta válida” en cualquiera de las cuatro consultas, el marcador aún no fue configurado o el proyecto fue movido. Cierre Power BI, vuelva a ejecutar el configurador y compruebe que la carpeta indicada exista.

Para mostrar la ruta activa desde PowerShell:

```powershell
Get-Content Retencion_Academica_SIES.SemanticModel/definition/expressions.tmdl | Select-Object -First 1
```
