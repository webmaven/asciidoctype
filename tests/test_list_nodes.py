"""Tests for list and listItem rendering in HTML5 and XHTML."""
from asciidoctype import AsciiDoctypeRenderer


def test_render_unordered_list_html5():
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "list",
        "type": "block",
        "variant": "unordered",
        "items": [
            {
                "name": "listItem",
                "type": "block",
                "principal": [{"name": "text", "type": "string", "value": "Item 1"}],
                "blocks": [],
            },
            {
                "name": "listItem",
                "type": "block",
                "principal": [{"name": "text", "type": "string", "value": "Item 2"}],
                "blocks": [],
            },
        ],
    }
    output = renderer.render(node)
    assert '<ul class="ulist">' in output
    assert "<li>Item 1</li>" in output
    assert "<li>Item 2</li>" in output
    assert "</ul>" in output


def test_render_ordered_list_xhtml():
    renderer = AsciiDoctypeRenderer(target_format="xhtml")
    node = {
        "name": "list",
        "type": "block",
        "variant": "ordered",
        "items": [
            {
                "name": "listItem",
                "type": "block",
                "principal": [{"name": "text", "type": "string", "value": "First"}],
                "blocks": [],
            }
        ],
    }
    output = renderer.render(node)
    assert '<ol class="olist">' in output
    assert "<li>First</li>" in output
    assert "</ol>" in output
