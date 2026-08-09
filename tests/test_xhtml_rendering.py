"""Tests for XHTML Strict rendering pipeline."""
import pytest
from asciidoctype import AsciiDoctypeRenderer


def test_render_xhtml_document_node():
    """Test XHTML document node rendering includes XML declaration, XHTML Strict DOCTYPE, namespace and meta tag."""
    renderer = AsciiDoctypeRenderer(target_format="xhtml")
    node = {
        "name": "document",
        "type": "block",
        "header": {"title": "Strict XHTML Document Title"},
        "blocks": [
            {
                "name": "paragraph",
                "type": "block",
                "attributes": {},
                "inlines": [{"name": "text", "type": "string", "value": "XHTML content."}],
            }
        ],
    }
    output = renderer.render(node)
    assert '<?xml version="1.0" encoding="UTF-8"?>' in output
    assert '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"' in output
    assert '<html xmlns="http://www.w3.org/1999/xhtml"' in output
    assert '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />' in output
    assert "Strict XHTML Document Title" in output
    assert "XHTML content." in output


def test_render_xhtml_paragraph_and_span():
    """Test paragraph and span rendering in XHTML format."""
    renderer = AsciiDoctypeRenderer(target_format="xhtml")
    node = {
        "name": "paragraph",
        "type": "block",
        "attributes": {"id": "p-xhtml"},
        "inlines": [
            {
                "name": "span",
                "type": "inline",
                "variant": "strong",
                "inlines": [{"name": "text", "type": "string", "value": "Strict Bold"}],
            }
        ],
    }
    output = renderer.render(node)
    assert '<p id="p-xhtml" class="">' in output
    assert "<strong>Strict Bold</strong>" in output
