"""TCK Integration tests for special blocks in HTML5 and XHTML."""
from asciidoctrine.lark_parser import parse_to_ast
from asciidoctrine.resolver import ASGResolver, WorkspaceCatalog

from asciidoctype import AsciiDoctypeRenderer


def test_render_special_blocks_html5():
    text = """
--
Open block content
--

[pass]
++++
<div class="custom-raw">Raw HTML</div>
++++

[latexmath]
++++
x^2 + y^2 = z^2
++++

[verse]
____
Verse line 1
Verse line 2
____

....
Literal content block
....

[discrete]
= Floating Heading
"""
    catalog = WorkspaceCatalog()
    ast = parse_to_ast(text)
    asg = ASGResolver(catalog, "test.adoc").resolve(ast)

    renderer = AsciiDoctypeRenderer(target_format="html5")
    output = renderer.render(asg)

    assert '<div class="openblock">' in output
    assert '<div class="custom-raw">Raw HTML</div>' in output
    assert '<math xmlns="http://www.w3.org/1998/Math/MathML"' in output
    assert '<div class="verseblock">' in output
    assert '<pre class="literalblock">' in output
    assert '<h1 class="discrete">' in output or '<h2 class="discrete">' in output


def test_render_special_blocks_xhtml():
    renderer = AsciiDoctypeRenderer(target_format="xhtml")

    # Stem node with asciimath variant fallback test
    node_stem_asciimath = {
        "name": "stem",
        "type": "block",
        "variant": "asciimath",
        "value": "sqrt(x)",
    }
    output = renderer.render(node_stem_asciimath)
    assert '<div class="stemblock">' in output
    assert "sqrt(x)" in output
