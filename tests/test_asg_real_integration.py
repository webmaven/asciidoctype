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


def test_real_table_cols_proportions_html5_and_xhtml():
    """Test real AsciiDoc table relative column proportions colgroup in HTML5 and XHTML."""
    doc = """
[cols="1,3,1", options="header"]
|===
|Header A |Header B |Header C

|Cell 1 |Cell 2 |Cell 3
|===
"""
    asg = resolve_adoc(doc)
    for fmt in ("html5", "xhtml"):
        renderer = AsciiDoctypeRenderer(target_format=fmt)
        output = renderer.render(asg)

        assert '<table class="tableblock">' in output
        assert "<colgroup>" in output
        assert '<col style="width: 20%;" />' in output or '<col style="width: 20%;">' in output
        assert '<col style="width: 60%;" />' in output or '<col style="width: 60%;">' in output
        assert "<thead>" in output
        assert "<th>Header A</th>" in output
        assert "<th>Header B</th>" in output
        assert "<th>Header C</th>" in output
        assert "<tbody>" in output
        assert "Cell 1" in output
        assert "Cell 2" in output
        assert "Cell 3" in output


def test_real_table_cols_percentages_html5_and_xhtml():
    """Test real AsciiDoc table percentage column widths colgroup in HTML5 and XHTML."""
    doc = """
[cols="20%,80%"]
|===
|Col 1 |Col 2

|Data 1 |Data 2
|===
"""
    asg = resolve_adoc(doc)
    for fmt in ("html5", "xhtml"):
        renderer = AsciiDoctypeRenderer(target_format=fmt)
        output = renderer.render(asg)

        assert '<table class="tableblock">' in output
        assert "<colgroup>" in output
        assert '<col style="width: 20%;" />' in output or '<col style="width: 20%;">' in output
        assert '<col style="width: 80%;" />' in output or '<col style="width: 80%;">' in output
        assert "<tbody>" in output
        assert "Col 1" in output
        assert "Col 2" in output
        assert "Data 1" in output
        assert "Data 2" in output


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


def test_real_asciidoctrine_source_highlighting():
    """Test AsciiDoctrine real parsed ASG source block with custom highlighter."""
    doc = """
[source,python]
----
def greet(name: str):
    return f"Hello, {name}"
----
"""
    asg = resolve_adoc(doc)

    def pygments_like_highlighter(code: str, lang: str) -> str:
        return f'<div class="highlighted-code lang-{lang}">{code.strip()}</div>'

    renderer = AsciiDoctypeRenderer(target_format="html5", highlighter=pygments_like_highlighter)
    html = renderer.render(asg)
    expected = (
        '<div class="highlighted-code lang-python">'
        'def greet(name: str):\n    return f"Hello, {name}"</div>'
    )
    assert expected in html


def test_real_multiline_list_items_html5():
    """Test AsciiDoctrine 0.2.0a7 multiline principal text in list items."""
    doc = """
* Primary line of first item
  continued multiline description on subsequent line
* Second item
"""
    asg = resolve_adoc(doc)
    renderer = AsciiDoctypeRenderer(target_format="html5")
    html = renderer.render(asg)

    assert '<ul class="ulist">' in html
    expected_item = (
        "<li>Primary line of first item\ncontinued multiline description on subsequent line</li>"
    )
    assert expected_item in html
    assert "<li>Second item</li>" in html


def test_real_backslash_escaped_inlines_html5():
    """Test AsciiDoctrine 0.2.0a7 backslash escaping for inline formatting delimiters."""
    doc = """
Here is \\*not bold*, \\_not italic_, and \\`not monospace`.
"""
    asg = resolve_adoc(doc)
    renderer = AsciiDoctypeRenderer(target_format="html5")
    html = renderer.render(asg)

    assert "<strong>" not in html
    assert "<em>" not in html
    assert "<code>" not in html
    assert "*not bold*" in html
    assert "_not italic_" in html
    assert "`not monospace`" in html
