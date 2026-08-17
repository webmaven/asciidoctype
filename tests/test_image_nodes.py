"""Tests for block and inline image node rendering in HTML5 and XHTML."""

from asciidoctype import AsciiDoctypeRenderer


def test_render_block_image_html5():
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "image",
        "type": "block",
        "target": "diagram.png",
        "attributes": {"alt": "Architecture Diagram", "id": "img-1"},
        "title": [{"name": "text", "type": "string", "value": "Figure 1"}],
    }
    output = renderer.render(node)
    assert 'class="imageblock"' in output
    assert 'id="img-1"' in output
    assert '<img src="diagram.png" alt="Architecture Diagram">' in output
    assert "Figure 1" in output
    assert "/>" not in output


def test_render_block_image_xhtml():
    renderer = AsciiDoctypeRenderer(target_format="xhtml")
    node = {
        "name": "image",
        "type": "block",
        "target": "diagram.png",
        "attributes": {"alt": "Architecture Diagram"},
    }
    output = renderer.render(node)
    assert '<img src="diagram.png" alt="Architecture Diagram" />' in output


def test_render_inline_image_html5():
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "image_inline",
        "type": "inline",
        "target": "icon.png",
        "attributes": {"alt": "icon"},
    }
    output = renderer.render(node)
    assert '<span class="image-inline">' in output
    assert '<img class="image-inline" src="icon.png" alt="icon">' in output


def test_render_inline_image_xhtml():
    renderer = AsciiDoctypeRenderer(target_format="xhtml")
    node = {
        "name": "image_inline",
        "type": "inline",
        "target": "icon.png",
        "attributes": {"alt": "icon"},
    }
    output = renderer.render(node)
    assert '<span class="image-inline">' in output
    assert '<img class="image-inline" src="icon.png" alt="icon" />' in output
