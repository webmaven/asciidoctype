#!/usr/bin/env python3
"""Static HTML5 E2E Showcase Gallery Generator.

Generates a standalone, responsive, interactive HTML5 gallery showcasing all
AsciiDoc ASG node types rendered with AsciiDoctype. Built with 100% pure HTML5
and Vanilla CSS3 (Zero JavaScript/TypeScript).
"""

import html
import json
from pathlib import Path
from typing import Any, Dict, List

from asciidoctrine.lark_parser import parse_to_ast
from asciidoctrine.resolver import ASGResolver, WorkspaceCatalog

from asciidoctype import AsciiDoctypeRenderer

GALLERY_DIR = Path(__file__).parent.resolve()
OUTPUT_HTML5 = GALLERY_DIR / "index.html"
OUTPUT_XHTML = GALLERY_DIR / "index-xhtml.html"
CSS_PATH = GALLERY_DIR / "gallery.css"

## Showcase sample definitions across all node categories
SHOWCASE_SAMPLES: List[Dict[str, Any]] = [
    # 1. Structural & Headings
    {
        "category": "Structure",
        "node_type": "document & section",
        "title": "Document Header & Hierarchical Sections",
        "description": (
            "Top-level document structure with title metadata and nested heading levels."
        ),
        "asciidoc": (
            "= Technical Specification & Architecture Manual\n"
            "Author Name <author@example.org>\n"
            "v2.4, 2026-08-15\n\n"
            "== System Architecture Overview\n"
            "This section outlines the primary architectural components of the pipeline.\n\n"
            "=== Rendering Subsystem\n"
            "The rendering subsystem transforms semantic graphs into accessible markup."
        ),
    },
    {
        "category": "Structure",
        "node_type": "floatingTitle",
        "title": "Discrete / Floating Title",
        "description": "Out-of-hierarchy heading rendered as an unindexed discrete section header.",
        "asciidoc": (
            "[discrete]\n"
            "=== Component Interface Summary\n"
            "This standalone heading does not increment chapter numbers or generate TOC entries."
        ),
    },
    # 2. Block Containers
    {
        "category": "Blocks",
        "node_type": "paragraph",
        "title": "Standard Paragraph with Role Attributes",
        "description": (
            "Standard textual body block supporting custom typography roles and inline formatting."
        ),
        "asciidoc": (
            "[.lead]\n"
            "AsciiDoc is a human-readable text document format for writing technical documents.\n\n"
            "Paragraphs flow naturally with automatic word wrapping and full inline markup support."
        ),
    },
    {
        "category": "Blocks",
        "node_type": "admonitions",
        "title": "Semantic Admonition Blocks",
        "description": "Callout panels for notes, tips, warnings, and caution directives.",
        "asciidoc": (
            "[NOTE]\n"
            "====\n"
            "AsciiDoctype renders headless HTML5 and XHTML with zero runtime dependencies.\n"
            "====\n\n"
            "[TIP]\n"
            "====\n"
            "Always run pre-commit quality checks before pushing changes.\n"
            "====\n\n"
            "[IMPORTANT]\n"
            "====\n"
            "Ensure all templates are audited for HTML entity escaping safety.\n"
            "====\n\n"
            "[WARNING]\n"
            "====\n"
            "Misplaced `structure` directives can bypass automatic XSS sanitization.\n"
            "===="
        ),
    },
    {
        "category": "Blocks",
        "node_type": "sidebar",
        "title": "Sidebar Aside Block",
        "description": (
            "Auxiliary informational content visually separated from primary article flow."
        ),
        "asciidoc": (
            ".AsciiDoc Design Philosophy\n"
            "****\n"
            "AsciiDoc separates semantic structure from visual presentation, enabling a single "
            "master document to compile into HTML5, EPUB, PDF, and XHTML.\n"
            "****"
        ),
    },
    {
        "category": "Blocks",
        "node_type": "quote & verse",
        "title": "Blockquote & Poetic Verse",
        "description": "Attributed quotes and whitespace-preserving poetic stanzas.",
        "asciidoc": (
            "[quote, Antoine de Saint-Exupéry, Airman's Odyssey]\n"
            "____\n"
            "Perfection is achieved, not when there is nothing more to add, but when there is "
            "nothing left to take away.\n"
            "____\n\n"
            "[verse, Robert Frost, The Road Not Taken]\n"
            "____\n"
            "Two roads diverged in a yellow wood,\n"
            "And sorry I could not travel both\n"
            "And be one traveler, long I stood\n"
            "And looked down one as far as I could.\n"
            "____"
        ),
    },
    {
        "category": "Blocks",
        "node_type": "example & open",
        "title": "Example Container & Generic Open Block",
        "description": "Numbered example blocks and nested heterogeneous open wrapper containers.",
        "asciidoc": (
            ".AsciiDoc Variable Binding Example\n"
            "====\n"
            "Variables in AsciiDoc are declared with attribute colons, e.g. "
            "`pass:[:version: 1.0.0]`.\n"
            "====\n\n"
            "[open]\n"
            ".Generic Open Wrapper Container\n"
            "~~~~\n"
            "An open block groups multiple heterogeneous blocks under a "
            "single structural container.\n\n"
            "[NOTE]\n"
            "====\n"
            "Open blocks do not enforce rigid semantic rules, making them "
            "versatile layout wrappers.\n"
            "====\n\n"
            "* First nested container feature\n"
            "* Second nested container feature\n"
            "~~~~"
        ),
    },
    {
        "category": "Blocks",
        "node_type": "collapsible",
        "title": "Interactive Collapsible / Accordion Block",
        "description": "Native HTML5 <details> / <summary> expandable drawer.",
        "asciidoc": (
            "[%collapsible]\n"
            ".Click here to view advanced configuration parameters\n"
            "====\n"
            "* *strict*: Enforces fail-fast validation on all nodes.\n"
            "* *max_depth*: Maximum recursion limit (default: 500).\n"
            "* *validate_templates*: Audits custom themes on startup.\n"
            "===="
        ),
    },
    {
        "category": "Blocks",
        "node_type": "listing & literal",
        "title": "Code Listing & Monospaced Literal",
        "description": "Syntax-highlighted code blocks and raw literal text stanzas.",
        "asciidoc": (
            "[source,python]\n"
            ".Pipeline Invocation Example\n"
            "----\n"
            "from asciidoctype import AsciiDoctypeRenderer\n\n"
            'renderer = AsciiDoctypeRenderer(target_format="html5", strict=True)\n'
            "html_result = renderer.render(asg_node)\n"
            "print(html_result)\n"
            "----\n\n"
            "....\n"
            "Configuration payload:\n"
            "  target_format = html5\n"
            "  strict = true\n"
            "...."
        ),
    },
    {
        "category": "Blocks",
        "node_type": "stem & passthrough",
        "title": "Mathematical Equations & Raw Passthrough",
        "description": "AsciiMath / LaTeX formulas with MathML compilation and raw HTML pass.",
        "asciidoc": (
            "[latexmath]\n"
            "++++\n"
            "E = mc^2 \\quad \\text{and} \\quad "
            "\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}\n"
            "++++\n\n"
            "[pass]\n"
            "++++\n"
            '<div style="padding: 1rem; border-left: 4px solid #3b82f6; background: #eff6ff;">\n'
            "    ⚡ Live Passthrough HTML Block with Custom Inline Styling\n"
            "</div>\n"
            "++++"
        ),
    },
    {
        "category": "Blocks",
        "node_type": "thematic_break & page_break",
        "title": "Thematic Breaks & Print Page Dividers",
        "description": "Horizontal thematic dividers and print-targeted page breaks.",
        "asciidoc": (
            "Content above the thematic divider.\n\n"
            "'''\n\n"
            "Content on this page (before print page break).\n\n"
            "<<<\n\n"
            "Content on the following page (after page break)."
        ),
    },
    # 3. Tables
    {
        "category": "Tables",
        "node_type": "table",
        "title": "Data Tables with Headers and Formatting",
        "description": "Multi-column data grids with headers, role styling, and formatted content.",
        "asciidoc": (
            '[cols="2,3,2",options="header",role="table-highlight"]\n'
            ".AsciiDoctype Feature Matrix\n"
            "|===\n"
            "|Feature |Description |Status\n\n"
            "|Headless Dispatch\n"
            "|Template routing driven by node metadata\n"
            "|*Complete*\n\n"
            "|Dual Backends\n"
            "|Native support for HTML5 and strict XHTML\n"
            "|*Complete*\n\n"
            "|Zero JavaScript\n"
            "|100% pure CSS presentation & interactions\n"
            "|*Complete*\n\n"
            "|==="
        ),
    },
    # 4. Lists & Callouts
    {
        "category": "Lists",
        "node_type": "list & listItem",
        "title": "Unordered & Ordered Lists",
        "description": "Bulleted and numbered hierarchical item collections.",
        "asciidoc": (
            "* High Performance Processing\n"
            "* Zero External Runtime Dependencies\n"
            "** Embedded Chameleon ZPT Engine\n"
            "** LaTeX to MathML Native Converter\n"
            "* Type Checked & Strictly Linted\n\n"
            "1. Parse document source into AST\n"
            "2. Resolve AST references into ASG\n"
            "3. Dispatch ASG nodes to Chameleon templates\n"
            "4. Emit valid HTML5 or XHTML"
        ),
    },
    {
        "category": "Lists",
        "node_type": "descriptionList",
        "title": "Description / Definition Lists with Continuation",
        "description": (
            "Term-and-definition glossary structures with multiple continued paragraphs."
        ),
        "asciidoc": (
            "AST (Abstract Syntax Tree)::\n"
            "Raw hierarchical parse tree generated directly by Lark grammar rules.\n"
            "+\n"
            "It preserves concrete syntax tokens and source character offsets before "
            "semantic resolution.\n\n"
            "ASG (Abstract Semantic Graph)::\n"
            "Resolved, fully cross-referenced semantic graph ready for compilation.\n\n"
            "Chameleon::\n"
            "High-speed Python implementation of the Zope Page Template (ZPT) specification."
        ),
    },
    {
        "category": "Lists",
        "node_type": "calloutList & callouts",
        "title": "Code Annotation Callouts",
        "description": "Numbered visual callouts referencing annotated code lines.",
        "asciidoc": (
            "[source,python]\n"
            "----\n"
            "renderer = AsciiDoctypeRenderer() <1>\n"
            "output = renderer.render(node)    <2>\n"
            "----\n"
            "<1> Initialize the renderer with default HTML5 target.\n"
            "<2> Execute recursive template compilation on the root node."
        ),
    },
    # 5. Inlines & Interactive Macros
    {
        "category": "Inlines",
        "node_type": "spans & inline macros",
        "title": "Typography Spans, Badges, Keyboard & Menus",
        "description": (
            "Rich text styling (bold, italic, monospace, mark) and user interface macros."
        ),
        "asciidoc": (
            "Inline text with *bold emphasis*, _italic styling_, `monospace code`, "
            "#highlighted mark#, and H~2~O with x^2^ formulas.\n\n"
            "Press kbd:[Ctrl+Shift+S] to trigger btn:[Save As...] via menu:File[Export > PDF].\n\n"
            "Learn more at https://docs.asciidoctor.org/asciidoc/latest/[AsciiDoc Language Docs]."
        ),
    },
    {
        "category": "Inlines",
        "node_type": "ref (footnote)",
        "title": "Footnote References & Endnote List",
        "description": "Numbered footnote citations linking directly to resolved definitions.",
        "asciidoc": (
            "AsciiDoctype implements the full ASG rendering contract "
            "footnote:[Validated against AsciiDoctrine test suites.].\n\n"
            "Documents compile into strict XML formats "
            "footnote:[Specifically XHTML 1.0 Strict]."
        ),
    },
    # 6. Media
    {
        "category": "Media",
        "node_type": "image (block & inline)",
        "title": "Images and Visual Assets",
        "description": "Block figures with captions and inline icon images.",
        "asciidoc": (
            "image::https://images.unsplash.com/photo-1518770660439-4636190af475?w=800"
            "[Microchip Architecture,800,400]\n\n"
            "You can also embed inline "
            "image:https://images.unsplash.com/photo-1518770660439-4636190af475?w=40[Chip,20,20] "
            "icons within flowing text."
        ),
    },
    {
        "category": "Media",
        "node_type": "audio & video",
        "title": "Audio & Video Media Players",
        "description": "Native HTML5 multimedia elements with player controls.",
        "asciidoc": (
            "video::https://www.w3schools.com/html/mov_bbb.mp4"
            '[width=640,options="controls"]\n\n'
            'audio::https://www.w3schools.com/html/horse.mp3[options="controls"]'
        ),
    },
]


def _enrich_asg(
    s: Dict[str, Any],
    asg: Dict[str, Any],
) -> None:
    """Apply gallery-specific ASG enrichments in-place."""
    pass


def generate_gallery_html(target_format: str = "html5") -> str:
    """Compile all showcase samples into a unified, zero-JS gallery.

    Args:
        target_format: Either ``"html5"`` or ``"xhtml"``.
    """
    catalog = WorkspaceCatalog()
    renderer = AsciiDoctypeRenderer(target_format=target_format)
    is_xhtml = target_format == "xhtml"
    format_label = "XHTML" if is_xhtml else "HTML5"

    css_content = CSS_PATH.read_text(encoding="utf-8")

    # Assign deterministic IDs to all samples
    for idx, s in enumerate(SHOWCASE_SAMPLES, start=1):
        s["id"] = f"sample-{idx}"

    # Build navigation in category order matching document flow
    cards_html: List[str] = []
    nav_links: List[str] = []
    category_order: List[str] = []
    for s in SHOWCASE_SAMPLES:
        if s["category"] not in category_order:
            category_order.append(s["category"])

    for cat in category_order:
        nav_links.append(f'<div class="nav-category-title">{cat}</div>')
        cat_samples = [s for s in SHOWCASE_SAMPLES if s["category"] == cat]
        for s in cat_samples:
            nav_links.append(f'<a href="#{s["id"]}" class="nav-item">{s["title"]}</a>')

    for s in SHOWCASE_SAMPLES:
        sample_id = s["id"]

        # Parse through AsciiDoctrine (fresh ASG per format)
        ast = parse_to_ast(s["asciidoc"])
        resolver = ASGResolver(catalog, f"{sample_id}.adoc")
        asg = resolver.resolve(ast)

        # Apply gallery-specific ASG enrichments
        _enrich_asg(s, asg)

        # Render output
        rendered_output = renderer.render(asg)

        # Format ASG JSON
        asg_json = json.dumps(asg, indent=2)

        # Build pure CSS tab interface
        tab_name = f"tab-{sample_id}"

        adoc_escaped = html.escape(s["asciidoc"].strip())
        asg_escaped = html.escape(asg_json)
        html_escaped = html.escape(rendered_output.strip())

        title_escaped = html.escape(s["title"])
        desc_escaped = html.escape(s["description"])

        card_markup = f"""
        <article id="{sample_id}" class="showcase-card">
            <header class="card-header">
                <div class="card-meta">
                    <span class="category-badge">{s["category"]}</span>
                    <span class="node-badge">node: {s["node_type"]}</span>
                </div>
                <h2 class="card-title">{title_escaped}</h2>
                <p class="card-desc">{desc_escaped}</p>
            </header>

            <div class="tab-container">
                <!-- Radio Controls for Pure CSS Tab Switching -->
                <input type="radio" name="{tab_name}" id="{tab_name}-preview"
                       class="tab-radio tab-radio-1" checked>
                <input type="radio" name="{tab_name}" id="{tab_name}-adoc"
                       class="tab-radio tab-radio-2">
                <input type="radio" name="{tab_name}" id="{tab_name}-asg"
                       class="tab-radio tab-radio-3">
                <input type="radio" name="{tab_name}" id="{tab_name}-html"
                       class="tab-radio tab-radio-4">

                <!-- Tab Navigation Bar -->
                <nav class="tab-nav">
                    <label for="{tab_name}-preview" class="tab-label label-1">
                        ✨ Live {format_label} Preview
                    </label>
                    <label for="{tab_name}-adoc" class="tab-label label-2">
                        📄 AsciiDoc Source
                    </label>
                    <label for="{tab_name}-asg" class="tab-label label-3">
                        🌳 Resolved ASG JSON
                    </label>
                    <label for="{tab_name}-html" class="tab-label label-4">
                        💻 Rendered {format_label} Source
                    </label>
                </nav>

                <!-- Tab Content Panels -->
                <div class="tab-panels">
                    <div class="tab-panel panel-preview">
                        <div class="preview-surface">
                            {rendered_output}
                        </div>
                    </div>
                    <div class="tab-panel panel-adoc">
                        <pre class="code-block language-asciidoc"><code>{adoc_escaped}</code></pre>
                    </div>
                    <div class="tab-panel panel-asg">
                        <pre class="code-block language-json"><code>{asg_escaped}</code></pre>
                    </div>
                    <div class="tab-panel panel-html">
                        <pre class="code-block language-html"><code>{html_escaped}</code></pre>
                    </div>
                </div>
            </div>
        </article>
        """
        cards_html.append(card_markup)

    nav_rendered = "\n".join(nav_links)
    cards_rendered = "\n".join(cards_html)

    # Peer gallery link
    if is_xhtml:
        peer_link = '<a href="index.html" class="pill-badge">→ View HTML5 Gallery</a>'
    else:
        peer_link = '<a href="index-xhtml.html" class="pill-badge">→ View XHTML Gallery</a>'

    # Assemble complete document with embedded Vanilla CSS
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AsciiDoctype {format_label} Showcase Gallery (Zero-JS E2E Node Gallery)</title>
    <style>
{css_content}
    </style>
</head>
<body>
    <!-- Sidebar Category Navigation -->
    <aside class="sidebar">
        <div class="brand-block">
            <div class="brand-title">AsciiDoctype</div>
            <p class="brand-desc">{format_label} Node Showcase Gallery</p>
        </div>
        <nav class="nav-list">
            {nav_rendered}
        </nav>
    </aside>

    <!-- Main Showcase Stage -->
    <main class="main-stage">
        <header class="stage-hero">
            <h1 class="hero-title">AsciiDoctype {format_label} Node Gallery</h1>
            <p class="hero-lead">
                A live, end-to-end interactive showcase of all 39 AsciiDoc ASG node structures
                rendered via AsciiDoctype into <strong>{format_label}</strong>. Built with
                100% pure HTML5 and Vanilla CSS3 without JavaScript or external frameworks.
            </p>
            <div class="hero-badges">
                <span class="pill-badge">⚡ 100% Pure HTML5 / CSS3</span>
                <span class="pill-badge">🛡️ Zero JavaScript / TypeScript</span>
                <span class="pill-badge">🎯 All 39 ASG Node Types</span>
                <span class="pill-badge">📐 Target: {format_label}</span>
                {peer_link}
            </div>
        </header>

        <section class="showcase-grid">
            {cards_rendered}
        </section>
    </main>
</body>
</html>
"""
    return full_html


def main() -> None:
    """Generate both HTML5 and XHTML showcase gallery files."""
    GALLERY_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating AsciiDoctype Zero-JS Showcase Gallery (HTML5)...")
    html5_content = generate_gallery_html(target_format="html5")
    OUTPUT_HTML5.write_text(html5_content, encoding="utf-8")
    print(f"✅ HTML5 gallery: {OUTPUT_HTML5}")

    print("Generating AsciiDoctype Zero-JS Showcase Gallery (XHTML)...")
    xhtml_content = generate_gallery_html(target_format="xhtml")
    OUTPUT_XHTML.write_text(xhtml_content, encoding="utf-8")
    print(f"✅ XHTML gallery: {OUTPUT_XHTML}")


if __name__ == "__main__":
    main()
