"""Tests for template inheritance, custom theme paths, and fallback precedence."""
from pathlib import Path
import pytest
from asciidoctype import AsciiDoctypeRenderer


def test_custom_template_override(tmp_path: Path):
    """Test that a custom template in search_paths overrides internal core fallback template."""
    custom_theme = tmp_path / "custom_theme"
    custom_theme.mkdir()
    
    # Create custom paragraph.html in custom_theme
    custom_paragraph = custom_theme / "paragraph.html"
    custom_paragraph.write_text(
        '<p class="custom-override" tal:attributes="id node.get(\'attributes\', {}).get(\'id\')">\n'
        '  <tal:block tal:repeat="inline node.get(\'inlines\', [])" tal:replace="structure renderer.render(inline, ctx)" />\n'
        '</p>\n'
    )

    renderer = AsciiDoctypeRenderer(target_format="html5", search_paths=[custom_theme])
    node = {
        "name": "paragraph",
        "type": "block",
        "attributes": {"id": "custom-p"},
        "inlines": [{"name": "text", "type": "string", "value": "Custom Theme Paragraph"}],
    }

    output = renderer.render(node)
    assert 'class="custom-override"' in output
    assert 'id="custom-p"' in output
    assert "Custom Theme Paragraph" in output


def test_custom_template_fallback_to_core(tmp_path: Path):
    """Test that missing templates in custom search_paths fall back to core system templates."""
    custom_theme = tmp_path / "partial_theme"
    custom_theme.mkdir()
    
    # Only create custom paragraph.html in partial_theme, leaving section.html missing
    custom_paragraph = custom_theme / "paragraph.html"
    custom_paragraph.write_text('<p class="partial-para">Custom Para</p>')

    renderer = AsciiDoctypeRenderer(target_format="html5", search_paths=[custom_theme])
    
    # Section should fall back seamlessly to core_templates/html5/section.html
    section_node = {
        "name": "section",
        "type": "block",
        "level": 1,
        "attributes": {"id": "fallback-section"},
        "title": [{"name": "text", "type": "string", "value": "Fallback Section"}],
        "blocks": [],
    }

    output = renderer.render(section_node)
    assert 'class="adoc-section level-1"' in output
    assert 'id="fallback-section"' in output
    assert "Fallback Section" in output
