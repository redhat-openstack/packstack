# -*- coding: utf-8 -*-

__all__ = (
    'PackStackError',

    'InstallError',
    'FlagValidationError',

    'PluginError',
    'ParamProcessingError',

    'NetworkError',
    'ScriptRuntimeError',
)


class PackStackError(Exception):
    """Default Exception class for packstack installer."""
    pass


class MissingRequirements(PackStackError):
    """Raised when minimum install requirements are not met."""
    pass


class InstallError(PackStackError):
    """Exception for generic errors during setup run."""
    pass

class FlagValidationError(InstallError):
    """Raised when single flag validation fails."""
    pass

class ParamValidationError(InstallError):
    """Raised when parameter value validation fails."""
    pass


class PluginError(PackStackError):
    pass

class ParamProcessingError(PluginError):
    pass


class NetworkError(PackStackError):
    """Should be used for packstack's network failures."""
    pass


class ScriptRuntimeError(PackStackError):
    """Raised when ScriptRunner.execute does not end successfully."""
    pass
