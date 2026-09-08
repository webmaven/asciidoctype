"""Tests for template linter and security auditor."""

import os
import unittest.mock
from pathlib import Path

import pytest

from asciidoctype import AsciiDoctypeRenderer
from asciidoctype.exceptions import AsciiDoctypeSecurityError, AsciiDoctypeSecurityWarning
from asciidoctype.linter import (
    _audit_cache,
    audit_search_paths,
    audit_template,
    audit_template_directory,
    clear_audit_cache,
    lint_template_source,
)


def test_lint_safe_template():
    """Verify safe core template passes linter without warnings."""
    safe_code = """
<div class="paragraph" tal:attributes="id node.get('attributes', {}).get('id')">
    <tal:block tal:repeat="inline node.get('inlines', [])"
               tal:replace="structure renderer.render(inline, ctx)" />
</div>
"""

    findings = lint_template_source(safe_code, template_name="paragraph.html")
    assert len(findings) == 0


def test_lint_suspicious_structure_directive():
    """Verify linter catches suspicious structure usage on raw node value."""
    bad_code = """
<div class="custom">
    <tal:block tal:replace="structure python: node['value']" />
</div>
"""
    findings = lint_template_source(bad_code, template_name="custom.html")
    assert len(findings) == 1
    assert "structure python: node['value']" in findings[0].expression


def test_linter_warns_on_custom_search_path(tmp_path: Path):
    """Verify renderer audits custom template search paths and warns on unsafe templates."""
    custom_dir = tmp_path / "custom_theme"
    custom_dir.mkdir()
    bad_template = custom_dir / "paragraph.html"
    bad_template.write_text(
        "<p tal:replace=\"structure node.get('value')\"></p>",
        encoding="utf-8",
    )

    with pytest.warns(AsciiDoctypeSecurityWarning):
        AsciiDoctypeRenderer(search_paths=[custom_dir], strict=False)


def test_strict_mode_raises_on_unsafe_template(tmp_path: Path):
    """Verify renderer with strict=True raises AsciiDoctypeSecurityError on unsafe templates."""
    custom_dir = tmp_path / "custom_theme_strict"
    custom_dir.mkdir()
    bad_template = custom_dir / "heading.html"
    bad_template.write_text(
        "<h1 tal:replace=\"structure node.get('title')\"></h1>",
        encoding="utf-8",
    )

    with pytest.raises(AsciiDoctypeSecurityError):
        AsciiDoctypeRenderer(search_paths=[custom_dir], strict=True)


def test_lint_compilation_syntax_error():
    """Verify linter catches broken Chameleon syntax."""
    bad_syntax = "<div tal:condition='not valid python: :::'>"
    findings = lint_template_source(bad_syntax, template_name="syntax_error.html")
    assert len(findings) >= 1
    assert findings[0].severity == "error"


def test_audit_nonexistent_paths(tmp_path: Path):
    """Verify auditing nonexistent files or directories returns empty list cleanly."""
    non_file = tmp_path / "does_not_exist.html"
    assert audit_template(non_file) == []

    non_dir = tmp_path / "does_not_exist_dir"
    assert audit_template_directory(non_dir) == []


@pytest.fixture(autouse=True)
def reset_audit_cache():
    """Reset audit cache before and after each test."""
    clear_audit_cache()
    yield
    clear_audit_cache()


def test_audit_cache_hit_avoids_reaudit(tmp_path: Path):
    """Verify that repeated audit of the same directory hits cache and avoids re-auditing."""
    custom_dir = tmp_path / "custom"
    custom_dir.mkdir()
    tmpl = custom_dir / "custom.html"
    tmpl.write_text('<div tal:content="string:hello"></div>', encoding="utf-8")

    findings1 = audit_search_paths([custom_dir])
    assert findings1 == []
    assert len(_audit_cache) == 1

    with unittest.mock.patch("asciidoctype.linter.audit_template_directory") as mock_audit:
        findings2 = audit_search_paths([custom_dir])
        assert findings2 == []
        mock_audit.assert_not_called()


def test_audit_cache_invalidation_on_mtime_change(tmp_path: Path):
    """Verify cache invalidates when a template file mtime changes."""
    custom_dir = tmp_path / "custom"
    custom_dir.mkdir()
    tmpl = custom_dir / "custom.html"
    tmpl.write_text('<div tal:content="string:hello"></div>', encoding="utf-8")

    findings1 = audit_search_paths([custom_dir])
    assert findings1 == []

    # Modify template file and advance mtime
    new_mtime = tmpl.stat().st_mtime + 10.0
    tmpl.write_text("<div tal:replace=\"structure python: node['leak']\"></div>", encoding="utf-8")
    os.utime(tmpl, (new_mtime, new_mtime))

    with pytest.warns(AsciiDoctypeSecurityWarning):
        findings2 = audit_search_paths([custom_dir])
    assert len(findings2) == 1
    assert "structure python: node['leak']" in findings2[0].expression


def test_audit_cache_strict_mode_cached_findings(tmp_path: Path):
    """Verify strict mode raises AsciiDoctypeSecurityError even on cached findings."""
    custom_dir = tmp_path / "custom"
    custom_dir.mkdir()
    tmpl = custom_dir / "custom.html"
    tmpl.write_text("<div tal:replace=\"structure python: node['leak']\"></div>", encoding="utf-8")

    with pytest.warns(AsciiDoctypeSecurityWarning):
        findings = audit_search_paths([custom_dir], strict=False)
    assert len(findings) == 1

    # Second call with strict=True should raise using cached findings without re-audit
    with unittest.mock.patch("asciidoctype.linter.audit_template_directory") as mock_audit:
        with pytest.raises(AsciiDoctypeSecurityError):
            audit_search_paths([custom_dir], strict=True)
        mock_audit.assert_not_called()


def test_clear_audit_cache(tmp_path: Path):
    """Verify clear_audit_cache resets the cache dictionary."""
    custom_dir = tmp_path / "custom"
    custom_dir.mkdir()
    tmpl = custom_dir / "custom.html"
    tmpl.write_text("<div></div>", encoding="utf-8")

    audit_search_paths([custom_dir])
    assert len(_audit_cache) > 0
    clear_audit_cache()
    assert len(_audit_cache) == 0


def test_audit_cache_nonexistent_and_empty_dirs(tmp_path: Path):
    """Verify cache handles nonexistent directories and empty directories cleanly."""
    non_dir = tmp_path / "non_existent"
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    findings = audit_search_paths([non_dir, empty_dir])
    assert findings == []
    assert len(_audit_cache) == 1

    with unittest.mock.patch("asciidoctype.linter.audit_template_directory") as mock_audit:
        findings2 = audit_search_paths([non_dir, empty_dir])
        assert findings2 == []
        mock_audit.assert_not_called()
