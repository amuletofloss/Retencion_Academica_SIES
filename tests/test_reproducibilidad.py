import csv
import gzip
import hashlib
import json
import re
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datos"


def connection():
    con = duckdb.connect()
    files = sorted(DATA.glob("seguimiento_*.csv.gz"))
    values = ",".join("'" + path.as_posix().replace("'", "''") + "'" for path in files)
    con.execute(
        f"CREATE VIEW seguimiento AS SELECT * FROM read_csv([{values}], "
        "delim=';', header=true, union_by_name=true, all_varchar=false)"
    )
    con.execute(
        f"CREATE VIEW programas AS SELECT * FROM read_csv('{(DATA/'programas.csv').as_posix()}', "
        "delim=';', header=true, all_varchar=false)"
    )
    return con


def test_entrega_tiene_un_solo_pbip_y_siete_paginas():
    assert [path.name for path in ROOT.glob("*.pbip")] == ["Retencion_Academica_SIES.pbip"]
    assert (ROOT / "AUDITORIA_MODELO_SEMANTICO.md").exists()
    pages = json.loads(
        (ROOT / "Retencion_Academica_SIES.Report/definition/pages/pages.json").read_text(encoding="utf-8")
    )
    assert len(pages["pageOrder"]) == 7
    names = []
    for page_id in pages["pageOrder"]:
        payload = json.loads(
            (ROOT / f"Retencion_Academica_SIES.Report/definition/pages/{page_id}/page.json").read_text(encoding="utf-8")
        )
        names.append(payload["displayName"])
    assert "ECS" in names
    assert (ROOT / "TABLA_MATRICULA_PRIMER_ANO_IPLACEX_V2.pdf").stat().st_size > 5_000


def test_json_y_limite_github():
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".pbi" in path.parts:
            continue
        assert path.stat().st_size < 100 * 1024 * 1024, path
        if path.suffix in {".json", ".pbip", ".pbir", ".pbism"} or path.name == ".platform":
            json.loads(path.read_text(encoding="utf-8-sig"))


def test_mrun_esta_en_cada_csv_de_hechos_y_no_hay_columna_rut():
    files = sorted(DATA.glob("seguimiento_*.csv.gz"))
    assert len(files) == 15
    for path in files:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            columns = handle.readline().strip().split(";")
        assert "MRUN" in columns
        assert "RUT" not in columns


def test_fuentes_oficiales_y_cobertura():
    manifest = json.loads((DATA / "fuentes.json").read_text(encoding="utf-8"))
    assert len(manifest["archivos"]) == 29
    matricula = [row for row in manifest["archivos"] if row["fuente"] == "matricula"]
    titulados = [row for row in manifest["archivos"] if row["fuente"] == "titulados"]
    assert [row["anio"] for row in matricula] == list(range(2011, 2026))
    assert [row["anio"] for row in titulados] == list(range(2011, 2025))
    assert all(len(row["sha256"]) == 64 and row["archivo_oficial"].endswith(".csv") for row in manifest["archivos"])
    hashes = (DATA / "archivos_analiticos.sha256").read_text(encoding="utf-8").splitlines()
    assert len(hashes) == 18
    for line in hashes:
        expected, name = line.split(maxsplit=1)
        actual = hashlib.sha256((DATA / name).read_bytes()).hexdigest().upper()
        assert actual == expected.upper(), name


def test_unicidad_anidamiento_y_resultado_mas_reciente():
    con = connection()
    assert con.execute(
        "SELECT count(*)-count(DISTINCT concat_ws('|',TrayectoriaID,AnioObservado)) FROM seguimiento"
    ).fetchone()[0] == 0
    assert con.execute("SELECT count(*) FROM seguimiento WHERE MRUN IS NULL OR trim(MRUN::VARCHAR)='' ").fetchone()[0] == 0
    latest = con.execute(
        """
        SELECT count(DISTINCT TrayectoriaID),
          count(DISTINCT CASE WHEN EnCarrera=1 THEN TrayectoriaID END),
          count(DISTINCT CASE WHEN EnInstitucion=1 THEN TrayectoriaID END),
          count(DISTINCT CASE WHEN EnEducacionSuperior=1 THEN TrayectoriaID END)
        FROM seguimiento WHERE Cohorte=2024 AND AnioDesdeIngreso=2
        """
    ).fetchone()
    assert latest == (41056, 26470, 27111, 29383)
    assert latest[1] <= latest[2] <= latest[3] <= latest[0]
    con.close()


def test_resultados_control_concilian_el_total_de_trayectorias():
    con = duckdb.connect()
    control = (DATA / "resultados_control.csv").as_posix()
    row = con.execute(
        f"""
        SELECT sum(BaseTrayectorias),sum(RetenidosCarrera),sum(RetenidosInstitucion),
          sum(RetenidosEducacionSuperior)
        FROM read_csv('{control}',delim=';',header=true)
        WHERE Cohorte=2024 AND AnioDesdeIngreso=2
        """
    ).fetchone()
    assert row == (41056, 26470, 27111, 29383)


def test_ecs_usa_codigos_171_y_426_y_no_fusiona_instituciones():
    con = connection()
    ids = con.execute("SELECT DISTINCT InstitucionID FROM programas WHERE GrupoECS='ECS' ORDER BY 1").fetchall()
    assert ids == [(171,), (426,)] or ids == [("171",), ("426",)]
    latest = con.execute(
        """
        SELECT count(DISTINCT s.TrayectoriaID),
          count(DISTINCT CASE WHEN s.EnCarrera=1 THEN s.TrayectoriaID END),
          count(DISTINCT CASE WHEN s.EnInstitucion=1 THEN s.TrayectoriaID END),
          count(DISTINCT CASE WHEN s.EnEducacionSuperior=1 THEN s.TrayectoriaID END)
        FROM seguimiento s JOIN programas p USING(ProgramaID)
        WHERE s.Cohorte=2024 AND s.AnioDesdeIngreso=2 AND p.GrupoECS='ECS'
        """
    ).fetchone()
    assert latest == (1697, 1137, 1155, 1266)
    con.close()


def test_modelo_publico_no_contiene_ruta_personal():
    definition = ROOT / "Retencion_Academica_SIES.SemanticModel/definition"
    text = "\n".join(path.read_text(encoding="utf-8") for path in definition.rglob("*.tmdl"))
    assert "DISTINCTCOUNT('Seguimiento'[TrayectoriaID])" in text
    assert "DISTINCTCOUNT('Seguimiento'[MRUN])" in text
    expression = (definition / "expressions.tmdl").read_text(encoding="utf-8")
    match = re.search(r'^expression \'Ruta datos\' = "([^"]+)"', expression)
    assert match
    assert match.group(1) == "__RUTA_DATOS_ABSOLUTA__"
    assert "C:" + "/Users/" not in expression
    assert "C:" + "\\Users\\" not in expression
    assert "HASONEVALUE('Cohortes'[Cohorte])" in text
    assert "HASONEVALUE('Horizontes'[AnioDesdeIngreso])" in text
    assert "COALESCE(SELECTEDVALUE" not in text
    assert "measure 'Estado seleccion'" in text


def test_visuales_referencian_campos_existentes_y_estan_dentro_del_lienzo():
    table_dir = ROOT / "Retencion_Academica_SIES.SemanticModel/definition/tables"
    catalog = {}
    for path in table_dir.glob("*.tmdl"):
        source = path.read_text(encoding="utf-8")
        table_match = re.search(r"^table '?([^'\n]+)'?$", source, re.MULTILINE)
        assert table_match, path
        columns = re.findall(r"^\s*column\s+(?:'([^']+)'|([^\n]+?))\s*$", source, re.MULTILINE)
        measures = re.findall(r"^\s*measure\s+(?:'([^']+)'|([^=\n]+?))\s*=", source, re.MULTILINE)
        catalog[table_match.group(1)] = {
            "columns": {quoted or plain.strip() for quoted, plain in columns},
            "measures": {quoted or plain.strip() for quoted, plain in measures},
        }

    def walk(node):
        if isinstance(node, dict):
            column_node = node.get("Column")
            if column_node and column_node.get("Expression", {}).get("SourceRef", {}).get("Entity"):
                entity = column_node["Expression"]["SourceRef"]["Entity"]
                assert column_node["Property"] in catalog[entity]["columns"]
            measure_node = node.get("Measure")
            if measure_node and measure_node.get("Expression", {}).get("SourceRef", {}).get("Entity"):
                entity = measure_node["Expression"]["SourceRef"]["Entity"]
                assert measure_node["Property"] in catalog[entity]["measures"]
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    visuals = ROOT / "Retencion_Academica_SIES.Report/definition/pages"
    paths = list(visuals.glob("*/visuals/*/visual.json"))
    assert len(paths) == 73
    names = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        names.append(payload["name"])
        position = payload["position"]
        assert position["x"] >= 0 and position["y"] >= 0
        assert position["x"] + position["width"] <= 1600
        assert position["y"] + position["height"] <= 900
        assert payload["visual"].get("visualContainerObjects", {}).get("general")
        walk(payload)
    assert len(names) == len(set(names))


def test_segmentadores_exigen_una_cohorte_y_un_horizonte():
    pages = ROOT / "Retencion_Academica_SIES.Report/definition/pages"
    strict = []
    defaults = {"Cohortes": 0, "Horizontes": 0}
    slicers = 0
    for page in pages.iterdir():
        if not page.is_dir():
            continue
        page_name = json.loads((page / "page.json").read_text(encoding="utf-8"))["displayName"]
        for path in (page / "visuals").glob("*/visual.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            visual = payload["visual"]
            if visual.get("visualType") != "slicer":
                continue
            slicers += 1
            projection = visual["query"]["queryState"]["Values"]["projections"][0]["field"]["Column"]
            entity = projection["Expression"]["SourceRef"]["Entity"]
            if entity not in defaults:
                continue
            single = visual["objects"]["selection"][0]["properties"]["singleSelect"]["expr"]["Literal"]["Value"]
            assert single == "true"
            strict.append((page_name, entity))
            if "general" in visual["objects"]:
                defaults[entity] += 1
    assert slicers == 24
    assert len(strict) == 12
    assert defaults == {"Cohortes": 5, "Horizontes": 6}


def test_procedencia_iplacex_y_evidencia_auditada():
    con = duckdb.connect()
    source = (DATA / "iplacex_procedencia_cohortes.csv").as_posix()
    all_period = con.execute(
        f"""SELECT sum(TotalTrayectorias),sum(SinMatriculaPrevia),sum(ConMatriculaPrevia),
        sum(AntecedenteOtraIES),sum(AntecedenteOnlineOtraIES)
        FROM read_csv('{source}',delim=';',header=true)"""
    ).fetchone()
    recent = con.execute(
        f"""SELECT sum(TotalTrayectorias),sum(AntecedenteOtraIES),sum(AntecedenteOnlineOtraIES)
        FROM read_csv('{source}',delim=';',header=true) WHERE Cohorte IN (2024,2025)"""
    ).fetchone()
    assert all_period == (61905, 29751, 32154, 31448, 6618)
    assert recent == (27874, 15664, 3469)
    summary = json.loads((ROOT / "auditoria/evidencia/resumen_auditoria.json").read_text(encoding="utf-8"))
    assert summary["audit_version"] == "3.1.0"
    assert summary["controls"] == summary["passed"] == 4955
    assert summary["failed"] == 0
    assert summary["valid_cohort_horizon_cells"] == 120


def test_inventario_repositorio_concilia_archivos_y_hashes():
    inventory = ROOT / "auditoria/evidencia/inventario_repositorio.csv"
    with inventory.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter=";"))
    indexed = {row["ruta"] for row in rows}
    assert "Retencion_Academica_SIES.pbip" in indexed
    assert "TABLA_MATRICULA_PRIMER_ANO_IPLACEX_V2.pdf" in indexed
    assert "datos/iplacex_procedencia_cohortes.csv" in indexed
    for row in rows:
        path = ROOT / row["ruta"]
        assert path.is_file(), row["ruta"]
        data = path.read_bytes()
        assert len(data) == int(row["bytes"]), row["ruta"]
        assert hashlib.sha256(data).hexdigest().upper() == row["sha256"], row["ruta"]
    summary = json.loads((ROOT / "auditoria/evidencia/inventario_repositorio.json").read_text(encoding="utf-8"))
    assert summary["files"] == len(rows)
    assert summary["files_over_100_mib"] == 0
