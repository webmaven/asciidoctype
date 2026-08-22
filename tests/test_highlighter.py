"""Tests for syntax highlighter callable support and helpers in AsciiDoctypeRenderer."""

from asciidoctype import AsciiDoctypeRenderer, HighlighterCallable


def test_highlighter_callable_export():
    """Verify HighlighterCallable type alias is exported from asciidoctype."""
    assert HighlighterCallable is not None


def test_renderer_highlighter_initialization():
    """Verify AsciiDoctypeRenderer accepts and stores optional highlighter."""
    renderer_default = AsciiDoctypeRenderer()
    assert renderer_default.highlighter is None

    def custom_highlighter(code: str, lang: str) -> str:
        return f'<div class="pygments">{lang}:{code}</div>'

    renderer = AsciiDoctypeRenderer(highlighter=custom_highlighter)
    assert renderer.highlighter is custom_highlighter


def test_renderer_extract_text():
    """Verify extract_text extracts plain text from value or inlines."""
    renderer = AsciiDoctypeRenderer()

    # Leaf with value
    node_val = {"name": "source", "value": "print('hello')"}
    assert renderer.extract_text(node_val) == "print('hello')"

    # Inlines list
    node_inlines = {
        "name": "source",
        "inlines": [
            {"name": "text", "value": "def foo():\n"},
            {"name": "text", "value": "    return 42"},
        ],
    }
    assert renderer.extract_text(node_inlines) == "def foo():\n    return 42"

    # Nested inlines
    node_nested = {
        "name": "source",
        "inlines": [
            {
                "name": "span",
                "inlines": [{"name": "text", "value": "echo "}],
            },
            {"name": "text", "value": "done"},
        ],
    }
    assert renderer.extract_text(node_nested) == "echo done"

    # Empty / non-dict node
    assert renderer.extract_text({}) == ""
    assert renderer.extract_text(None) == ""


def test_renderer_highlight_code():
    """Verify highlight_code delegates to configured highlighter."""
    renderer_no_hl = AsciiDoctypeRenderer()
    node = {
        "name": "source",
        "attributes": {"language": "python"},
        "value": "print('test')",
    }
    assert renderer_no_hl.highlight_code(node) is None

    def sample_highlighter(code: str, lang: str):
        if lang == "python":
            return f'<pre class="py">{code}</pre>'
        return None

    renderer_hl = AsciiDoctypeRenderer(highlighter=sample_highlighter)
    assert renderer_hl.highlight_code(node) == "<pre class=\"py\">print('test')</pre>"

    # Unsupported lang returns None
    ruby_node = {
        "name": "source",
        "attributes": {"language": "ruby"},
        "value": "puts 'test'",
    }
    assert renderer_hl.highlight_code(ruby_node) is None

    # Language from root attribute fallback
    node_root_lang = {
        "name": "source",
        "language": "python",
        "value": "x = 1",
    }
    assert renderer_hl.highlight_code(node_root_lang) == '<pre class="py">x = 1</pre>'


def test_renderer_highlight_code_exception_fallback():
    """Verify highlight_code catches exceptions from highlighter and returns None."""

    def failing_highlighter(code: str, lang: str):
        raise RuntimeError("Highlighting failed")

    renderer = AsciiDoctypeRenderer(highlighter=failing_highlighter)
    node = {
        "name": "source",
        "attributes": {"language": "python"},
        "value": "print('fail')",
    }
    assert renderer.highlight_code(node) is None


def test_render_source_node_fallback_to_listing():
    """Verify 'source' node resolves candidates ['source.html', 'listing.html']."""
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "source",
        "type": "block",
        "attributes": {"language": "python"},
        "value": "print('hello')",
    }
    output = renderer.render(node)
    # listing.html produces a listingblock
    assert '<div class="listingblock"' in output
    assert "print('hello')" in output
