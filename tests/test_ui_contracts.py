"""Static contracts for the rebuilt atlas dashboard shell."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = REPO_ROOT / "index.html"
APP_JS = REPO_ROOT / "app.js"
README = REPO_ROOT / "README.md"


def test_index_exposes_rebuilt_modes() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")

    assert "Local Source Rebuild" in html
    assert 'value="effect_ratio"' in html
    assert 'value="transportability_score"' in html
    assert 'value="priority_score"' in html
    assert "local transportability matrix rebuild" in html


def test_app_reads_generated_json_and_source_backed_fields() -> None:
    js = APP_JS.read_text(encoding="utf-8")

    assert 'fetch("data/atlas_results.json")' in js
    assert "reference_profile" in js
    assert "transportability_score" in js
    assert "priority_score" in js
    assert "effect_ratio" in js
    assert "const centroids" not in js


def test_readme_documents_local_rebuild_inputs() -> None:
    readme = README.read_text(encoding="utf-8")

    assert "GLOBAL_TRANSPORTABILITY_MATRIX" in readme
    assert "WORLD_BANK_COUNTRIES_CSV" in readme
    assert "WORLD_BANK_WDI_COUNTRY_CSV" in readme
    assert "python core/pipeline.py" in readme
