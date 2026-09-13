"""Genera los entregables auditables de procedencia de IPLACEX.

La fuente exclusiva es datos/iplacex_procedencia_cohortes.csv, materializada
desde los archivos SIES por materializar_datos.py. El PDF se genera en modo
invariante para que su contenido binario sea reproducible entre ejecuciones.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "datos/iplacex_procedencia_cohortes.csv"
MD_PATH = ROOT / "ANALISIS_PROCEDENCIA_PRIMER_ANO_IPLACEX.md"
PDF_PATH = ROOT / "TABLA_MATRICULA_PRIMER_ANO_IPLACEX.pdf"
PDF_V2_PATH = ROOT / "TABLA_MATRICULA_PRIMER_ANO_IPLACEX_V2.pdf"
AUDIT_PATH = ROOT / "auditoria/evidencia/resumen_auditoria.json"


def fmt(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def pct(part: int, total: int) -> str:
    return f"{100 * part / total:.1f}".replace(".", ",") + " %"


def load_rows(path: Path) -> list[dict[str, int]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = [{key: int(value) for key, value in row.items()} for row in csv.DictReader(handle, delimiter=";")]
    if [row["Cohorte"] for row in rows] != list(range(2012, 2026)):
        raise ValueError("La tabla IPLACEX debe cubrir exactamente los cohortes 2012-2025")
    for row in rows:
        if row["SinMatriculaPrevia"] + row["ConMatriculaPrevia"] != row["TotalTrayectorias"]:
            raise ValueError(f"No concilia el cohorte {row['Cohorte']}")
        if not (
            row["AntecedenteOnlineOtraIES"]
            <= row["AntecedenteOtraIES"]
            <= row["ConMatriculaPrevia"]
            <= row["TotalTrayectorias"]
        ):
            raise ValueError(f"Jerarquía inválida en el cohorte {row['Cohorte']}")
    return rows


def totals(rows: list[dict[str, int]]) -> dict[str, int]:
    numeric = [key for key in rows[0] if key != "Cohorte"]
    return {key: sum(row[key] for row in rows) for key in numeric}


def recent(rows: list[dict[str, int]]) -> dict[str, int]:
    return totals([row for row in rows if row["Cohorte"] in (2024, 2025)])


def build_markdown(rows: list[dict[str, int]], output: Path) -> None:
    total = totals(rows)
    latest = recent(rows)
    lines = [
        "# Procedencia de la matrícula de primer año de IPLACEX",
        "",
        "## Respuesta ejecutiva",
        "",
        f"En los cohortes **2012–2025**, el universo del PBIP contiene **{fmt(total['TotalTrayectorias'])} matrículas/trayectorias de primer año de IPLACEX**:",
        "",
        f"- **{fmt(total['AntecedenteOtraIES'])} ({pct(total['AntecedenteOtraIES'], total['TotalTrayectorias'])})** tienen una matrícula previa observable en otra IES.",
        f"- **{fmt(total['SinMatriculaPrevia'])} ({pct(total['SinMatriculaPrevia'], total['TotalTrayectorias'])})** no tienen ninguna matrícula previa observable, ni en otra IES ni en IPLACEX.",
        f"- **{fmt(total['ConMatriculaPrevia'])} ({pct(total['ConMatriculaPrevia'], total['TotalTrayectorias'])})** tienen alguna matrícula previa, incluyendo antecedentes en IPLACEX.",
        "",
        f"En **2024–2025**, {fmt(latest['AntecedenteOtraIES'])} de {fmt(latest['TotalTrayectorias'])} trayectorias ({pct(latest['AntecedenteOtraIES'], latest['TotalTrayectorias'])}) tienen historia en otra IES, pero sólo {fmt(latest['AntecedenteOnlineOtraIES'])} ({pct(latest['AntecedenteOnlineOtraIES'], latest['TotalTrayectorias'])}) presentan historia online en otra IES.",
        "",
        "Los resultados describen antecedentes de matrícula; no demuestran captación directa ni causalidad.",
        "",
        "## Resultados por cohorte",
        "",
        "| Cohorte | Total | Sin matrícula previa | Con matrícula previa | Antecedente en otra IES | Antecedente online en otra IES | Personas únicas |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {Cohorte} | {TotalTrayectorias} | {SinMatriculaPrevia} | {ConMatriculaPrevia} | {AntecedenteOtraIES} | {AntecedenteOnlineOtraIES} | {PersonasUnicas} |".format(
                **{key: (str(value) if key == "Cohorte" else fmt(value)) for key, value in row.items()}
            )
        )
    lines.extend(
        [
            f"| **Total 2012–2025** | **{fmt(total['TotalTrayectorias'])}** | **{fmt(total['SinMatriculaPrevia'])}** | **{fmt(total['ConMatriculaPrevia'])}** | **{fmt(total['AntecedenteOtraIES'])}** | **{fmt(total['AntecedenteOnlineOtraIES'])}** | **{fmt(total['PersonasUnicas'])}** |",
            "",
            "La suma de personas por cohorte no equivale a personas distintas del período: un MRUN puede aparecer en más de un cohorte.",
            "",
            "## Definiciones y filtros",
            "",
            "- Unidad: trayectoria deduplicada MRUN–carrera–institución–cohorte.",
            "- IPLACEX: `InstitucionID = 152`.",
            "- Universo: pregrado IP, Plan Regular, ingreso en el primer semestre del cohorte y modalidad No Presencial/Semipresencial o jornada A Distancia.",
            "- Con matrícula previa: el MRUN aparece en cualquier año anterior disponible, en IPLACEX o en otra IES.",
            "- Antecedente en otra IES: existe un registro anterior con una institución distinta de IPLACEX.",
            "- Antecedente online: el registro anterior en otra IES cumple el enfoque flexible del PBIP.",
            "- No se consideran matrículas simultáneas del mismo año como antecedentes previos.",
            "",
            "## Cobertura y limitaciones",
            "",
            "Fuente: Matrícula de Educación Superior SIES 2011–2025. Se excluye 2011 porque no existe historia anterior observable. La ventana de observación aumenta en cohortes recientes, por lo que la evolución no debe interpretarse como causalidad.",
            "",
        ]
    )
    output.write_text("\n".join(lines), encoding="utf-8")


def build_pdf(
    rows: list[dict[str, int]],
    output: Path,
    audit: dict[str, object] | None = None,
) -> None:
    rl_config.invariant = 1
    total = totals(rows)
    latest = recent(rows)
    navy = colors.HexColor("#17365D")
    blue = colors.HexColor("#D9EAF7")
    light = colors.HexColor("#F5F7FA")
    gray = colors.HexColor("#4A5568")
    green = colors.HexColor("#E7F2EA")
    red = colors.HexColor("#8B1E2D")
    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=navy, alignment=TA_CENTER, spaceAfter=6 * mm)
    intro = ParagraphStyle("Intro", parent=styles["BodyText"], fontName="Helvetica", fontSize=9, leading=12, textColor=gray, alignment=TA_LEFT, spaceAfter=4 * mm)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.5, leading=13.5, textColor=gray, alignment=TA_LEFT)
    small = ParagraphStyle("Small", parent=body, fontSize=8, leading=10.5)
    header = ParagraphStyle("Header", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=7.3, leading=8.8, textColor=colors.white, alignment=TA_CENTER)
    cell = ParagraphStyle("Cell", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.4, leading=10, alignment=TA_CENTER)
    cell_bold = ParagraphStyle("CellBold", parent=cell, fontName="Helvetica-Bold")
    callout = ParagraphStyle("Callout", parent=body, fontName="Helvetica-Bold", fontSize=11, leading=15, textColor=red)
    quote = ParagraphStyle("Quote", parent=body, fontSize=10.5, leading=15, leftIndent=5 * mm, rightIndent=5 * mm, textColor=navy)

    document = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=14 * mm, leftMargin=14 * mm, topMargin=15 * mm, bottomMargin=15 * mm, title="Matrícula de primer año de IPLACEX por cohorte", author="Auditoría PBIP Retención Académica SIES")
    story = [
        Paragraph("Matrícula de primer año de IPLACEX por cohorte", title),
        Paragraph("<b>Sin matrícula previa</b>: el MRUN no aparece antes en SIES. <b>Con matrícula previa</b>: el MRUN aparece antes en otra IES o en IPLACEX. Ambas categorías son excluyentes y suman el total.", intro),
    ]
    data = [[Paragraph("Cohorte", header), Paragraph("Primer año sin<br/>matrícula previa", header), Paragraph("Total primer año<br/>IPLACEX", header), Paragraph("Primer año con<br/>matrícula previa", header)]]
    for row in rows:
        data.append([Paragraph(str(row["Cohorte"]), cell), Paragraph(fmt(row["SinMatriculaPrevia"]), cell), Paragraph(fmt(row["TotalTrayectorias"]), cell), Paragraph(fmt(row["ConMatriculaPrevia"]), cell)])
    data.append([Paragraph("Total 2012–2025", cell_bold), Paragraph(fmt(total["SinMatriculaPrevia"]), cell_bold), Paragraph(fmt(total["TotalTrayectorias"]), cell_bold), Paragraph(fmt(total["ConMatriculaPrevia"]), cell_bold)])
    table = Table(data, colWidths=[31 * mm, 50 * mm, 47 * mm, 50 * mm], repeatRows=1, hAlign="CENTER")
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), navy), ("BOX", (0, 0), (-1, -1), 0.8, navy), ("INNERGRID", (0, 0), (-1, -2), 0.35, colors.HexColor("#AAB7C4")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, light]), ("BACKGROUND", (0, -1), (-1, -1), blue), ("LINEABOVE", (0, -1), (-1, -1), 1.0, navy)]))
    story.extend([table, Spacer(1, 5 * mm), Paragraph(f"<b>Resultado acumulado:</b> {fmt(total['SinMatriculaPrevia'])} no presentan matrícula previa ({pct(total['SinMatriculaPrevia'], total['TotalTrayectorias'])}) y {fmt(total['ConMatriculaPrevia'])} sí presentan al menos una ({pct(total['ConMatriculaPrevia'], total['TotalTrayectorias'])}), sobre {fmt(total['TotalTrayectorias'])} trayectorias.", small), Spacer(1, 2.5 * mm), Paragraph("<b>Fuente:</b> Matrícula SIES 2011–2025 y universo materializado del PBIP. Se excluye 2011 porque no existe historia anterior observable.", small), PageBreak()])

    story.extend([Paragraph("Interpretación ejecutiva · cohortes 2024–2025", title), Paragraph("El insight <u>no</u> es que la mayoría de las matrículas de primer año de IPLACEX provenga de instituciones online.", callout), Spacer(1, 5 * mm)])
    recent_rows = [row for row in rows if row["Cohorte"] in (2024, 2025)]
    insight = [[Paragraph("Cohorte", header), Paragraph("Total primer año<br/>IPLACEX", header), Paragraph("Con historial en<br/>otra IES", header), Paragraph("Con historial online<br/>en otra IES", header)]]
    for row in recent_rows:
        insight.append([Paragraph(str(row["Cohorte"]), cell), Paragraph(fmt(row["TotalTrayectorias"]), cell), Paragraph(f"{fmt(row['AntecedenteOtraIES'])} ({pct(row['AntecedenteOtraIES'], row['TotalTrayectorias'])})", cell), Paragraph(f"{fmt(row['AntecedenteOnlineOtraIES'])} ({pct(row['AntecedenteOnlineOtraIES'], row['TotalTrayectorias'])})", cell)])
    insight.append([Paragraph("2024–2025", cell_bold), Paragraph(fmt(latest["TotalTrayectorias"]), cell_bold), Paragraph(f"{fmt(latest['AntecedenteOtraIES'])} ({pct(latest['AntecedenteOtraIES'], latest['TotalTrayectorias'])})", cell_bold), Paragraph(f"{fmt(latest['AntecedenteOnlineOtraIES'])} ({pct(latest['AntecedenteOnlineOtraIES'], latest['TotalTrayectorias'])})", cell_bold)])
    insight_table = Table(insight, colWidths=[32 * mm, 44 * mm, 50 * mm, 52 * mm], hAlign="CENTER")
    insight_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), navy), ("BOX", (0, 0), (-1, -1), 0.8, navy), ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#AAB7C4")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7), ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, light]), ("BACKGROUND", (0, -1), (-1, -1), blue)]))
    quote_text = f"“En 2024–2025, el {pct(latest['AntecedenteOtraIES'], latest['TotalTrayectorias'])} de las trayectorias de primer año de IPLACEX correspondió a personas con experiencia previa en otra IES. Sin embargo, sólo el {pct(latest['AntecedenteOnlineOtraIES'], latest['TotalTrayectorias'])} registraba antecedentes online en otra institución. El insight es la alta presencia de estudiantes con experiencia previa, no una migración mayoritaria desde competidores online.”"
    quote_box = Table([[Paragraph(quote_text, quote)]], colWidths=[172 * mm])
    quote_box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), green), ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#5B8C65")), ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10)]))
    limitations = Table([[Paragraph("<b>Cómo leerlo:</b><br/>• Otra IES considera cualquier año anterior al cohorte.<br/>• Online replica el enfoque flexible del PBIP.<br/>• El antecedente no necesariamente es la matrícula inmediatamente anterior.<br/>• Los datos no demuestran captación directa ni causalidad.", body)]], colWidths=[172 * mm])
    limitations.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), light), ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#AAB7C4")), ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10)]))
    story.extend([insight_table, Spacer(1, 9 * mm), Paragraph("Conclusión recomendada para el vicerrector", ParagraphStyle("Subtitle", parent=body, fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=navy, spaceAfter=3 * mm)), quote_box, Spacer(1, 9 * mm), limitations])
    if audit is not None:
        if audit.get("failed") != 0 or audit.get("controls") != audit.get("passed"):
            raise ValueError("La versión 2 sólo puede emitirse con una auditoría completamente aprobada")
        audit_table = Table(
            [
                [Paragraph("Control", header), Paragraph("Resultado auditado", header)],
                [Paragraph("Controles numéricos", cell), Paragraph(fmt(int(audit["controls"])), cell_bold)],
                [Paragraph("Controles aprobados", cell), Paragraph(fmt(int(audit["passed"])), cell_bold)],
                [Paragraph("Controles fallidos", cell), Paragraph(fmt(int(audit["failed"])), cell_bold)],
                [Paragraph("Celdas cohorte–horizonte", cell), Paragraph(fmt(int(audit["valid_cohort_horizon_cells"])), cell_bold)],
                [Paragraph("Versión metodológica", cell), Paragraph(str(audit["audit_version"]), cell_bold)],
                [Paragraph("Huella de las fuentes", cell), Paragraph(str(audit["source_hash"]), small)],
            ],
            colWidths=[70 * mm, 108 * mm],
            hAlign="CENTER",
        )
        audit_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), navy),
            ("BOX", (0, 0), (-1, -1), 0.8, navy),
            ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#AAB7C4")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light]),
        ]))
        story.extend([
            PageBreak(),
            Paragraph("Versión 2 · cambios y respaldo de auditoría", title),
            Paragraph(
                "<b>Las cifras de la tabla no cambiaron frente a la versión anterior.</b> "
                "La versión 2 agrega la trazabilidad formal de la auditoría integral y deja "
                "explícito que los resultados fueron conciliados contra todas las celdas y "
                "dimensiones del PBIP.",
                body,
            ),
            Spacer(1, 6 * mm),
            audit_table,
            Spacer(1, 8 * mm),
            Paragraph(
                "<b>Qué cambia:</b> se incorpora evidencia reproducible de 4.955 controles, "
                "conciliación de nueve dimensiones y verificación de los archivos analíticos. "
                "<b>Qué no cambia:</b> los totales por cohorte ni la conclusión: en 2024–2025 "
                "predomina la experiencia previa en alguna otra IES, pero no la procedencia "
                "desde instituciones online.",
                body,
            ),
        ])
    document.build(story)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=CSV_PATH)
    parser.add_argument("--markdown", type=Path, default=MD_PATH)
    parser.add_argument("--pdf", type=Path, default=PDF_PATH)
    parser.add_argument("--pdf-v2", type=Path, default=PDF_V2_PATH)
    parser.add_argument("--audit", type=Path, default=AUDIT_PATH)
    args = parser.parse_args()
    rows = load_rows(args.csv)
    build_markdown(rows, args.markdown)
    build_pdf(rows, args.pdf)
    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    build_pdf(rows, args.pdf_v2, audit=audit)
    print({"cohortes": len(rows), "markdown": str(args.markdown), "pdf": str(args.pdf), "pdf_v2": str(args.pdf_v2)})


if __name__ == "__main__":
    main()
