"""Tests for admonition and sidebar node rendering in HTML5 and XHTML."""

from asciidoctype import AsciiDoctypeRenderer


def test_render_admonition_html5():
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "admonition",
        "type": "block",
        "variant": "note",
        "title": [{"name": "text", "type": "string", "value": "Note Title"}],
        "blocks": [
            {
                "name": "paragraph",
                "type": "block",
                "inlines": [{"name": "text", "type": "string", "value": "Note body."}],
            }
        ],
    }
    output = renderer.render(node)
    assert 'class="admonitionblock note"' in output
    assert "Note Title" in output
    assert '<div class="title">' in output
    assert "<p>Note body.</p>" in output


def test_render_sidebar_xhtml():
    renderer = AsciiDoctypeRenderer(target_format="xhtml")
    node = {
        "name": "sidebar",
        "type": "block",
        "attributes": {"id": "sidebar-1"},
        "title": [{"name": "text", "type": "string", "value": "Sidebar Title"}],
        "blocks": [
            {
                "name": "paragraph",
                "type": "block",
                "inlines": [{"name": "text", "type": "string", "value": "Sidebar text."}],
            }
        ],
    }
    output = renderer.render(node)
    assert 'class="sidebarblock"' in output
    assert 'id="sidebar-1"' in output
    assert "Sidebar Title" in output
    assert '<div class="title">' in output
    assert "<p>Sidebar text.</p>" in output
