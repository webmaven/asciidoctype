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
