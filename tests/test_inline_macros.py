"""TCK Integration tests for inline macros and break nodes in HTML5 and XHTML."""
from asciidoctrine.lark_parser import parse_to_ast
from asciidoctrine.resolver import ASGResolver, WorkspaceCatalog

from asciidoctype import AsciiDoctypeRenderer


def test_render_inline_macros_html5():
    text = """
kbd:[Ctrl+S]

btn:[Save]

menu:File[Save]
"""
    catalog = WorkspaceCatalog()
    ast = parse_to_ast(text)
    asg = ASGResolver(catalog, "test.adoc").resolve(ast)

    renderer = AsciiDoctypeRenderer(target_format="html5")
    output = renderer.render(asg)

    assert "<kbd>" in output
    assert '<b class="button">' in output or '<kbd class="button">' in output
    assert '<span class="menuseq">' in output or "File" in output


def test_render_breaks_and_callout_xhtml():
    renderer = AsciiDoctypeRenderer(target_format="xhtml")

    node_break = {"name": "break", "type": "inline"}
    node_thematic = {"name": "thematic_break", "type": "block"}
    node_page = {"name": "page_break", "type": "block"}
    node_callout = {"name": "callout", "type": "inline", "number": 1}

    out_break = renderer.render(node_break)
    out_thematic = renderer.render(node_thematic)
    out_page = renderer.render(node_page)
    out_callout = renderer.render(node_callout)

    assert out_break.strip() == "<br />"
    assert out_thematic.strip() == "<hr />"
    assert 'style="break-after: page;"' in out_page or 'class="page-break"' in out_page
    assert 'class="conum"' in out_callout
