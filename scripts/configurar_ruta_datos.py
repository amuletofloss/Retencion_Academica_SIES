"""Configura Ruta datos sin regenerar ni reemplazar el resto del PBIP."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPRESSIONS = ROOT / "Retencion_Academica_SIES.SemanticModel/definition/expressions.tmdl"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ruta", nargs="?", type=Path, default=ROOT / "datos")
    args = parser.parse_args()
    data_path = args.ruta.expanduser().resolve()
    if not data_path.is_dir():
        raise SystemExit(f"La carpeta no existe: {data_path}")
    required = ["programas.csv", "cohortes.csv", "horizontes.csv"]
    missing = [name for name in required if not (data_path / name).is_file()]
    if not list(data_path.glob("seguimiento_*.csv.gz")):
        missing.append("seguimiento_*.csv.gz")
    if missing:
        raise SystemExit("Faltan archivos requeridos: " + ", ".join(missing))

    source = EXPRESSIONS.read_text(encoding="utf-8")
    escaped = str(data_path).replace('"', '""')
    updated, replacements = re.subn(
        r'(?m)^(expression \'Ruta datos\'\s*=\s*")[^"]*("\s+meta\s+\[)',
        lambda match: match.group(1) + escaped + match.group(2),
        source,
        count=1,
    )
    if replacements != 1:
        raise SystemExit("No se encontró una única expresión Ruta datos")
    EXPRESSIONS.write_text(updated, encoding="utf-8")
    print(data_path)


if __name__ == "__main__":
    main()
