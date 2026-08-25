"""Tests for table node rendering in HTML5 and XHTML."""

from asciidoctype import AsciiDoctypeRenderer


def test_render_table_html5():
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "table",
        "type": "block",
        "attributes": {"id": "table-1", "options": "header", "cols": "1,3"},
        "title": [{"name": "text", "type": "string", "value": "Data Table"}],
        "rows": [
            {
                "name": "row",
                "type": "block",
                "cells": [
                    {
                        "name": "cell",
                        "type": "block",
                        "halign": "left",
                        "valign": "top",
                        "inlines": [{"name": "text", "type": "string", "value": "Col 1"}],
                    },
                    {
                        "name": "cell",
                        "type": "block",
                        "halign": "right",
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
                        "halign": "center",
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
    assert "<colgroup>" in output
    assert '<col style="width: 25%;" />' in output or '<col style="width: 25%;">' in output
    assert '<col style="width: 75%;" />' in output or '<col style="width: 75%;">' in output
    assert "<thead>" in output
    assert '<th class="halign-left valign-top">Col 1</th>' in output
    assert '<th class="halign-right">Col 2</th>' in output
    assert "<tbody>" in output
    assert "<td><p>Cell 1</p></td>" in output
    assert '<td class="halign-center"><p>Cell 2</p></td>' in output


def test_render_table_xhtml():
    renderer = AsciiDoctypeRenderer(target_format="xhtml")
    node = {
        "name": "table",
        "type": "block",
        "attributes": {"cols": "20%,80%"},
        "rows": [
            {
                "name": "row",
                "type": "block",
                "cells": [
                    {
                        "name": "cell",
                        "type": "block",
                        "halign": "center",
                        "inlines": [{"name": "text", "type": "string", "value": "Value 1"}],
                    },
                    {
                        "name": "cell",
                        "type": "block",
                        "inlines": [{"name": "text", "type": "string", "value": "Value 2"}],
                    },
                ],
            }
        ],
    }
    output = renderer.render(node)
    assert 'class="tableblock"' in output
    assert "<colgroup>" in output
    assert '<col style="width: 20%;" />' in output or '<col style="width: 20%;">' in output
    assert '<col style="width: 80%;" />' in output or '<col style="width: 80%;">' in output
    assert '<td class="halign-center">Value 1</td>' in output
    assert "<td>Value 2</td>" in output


def test_render_table_cell_roles_and_alignments():
    for fmt in ("html5", "xhtml"):
        renderer = AsciiDoctypeRenderer(target_format=fmt)
        node = {
            "name": "table",
            "type": "block",
            "attributes": {"cols": "1,1"},
            "rows": [
                {
                    "name": "row",
                    "type": "block",
                    "cells": [
                        {
                            "name": "cell",
                            "type": "block",
                            "halign": "center",
                            "valign": "middle",
                            "attributes": {"role": "custom-cell"},
                            "inlines": [
                                {"name": "text", "type": "string", "value": "Special Cell"}
                            ],
                        },
                        {
                            "name": "cell",
                            "type": "block",
                            "attributes": {"role": "plain-cell"},
                            "inlines": [{"name": "text", "type": "string", "value": "Normal Cell"}],
                        },
                    ],
                }
            ],
        }
        output = renderer.render(node)
        assert 'class="halign-center valign-middle custom-cell"' in output
        assert 'class="plain-cell"' in output


def test_render_table_no_colgroup():
    for fmt in ("html5", "xhtml"):
        renderer = AsciiDoctypeRenderer(target_format=fmt)
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
                            "inlines": [{"name": "text", "type": "string", "value": "Simple Cell"}],
                        }
                    ],
                }
            ],
        }
        output = renderer.render(node)
        assert "<colgroup>" not in output
        assert "<td>Simple Cell</td>" in output


def test_extract_col_widths():
    renderer = AsciiDoctypeRenderer()

    # Proportions: 1 + 3 + 1 = 5
    assert renderer.extract_col_widths({"attributes": {"cols": "1,3,1"}}) == ["20%", "60%", "20%"]

    # Explicit percentages
    assert renderer.extract_col_widths({"attributes": {"cols": "20%,80%"}}) == ["20%", "80%"]

    # Equal columns / repeat multiplier
    assert renderer.extract_col_widths({"attributes": {"cols": "3*"}}) == [
        "33.3333%",
        "33.3333%",
        "33.3333%",
    ]

    # Multiplier with width
    assert renderer.extract_col_widths({"attributes": {"cols": "2*1,2"}}) == ["25%", "25%", "50%"]

    # Alignment and style specifiers
    assert renderer.extract_col_widths({"attributes": {"cols": ">1s,^3e,<1"}}) == [
        "20%",
        "60%",
        "20%",
    ]

    # Structured columns list (specification-compliant ASG)
    assert renderer.extract_col_widths({"columns": [{"width": "20%"}, {"width": "80%"}]}) == [
        "20%",
        "80%",
    ]
    assert renderer.extract_col_widths({"columns": [{"width": 1}, {"width": 3}, {"width": 1}]}) == [
        "20%",
        "60%",
        "20%",
    ]

    # Empty or missing attributes
    assert renderer.extract_col_widths({}) == []
    assert renderer.extract_col_widths({"attributes": {}}) == []
    assert renderer.extract_col_widths({"attributes": {"cols": ""}}) == []
