"""Tests for template linter and security auditor."""

from pathlib import Path

import pytest

from asciidoctype import AsciiDoctypeRenderer
from asciidoctype.exceptions import AsciiDoctypeSecurityError, AsciiDoctypeSecurityWarning
from asciidoctype.linter import audit_template, audit_template_directory, lint_template_source


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
