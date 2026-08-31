"""AsciiDoctype package.

`asciidoctype` provides headless HTML5 and XHTML rendering pipelines for
AsciiDoc Abstract Semantic Graph (ASG) structures.
"""

from .exceptions import (
    AsciiDoctypeRenderingError,
    AsciiDoctypeSecurityError,
    AsciiDoctypeSecurityWarning,
)
from .linter import TemplateFinding, audit_search_paths, audit_template
from .renderer import AsciiDoctypeRenderer, HighlighterCallable, TargetFormat, render

__version__ = "0.1.0a4"


__all__ = [
    "AsciiDoctypeRenderer",
    "AsciiDoctypeRenderingError",
    "AsciiDoctypeSecurityError",
    "AsciiDoctypeSecurityWarning",
    "HighlighterCallable",
    "TargetFormat",
    "TemplateFinding",
    "audit_search_paths",
    "audit_template",
    "render",
]
