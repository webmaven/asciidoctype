"""AsciiDoctype package.

`asciidoctype` provides headless HTML5 and XHTML rendering pipelines for
AsciiDoc Abstract Semantic Graph (ASG) structures.
"""

from .exceptions import (
    AsciiDoctypeRenderingError,
    AsciiDoctypeSecurityError,
    AsciiDoctypeSecurityWarning,
)
from .renderer import AsciiDoctypeRenderer, HighlighterCallable

__version__ = "0.1.0a3"


__all__ = [
    "AsciiDoctypeRenderer",
    "AsciiDoctypeRenderingError",
    "AsciiDoctypeSecurityError",
    "AsciiDoctypeSecurityWarning",
    "HighlighterCallable",
]
