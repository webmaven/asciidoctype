"""Tests for native MathML rendering of AsciiMath and LaTeX math in STEM blocks and inlines."""

import pytest
from asciidoctrine.lark_parser import parse_to_ast
from asciidoctrine.resolver import ASGResolver, WorkspaceCatalog

from asciidoctype import AsciiDoctypeRenderer


def _resolve_adoc(text: str):
    catalog = WorkspaceCatalog()
    ast = parse_to_ast(text)
    return ASGResolver(catalog, "test.adoc").resolve(ast)


@pytest.mark.parametrize("target_format", ["html5", "xhtml"])
def test_stem_block_asciimath(target_format: str):
    """Test block stem with variant='asciimath' renders native MathML in both HTML5 and XHTML."""
    renderer = AsciiDoctypeRenderer(target_format=target_format)
    node = {
        "name": "stem",
        "type": "block",
        "variant": "asciimath",
        "value": "x^2 + y^2 = z^2",
    }
    output = renderer.render(node)
    assert '<div class="stemblock">' in output
    assert '<div class="content">' in output
    assert '<math xmlns="http://www.w3.org/1998/Math/MathML"' in output
    assert "<msup>" in output
    assert "<mi>x</mi>" in output


@pytest.mark.parametrize("target_format", ["html5", "xhtml"])
def test_stem_block_asciimath_with_inlines(target_format: str):
    """Test block stem with inlines rendering native MathML."""
    renderer = AsciiDoctypeRenderer(target_format=target_format)
    node = {
        "name": "stem",
        "type": "block",
        "variant": "asciimath",
        "inlines": [{"name": "text", "type": "string", "value": "sqrt(x)"}],
    }
    output = renderer.render(node)
    assert '<div class="stemblock">' in output
    assert '<math xmlns="http://www.w3.org/1998/Math/MathML"' in output
    assert "<msqrt>" in output


@pytest.mark.parametrize("target_format", ["html5", "xhtml"])
def test_stem_inline_asciimath(target_format: str):
    """Test inline stem with variant='asciimath' renders native MathML in both HTML5 and XHTML."""
    renderer = AsciiDoctypeRenderer(target_format=target_format)
    node = {
        "name": "stem",
        "type": "inline",
        "variant": "asciimath",
        "value": "sqrt(x)",
    }
    output = renderer.render(node)
    assert '<span class="stem">' in output
    assert '<math xmlns="http://www.w3.org/1998/Math/MathML"' in output
    assert "<msqrt>" in output
    assert "<mi>x</mi>" in output


@pytest.mark.parametrize("target_format", ["html5", "xhtml"])
def test_passthrough_asciimath_block(target_format: str):
    """Test passthrough block with style='asciimath' renders MathML inside a stemblock."""
    renderer = AsciiDoctypeRenderer(target_format=target_format)
    node = {
        "name": "passthrough",
        "type": "block",
        "attributes": {"style": "asciimath"},
        "value": "x^2 + y^2 = z^2",
    }
    output = renderer.render(node)
    assert '<div class="stemblock">' in output
    assert '<math xmlns="http://www.w3.org/1998/Math/MathML"' in output
    assert "<msup>" in output


@pytest.mark.parametrize("target_format", ["html5", "xhtml"])
def test_passthrough_asciimath_block_inlines(target_format: str):
    """Test passthrough block with style='asciimath' having inlines renders MathML."""
    renderer = AsciiDoctypeRenderer(target_format=target_format)
    node = {
        "name": "passthrough",
        "type": "block",
        "attributes": {"style": "asciimath"},
        "inlines": [{"name": "text", "type": "string", "value": "sqrt(16) = 4"}],
    }
    output = renderer.render(node)
    assert '<div class="stemblock">' in output
    assert '<math xmlns="http://www.w3.org/1998/Math/MathML"' in output
    assert "<msqrt>" in output


@pytest.mark.parametrize("target_format", ["html5", "xhtml"])
def test_passthrough_asciimath_multi_inlines_single_math(target_format: str):
    """Test passthrough asciimath with multi-token inlines renders single MathML."""
    renderer = AsciiDoctypeRenderer(target_format=target_format)
    node = {
        "name": "passthrough",
        "type": "block",
        "attributes": {"style": "asciimath"},
        "inlines": [
            {"name": "text", "type": "string", "value": "x^2"},
            {"name": "text", "type": "string", "value": " + "},
            {"name": "text", "type": "string", "value": "y^2"},
        ],
    }
    output = renderer.render(node)
    assert output.count('<math xmlns="http://www.w3.org/1998/Math/MathML"') == 1
    assert "<msup>" in output


@pytest.mark.parametrize("target_format", ["html5", "xhtml"])
def test_passthrough_latexmath_multi_inlines_single_math(target_format: str):
    """Test passthrough latexmath with multi-token inlines renders single MathML."""
    renderer = AsciiDoctypeRenderer(target_format=target_format)
    node = {
        "name": "passthrough",
        "type": "block",
        "attributes": {"style": "latexmath"},
        "inlines": [
            {"name": "text", "type": "string", "value": r"\frac{a}"},
            {"name": "text", "type": "string", "value": r"{b}"},
        ],
    }
    output = renderer.render(node)
    assert output.count('<math xmlns="http://www.w3.org/1998/Math/MathML"') == 1
    assert "<mfrac>" in output


@pytest.mark.parametrize("target_format", ["html5", "xhtml"])
def test_stem_latexmath_block_and_inline(target_format: str):
    """Test latexmath block and inline continue to render MathML via latex2mathml."""
    renderer = AsciiDoctypeRenderer(target_format=target_format)

    # Block latexmath
    node_block = {
        "name": "stem",
        "type": "block",
        "variant": "latexmath",
        "value": r"\frac{a}{b}",
    }
    output_block = renderer.render(node_block)
    assert '<div class="stemblock">' in output_block
    assert '<math xmlns="http://www.w3.org/1998/Math/MathML"' in output_block
    assert "<mfrac>" in output_block

    # Inline latexmath
    node_inline = {
        "name": "stem",
        "type": "inline",
        "variant": "latexmath",
        "value": r"\alpha + \beta",
    }
    output_inline = renderer.render(node_inline)
    assert '<span class="stem">' in output_inline
    assert '<math xmlns="http://www.w3.org/1998/Math/MathML"' in output_inline
    assert "&#x003B1;" in output_inline or "α" in output_inline


@pytest.mark.parametrize("target_format", ["html5", "xhtml"])
def test_stem_unrecognized_variant_fallback(target_format: str):
    """Test stem with unrecognized variant falls back to raw content/inlines."""
    renderer = AsciiDoctypeRenderer(target_format=target_format)

    node_block = {
        "name": "stem",
        "type": "block",
        "variant": "custommath",
        "value": "custom_raw_equation",
    }
    output_block = renderer.render(node_block)
    assert '<div class="stemblock">' in output_block
    assert "<math" not in output_block
    assert "custom_raw_equation" in output_block

    node_inline = {
        "name": "stem",
        "type": "inline",
        "variant": "custommath",
        "value": "inline_custom_raw",
    }
    output_inline = renderer.render(node_inline)
    assert '<span class="stem">' in output_inline
    assert "<math" not in output_inline
    assert "inline_custom_raw" in output_inline


def test_real_adoc_asciimath_rendering_html5():
    """Integration test: AsciiDoc source with [stem], [asciimath], and stem:[] inline."""
    doc = """
[stem]
++++
sqrt(x)
++++

[asciimath]
++++
x^2 + y^2 = z^2
++++

Inline math stem:[x / y] here.
"""
    asg = _resolve_adoc(doc)
    renderer = AsciiDoctypeRenderer(target_format="html5")
    output = renderer.render(asg)

    # 3 math elements rendered
    assert output.count('<math xmlns="http://www.w3.org/1998/Math/MathML"') == 3
    assert "<msqrt>" in output
    assert "<msup>" in output
    assert "<mfrac>" in output
