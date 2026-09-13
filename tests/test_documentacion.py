import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


REQUIRED = [
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "docs/README.md",
    "docs/00-introduccion.md",
    "docs/01-estructura-pbip.md",
    "docs/02-modelo-semantico.md",
    "docs/03-dax.md",
    "docs/04-power-query.md",
    "docs/05-reporte.md",
    "docs/06-seguridad.md",
    "docs/07-alm-devops.md",
    "docs/08-estandares.md",
    "docs/09-glosario.md",
    "docs/10-adr/0000-plantilla.md",
    "docs/11-checklists.md",
    ".github/CODEOWNERS",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/bug.yml",
    ".github/ISSUE_TEMPLATE/calidad-datos.yml",
    ".github/ISSUE_TEMPLATE/documentacion.yml",
]


def markdown_files():
    return [path for path in ROOT.rglob("*.md") if ".pbi" not in path.parts]


def test_archivos_documentales_obligatorios_existen():
    missing = [relative for relative in REQUIRED if not (ROOT / relative).is_file()]
    assert not missing, missing


def test_enlaces_markdown_locales_resuelven():
    pattern = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
    failures = []
    for path in markdown_files():
        text = path.read_text(encoding="utf-8")
        for raw_target in pattern.findall(text):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            target = target.split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                failures.append((path.relative_to(ROOT).as_posix(), raw_target, "fuera del repo"))
                continue
            if not resolved.exists():
                failures.append((path.relative_to(ROOT).as_posix(), raw_target, "no existe"))
    assert not failures, failures


def test_bloques_markdown_estan_balanceados_y_mermaid_presente():
    mermaid = 0
    for path in markdown_files():
        text = path.read_text(encoding="utf-8")
        assert len(re.findall(r"^```", text, flags=re.MULTILINE)) % 2 == 0, path
        mermaid += len(re.findall(r"^```mermaid\s*$", text, flags=re.MULTILINE))
    assert mermaid >= 5


def test_no_hay_rutas_personales_en_documentos_canonicos():
    forbidden = ["C:" + "/Users/", "C:" + "\\Users\\", "/Users/" + "nick_", "\\" + "nick_" + "\\"]
    for path in markdown_files() + [ROOT / "docs/documentacion-manifest.yml"]:
        text = path.read_text(encoding="utf-8")
        for value in forbidden:
            assert value not in text, (path, value)


def test_manifiesto_documental_y_formularios_yaml_son_validos():
    manifest = yaml.safe_load((ROOT / "docs/documentacion-manifest.yml").read_text(encoding="utf-8"))
    assert manifest["project"] == "Retencion_Academica_SIES"
    assert manifest["project_version"] == "3.1.0"
    assert len(manifest["canonical_documents"]) == 12
    for relative in manifest["canonical_documents"]:
        assert (ROOT / relative).exists(), relative
    for path in (ROOT / ".github/ISSUE_TEMPLATE").glob("*.yml"):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(payload, dict), path


def test_git_lfs_no_esta_habilitado_y_fuentes_brutas_se_ignoran():
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "filter=lfs" not in attributes
    assert "datos_fuente/" in gitignore
    assert ".env" in gitignore


def test_concepto_mrun_es_congruente():
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in markdown_files())
    assert "MRUN" in corpus
    assert "no es el RUT real" in corpus or "no es RUT real" in corpus
    assert "columna `RUT`" in corpus
