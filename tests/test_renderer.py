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
    with pytest.raises(ValueError, match="target_format must be 'html5' or 'xhtml'"):
        AsciiDoctypeRenderer(target_format="markdown")


def test_renderer_search_paths_string_conversion(tmp_path):
    """Test search_paths accepts string representations of paths."""
    custom_dir = tmp_path / "custom"
    custom_dir.mkdir()
    renderer = AsciiDoctypeRenderer(search_paths=[str(custom_dir)])
    assert any(p == custom_dir for p in renderer.search_paths)


def test_top_level_render_function():
    """Test top-level render() convenience function renders ASG node properly."""
    from asciidoctype import render

    node = {
        "name": "paragraph",
        "type": "block",
        "inlines": [{"name": "text", "value": "Convenience function rendering"}],
    }
    output_html5 = render(node, target_format="html5")
    assert "<p>Convenience function rendering</p>" in output_html5

    output_xhtml = render(node, target_format="xhtml")
    assert "<p>Convenience function rendering</p>" in output_xhtml


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


def test_loader_caching_identical_search_paths():
    """Test renderers with identical search paths share the same PageTemplateLoader."""
    from asciidoctype.renderer import _LOADER_CACHE, clear_loader_cache

    clear_loader_cache()
    renderer1 = AsciiDoctypeRenderer(target_format="html5")
    renderer2 = AsciiDoctypeRenderer(target_format="html5")
    assert renderer1.loader is renderer2.loader
    assert len(_LOADER_CACHE) == 1


def test_loader_caching_different_search_paths(tmp_path):
    """Test that renderers with different search paths get different loader instances."""
    from asciidoctype.renderer import clear_loader_cache

    clear_loader_cache()
    dir1 = tmp_path / "theme1"
    dir2 = tmp_path / "theme2"
    dir1.mkdir()
    dir2.mkdir()

    renderer1 = AsciiDoctypeRenderer(target_format="html5", search_paths=[dir1])
    renderer2 = AsciiDoctypeRenderer(target_format="html5", search_paths=[dir2])
    assert renderer1.loader is not renderer2.loader


def test_clear_loader_cache():
    """Test that clear_loader_cache empties the cache dictionary."""
    from asciidoctype.renderer import _LOADER_CACHE, clear_loader_cache

    clear_loader_cache()
    AsciiDoctypeRenderer(target_format="html5")
    assert len(_LOADER_CACHE) > 0
    clear_loader_cache()
    assert len(_LOADER_CACHE) == 0


def test_renderer_static_url_prefix_default():
    """Test AsciiDoctypeRenderer defaults static_url_prefix to '/'."""
    renderer = AsciiDoctypeRenderer()
    assert renderer.static_url_prefix == "/"


def test_renderer_static_url_prefix_custom():
    """Test AsciiDoctypeRenderer accepts custom static_url_prefix."""
    renderer = AsciiDoctypeRenderer(static_url_prefix="/static/")
    assert renderer.static_url_prefix == "/static/"


def test_top_level_render_static_url_prefix(tmp_path):
    """Test top-level render() accepts static_url_prefix and injects into template ctx."""
    from asciidoctype import render

    custom_tpl_dir = tmp_path / "templates"
    custom_tpl_dir.mkdir()
    tpl_content = "<p class=\"${ctx.get('static_url_prefix')}\">${node.value}</p>"
    (custom_tpl_dir / "paragraph.html").write_text(tpl_content)

    node = {
        "name": "paragraph",
        "value": "Test content",
    }
    output = render(node, search_paths=[custom_tpl_dir], static_url_prefix="/assets/")
    assert '<p class="/assets/">Test content</p>' in output


def test_render_static_url_prefix_in_context(tmp_path):
    """Test static_url_prefix is accessible in template ctx during rendering."""
    custom_tpl_dir = tmp_path / "templates"
    custom_tpl_dir.mkdir()
    tpl_content = "<span data-prefix=\"${ctx['static_url_prefix']}\">${node.value}</span>"
    (custom_tpl_dir / "span.html").write_text(tpl_content)

    renderer = AsciiDoctypeRenderer(search_paths=[custom_tpl_dir], static_url_prefix="/cdn/")
    node = {"name": "span", "value": "Prefix test"}
    output = renderer.render(node)
    assert '<span data-prefix="/cdn/">Prefix test</span>' in output


def test_render_static_url_prefix_context_override(tmp_path):
    """Test explicit context['static_url_prefix'] overrides renderer default and instance prefix."""
    custom_tpl_dir = tmp_path / "templates"
    custom_tpl_dir.mkdir()
    tpl_content = "<span data-prefix=\"${ctx['static_url_prefix']}\">${node.value}</span>"
    (custom_tpl_dir / "span.html").write_text(tpl_content)

    renderer = AsciiDoctypeRenderer(
        search_paths=[custom_tpl_dir], static_url_prefix="/default_prefix/"
    )
    node = {"name": "span", "value": "Override test"}
    output = renderer.render(node, context={"static_url_prefix": "/custom_override/"})
    assert '<span data-prefix="/custom_override/">Override test</span>' in output
