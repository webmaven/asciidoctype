import pytest

from asciidoctype import AsciiDoctypeRenderer, AsciiDoctypeRenderingError
from asciidoctype.exceptions import (
    AsciiDoctypeRenderingError as AsciiDoctypeRenderingErrorFromExceptions,
)


def test_asciidoctype_rendering_error_import():
    """Test AsciiDoctypeRenderingError can be imported from exceptions and top level."""
    assert issubclass(AsciiDoctypeRenderingError, Exception)
    assert AsciiDoctypeRenderingError is AsciiDoctypeRenderingErrorFromExceptions


def test_renderer_initialization_html5():
    """Test AsciiDoctypeRenderer initializes properly with html5 format."""
    renderer = AsciiDoctypeRenderer(target_format="html5")
    assert renderer.target_format == "html5"
    assert hasattr(renderer, "loader")
    assert renderer.loader is not None


def test_renderer_initialization_xhtml():
    """Test AsciiDoctypeRenderer initializes properly with xhtml format."""
    renderer = AsciiDoctypeRenderer(target_format="xhtml")
    assert renderer.target_format == "xhtml"
    assert hasattr(renderer, "loader")
    assert renderer.loader is not None


def test_renderer_initialization_default():
    """Test AsciiDoctypeRenderer initializes properly with default target_format (html5)."""
    renderer = AsciiDoctypeRenderer()
    assert renderer.target_format == "html5"
    assert hasattr(renderer, "loader")
    assert renderer.loader is not None


def test_renderer_initialization_invalid_format():
    """Test ValueError is raised when initialized with an invalid format like markdown."""
    with pytest.raises(ValueError):
        AsciiDoctypeRenderer(target_format="markdown")


def test_render_polymorphic_image_inline():
    """Test polymorphic dispatch for image node with type='inline'."""
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "image",
        "type": "inline",
        "target": "icon.png",
        "attributes": {"alt": "icon"},
    }
    output = renderer.render(node)
    assert '<span class="image-inline">' in output
    assert '<img class="image-inline" src="icon.png" alt="icon">' in output
    assert '<div class="imageblock">' not in output


def test_render_polymorphic_image_block():
    """Test standard dispatch for image node with type='block'."""
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "image",
        "type": "block",
        "target": "diagram.png",
        "attributes": {"alt": "Architecture Diagram"},
    }
    output = renderer.render(node)
    assert '<div class="imageblock">' in output
    assert '<img src="diagram.png" alt="Architecture Diagram">' in output


def test_render_polymorphic_ref_footnote():
    """Test polymorphic dispatch for ref node with variant='footnote'."""
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "ref",
        "variant": "footnote",
        "id": "fn-1",
        "number": 1,
        "value": "Footnote text.",
    }
    output = renderer.render(node)
    assert '<sup class="footnote"' in output
    assert '<a href="#_footnotedef_1">1</a>' in output


def test_render_polymorphic_ref_link():
    """Test standard dispatch for ref node with variant='link'."""
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "ref",
        "type": "inline",
        "variant": "link",
        "target": "https://example.com",
        "inlines": [{"name": "text", "type": "string", "value": "Example"}],
    }
    output = renderer.render(node)
    assert '<a href="https://example.com">Example</a>' in output


def test_render_polymorphic_image_inline_fallback_to_image(tmp_path):
    """Test that image node (type='inline') falls back to image.html if image_inline missing."""
    custom_tpl_dir = tmp_path / "templates"
    custom_tpl_dir.mkdir()
    # Provide fallback_container.html and image.html only, but NOT image_inline.html
    tpl_content = '<div class="custom-image-fallback">${node.target}</div>'
    (custom_tpl_dir / "image.html").write_text(tpl_content)
    (custom_tpl_dir / "fallback_container.html").write_text("<div>fallback</div>")

    # Isolate loader to custom directory without image_inline.html to test fallback
    renderer = AsciiDoctypeRenderer(target_format="html5")
    from chameleon import PageTemplateLoader

    renderer.loader = PageTemplateLoader([str(custom_tpl_dir)], default_extension=".html")

    node = {
        "name": "image",
        "type": "inline",
        "target": "icon.png",
        "attributes": {"alt": "icon"},
    }
    output = renderer.render(node)
    assert '<div class="custom-image-fallback">icon.png</div>' in output


def test_render_polymorphic_ref_footnote_fallback_to_ref(tmp_path):
    """Test that ref node (variant='footnote') falls back to ref.html if footnote missing."""
    custom_tpl_dir = tmp_path / "templates"
    custom_tpl_dir.mkdir()
    ref_content = '<a class="custom-ref-fallback" href="${node.target}">ref</a>'
    (custom_tpl_dir / "ref.html").write_text(ref_content)
    (custom_tpl_dir / "fallback_container.html").write_text("<div>fallback</div>")

    renderer = AsciiDoctypeRenderer(target_format="html5")
    from chameleon import PageTemplateLoader

    renderer.loader = PageTemplateLoader([str(custom_tpl_dir)], default_extension=".html")

    node = {
        "name": "ref",
        "variant": "footnote",
        "target": "#fn-1",
    }
    output = renderer.render(node)
    assert '<a class="custom-ref-fallback" href="#fn-1">ref</a>' in output


def test_render_fallback_container_for_unknown_node():
    """Test that unknown node names fall back to fallback_container.html."""
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "unknown_custom_element",
        "inlines": [{"name": "text", "type": "string", "value": "Fallback content"}],
    }
    output = renderer.render(node)
    assert "Fallback content" in output


def test_render_invalid_node():
    """Test that invalid nodes raise TypeError."""
    renderer = AsciiDoctypeRenderer(target_format="html5")
    with pytest.raises(TypeError):
        renderer.render("not a dict")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        renderer.render({})


def test_render_error_wrapping():
    """Test that rendering errors are wrapped in AsciiDoctypeRenderingError."""
    renderer = AsciiDoctypeRenderer(target_format="html5")

    class BrokenTemplate:
        def __call__(self, **kwargs):
            raise RuntimeError("Template broke")

    renderer.loader = {"broken.html": BrokenTemplate()}  # type: ignore[assignment]
    with pytest.raises(AsciiDoctypeRenderingError) as exc_info:
        renderer.render({"name": "broken"})
    assert "Critical rendering failure" in str(exc_info.value)
    assert "broken" in str(exc_info.value)
