"""Dual-target (HTML5 and XHTML) matrix parity tests with DOM parsing validation."""

import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

import pytest

from asciidoctype import AsciiDoctypeRenderer


class StrictHTMLValidator(HTMLParser):
    """Validates that HTML tags are properly balanced and well-formed."""

    VOID_TAGS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() not in self.VOID_TAGS:
            self.stack.append(tag.lower())

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in self.VOID_TAGS:
            return
        if not self.stack:
            self.errors.append(f"Unexpected closing tag </{tag}> with empty stack")
        elif self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.errors.append(f"Mismatched closing tag </{tag}>, expected </{self.stack[-1]}>")


def validate_markup(output: str, target_format: str) -> None:
    """Validate output well-formedness using XML parser for XHTML and HTMLParser for HTML5."""
    if target_format == "xhtml":
        # If output is a full XHTML document, parse directly or strip prolog
        if "<?xml" in output:
            # Full document
            try:
                # Strip DOCTYPE for standalone ElementTree parse if needed
                clean_xml = re.sub(r"<!DOCTYPE[^>]+>", "", output)
                ET.fromstring(clean_xml)
            except ET.ParseError as err:
                pytest.fail(
                    f"XHTML document failed XML well-formedness: {err}\nOutput was:\n{output}"
                )
        else:
            # Fragment: wrap in XML root
            xml_doc = f'<root xmlns="http://www.w3.org/1999/xhtml">\n{output}\n</root>'
            try:
                ET.fromstring(xml_doc)
            except ET.ParseError as err:
                pytest.fail(
                    f"XHTML fragment failed XML well-formedness: {err}\nOutput was:\n{output}"
                )
    else:
        validator = StrictHTMLValidator()
        validator.feed(output)
        validator.close()
        if validator.errors:
            pytest.fail(f"HTML5 tag balance errors: {validator.errors}\nOutput was:\n{output}")


@pytest.mark.parametrize("target_format", ["html5", "xhtml"])
def test_matrix_document_and_section(target_format: str):
    renderer = AsciiDoctypeRenderer(target_format=target_format)
    node = {
        "name": "document",
        "type": "block",
        "title": [{"name": "text", "type": "string", "value": "Document Title"}],
        "blocks": [
            {
                "name": "section",
                "type": "block",
                "level": 1,
                "title": [{"name": "text", "type": "string", "value": "Section One"}],
                "blocks": [
                    {
                        "name": "paragraph",
                        "type": "block",
                        "inlines": [{"name": "text", "type": "string", "value": "Paragraph text"}],
                    }
                ],
            }
        ],
    }
    output = renderer.render(node)
    assert "Document Title" in output
    assert "Section One" in output
    assert "Paragraph text" in output
    validate_markup(output, target_format)


@pytest.mark.parametrize("target_format", ["html5", "xhtml"])
def test_matrix_blocks_core(target_format: str):
    renderer = AsciiDoctypeRenderer(target_format=target_format)

    nodes = [
        {
            "name": "admonition",
            "type": "block",
            "variant": "note",
            "blocks": [
                {
                    "name": "paragraph",
                    "type": "block",
                    "inlines": [{"name": "text", "value": "Note text"}],
                }
            ],
        },
        {
            "name": "sidebar",
            "type": "block",
            "title": [{"name": "text", "value": "Sidebar Title"}],
            "blocks": [
                {
                    "name": "paragraph",
                    "type": "block",
                    "inlines": [{"name": "text", "value": "Sidebar body"}],
                }
            ],
        },
        {
            "name": "example",
            "type": "block",
            "title": [{"name": "text", "value": "Example Title"}],
            "blocks": [
                {
                    "name": "paragraph",
                    "type": "block",
                    "inlines": [{"name": "text", "value": "Example content"}],
                }
            ],
        },
        {
            "name": "quote",
            "type": "block",
            "attribution": [{"name": "text", "value": "Author Name"}],
            "blocks": [
                {
                    "name": "paragraph",
                    "type": "block",
                    "inlines": [{"name": "text", "value": "Quote text"}],
                }
            ],
        },
        {
            "name": "verse",
            "type": "block",
            "attribution": [{"name": "text", "value": "Poet"}],
            "blocks": [
                {
                    "name": "paragraph",
                    "type": "block",
                    "inlines": [{"name": "text", "value": "Verse line"}],
                }
            ],
        },
        {
            "name": "open",
            "type": "block",
            "blocks": [
                {
                    "name": "paragraph",
                    "type": "block",
                    "inlines": [{"name": "text", "value": "Open block content"}],
                }
            ],
        },
        {
            "name": "collapsible",
            "type": "block",
            "title": [{"name": "text", "value": "Click to expand"}],
            "blocks": [
                {
                    "name": "paragraph",
                    "type": "block",
                    "inlines": [{"name": "text", "value": "Hidden details"}],
                }
            ],
        },
        {
            "name": "listing",
            "type": "block",
            "attributes": {"language": "python"},
            "title": [{"name": "text", "value": "Code snippet"}],
            "inlines": [{"name": "text", "value": "def hello():\n    return 'world'"}],
        },
        {
            "name": "literal",
            "type": "block",
            "inlines": [{"name": "text", "value": "Literal monospaced block"}],
        },
    ]

    for node in nodes:
        out = renderer.render(node)
        assert len(out) > 0
        validate_markup(out, target_format)


@pytest.mark.parametrize("target_format", ["html5", "xhtml"])
def test_matrix_lists(target_format: str):
    renderer = AsciiDoctypeRenderer(target_format=target_format)

    # Unordered / Ordered list
    list_node = {
        "name": "list",
        "type": "block",
        "variant": "unordered",
        "items": [
            {
                "name": "listItem",
                "type": "block",
                "inlines": [{"name": "text", "value": "Item 1"}],
            },
            {
                "name": "listItem",
                "type": "block",
                "inlines": [{"name": "text", "value": "Item 2"}],
            },
        ],
    }
    out_list = renderer.render(list_node)
    assert '<ul class="ulist">' in out_list or "<ul>" in out_list
    assert "<li>Item 1</li>" in out_list
    validate_markup(out_list, target_format)

    # Description list
    dlist_node = {
        "name": "descriptionList",
        "type": "block",
        "items": [
            {
                "name": "descriptionListItem",
                "type": "block",
                "terms": [
                    {
                        "name": "descriptionListTerm",
                        "type": "inline",
                        "inlines": [{"name": "text", "value": "Term 1"}],
                    }
                ],
                "description": [
                    {
                        "name": "paragraph",
                        "type": "block",
                        "inlines": [{"name": "text", "value": "Desc 1"}],
                    }
                ],
            }
        ],
    }
    out_dlist = renderer.render(dlist_node)
    assert "<dl" in out_dlist
    validate_markup(out_dlist, target_format)

    # Callout list
    colist_node = {
        "name": "calloutList",
        "type": "block",
        "items": [
            {
                "name": "calloutListItem",
                "type": "block",
                "inlines": [{"name": "text", "value": "Callout description 1"}],
            }
        ],
    }
    out_colist = renderer.render(colist_node)
    assert '<ol class="colist"' in out_colist or "<ol" in out_colist
    validate_markup(out_colist, target_format)


@pytest.mark.parametrize("target_format", ["html5", "xhtml"])
def test_matrix_table(target_format: str):
    renderer = AsciiDoctypeRenderer(target_format=target_format)
    table_node = {
        "name": "table",
        "type": "block",
        "title": [{"name": "text", "value": "Test Table"}],
        "attributes": {"options": "header"},
        "rows": [
            {
                "name": "row",
                "type": "block",
                "cells": [
                    {
                        "name": "cell",
                        "type": "block",
                        "inlines": [{"name": "text", "value": "Col A"}],
                    },
                    {
                        "name": "cell",
                        "type": "block",
                        "inlines": [{"name": "text", "value": "Col B"}],
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
                                "inlines": [{"name": "text", "value": "Data 1"}],
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
                                "inlines": [{"name": "text", "value": "Data 2"}],
                            }
                        ],
                    },
                ],
            },
        ],
    }
    out = renderer.render(table_node)
    assert "<thead>" in out
    assert "<th>Col A</th>" in out
    assert "<tbody>" in out
    validate_markup(out, target_format)


@pytest.mark.parametrize("target_format", ["html5", "xhtml"])
def test_matrix_inlines_and_media(target_format: str):
    renderer = AsciiDoctypeRenderer(target_format=target_format)

    inlines = [
        {
            "name": "span",
            "type": "inline",
            "variant": "strong",
            "inlines": [{"name": "text", "value": "Bold"}],
        },
        {
            "name": "span",
            "type": "inline",
            "variant": "emphasis",
            "inlines": [{"name": "text", "value": "Italic"}],
        },
        {
            "name": "span",
            "type": "inline",
            "variant": "code",
            "inlines": [{"name": "text", "value": "monospace"}],
        },
        {
            "name": "span",
            "type": "inline",
            "variant": "mark",
            "inlines": [{"name": "text", "value": "highlighted"}],
        },
        {
            "name": "span",
            "type": "inline",
            "variant": "subscript",
            "inlines": [{"name": "text", "value": "2"}],
        },
        {
            "name": "span",
            "type": "inline",
            "variant": "superscript",
            "inlines": [{"name": "text", "value": "10"}],
        },
        {"name": "kbd", "type": "inline", "value": ["Ctrl", "Alt", "Del"]},
        {"name": "button", "type": "inline", "value": "Submit"},
        {
            "name": "menu",
            "type": "inline",
            "menu": "File",
            "submenus": ["Export"],
            "menuitem": "PDF",
        },
        {"name": "callout", "type": "inline", "number": 1},
        {
            "name": "ref",
            "type": "inline",
            "target": "https://example.com",
            "inlines": [{"name": "text", "value": "Link"}],
        },
        {
            "name": "ref",
            "type": "inline",
            "variant": "footnote",
            "inlines": [{"name": "text", "value": "Note text"}],
        },
        {"name": "image", "type": "inline", "target": "icon.png", "attributes": {"alt": "Icon"}},
        {"name": "break", "type": "inline"},
    ]

    for inline in inlines:
        out = renderer.render(inline)
        assert len(out) > 0
        validate_markup(out, target_format)

    media = [
        {
            "name": "image",
            "type": "block",
            "target": "photo.jpg",
            "title": [{"name": "text", "value": "Photo"}],
        },
        {
            "name": "audio",
            "type": "block",
            "target": "audio.mp3",
            "title": [{"name": "text", "value": "Sound"}],
        },
        {
            "name": "video",
            "type": "block",
            "target": "video.mp4",
            "title": [{"name": "text", "value": "Clip"}],
        },
    ]

    for m in media:
        out = renderer.render(m)
        assert len(out) > 0
        validate_markup(out, target_format)
