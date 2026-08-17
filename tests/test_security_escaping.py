"""Tests for XSS escaping, URI scheme sanitization, recursion limits, and strict mode."""

import pytest

from asciidoctype import AsciiDoctypeRenderer
from asciidoctype.exceptions import (
    AsciiDoctypeRenderingError,
    AsciiDoctypeSecurityError,
)


def test_text_node_html_entity_escaping():
    """Verify raw HTML in text nodes is escaped and does not inject tags."""
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "paragraph",
        "type": "block",
        "inlines": [
            {
                "name": "text",
                "type": "string",
                "value": "<script>alert('xss')</script> & a < b > c",
            }
        ],
    }
    output = renderer.render(node)
    assert "<script>" not in output
    assert "&lt;script&gt;alert('xss')&lt;/script&gt;" in output
    assert "&amp; a &lt; b &gt; c" in output


def test_listing_code_html_entity_escaping():
    """Verify code inside listing blocks is safely escaped."""
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "listing",
        "type": "block",
        "attributes": {"language": "html"},
        "inlines": [
            {
                "name": "text",
                "type": "string",
                "value": "<div><img src=x onerror=alert(1)></div>",
            }
        ],
    }
    output = renderer.render(node)
    assert "<img src=x onerror=alert(1)>" not in output
    assert "&lt;div&gt;&lt;img src=x onerror=alert(1)&gt;&lt;/div&gt;" in output


def test_passthrough_preserves_raw_html():
    """Verify explicit passthrough blocks preserve raw HTML markup intentionally."""
    renderer = AsciiDoctypeRenderer(target_format="html5")
    node = {
        "name": "passthrough",
        "type": "block",
        "value": '<div class="custom-widget"><span>Safe Widget</span></div>',
    }
    output = renderer.render(node)
    assert '<div class="custom-widget"><span>Safe Widget</span></div>' in output


def test_uri_scheme_sanitization_in_ref():
    """Verify dangerous URI schemes like javascript: are neutralized in link references."""
    renderer = AsciiDoctypeRenderer(target_format="html5", strict=False)
    node = {
        "name": "ref",
        "type": "inline",
        "target": "javascript:alert('pwned')",
        "inlines": [{"name": "text", "type": "string", "value": "Click me"}],
    }
    output = renderer.render(node)
    assert "javascript:" not in output
    assert '<a href=""' in output or 'href="#"' in output


def test_src_scheme_sanitization_in_media():
    """Verify dangerous URI schemes in media src attributes are neutralized."""
    renderer = AsciiDoctypeRenderer(target_format="html5", strict=False)
    node = {
        "name": "image",
        "type": "block",
        "src": "javascript:alert(1)",
    }
    output = renderer.render(node)
    assert "javascript:" not in output


def test_strict_mode_rejects_dangerous_uri():
    """Verify strict=True raises AsciiDoctypeSecurityError on dangerous URI schemes."""
    renderer = AsciiDoctypeRenderer(target_format="html5", strict=True)
    node = {
        "name": "ref",
        "type": "inline",
        "target": "javascript:alert(1)",
        "inlines": [{"name": "text", "type": "string", "value": "Click me"}],
    }
    with pytest.raises(AsciiDoctypeSecurityError):
        renderer.render(node)


def test_recursion_depth_limit_protection():
    """Verify recursion depth limit prevents infinite loops on cyclic or deeply nested ASTs."""
    renderer = AsciiDoctypeRenderer(target_format="html5")

    # Create cyclic structure
    node_a = {"name": "open", "type": "block", "blocks": []}
    node_b = {"name": "open", "type": "block", "blocks": [node_a]}
    node_a["blocks"].append(node_b)

    with pytest.raises(AsciiDoctypeRenderingError) as exc_info:
        renderer.render(node_a)
    assert "Recursion depth limit exceeded" in str(exc_info.value) or "Cycle detected" in str(
        exc_info.value
    )


def test_strict_mode_rejects_unknown_node_type():
    """Verify strict=True raises AsciiDoctypeRenderingError instead of falling back to container."""
    renderer = AsciiDoctypeRenderer(target_format="html5", strict=True)
    node = {"name": "completely_unknown_macro_type", "type": "block", "value": "test"}

    with pytest.raises(AsciiDoctypeRenderingError):
        renderer.render(node)
