"""Regression tests for showcase gallery generation output.

Verifies that footnotes and container definitions render with exact uniqueness
(no duplicate footnote injection or redundant bibliography sections).
"""

from pathlib import Path

import pytest
from examples.gallery.generate_gallery import (
    OUTPUT_HTML5,
    OUTPUT_XHTML,
    SHOWCASE_SAMPLES,
    generate_gallery_html,
)

from asciidoctype import AsciiDoctypeRenderer


@pytest.mark.parametrize("gallery_path", [OUTPUT_HTML5, OUTPUT_XHTML])
def test_gallery_file_footnote_uniqueness(gallery_path: Path) -> None:
    """Ensure generated gallery HTML files have no duplicate footnote containers or definitions."""
    assert gallery_path.exists(), f"Gallery file {gallery_path} must exist."
    content = gallery_path.read_text(encoding="utf-8")

    footnotes_container_count = content.count('<div id="footnotes"')
    fn_def_1_count = content.count('id="_footnotedef_1"')
    fn_def_2_count = content.count('id="_footnotedef_2"')

    assert footnotes_container_count == 1
    assert fn_def_1_count == 1
    assert fn_def_2_count == 1


@pytest.mark.parametrize("target_format", ["html5", "xhtml"])
def test_generate_gallery_html_footnote_uniqueness(target_format: str) -> None:
    """Ensure generate_gallery_html() produces output without duplicate footnote definitions."""
    output = generate_gallery_html(target_format=target_format)

    footnotes_container_count = output.count('<div id="footnotes"')
    fn_def_1_count = output.count('id="_footnotedef_1"')
    fn_def_2_count = output.count('id="_footnotedef_2"')

    assert footnotes_container_count == 1
    assert fn_def_1_count == 1
    assert fn_def_2_count == 1


@pytest.mark.parametrize("target_format", ["html5", "xhtml"])
def test_footnote_sample_render_output(target_format: str) -> None:
    """Verify that rendering the footnote showcase sample produces singular footnote definitions."""
    footnote_sample = next(s for s in SHOWCASE_SAMPLES if s.get("node_type") == "ref (footnote)")
    from asciidoctrine.lark_parser import parse_to_ast
    from asciidoctrine.resolver import ASGResolver, WorkspaceCatalog

    catalog = WorkspaceCatalog()
    renderer = AsciiDoctypeRenderer(target_format=target_format)
    ast = parse_to_ast(footnote_sample["asciidoc"])
    resolver = ASGResolver(catalog, "test_sample.adoc")
    asg = resolver.resolve(ast)

    rendered = renderer.render(asg)
    assert rendered.count('<div id="footnotes"') == 1
    assert rendered.count('id="_footnotedef_1"') == 1
    assert rendered.count('id="_footnotedef_2"') == 1


@pytest.mark.parametrize("target_format", ["html5", "xhtml"])
def test_sample_13_ordered_list_integrity(target_format: str) -> None:
    """Verify that sample 13 (lists) renders a single continuous ordered list with all 4 items."""
    list_sample = next(s for s in SHOWCASE_SAMPLES if s.get("node_type") == "list & listItem")
    from asciidoctrine.lark_parser import parse_to_ast
    from asciidoctrine.resolver import ASGResolver, WorkspaceCatalog

    catalog = WorkspaceCatalog()
    renderer = AsciiDoctypeRenderer(target_format=target_format)
    ast = parse_to_ast(list_sample["asciidoc"])
    resolver = ASGResolver(catalog, "test_list_sample.adoc")
    asg = resolver.resolve(ast)

    rendered = renderer.render(asg)
    assert rendered.count('<ol class="olist">') == 1
    assert rendered.count("<li>Parse document source into AST</li>") == 1
    assert rendered.count("<li>Resolve AST references into ASG</li>") == 1
    assert rendered.count("<li>Dispatch ASG nodes to Chameleon templates</li>") == 1
    assert rendered.count("<li>Emit valid HTML5 or XHTML</li>") == 1
