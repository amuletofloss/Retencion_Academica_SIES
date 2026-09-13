"""Construye los CSV analíticos reproducibles del PBIP de retención SIES.

La llave MRUN se conserva como texto: es el identificador enmascarado que SIES
publica en sus bases abiertas. El proceso no busca ni utiliza una columna RUT.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import duckdb


MATRICULA_YEARS = list(range(2011, 2026))
TITULADOS_YEARS = list(range(2011, 2025))
ECS_IDS = ("171", "426")


def sql_literal(value: Path | str) -> str:
    return "'" + str(value).replace("\\", "/").replace("'", "''") + "'"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def discover_sources(source_root: Path, source: str, years: list[int]) -> list[Path]:
    silver = source_root / "silver" / f"source={source}"
    if silver.exists():
        files = sorted(silver.glob("year=*/data.parquet"))
    else:
        token = "Matricula" if source == "matricula" else "Titulados"
        files = sorted(source_root.glob(f"{token}-Ed-Superior-*/*.csv"))
    found = {int(re.search(r"(20\d{2})", str(path.parent)).group(1)): path for path in files}
    missing = sorted(set(years) - set(found))
    if missing:
        raise FileNotFoundError(f"Faltan archivos de {source}: {missing}")
    return [found[year] for year in years]


def create_source_view(con: duckdb.DuckDBPyConnection, name: str, files: list[Path]) -> None:
    if files[0].suffix == ".parquet":
        values = ",".join(sql_literal(path.resolve()) for path in files)
        con.execute(
            f"CREATE VIEW raw_{name} AS SELECT * FROM read_parquet([{values}], "
            "union_by_name=true, hive_partitioning=false)"
        )
        return
    selects = []
    for path in files:
        year = int(re.search(r"(20\d{2})", str(path.parent)).group(1))
        selects.append(
            f"SELECT *, {year}::INTEGER AS year FROM read_csv({sql_literal(path.resolve())}, "
            "delim=';', header=true, all_varchar=true, normalize_names=true, "
            "ignore_errors=false, sample_size=-1)"
        )
    con.execute(f"CREATE VIEW raw_{name} AS " + " UNION ALL BY NAME ".join(selects))


def build_manifest(files: dict[str, list[Path]], source_root: Path) -> dict:
    inventory = source_root / "inventory" / "source_inventory.json"
    if not inventory.exists():
        inventory = source_root.parent / "inventory" / "source_inventory.json"
    indexed: dict[tuple[str, int], dict] = {}
    if inventory.exists():
        for item in json.loads(inventory.read_text(encoding="utf-8"))["files"]:
            indexed[(item["source"], int(item["source_year"]))] = item
    rows = []
    for source, paths in files.items():
        for path in paths:
            year = int(re.search(r"(20\d{2})", str(path.parent)).group(1))
            meta = indexed.get((source, year), {})
            original = Path(meta.get("path", path))
            rows.append(
                {
                    "fuente": source,
                    "anio": year,
                    "archivo_oficial": original.name,
                    "filas": meta.get("rows"),
                    "bytes": meta.get("size_bytes", original.stat().st_size if original.exists() else None),
                    "sha256": meta.get("sha256") or file_sha256(original),
                }
            )
    return {
        "portal": "https://centroestudios.mineduc.cl/datos-abiertos/",
        "matricula": "corte anual al 30 de abril",
        "titulados": "registros informados por año",
        "archivos": rows,
    }


def materialize(source_root: Path, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    matricula = discover_sources(source_root, "matricula", MATRICULA_YEARS)
    titulados = discover_sources(source_root, "titulados", TITULADOS_YEARS)
    con = duckdb.connect()
    con.execute("SET enable_progress_bar=false")
    con.execute("SET memory_limit='6GB'")
    con.execute("SET threads=4")
    create_source_view(con, "matricula", matricula)
    create_source_view(con, "titulados", titulados)

    # La clave académica excluye modalidad, jornada y plan. Un cambio de formato
    # dentro de la misma institución/carrera no rompe la retención académica.
    career_key = "concat_ws('|', trim(cod_inst), trim(cod_carrera), lower(trim(nivel_carrera_1)))"
    valid_mrun = "mrun IS NOT NULL AND regexp_full_match(trim(mrun), '[0-9]+') AND try_cast(mrun AS HUGEINT)>0"
    flexible = "(lower(trim(modalidad)) IN ('no presencial','semipresencial') OR lower(trim(jornada))='a distancia')"
    ip_cft = "tipo_inst_1 IN ('Institutos Profesionales','Centros de Formación Técnica')"

    con.execute(
        f"""
        CREATE TEMP TABLE enrollment AS
        SELECT *, year::INTEGER AS periodo, {career_key} AS clave_carrera,
          {valid_mrun} AS mrun_valido,
          try_cast(anio_ing_carr_ori AS INTEGER) AS ingreso_origen,
          try_cast(sem_ing_carr_ori AS INTEGER) AS semestre_origen
        FROM raw_matricula
        """
    )
    con.execute(
        f"""
        CREATE TEMP TABLE candidatos AS
        SELECT * FROM enrollment
        WHERE mrun_valido AND lower(trim(nivel_global))='pregrado' AND {ip_cft} AND {flexible}
          AND lower(trim(tipo_plan_carr))='plan regular'
          AND ingreso_origen=periodo AND semestre_origen=1
          AND nullif(trim(cod_inst),'') IS NOT NULL
          AND nullif(trim(cod_carrera),'') IS NOT NULL
          AND nullif(trim(nivel_carrera_1),'') IS NOT NULL
        """
    )
    con.execute(
        """
        CREATE TEMP TABLE origenes AS
        SELECT periodo AS cohorte, trim(mrun) AS mrun, clave_carrera,
          min(trim(cod_inst)) AS cod_inst,
          min(nomb_inst) AS institucion,
          min(tipo_inst_1) AS tipo_institucion,
          min(trim(cod_carrera)) AS cod_carrera,
          min(nomb_carrera) AS carrera,
          min(nivel_carrera_1) AS nivel,
          min(area_conocimiento) AS area,
          CASE WHEN count(DISTINCT modalidad)=1 THEN min(modalidad) ELSE 'Multimodal' END AS modalidad,
          CASE WHEN count(DISTINCT jornada)=1 THEN min(jornada) ELSE 'Multijornada' END AS jornada,
          CASE
            WHEN bool_or(lower(trim(modalidad))='no presencial') AND bool_or(lower(trim(modalidad))='semipresencial') THEN 'No presencial + semipresencial'
            WHEN bool_or(lower(trim(modalidad))='no presencial') THEN 'No presencial'
            WHEN bool_or(lower(trim(modalidad))='semipresencial') THEN 'Semipresencial'
            ELSE 'Jornada a distancia'
          END AS ambito_flexible,
          count(*)::INTEGER AS registros_origen
        FROM candidatos
        GROUP BY periodo,mrun,clave_carrera
        """
    )
    con.execute(
        """
        ALTER TABLE origenes ADD COLUMN trayectoria_id VARCHAR;
        UPDATE origenes SET trayectoria_id=md5(concat_ws('|',mrun,clave_carrera,cohorte));
        ALTER TABLE origenes ADD COLUMN programa_id VARCHAR;
        UPDATE origenes SET programa_id=md5(concat_ws('|',clave_carrera,cohorte,modalidad,jornada));
        """
    )
    con.execute(
        f"""
        CREATE TEMP TABLE presencia AS
        SELECT DISTINCT periodo AS anio, trim(mrun) AS mrun, clave_carrera, trim(cod_inst) AS cod_inst,
          CASE WHEN {flexible} THEN 1 ELSE 0 END::INTEGER AS EsFlexible
        FROM enrollment WHERE mrun_valido
        """
    )
    con.execute(
        """
        CREATE TEMP TABLE titulacion AS
        SELECT trim(mrun) AS mrun,
          concat_ws('|', trim(cod_inst), trim(cod_carrera), lower(trim(nivel_carrera_1))) AS clave_carrera,
          min(COALESCE(
            year(try_strptime(replace(trim(fecha_obtencion_titulo),'-',''),'%Y%m%d')),
            year::INTEGER
          ))::INTEGER AS primer_anio_titulacion
        FROM raw_titulados
        WHERE mrun IS NOT NULL AND regexp_full_match(trim(mrun), '[0-9]+')
          AND try_cast(mrun AS HUGEINT)>0
          AND (
            (nullif(trim(nombre_titulo_obtenido),'') IS NOT NULL AND NOT regexp_matches(lower(trim(nombre_titulo_obtenido)), '^(no(\\s|$)|sin(\\s|$)|n/?a$|s/?i$|0$|-+$)'))
            OR
            (nullif(trim(nombre_grado_obtenido),'') IS NOT NULL AND NOT regexp_matches(lower(trim(nombre_grado_obtenido)), '^(no(\\s|$)|sin(\\s|$)|n/?a$|s/?i$|0$|-+$)'))
          )
        GROUP BY mrun,clave_carrera
        """
    )
    con.execute(
        """
        CREATE TEMP TABLE seguimiento AS
        SELECT o.mrun AS MRUN,o.trayectoria_id AS TrayectoriaID,o.programa_id AS ProgramaID,
          o.cohorte AS Cohorte,y.range::INTEGER AS AnioObservado,
          (y.range-o.cohorte+1)::INTEGER AS AnioDesdeIngreso,
          1::INTEGER AS Observable,
          CASE WHEN bool_or(p.clave_carrera=o.clave_carrera) THEN 1 ELSE 0 END::INTEGER AS EnCarrera,
          CASE WHEN bool_or(p.cod_inst=o.cod_inst) THEN 1 ELSE 0 END::INTEGER AS EnInstitucion,
          CASE WHEN count(p.mrun)>0 THEN 1 ELSE 0 END::INTEGER AS EnEducacionSuperior,
          CASE WHEN bool_or(p.cod_inst IN ('171','426')) THEN 1 ELSE 0 END::INTEGER AS EnECS,
          CASE WHEN o.cod_inst IN ('171','426') AND bool_or(p.cod_inst IN ('171','426') AND p.cod_inst<>o.cod_inst)
            THEN 1 ELSE 0 END::INTEGER AS MovilidadInternaECS,
          CASE WHEN t.primer_anio_titulacion<=y.range THEN 1 ELSE 0 END::INTEGER AS TituladoAcumulado
        FROM origenes o CROSS JOIN range(o.cohorte,2026) y
        LEFT JOIN presencia p ON p.mrun=o.mrun AND p.anio=y.range
        LEFT JOIN titulacion t ON t.mrun=o.mrun AND t.clave_carrera=o.clave_carrera
        GROUP BY o.mrun,o.trayectoria_id,o.programa_id,o.cohorte,y.range,o.cod_inst,t.primer_anio_titulacion
        """
    )
    con.execute(
        """
        CREATE TEMP TABLE programas AS
        SELECT programa_id AS ProgramaID,cohorte AS Cohorte,cod_inst AS InstitucionID,
          min(institucion) AS Institucion,min(tipo_institucion) AS TipoInstitucion,
          min(cod_carrera) AS CodigoCarrera,min(carrera) AS Carrera,min(nivel) AS Nivel,
          min(area) AS Area,min(modalidad) AS ModalidadOrigen,min(jornada) AS JornadaOrigen,
          min(ambito_flexible) AS AmbitoFlexible,
          CASE WHEN cod_inst IN ('171','426') THEN 'ECS' ELSE 'Resto IP+CFT' END AS GrupoECS,
          sum(registros_origen)::BIGINT AS RegistrosOrigen
        FROM origenes GROUP BY programa_id,cohorte,cod_inst
        """
    )
    # Procedencia de primer año de IPLACEX. El universo objetivo reutiliza
    # exactamente las trayectorias de origen del PBIP; la historia previa se
    # busca en toda la matrícula SIES disponible, sin restringir subsistema.
    con.execute(
        f"""
        CREATE TEMP TABLE historial_iplacex AS
        SELECT o.cohorte AS Cohorte,o.mrun AS MRUN,o.trayectoria_id AS TrayectoriaID,
          count(p.mrun)>0 AS TieneMatriculaPrevia,
          COALESCE(bool_or(p.cod_inst<>o.cod_inst),false) AS AntecedenteOtraIES,
          COALESCE(bool_or(
            p.cod_inst<>o.cod_inst AND p.EsFlexible=1
          ),false) AS AntecedenteOnlineOtraIES
        FROM origenes o
        LEFT JOIN presencia p
          ON p.mrun=o.mrun AND p.anio<o.cohorte
        WHERE o.cod_inst='152' AND o.cohorte>=2012
        GROUP BY o.cohorte,o.mrun,o.trayectoria_id,o.cod_inst
        """
    )
    con.execute(
        """
        CREATE TEMP TABLE iplacex_procedencia AS
        SELECT Cohorte,
          count(*)::BIGINT AS TotalTrayectorias,
          count(DISTINCT MRUN)::BIGINT AS PersonasUnicas,
          count(*) FILTER (WHERE NOT TieneMatriculaPrevia)::BIGINT AS SinMatriculaPrevia,
          count(*) FILTER (WHERE TieneMatriculaPrevia)::BIGINT AS ConMatriculaPrevia,
          count(*) FILTER (WHERE AntecedenteOtraIES)::BIGINT AS AntecedenteOtraIES,
          count(*) FILTER (WHERE AntecedenteOnlineOtraIES)::BIGINT AS AntecedenteOnlineOtraIES,
          count(*) FILTER (
            WHERE TieneMatriculaPrevia AND NOT AntecedenteOtraIES
          )::BIGINT AS PreviaSoloIPLACEX
        FROM historial_iplacex
        GROUP BY Cohorte
        ORDER BY Cohorte
        """
    )
    # El resultado de control replica exactamente las medidas DAX documentadas.
    con.execute(
        """
        CREATE TEMP TABLE resultados AS
        SELECT s.Cohorte,s.AnioDesdeIngreso,s.AnioObservado,p.TipoInstitucion,p.AmbitoFlexible,p.GrupoECS,
          count(DISTINCT s.TrayectoriaID)::BIGINT AS BaseTrayectorias,
          count(DISTINCT CASE WHEN s.EnCarrera=1 THEN s.TrayectoriaID END)::BIGINT AS RetenidosCarrera,
          count(DISTINCT CASE WHEN s.EnInstitucion=1 THEN s.TrayectoriaID END)::BIGINT AS RetenidosInstitucion,
          count(DISTINCT CASE WHEN s.EnEducacionSuperior=1 THEN s.TrayectoriaID END)::BIGINT AS RetenidosEducacionSuperior,
          count(DISTINCT s.MRUN)::BIGINT AS Personas,
          count(DISTINCT CASE WHEN s.EnInstitucion=1 THEN s.MRUN END)::BIGINT AS PersonasInstitucion,
          count(DISTINCT CASE WHEN s.EnEducacionSuperior=1 THEN s.MRUN END)::BIGINT AS PersonasEducacionSuperior
        FROM seguimiento s JOIN programas p USING(ProgramaID)
        GROUP BY ALL
        """
    )

    for old in output.glob("seguimiento_*.csv.gz"):
        old.unlink()
    for year in MATRICULA_YEARS:
        path = (output / f"seguimiento_{year}.csv.gz").resolve()
        con.execute(
            f"COPY (SELECT * FROM seguimiento WHERE Cohorte={year} ORDER BY TrayectoriaID,AnioObservado) "
            f"TO {sql_literal(path)} (FORMAT CSV, HEADER, DELIMITER ';', COMPRESSION GZIP)"
        )
    con.execute(
        f"COPY (SELECT * FROM programas ORDER BY Cohorte,Institucion,Carrera,ProgramaID) TO {sql_literal((output/'programas.csv').resolve())} "
        "(FORMAT CSV, HEADER, DELIMITER ';')"
    )
    con.execute(
        f"COPY (SELECT range::INTEGER AS Cohorte FROM range(2011,2026)) TO {sql_literal((output/'cohortes.csv').resolve())} "
        "(FORMAT CSV, HEADER, DELIMITER ';')"
    )
    con.execute(
        f"COPY (SELECT range::INTEGER AS AnioDesdeIngreso, CASE WHEN range=1 THEN 'Ingreso' ELSE 'Seguimiento '||(range-1) END AS Etiqueta FROM range(1,16)) "
        f"TO {sql_literal((output/'horizontes.csv').resolve())} (FORMAT CSV, HEADER, DELIMITER ';')"
    )
    con.execute(
        f"COPY (SELECT * FROM resultados ORDER BY Cohorte,AnioDesdeIngreso,TipoInstitucion,AmbitoFlexible,GrupoECS) "
        f"TO {sql_literal((output/'resultados_control.csv').resolve())} (FORMAT CSV, HEADER, DELIMITER ';')"
    )
    con.execute(
        f"COPY (SELECT * FROM iplacex_procedencia ORDER BY Cohorte) "
        f"TO {sql_literal((output/'iplacex_procedencia_cohortes.csv').resolve())} "
        "(FORMAT CSV, HEADER, DELIMITER ';')"
    )

    checks = {
        "filas_seguimiento": con.execute("SELECT count(*) FROM seguimiento").fetchone()[0],
        "trayectorias": con.execute("SELECT count(*) FROM origenes").fetchone()[0],
        "personas": con.execute("SELECT count(DISTINCT mrun) FROM origenes").fetchone()[0],
        "programas_cohorte_modalidad": con.execute("SELECT count(*) FROM programas").fetchone()[0],
        "violaciones_orden": con.execute(
            "SELECT count(*) FROM resultados WHERE RetenidosCarrera>RetenidosInstitucion "
            "OR RetenidosInstitucion>RetenidosEducacionSuperior OR RetenidosEducacionSuperior>BaseTrayectorias"
        ).fetchone()[0],
        "duplicados_fact": con.execute(
            "SELECT count(*)-count(DISTINCT concat_ws('|',TrayectoriaID,AnioObservado)) FROM seguimiento"
        ).fetchone()[0],
        "mrun_nulos": con.execute("SELECT count(*) FROM seguimiento WHERE nullif(trim(MRUN),'') IS NULL").fetchone()[0],
        "celdas_cohorte_horizonte": con.execute(
            "SELECT count(*) FROM (SELECT DISTINCT Cohorte,AnioDesdeIngreso FROM seguimiento)"
        ).fetchone()[0],
        "iplacex_conciliacion": con.execute(
            "SELECT count(*) FROM iplacex_procedencia "
            "WHERE SinMatriculaPrevia+ConMatriculaPrevia<>TotalTrayectorias "
            "OR AntecedenteOnlineOtraIES>AntecedenteOtraIES "
            "OR AntecedenteOtraIES>ConMatriculaPrevia"
        ).fetchone()[0],
    }
    if (
        checks["violaciones_orden"]
        or checks["duplicados_fact"]
        or checks["mrun_nulos"]
        or checks["celdas_cohorte_horizonte"] != 120
        or checks["iplacex_conciliacion"]
    ):
        raise RuntimeError(f"Validación fallida: {checks}")
    latest = con.execute(
        """
        SELECT count(DISTINCT TrayectoriaID) AS base,
          count(DISTINCT CASE WHEN EnCarrera=1 THEN TrayectoriaID END) AS carrera,
          count(DISTINCT CASE WHEN EnInstitucion=1 THEN TrayectoriaID END) AS institucion,
          count(DISTINCT CASE WHEN EnEducacionSuperior=1 THEN TrayectoriaID END) AS es
        FROM seguimiento WHERE Cohorte=2024 AND AnioDesdeIngreso=2
        """
    ).fetchone()
    ecs = con.execute(
        """
        SELECT count(DISTINCT s.TrayectoriaID) AS base,
          count(DISTINCT CASE WHEN s.EnCarrera=1 THEN s.TrayectoriaID END) AS carrera,
          count(DISTINCT CASE WHEN s.EnInstitucion=1 THEN s.TrayectoriaID END) AS institucion,
          count(DISTINCT CASE WHEN s.EnEducacionSuperior=1 THEN s.TrayectoriaID END) AS es
        FROM seguimiento s JOIN programas p USING(ProgramaID)
        WHERE s.Cohorte=2024 AND s.AnioDesdeIngreso=2 AND p.GrupoECS='ECS'
        """
    ).fetchone()
    iplacex = con.execute(
        """
        SELECT sum(TotalTrayectorias),sum(SinMatriculaPrevia),sum(ConMatriculaPrevia),
          sum(AntecedenteOtraIES),sum(AntecedenteOnlineOtraIES)
        FROM iplacex_procedencia
        """
    ).fetchone()
    iplacex_reciente = con.execute(
        """
        SELECT sum(TotalTrayectorias),sum(AntecedenteOtraIES),
          sum(AntecedenteOnlineOtraIES)
        FROM iplacex_procedencia WHERE Cohorte IN (2024,2025)
        """
    ).fetchone()
    manifest = build_manifest({"matricula": matricula, "titulados": titulados}, source_root)
    (output / "fuentes.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    metadata = {
        "version_metodologica": "3.1.0",
        "universo": "Pregrado IP+CFT; modalidad No Presencial o Semipresencial o jornada A Distancia; Plan Regular; ingreso de origen en primer semestre",
        "unidad_principal": "trayectoria MRUN-carrera-institución-cohorte",
        "mrun": "Identificador enmascarado publicado por SIES; se conserva como texto",
        "campo_rut": False,
        "matricula_anios": MATRICULA_YEARS,
        "titulados_anios": TITULADOS_YEARS,
        "ecs_ids": list(ECS_IDS),
        "checks": checks,
        "ultimo_periodo": {"cohorte": 2024, "anio_observado": 2025, "base": latest[0], "carrera": latest[1], "institucion": latest[2], "educacion_superior": latest[3]},
        "ecs_ultimo_periodo": {"cohorte": 2024, "anio_observado": 2025, "base": ecs[0], "carrera": ecs[1], "institucion": ecs[2], "educacion_superior": ecs[3]},
        "iplacex_procedencia_2012_2025": {
            "total": iplacex[0],
            "sin_matricula_previa": iplacex[1],
            "con_matricula_previa": iplacex[2],
            "antecedente_otra_ies": iplacex[3],
            "antecedente_online_otra_ies": iplacex[4],
        },
        "iplacex_procedencia_2024_2025": {
            "total": iplacex_reciente[0],
            "antecedente_otra_ies": iplacex_reciente[1],
            "antecedente_online_otra_ies": iplacex_reciente[2],
        },
    }
    (output / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    checksums = []
    for path in sorted(output.glob("seguimiento_*.csv.gz")) + [
        output / "programas.csv",
        output / "resultados_control.csv",
        output / "iplacex_procedencia_cohortes.csv",
    ]:
        checksums.append(f"{file_sha256(path)}  {path.name}")
    (output / "archivos_analiticos.sha256").write_text("\n".join(checksums) + "\n", encoding="utf-8")
    con.close()
    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=Path("../artifacts"))
    parser.add_argument("--output", type=Path, default=Path("datos"))
    parser.add_argument("--solo-manifiesto", action="store_true")
    args = parser.parse_args()
    source_root = args.source_root.resolve()
    output = args.output.resolve()
    if args.solo_manifiesto:
        files = {
            "matricula": discover_sources(source_root, "matricula", MATRICULA_YEARS),
            "titulados": discover_sources(source_root, "titulados", TITULADOS_YEARS),
        }
        manifest = build_manifest(files, source_root)
        (output / "fuentes.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"archivos": len(manifest["archivos"])}, ensure_ascii=False))
    else:
        print(json.dumps(materialize(source_root, output), ensure_ascii=False, indent=2))
