"""Tests for ref and footnote inline node rendering in HTML5 and XHTML."""

from asciidoctype import AsciiDoctypeRenderer


def test_render_ref_link_html5():
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "ref",
        "type": "inline",
        "variant": "link",
        "target": "https://asciidoc.org",
        "inlines": [{"name": "text", "type": "string", "value": "AsciiDoc Site"}],
    }
    output = renderer.render(node)
    assert '<a href="https://asciidoc.org">AsciiDoc Site</a>' in output


def test_render_ref_xref_xhtml():
    renderer = AsciiDoctypeRenderer(target_format="xhtml")
    node = {
        "name": "ref",
        "type": "inline",
        "variant": "xref",
        "target": "#section-1",
        "inlines": [{"name": "text", "type": "string", "value": "Section 1"}],
    }
    output = renderer.render(node)
    assert '<a href="#section-1" class="xref">Section 1</a>' in output


def test_render_footnote_html5():
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "footnote",
        "type": "inline",
        "id": "fn-1",
        "number": 1,
        "value": "Footnote text.",
    }
    output = renderer.render(node)
    expected_footnote = (
        '<sup class="footnote" id="_footnote_fn-1"><a href="#_footnotedef_1">1</a></sup>'
    )
    assert expected_footnote in output
