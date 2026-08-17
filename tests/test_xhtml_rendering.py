"""Tests for XHTML Strict rendering pipeline."""

from asciidoctype import AsciiDoctypeRenderer


def test_render_xhtml_document_node():
    """Test XHTML document node rendering includes XML declaration, DOCTYPE, and namespace."""
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
    assert 'id="p-xhtml"' in output
    assert "<strong>Strict Bold</strong>" in output


def test_render_xhtml_listing_node():
    """Test listing block rendering in XHTML format."""
    renderer = AsciiDoctypeRenderer(target_format="xhtml")
    node = {
        "name": "listing",
        "type": "block",
        "form": "delimited",
        "delimiter": "----",
        "attributes": {"id": "listing-xhtml", "language": "python"},
        "title": [{"name": "text", "type": "string", "value": "XHTML Code"}],
        "inlines": [{"name": "text", "type": "string", "value": "x = 42\nprint(x)"}],
    }
    output = renderer.render(node)
    assert '<div class="listingblock" id="listing-xhtml">' in output
    assert '<div class="title">XHTML Code</div>' in output
    expected_code = (
        '<pre class="highlight python"><code class="language-python">x = 42\nprint(x)</code></pre>'
    )
    assert expected_code in output
