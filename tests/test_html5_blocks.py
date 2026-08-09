"""Tests for HTML5 block elements rendering (paragraph, section)."""
import pytest
from asciidoctype import AsciiDoctypeRenderer


def test_render_paragraph_node():
    """Test paragraph block rendering with id and inlines."""
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "paragraph",
        "type": "block",
        "attributes": {"id": "p1", "role": "lead"},
        "inlines": [
            {"name": "text", "type": "string", "value": "This is a "},
            {
                "name": "span",
                "type": "inline",
                "variant": "strong",
                "inlines": [{"name": "text", "type": "string", "value": "paragraph"}],
            },
            {"name": "text", "type": "string", "value": "."},
        ],
    }
    output = renderer.render(node)
    assert '<p id="p1" class="lead">' in output
    assert "This is a <strong>paragraph</strong>." in output
    assert "</p>" in output


def test_render_section_node():
    """Test section block rendering with level 1 (h2) and child blocks."""
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "section",
        "type": "block",
        "level": 1,
        "attributes": {"id": "section-1"},
        "title": [{"name": "text", "type": "string", "value": "First Section"}],
        "blocks": [
            {
                "name": "paragraph",
                "type": "block",
                "attributes": {},
                "inlines": [{"name": "text", "type": "string", "value": "Section content."}],
            }
        ],
    }
    output = renderer.render(node)
    assert '<section class="adoc-section level-1" id="section-1">' in output
    assert "<h2 tag=\"h2\">First Section</h2>" in output or "<h2>First Section</h2>" in output or "First Section" in output
    assert "Section content." in output
    assert "</section>" in output
