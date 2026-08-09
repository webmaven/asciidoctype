"""Tests for HTML5 inline elements rendering (text, span)."""
import pytest
from asciidoctype import AsciiDoctypeRenderer, AsciiDoctypeRenderingError


def test_render_text_node():
    """Test text leaf node renders value raw."""
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {"name": "text", "type": "string", "value": "Hello World!"}
    output = renderer.render(node)
    assert output.strip() == "Hello World!"


def test_render_span_strong():
    """Test span node with strong variant."""
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "span",
        "type": "inline",
        "variant": "strong",
        "attributes": {"role": "highlight"},
        "inlines": [{"name": "text", "type": "string", "value": "Bold Text"}],
    }
    output = renderer.render(node)
    assert '<strong class="highlight">Bold Text</strong>' in output


def test_render_span_emphasis():
    """Test span node with emphasis variant."""
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "span",
        "type": "inline",
        "variant": "emphasis",
        "attributes": {},
        "inlines": [{"name": "text", "type": "string", "value": "Italic Text"}],
    }
    output = renderer.render(node)
    assert "<em>Italic Text</em>" in output


def test_render_invalid_node_structure():
    """Test invalid node structure raises TypeError."""
    renderer = AsciiDoctypeRenderer(target_format="html5")
    with pytest.raises(TypeError):
        renderer.render("not a dict")

    with pytest.raises(TypeError):
        renderer.render({"no_name": "key"})


def test_render_rendering_error():
    """Test rendering failure raises AsciiDoctypeRenderingError."""
    renderer = AsciiDoctypeRenderer(target_format="html5")
    # Missing value attribute in text node causes template execution error
    bad_node = {"name": "text"}
    with pytest.raises(AsciiDoctypeRenderingError):
        renderer.render(bad_node)
