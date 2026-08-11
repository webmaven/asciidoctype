"""Integration tests for description list and callout list rendering in HTML5 and XHTML."""

from asciidoctrine.lark_parser import parse_to_ast
from asciidoctrine.resolver import ASGResolver

from asciidoctype import AsciiDoctypeRenderer


def test_description_and_callout_list_html5():
    doc_text = """First Term:: Description text

<1> Callout item text
"""
    ast = parse_to_ast(doc_text)
    resolver = ASGResolver(ast)
    asg = resolver.resolve(ast)

    renderer = AsciiDoctypeRenderer(target_format="html5")
    output = renderer.render(asg)

    assert '<dl class="dlist">' in output
    assert "<dt>First Term</dt>" in output
    assert "<dd>" in output
    assert "Description text" in output
    assert "</dd>" in output
    assert "</dl>" in output

    assert '<ol class="colist">' in output
    assert "<li>" in output
    assert "Callout item text" in output
    assert "</li>" in output
    assert "</ol>" in output


def test_description_and_callout_list_xhtml():
    doc_text = """First Term:: Description text

<1> Callout item text
"""
    ast = parse_to_ast(doc_text)
    resolver = ASGResolver(ast)
    asg = resolver.resolve(ast)

    renderer = AsciiDoctypeRenderer(target_format="xhtml")
    output = renderer.render(asg)

    assert '<dl class="dlist">' in output
    assert "<dt>First Term</dt>" in output
    assert "<dd>" in output
    assert "Description text" in output
    assert "</dd>" in output
    assert "</dl>" in output

    assert '<ol class="colist">' in output
    assert "<li>" in output
    assert "Callout item text" in output
    assert "</li>" in output
    assert "</ol>" in output
