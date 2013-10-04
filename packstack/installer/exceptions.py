# -*- coding: utf-8 -*-

__all__ = (
    'PackStackError',

    'InstallError',
    'FlagValidationError',
    'MissingRequirements',

    'PluginError',
    'ParamProcessingError',
    'ParamValidationError',

    'NetworkError',
    'ScriptRuntimeError',
)


class PackStackError(Exception):
    """Default Exception class for packstack installer."""
    def __init__(self, *args, **kwargs):
        super(PackStackError, self).__init__(*args)
        self.stdout = kwargs.get('stdout', None)
        self.stderr = kwargs.get('stderr', None)


class PuppetError(Exception):
    """Raised when Puppet will have some problems."""


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
    """
    Raised when utils.ScriptRunner.execute does not end successfully.
    """
    pass


class ExecuteRuntimeError(PackStackError):
    """Raised when utils.execute does not end successfully."""


class SequenceError(PackStackError):
    """Exception for errors during setup sequence run."""
    pass
