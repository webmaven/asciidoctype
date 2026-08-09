"""Test project environment and dependencies setup."""
import asciidoctype


def test_asciidoctype_import():
    """Verify that asciidoctype package is importable."""
    assert asciidoctype.__version__ is not None
