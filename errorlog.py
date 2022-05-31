from typing import TYPE_CHECKING, Optional
from names import Names

if TYPE_CHECKING:
    from scanner import Symbol

class ErrorLog:
    def __init__(self):
        self.errors = {}

        self._error_names = Names()

        self.SYNTAXERRORS = [
            self.PUNCTUATION,
            self.DEVICE,
            self.MISSINGKEYWORD,
            self.NAME,
        ] = self._error_names.lookup([
            "PunctuationError",
            "DeviceDefinitionError",
            "MissingKeywordError",
            "NameError",
        ])

        self.SEMANTICERRORS = [
            self.REFERENCE,
            self.KEYWORD,
            self.CONNECTION,
            self.QUALIFIER,
            self.GATESPECIFIC,
            self.OUTOFBOUNDS,
        ] = self._error_names.lookup([
            "ReferenceError",
            "KeywordError",
            "ConnectionError",
            "QualifierError",
            "GateSpecificError",
            "OutOfBoundsError",
        ])

    def __call__(self, symbol: 'Symbol', error_type: Optional[int], error_message=""):
        error_name = self._error_names.get_name_string(error_type)
        print(f"{error_name}: {error_message} \n"
              f" > error on line {symbol.cursor_line}, column {symbol.cursor_column}")

        self.errors[error_type] = self.errors.get(error_type, 0) + 1

    def no_errors(self):
        return len(self.errors) == 0

