# Publicación en GitHub

Esta carpeta es la distribución pública y portable del proyecto. No contiene repositorio Git interno, fuentes brutas, cachés de Power BI ni rutas personales.

## Publicar

1. Cree en GitHub un repositorio vacío y público, sin README ni licencia automática.
2. Abra una terminal en esta carpeta y ejecute:

```powershell
git init -b main
git add .
git commit -m "feat: publica PBIP de retención académica SIES"
$repoUrl = Read-Host "URL HTTPS del repositorio GitHub"
git remote add origin $repoUrl
git push -u origin main
```

3. Active protección de `main`, ejecución obligatoria del workflow y **Private vulnerability reporting**.

## Abrir después de clonar

```powershell
python scripts/configurar_ruta_datos.py
```

Luego abra `Retencion_Academica_SIES.pbip` y actualice. El configurador valida `programas.csv`, `cohortes.csv`, `horizontes.csv` y los archivos `seguimiento_*.csv.gz` antes de escribir la ruta absoluta local.

## Datos

La distribución incluye datos derivados de fuentes abiertas SIES. `MRUN` es un identificador enmascarado, permanece oculto en el modelo/reporte y no debe emplearse para reidentificación.
