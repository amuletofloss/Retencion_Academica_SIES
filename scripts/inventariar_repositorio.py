"""Genera un inventario determinista de los archivos canónicos del repositorio."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "auditoria/evidencia/inventario_repositorio.csv"
SUMMARY = ROOT / "auditoria/evidencia/inventario_repositorio.json"
EXCLUDED_DIRS = {".git", ".pbi", ".pytest_cache", "__pycache__", ".venv", "github", "node_modules"}
EXCLUDED_NAMES = {OUTPUT.name, SUMMARY.name}


def role(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    if relative.startswith("datos/"):
        return "datos_analiticos"
    if relative.startswith("Retencion_Academica_SIES.Report/"):
        return "reporte_pbip"
    if relative.startswith("Retencion_Academica_SIES.SemanticModel/"):
        return "modelo_semantico"
    if relative.startswith("scripts/"):
        return "codigo_reproducible"
    if relative.startswith("tests/") or relative.startswith(".github/"):
        return "calidad_y_gobierno"
    if relative.startswith("auditoria/"):
        return "evidencia_auditoria"
    if relative.startswith("docs/") or path.suffix.lower() in {".md", ".pdf"}:
        return "documentacion_entregable"
    return "configuracion_proyecto"


def included(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        return False
    if path.name in EXCLUDED_NAMES or path.name.startswith("powerbi_"):
        return False
    return True


def main() -> None:
    rows = []
    for path in sorted((path for path in ROOT.rglob("*") if path.is_file() and included(path)), key=lambda item: item.relative_to(ROOT).as_posix()):
        data = path.read_bytes()
        rows.append(
            {
                "ruta": path.relative_to(ROOT).as_posix(),
                "rol": role(path),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest().upper(),
            }
        )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["ruta", "rol", "bytes", "sha256"], delimiter=";", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "inventory_version": "1.0.0",
        "project_version": "3.1.0",
        "files": len(rows),
        "bytes": sum(row["bytes"] for row in rows),
        "largest_file_bytes": max(row["bytes"] for row in rows),
        "files_over_100_mib": sum(row["bytes"] >= 100 * 1024 * 1024 for row in rows),
        "roles": {name: sum(row["rol"] == name for row in rows) for name in sorted({row["rol"] for row in rows})},
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
