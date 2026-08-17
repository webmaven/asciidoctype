"""Tests for HTML5 listing and document root rendering."""

from asciidoctype import AsciiDoctypeRenderer


def test_render_listing_node():
    """Test listing block rendering with language syntax highlighting and title."""
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "listing",
        "type": "block",
        "form": "delimited",
        "delimiter": "----",
        "attributes": {"id": "listing-1", "language": "python"},
        "title": [{"name": "text", "type": "string", "value": "Example Code"}],
        "inlines": [
            {"name": "text", "type": "string", "value": "def hello():\n    print('world')"}
        ],
    }
    output = renderer.render(node)
    assert '<div class="listingblock" id="listing-1">' in output
    assert '<div class="title">Example Code</div>' in output
    expected_code = (
        '<pre class="highlight python">'
        "<code class=\"language-python\">def hello():\n    print('world')</code></pre>"
    )
    assert expected_code in output


def test_render_document_node():
    """Test document root rendering with DOCTYPE, head, body, header and content blocks."""
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "document",
        "type": "block",
        "header": {"title": "Test Document Title"},
        "blocks": [
            {
                "name": "paragraph",
                "type": "block",
                "attributes": {},
                "inlines": [{"name": "text", "type": "string", "value": "Hello world!"}],
            }
        ],
    }
    output = renderer.render(node)
    assert "<!DOCTYPE html>" in output
    assert '<html lang="en">' in output
    assert "<title>Test Document Title</title>" in output
    expected_header = '<div id="header">\n        <h1>Test Document Title</h1>\n    </div>'
    assert expected_header in output or "<h1>Test Document Title</h1>" in output
    assert "Hello world!" in output
