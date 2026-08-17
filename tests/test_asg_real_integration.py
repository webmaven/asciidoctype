"""Integration tests parsing AsciiDoc with AsciiDoctrine and rendering ASG with AsciiDoctype."""

from asciidoctrine.lark_parser import parse_to_ast
from asciidoctrine.resolver import ASGResolver, WorkspaceCatalog

from asciidoctype import AsciiDoctypeRenderer


def resolve_adoc(doc: str) -> dict:
    """Helper to parse AsciiDoc into AST and resolve into ASG."""
    catalog = WorkspaceCatalog()
    ast = parse_to_ast(doc)
    return ASGResolver(catalog, "test.adoc").resolve(ast)


def test_real_table_rendering_html5():
    """Test rendering of an AsciiDoc table parsed into real ASG."""
    doc = """
[options="header"]
|===
|Header A |Header B

|Cell 1 |Cell 2
|===
"""
    asg = resolve_adoc(doc)
    renderer = AsciiDoctypeRenderer(target_format="html5")
    output = renderer.render(asg)

    assert '<table class="tableblock">' in output
    assert "<thead>" in output
    assert "<th>Header A</th>" in output
    assert "<th>Header B</th>" in output
    assert "<tbody>" in output
    assert "<td><p>Cell 1</p></td>" in output or "<td>Cell 1</td>" in output
    assert "<td><p>Cell 2</p></td>" in output or "<td>Cell 2</td>" in output


def test_real_table_rendering_xhtml():
    """Test rendering of an AsciiDoc table parsed into real ASG in XHTML target."""
    doc = """
|===
|Alpha |Beta
|===
"""
    asg = resolve_adoc(doc)
    renderer = AsciiDoctypeRenderer(target_format="xhtml")
    output = renderer.render(asg)

    assert '<table class="tableblock">' in output
    assert "Alpha" in output
    assert "Beta" in output


def test_real_button_macro_html5():
    """Test button macro btn:[Save] rendering actual button label text."""
    doc = "Click btn:[Save] to finish."
    asg = resolve_adoc(doc)
    renderer = AsciiDoctypeRenderer(target_format="html5")
    output = renderer.render(asg)

    assert '<b class="button">Save</b>' in output


def test_real_kbd_macro_html5():
    """Test kbd macro kbd:[Ctrl+Shift+T] rendering separate key elements."""
    doc = "Press kbd:[Ctrl+Shift+T] to reopen."
    asg = resolve_adoc(doc)
    renderer = AsciiDoctypeRenderer(target_format="html5")
    output = renderer.render(asg)

    assert "<kbd>Ctrl</kbd>" in output
    assert "<kbd>Shift</kbd>" in output
    assert "<kbd>T</kbd>" in output
    assert "['Ctrl'" not in output  # Ensure raw Python repr is not emitted


def test_real_stem_block_and_inline_html5():
    """Test block and inline STEM formulas rendering with proper content and tags."""
    doc_block = """
[stem]
++++
x + y = z
++++
"""
    asg_block = resolve_adoc(doc_block)
    renderer = AsciiDoctypeRenderer(target_format="html5")
    out_block = renderer.render(asg_block)

    assert '<div class="stemblock">' in out_block
    assert "x + y = z" in out_block

    doc_inline = "Inline math stem:[sqrt(4) = 2] here."
    asg_inline = resolve_adoc(doc_inline)
    out_inline = renderer.render(asg_inline)

    assert "sqrt(4) = 2" in out_inline
    assert '<div class="stemblock">' not in out_inline


def test_real_image_block_and_inline_html5():
    """Test block image vs inline image rendering distinction."""
    doc_block = "image::diagram.png[Architecture Diagram, 600, 400]"
    asg_block = resolve_adoc(doc_block)
    renderer = AsciiDoctypeRenderer(target_format="html5")
    out_block = renderer.render(asg_block)

    assert '<div class="imageblock">' in out_block
    assert 'src="diagram.png"' in out_block

    doc_inline = "An icon image:icon.png[Icon] in text."
    asg_inline = resolve_adoc(doc_inline)
    out_inline = renderer.render(asg_inline)

    assert 'src="icon.png"' in out_inline
    assert '<span class="image">' in out_inline or '<span class="image-inline">' in out_inline
    assert '<div class="imageblock">' not in out_inline


def test_real_footnote_html5():
    """Test footnote macro rendering footnote reference element."""
    doc = "Statement footnote:[Important detail]."
    asg = resolve_adoc(doc)
    renderer = AsciiDoctypeRenderer(target_format="html5")
    output = renderer.render(asg)

    assert '<sup class="footnote">' in output or 'class="footnote"' in output
    assert "Important detail" in output
