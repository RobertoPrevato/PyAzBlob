"""Common exceptions classes that can be reused in any application, and are not replaceable by built-in exceptions.
https://docs.python.org/3/library/exceptions.html
"""

class InvalidOperation(RuntimeError):
    """
    Exception to raise upon invalid operations - i.e. operations that don't make sense in their context.
    """
    pass


class ConfigurationError(Exception):
    """
    Exception to raise upon configuration error - i.e. when a configuration file is misconfigured.
    """
    pass


class ArgumentNullException(RuntimeError):
    def __init__(self, param_name):
        super().__init__("Parameter cannot be null or empty: `%s`" % param_name)


class InvalidArgument(Exception):
    pass


class MissingDependency(Exception):
    """Exception risen when code is executed in a Python interpreter that is lacking required dependencies."""
    def __init__(self, module_name):
        super().__init__("Missing dependency: `{}` - make sure that Python environment has dependencies listed in 'requirements.txt'".format(module_name))
