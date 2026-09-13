"""Auditoría numérica reproducible del PBIP.

Compara la tabla longitudinal con los controles materializados, verifica las
120 celdas cohorte-horizonte y demuestra que cada dimensión usada por el
reporte reconcilia con el total correspondiente.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DIMENSIONS = [
    "TipoInstitucion",
    "Institucion",
    "Carrera",
    "Nivel",
    "Area",
    "ModalidadOrigen",
    "JornadaOrigen",
    "AmbitoFlexible",
    "GrupoECS",
]
METRICS = ["Base", "Carrera", "Institucion", "EducacionSuperior"]


@dataclass
class Evidence:
    control_id: str
    layer: str
    context: str
    metric: str
    expected: str
    actual: str
    difference: str
    tolerance: str
    status: str
    source: str


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def add(rows: list[Evidence], control_id: str, layer: str, context: str, metric: str, expected: int | float | str, actual: int | float | str, tolerance: int | float, source: str) -> None:
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        difference = actual - expected
        passed = abs(difference) <= tolerance
    else:
        difference = "0" if actual == expected else "1"
        passed = actual == expected
    rows.append(Evidence(control_id, layer, context, metric, str(expected), str(actual), str(difference), str(tolerance), "PASS" if passed else "FAIL", source))


def connection(data: Path) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("SET enable_progress_bar=false")
    def literal(path: Path) -> str:
        return "'" + path.as_posix().replace("'", "''") + "'"

    fact_files = ",".join(literal(path) for path in sorted(data.glob("seguimiento_*.csv.gz")))
    con.execute(
        f"CREATE VIEW seguimiento AS SELECT * FROM read_csv([{fact_files}],delim=';',header=true,union_by_name=true,all_varchar=false)"
    )
    con.execute(f"CREATE VIEW programas AS SELECT * FROM read_csv({literal(data / 'programas.csv')},delim=';',header=true,all_varchar=false)")
    con.execute(f"CREATE VIEW control AS SELECT * FROM read_csv({literal(data / 'resultados_control.csv')},delim=';',header=true,all_varchar=false)")
    con.execute(f"CREATE VIEW iplacex AS SELECT * FROM read_csv({literal(data / 'iplacex_procedencia_cohortes.csv')},delim=';',header=true,all_varchar=false)")
    return con


def audit(data: Path) -> tuple[list[Evidence], dict]:
    rows: list[Evidence] = []
    con = connection(data)
    actual_cells = con.execute("SELECT count(*) FROM (SELECT DISTINCT Cohorte,AnioDesdeIngreso FROM seguimiento)").fetchone()[0]
    add(rows, "STRUCT-001", "datos", "global", "celdas_cohorte_horizonte", 120, actual_cells, 0, "seguimiento_*.csv.gz")

    base_query = """
        SELECT Cohorte,AnioDesdeIngreso,
          count(DISTINCT TrayectoriaID)::BIGINT AS Base,
          count(DISTINCT CASE WHEN EnCarrera=1 THEN TrayectoriaID END)::BIGINT AS Carrera,
          count(DISTINCT CASE WHEN EnInstitucion=1 THEN TrayectoriaID END)::BIGINT AS Institucion,
          count(DISTINCT CASE WHEN EnEducacionSuperior=1 THEN TrayectoriaID END)::BIGINT AS EducacionSuperior
        FROM seguimiento GROUP BY Cohorte,AnioDesdeIngreso ORDER BY 1,2
    """
    control_query = """
        SELECT Cohorte,AnioDesdeIngreso,
          sum(BaseTrayectorias)::BIGINT AS Base,
          sum(RetenidosCarrera)::BIGINT AS Carrera,
          sum(RetenidosInstitucion)::BIGINT AS Institucion,
          sum(RetenidosEducacionSuperior)::BIGINT AS EducacionSuperior
        FROM control GROUP BY Cohorte,AnioDesdeIngreso ORDER BY 1,2
    """
    actual = {(row[0], row[1]): row[2:] for row in con.execute(base_query).fetchall()}
    expected = {(row[0], row[1]): row[2:] for row in con.execute(control_query).fetchall()}
    for context in sorted(actual):
        for index, metric in enumerate(METRICS):
            add(rows, f"CELL-{context[0]}-{context[1]}-{metric}", "medidas", f"cohorte={context[0]};horizonte={context[1]}", metric, expected[context][index], actual[context][index], 0, "resultados_control.csv vs seguimiento")
        base, career, institution, higher_ed = actual[context]
        add(rows, f"ORDER-{context[0]}-{context[1]}", "invariantes", f"cohorte={context[0]};horizonte={context[1]}", "Carrera<=Institucion<=EducacionSuperior<=Base", 1, int(career <= institution <= higher_ed <= base), 0, "seguimiento")

    for dimension in DIMENSIONS:
        grouped = con.execute(
            f"""
            SELECT Cohorte,AnioDesdeIngreso,
              sum(NBase),sum(NCarrera),sum(NInstitucion),sum(NEducacionSuperior)
            FROM (
              SELECT s.Cohorte,s.AnioDesdeIngreso,p.{dimension},
                count(DISTINCT s.TrayectoriaID) AS NBase,
                count(DISTINCT CASE WHEN s.EnCarrera=1 THEN s.TrayectoriaID END) AS NCarrera,
                count(DISTINCT CASE WHEN s.EnInstitucion=1 THEN s.TrayectoriaID END) AS NInstitucion,
                count(DISTINCT CASE WHEN s.EnEducacionSuperior=1 THEN s.TrayectoriaID END) AS NEducacionSuperior
              FROM seguimiento s JOIN programas p USING(ProgramaID)
              GROUP BY s.Cohorte,s.AnioDesdeIngreso,p.{dimension}
            ) GROUP BY Cohorte,AnioDesdeIngreso ORDER BY 1,2
            """
        ).fetchall()
        for cohort, horizon, *values in grouped:
            for index, metric in enumerate(METRICS):
                add(rows, f"DIM-{dimension}-{cohort}-{horizon}-{metric}", "dimensiones", f"dimension={dimension};cohorte={cohort};horizonte={horizon}", metric, actual[(cohort, horizon)][index], int(values[index]), 0, "seguimiento JOIN programas")

    latest = actual[(2024, 2)]
    for metric, value, certified in zip(METRICS, latest, (41056, 26470, 27111, 29383), strict=True):
        add(rows, f"CERT-NACIONAL-{metric}", "certificados", "cohorte=2024;horizonte=2", metric, certified, value, 0, "control ejecutivo 3.0.0")
    ecs = con.execute(
        """
        SELECT count(DISTINCT s.TrayectoriaID),
          count(DISTINCT CASE WHEN s.EnCarrera=1 THEN s.TrayectoriaID END),
          count(DISTINCT CASE WHEN s.EnInstitucion=1 THEN s.TrayectoriaID END),
          count(DISTINCT CASE WHEN s.EnEducacionSuperior=1 THEN s.TrayectoriaID END)
        FROM seguimiento s JOIN programas p USING(ProgramaID)
        WHERE s.Cohorte=2024 AND s.AnioDesdeIngreso=2 AND p.GrupoECS='ECS'
        """
    ).fetchone()
    for metric, value, certified in zip(METRICS, ecs, (1697, 1137, 1155, 1266), strict=True):
        add(rows, f"CERT-ECS-{metric}", "certificados", "grupo=ECS;cohorte=2024;horizonte=2", metric, certified, value, 0, "control ejecutivo 3.0.0")

    ip_totals = con.execute(
        """
        SELECT sum(TotalTrayectorias),sum(SinMatriculaPrevia),sum(ConMatriculaPrevia),
          sum(AntecedenteOtraIES),sum(AntecedenteOnlineOtraIES)
        FROM iplacex
        """
    ).fetchone()
    for metric, value, certified in zip(
        ("TotalTrayectorias", "SinMatriculaPrevia", "ConMatriculaPrevia", "AntecedenteOtraIES", "AntecedenteOnlineOtraIES"),
        ip_totals,
        (61905, 29751, 32154, 31448, 6618),
        strict=True,
    ):
        add(rows, f"CERT-IPLACEX-{metric}", "certificados", "cohortes=2012-2025", metric, certified, value, 0, "iplacex_procedencia_cohortes.csv")
    ip_recent = con.execute("SELECT sum(TotalTrayectorias),sum(AntecedenteOtraIES),sum(AntecedenteOnlineOtraIES) FROM iplacex WHERE Cohorte IN (2024,2025)").fetchone()
    for metric, value, certified in zip(("TotalTrayectorias", "AntecedenteOtraIES", "AntecedenteOnlineOtraIES"), ip_recent, (27874, 15664, 3469), strict=True):
        add(rows, f"CERT-IPLACEX-RECIENTE-{metric}", "certificados", "cohortes=2024-2025", metric, certified, value, 0, "iplacex_procedencia_cohortes.csv")

    hashes_path = data / "archivos_analiticos.sha256"
    expected_hashes = {line.split()[1]: line.split()[0] for line in hashes_path.read_text(encoding="utf-8").splitlines()}
    for name, expected_hash in sorted(expected_hashes.items()):
        actual_hash = sha256(data / name)
        add(rows, f"HASH-{name}", "integridad", "global", name, expected_hash, actual_hash, 0, "archivos_analiticos.sha256")

    summary = {
        "audit_version": "3.1.0",
        "data_cutoff": "matrícula 2025 / titulados 2024",
        "data_directory": data.name,
        "controls": len(rows),
        "passed": sum(row.status == "PASS" for row in rows),
        "failed": sum(row.status == "FAIL" for row in rows),
        "valid_cohort_horizon_cells": actual_cells,
        "dimensions_reconciled": DIMENSIONS,
        "source_hash": hashlib.sha256("\n".join(f"{row.control_id}|{row.expected}|{row.actual}|{row.status}" for row in rows).encode()).hexdigest().upper(),
    }
    con.close()
    return rows, summary


def write_evidence(rows: list[Evidence], summary: dict, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    csv_path = output / "evidencia_numerica.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0])))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)
    (output / "resumen_auditoria.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "datos")
    parser.add_argument("--output", type=Path, default=ROOT / "auditoria/evidencia")
    args = parser.parse_args()
    evidence, summary = audit(args.data.resolve())
    write_evidence(evidence, summary, args.output.resolve())
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
