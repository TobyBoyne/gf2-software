"""Record and display errors using custom exceptions.

File containing custom exceptions, and the ErrorLog class used for
reporting and tracking errors in the file.

CustomExceptions are used to prevent overlap with inbuilt Python Exceptions
"""


from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from scanner import Symbol


class CustomException(BaseException):
    """A base Exception class used for the syntax and semantic errors.

    Attributes
    ----------
    error_line: the line number of the Symbol that caused the error within the input 
        text file.
    error_column: the index of the Symbol within a line.
    """

    def __init__(self, *args):
        """Create the exception, passing any arguments to the BaseException.

        Parameters
        ----------
        *args: list of arguments passed into the BaseException class. Typically only one
            argument, the error message, is passed to __init__
        """
        super().__init__(*args)
        self.error_line = None
        self.error_column = None

    def set_error_pos(self, symbol: "Symbol"):
        """Set the position of the error to the cursor position of the Symbol."""
        self.cursor_line = symbol.cursor_line
        self.cursor_column = symbol.cursor_column

    def name(self) -> str:
        """Return the name of the error type."""
        return type(self).__name__


# --- SYNTAX ERRORS ---


class PunctuationError(CustomException):
    """Raised when a punctuation symbol (colon, comma, etc.) is missing."""


class DeviceDefinitionError(CustomException):
    """Raised when a device is defined incorrectly."""


class MissingKeywordError(CustomException):
    """Raised when a keyword (DEVICE, CONNECT, MONITOR, INPUTS) is missing."""


class NameSyntaxError(CustomException):
    """Raised when a device name is invalid (i.e. not alphanumeric)."""


# --- SEMANTIC ERRORS ---


class DeviceReferenceError(CustomException):
    """Raised when a device is referenced without being properly defined.
    
    This uses the Devices.device_list, and so may be raised if a device is defined in 
    the file but not created due to other errors.
    """


class PortReferenceError(CustomException):
    """Raised when an input/output port is referenced but doesn't exist on device."""


class ProtectedKeywordError(CustomException):
    """Raised when a device or port name clashes with a keyword."""


class MultipleConnectionError(CustomException):
    """Raised when multiple outputs are connected to the same input."""


class OutOfBoundsError(CustomException):
    """Raised when a numerical value is outside the valid range.
    
    Used in gate devices, where the number of inputs is in the range [0, 16]
    """


class ErrorLog:
    """Record, store, and display both syntax and semantic errors that occur during parsing.

    The errors are stored as instances of `CustomException`.

    `self.errors` stores a list of the CustomException objects
    """

    def __init__(self):
        """Create an empty list of errors."""
        self.errors: List[CustomException] = []

    def __call__(self, err: CustomException) -> None:
        """Add the new error to the list of errors."""
        self.errors.append(err)

    def no_errors(self) -> bool:
        """Return True if no errors have been raised."""
        return len(self.errors) == 0

    def error_counts(self) -> Dict[str, int]:
        """Return a dictionary with the type and frequency of errors.
        
        Mainly useful for testing to ensure the correct errors are raised.
        """
        counts = {}
        for err in self.errors:
            error_name = err.name()
            counts[error_name] = counts.get(error_name, 0) + 1
        return counts

    def contains_error(self, error_type: CustomException) -> bool:
        """Return True if the error of the given type has been raised.
        
        Parameters
        ----------
        error_type: the type of the error that is being checked.
        """
        return any(isinstance(err, error_type) for err in self.errors)

    def print_errors(self, path: str) -> None:
        """Print all the errors found in parse_network, and their line position."""
        with open(path, "r") as file:
            lines = [l.strip("\n") for l in file.readlines()] + [""]

            for err in self.errors:
                line_str = lines[err.cursor_line - 1]
                cursor_pos_str = f"(Ln {err.cursor_line}, Col {err.cursor_column})"

                print(
                    f"{err.name()}: {err}\n"
                    f"{cursor_pos_str} {line_str}\n"
                    f"{' '*len(cursor_pos_str)} {' '*err.cursor_column}^\n"
                )
