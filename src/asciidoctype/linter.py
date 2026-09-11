"""Template Security and Structural Linter.

`asciidoctype.linter` provides static analysis utilities for Chameleon ZPT
templates to detect syntax errors, structural flaws, and unsafe `structure`
directives that could introduce HTML escaping vulnerabilities.
"""

import re
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from chameleon.zpt.template import PageTemplate

from .exceptions import AsciiDoctypeSecurityError, AsciiDoctypeSecurityWarning

STRUCTURE_PATTERN = re.compile(
    r'(?:tal:(?:replace|content))\s*=\s*(?:"\s*structure\s+([^"]+)"|\'\s*structure\s+([^\']+)\')'
)

SAFE_EXPRESSIONS = (
    "renderer.render",
    "latex2mathml",
    "asciimath2mathml",
)

_audit_cache: Dict[Tuple[Tuple[str, ...], float], List["TemplateFinding"]] = {}


def clear_audit_cache() -> None:
    """Clear the in-memory template audit cache."""
    _audit_cache.clear()


@dataclass
class TemplateFinding:
    """Represents a diagnostic finding discovered during template static analysis.

    [attributes]
    `template_name` (str):: Filename or identifier of the audited template.
    `line_number` (int):: Line number where the pattern was detected.
    `expression` (str):: The extracted expression argument.
    `severity` (str):: Severity classification (`"warning"`, `"error"`).
    `message` (str):: Human-readable explanation and remediation guidance.
    """

    template_name: str
    line_number: int
    expression: str
    severity: str
    message: str


def lint_template_source(
    source: str, template_name: str = "template.html"
) -> List[TemplateFinding]:
    """Analyze template source code for compilation errors and suspicious directives.

    [parameters]
    `source` (str):: Raw HTML/ZPT template markup string.
    `template_name` (str, optional):: Name of the template being analyzed. Defaults to
                                      `"template.html"`.

    [returns]
    `list[TemplateFinding]`:: Ordered list of detected diagnostics.
    """
    findings: List[TemplateFinding] = []

    # 1. Verify Chameleon syntax compilation
    try:
        PageTemplate(source)
    except Exception as err:
        findings.append(
            TemplateFinding(
                template_name=template_name,
                line_number=1,
                expression="",
                severity="error",
                message=f"Chameleon template compilation error: {err!s}",
            )
        )

    # 2. Check for unsafe structure directives (whitelisting passthrough.html)
    if template_name != "passthrough.html":
        for line_idx, line in enumerate(source.splitlines(), start=1):
            for match in STRUCTURE_PATTERN.finditer(line):
                expr = (match.group(1) or match.group(2) or "").strip()
                if not any(safe in expr for safe in SAFE_EXPRESSIONS):
                    findings.append(
                        TemplateFinding(
                            template_name=template_name,
                            line_number=line_idx,
                            expression=f"structure {expr}",
                            severity="warning",
                            message=(
                                "Suspicious 'structure' directive on unvetted expression "
                                f"'{expr}'. 'structure' disables HTML escaping and should "
                                "only be used for 'renderer.render(...)' or validated "
                                "markup generators."
                            ),
                        )
                    )

    return findings


def audit_template(template_path: Path) -> List[TemplateFinding]:
    """Audit a template file on the filesystem.

    [parameters]
    `template_path` (Path):: Path to the `.html` template file.

    [returns]
    `list[TemplateFinding]`:: Diagnostics found in the template.
    """
    if not template_path.is_file():
        return []
    source = template_path.read_text(encoding="utf-8")
    return lint_template_source(source, template_name=template_path.name)


def audit_template_directory(directory: Path, recursive: bool = True) -> List[TemplateFinding]:
    """Audit all `.html` templates within a given directory.

    [parameters]
    `directory` (Path):: Directory containing template files.
    `recursive` (bool, optional):: Whether to search child subdirectories. Defaults to `True`.

    [returns]
    `list[TemplateFinding]`:: Aggregated diagnostics across all discovered templates.
    """
    findings: List[TemplateFinding] = []
    if not directory.is_dir():
        return findings

    pattern = "**/*.html" if recursive else "*.html"
    for template_file in sorted(directory.glob(pattern)):
        findings.extend(audit_template(template_file))
    return findings


def audit_search_paths(search_paths: List[Path], strict: bool = False) -> List[TemplateFinding]:
    """Audit a list of template search paths, emitting warnings or raising security errors.

    [parameters]
    `search_paths` (list[Path]):: List of directories to audit.
    `strict` (bool, optional):: If `True`, raises `AsciiDoctypeSecurityError` on warnings.
                                Defaults to `False`.

    [returns]
    `list[TemplateFinding]`:: All findings recorded across all search paths.

    [raises]
    `AsciiDoctypeSecurityError`:: When `strict=True` and one or more findings are detected.
    """
    sorted_paths_tuple = tuple(str(p.resolve()) for p in sorted(search_paths, key=lambda x: str(x)))

    max_mtime = 0.0
    for path in search_paths:
        if path.is_dir():
            for template_file in path.glob("*.html"):
                try:
                    mtime = template_file.stat().st_mtime
                    if mtime > max_mtime:
                        max_mtime = mtime
                except OSError:
                    pass

    cache_key = (sorted_paths_tuple, max_mtime)
    if cache_key in _audit_cache:
        all_findings = _audit_cache[cache_key]
    else:
        all_findings = []
        for path in search_paths:
            if path.is_dir():
                findings = audit_template_directory(path, recursive=False)
                all_findings.extend(findings)
        _audit_cache[cache_key] = all_findings

    for finding in all_findings:
        if strict:
            raise AsciiDoctypeSecurityError(
                f"Security check failed in '{finding.template_name}': {finding.message}"
            )
        warnings.warn(
            f"Template security audit warning in '{finding.template_name}': {finding.message}",
            category=AsciiDoctypeSecurityWarning,
            stacklevel=3,
        )

    return all_findings
