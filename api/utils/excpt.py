"""Custom exception class."""


class BindError(EnvironmentError):
    """Handle error with bind."""


class ZoneError(KeyError):
    """Handle Error when a zone is invalid or a record is not found."""
