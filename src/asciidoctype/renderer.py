"""AsciiDoctype document rendering engine."""
from pathlib import Path
from typing import Any, Dict, List, Optional

from chameleon import PageTemplateLoader

from .exceptions import AsciiDoctypeRenderingError


class AsciiDoctypeRenderer:
    """Renders AsciiDoctrine ASG nodes into HTML5 or XHTML string fragments."""

    def __init__(
        self,
        target_format: str = "html5",
        search_paths: Optional[List[Path]] = None,
    ):
        """Initializes the rendering engine with format choices and template search paths."""
        self.target_format = target_format.lower()
        if self.target_format not in ("html5", "xhtml"):
            raise ValueError("Target target_format must be 'html5' or 'xhtml'")

        base_dir = Path(__file__).parent.resolve()
        core_fallback = base_dir / "core_templates" / self.target_format

        self.search_paths: List[Path] = list(search_paths) if search_paths else []
        self.search_paths.append(core_fallback)

        self.loader = PageTemplateLoader(
            [str(p) for p in self.search_paths],
            default_extension=".html",
        )

    def render(self, node: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
        """Central dispatch router for resolving ASG nodes recursively."""
        if not isinstance(node, dict) or "name" not in node:
            raise TypeError("Invalid node structure passed to rendering processor.")

        ctx = context or {}
        node_name = node["name"]

        try:
            try:
                template = self.loader[f"{node_name}.html"]
            except ValueError:
                template = self.loader["fallback_container.html"]

            res: str = template(node=node, renderer=self, ctx=ctx)
            return res
        except Exception as err:
            node_id = node.get("name", "unknown")
            raise AsciiDoctypeRenderingError(
                f"Critical rendering failure processing structural node entity: '{node_id}' "
                f"Target Specification Pipeline: [{self.target_format}]. Base Error: {err!s}"
            ) from err
