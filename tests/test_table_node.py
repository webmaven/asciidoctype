"""Tests for table node rendering in HTML5 and XHTML."""

from asciidoctype import AsciiDoctypeRenderer


def test_render_table_html5():
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "table",
        "type": "block",
        "attributes": {"id": "table-1", "options": "header"},
        "title": [{"name": "text", "type": "string", "value": "Data Table"}],
        "rows": [
            {
                "name": "row",
                "type": "block",
                "cells": [
                    {
                        "name": "cell",
                        "type": "block",
                        "inlines": [{"name": "text", "type": "string", "value": "Col 1"}],
                    },
                    {
                        "name": "cell",
                        "type": "block",
                        "inlines": [{"name": "text", "type": "string", "value": "Col 2"}],
                    },
                ],
            },
            {
                "name": "row",
                "type": "block",
                "cells": [
                    {
                        "name": "cell",
                        "type": "block",
                        "blocks": [
                            {
                                "name": "paragraph",
                                "type": "block",
                                "inlines": [{"name": "text", "type": "string", "value": "Cell 1"}],
                            }
                        ],
                    },
                    {
                        "name": "cell",
                        "type": "block",
                        "blocks": [
                            {
                                "name": "paragraph",
                                "type": "block",
                                "inlines": [{"name": "text", "type": "string", "value": "Cell 2"}],
                            }
                        ],
                    },
                ],
            },
        ],
    }
    output = renderer.render(node)
    assert 'class="tableblock"' in output
    assert 'id="table-1"' in output
    assert "Data Table" in output
    assert "<thead>" in output
    assert "<th>Col 1</th>" in output
    assert "<tbody>" in output
    assert "<td><p>Cell 1</p></td>" in output


def test_render_table_xhtml():
    renderer = AsciiDoctypeRenderer(target_format="xhtml")
    node = {
        "name": "table",
        "type": "block",
        "rows": [
            {
                "name": "row",
                "type": "block",
                "cells": [
                    {
                        "name": "cell",
                        "type": "block",
                        "inlines": [{"name": "text", "type": "string", "value": "Value 1"}],
                    }
                ],
            }
        ],
    }
    output = renderer.render(node)
    assert 'class="tableblock"' in output
    assert "<td>Value 1</td>" in output
