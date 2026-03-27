class AutoGuiError(Exception):
    """Base exception for baihe-autogui."""


class ValidationError(ValueError, AutoGuiError):
    """Raised when user input is invalid."""


class ElementNotFoundError(AssertionError, AutoGuiError):
    """Raised when a required element is missing."""


class ElementTimeoutError(TimeoutError, AutoGuiError):
    """Raised when waiting for an element times out."""


class ImageNotFoundError(AutoGuiError):
    """Raised when an image target cannot be found."""
