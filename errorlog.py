"""File containing custom exceptions, and the ErrorLog class used for
reporting and tracking errors in the file.

CustomExceptions are used to prevent overlap with inbuilt Python Exceptions"""


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scanner import Symbol


class CustomException(BaseException):
    """A base Exception class used for the syntax and semantic errors that arise during
    the parsing of the circuit definition file.

    Parameters
    ----------
    *args: list of arguments passed into the BaseException class. Typically only one
    argument, the error message, is passed to __init__

    Public methods
    --------------
    set_error_pos(self, symbol): Sets the cursor position at which the error
            occurs.

    name(self): Return the name string of the error"""

    def __init__(self, *args):
        super().__init__(*args)
        self.error_line = None
        self.error_column = None

    def set_error_pos(self, symbol: "Symbol"):
        self.cursor_line = symbol.cursor_line
        self.cursor_column = symbol.cursor_column

    def name(self):
        return type(self).__name__


# --- SYNTAX ERRORS ---


class PunctuationError(CustomException):
    pass


class DeviceDefinitionError(CustomException):
    pass


class MissingKeywordError(CustomException):
    pass


class NameSyntaxError(CustomException):
    pass


# --- SEMANTIC ERRORS ---


class DeviceReferenceError(CustomException):
    pass


class PortReferenceError(CustomException):
    pass


class ProtectedKeywordError(CustomException):
    pass


class MultipleConnectionError(CustomException):
    pass


class OutOfBoundsError(CustomException):
    pass


class ErrorLog:
    """Record, store, and display both syntax and semantic errors that occur during parsing.

    The errors are stored as instances of `CustomException`.

    `self.errors` stores a list of the CustomException objects

    Public methods
    --------------
    __call__(self, err): The instance is called with a CustomException to print
        and store the error.

    no_errors(self): Returns True if no errors have been raised

    error_counts(self): Returns a dictionary of the type and frequency of the errors
        encountered in parsing the file"""

    def __init__(self):
        self.errors = []

    def __call__(self, err: CustomException):
        self.errors.append(err)

        error_name = err.name()
        print(
            f"{error_name}: {err} \n"
            f" > error on line {err.cursor_line}, column {err.cursor_column}"
        )

    def no_errors(self):
        """Returns True if no errors have been raised"""
        return len(self.errors) == 0

    def error_counts(self):
        """Return a dictionary with the type and frequency of errors. Mainly
        useful for testing to ensure the correct errors are raised."""
        counts = {}
        for err in self.errors:
            error_name = err.name()
            counts[error_name] = counts.get(error_name, 0) + 1
        return counts

    def contains_error(self, error_type: CustomException):
        """Returns True if the error of the given type has been raised"""
        return any(isinstance(err, error_type) for err in self.errors)
