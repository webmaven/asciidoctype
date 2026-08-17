"""AsciiDoctype custom exceptions and warning definitions.

`asciidoctype.exceptions` defines the standard error hierarchy and warning types
used across rendering, template linting, and security audits.
"""


class AsciiDoctypeRenderingError(Exception):
    """Raised when rendering an ASG node fails or a critical pipeline error occurs.

    *Attributes:*

    `message` (str):: Detailed explanation of the rendering failure context.
    """

    pass


class AsciiDoctypeSecurityError(AsciiDoctypeRenderingError):
    """Raised when strict security enforcement detects an unsafe template or dangerous URI.

    *Attributes:*

    `message` (str):: Description of the security violation detected.
    """

    pass


class AsciiDoctypeSecurityWarning(UserWarning):
    """Emitted when non-strict template auditing discovers suspicious structure directives.

    *Attributes:*

    `message` (str):: Context of the potentially unsafe template pattern.
    """

    pass
