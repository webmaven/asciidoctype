"""Tests for example and quote node rendering in HTML5 and XHTML."""

from asciidoctype import AsciiDoctypeRenderer


def test_render_example_block_html5():
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "example",
        "type": "block",
        "title": [{"name": "text", "type": "string", "value": "Example 1"}],
        "blocks": [
            {
                "name": "paragraph",
                "type": "block",
                "inlines": [{"name": "text", "type": "string", "value": "Sample output."}],
            }
        ],
    }
    output = renderer.render(node)
    assert 'class="exampleblock"' in output
    assert "Example 1" in output
    assert "<p>Sample output.</p>" in output


def test_render_quote_block_xhtml():
    renderer = AsciiDoctypeRenderer(target_format="xhtml")
    node = {
        "name": "quote",
        "type": "block",
        "attribution": [{"name": "text", "type": "string", "value": "Author Name"}],
        "blocks": [
            {
                "name": "paragraph",
                "type": "block",
                "inlines": [{"name": "text", "type": "string", "value": "Famous quote."}],
            }
        ],
    }
    output = renderer.render(node)
    assert 'class="quoteblock"' in output
    assert "<blockquote>" in output
    assert "<p>Famous quote.</p>" in output
    assert "Author Name" in output
