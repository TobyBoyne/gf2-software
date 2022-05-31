"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""


from os import PathLike
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from names import Names


class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self, scanner: 'Scanner'):
        """Initialise symbol properties."""
        self.type = None
        self.id = None
        self.cursor_line = scanner.cursor_line
        self.cursor_column = scanner.cursor_column

    def __repr__(self):
        return f"S(type={self.type}, id={self.id})"


class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Class variables are used for values that are constant for all Scanner
    instances. For example, the keywords are the same for all Scanners.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Class variables
    ----------
    SYMBOL_TYPES_LIST: all symbols with associated index
    KEYWORDS_LIST: all keywords in language definition

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    """

    SYMBOL_TYPES_LIST = [
        COMMA,
        SEMICOLON,
        COLON,
        DOT,
        SLASH,
        KEYWORD,
        NUMBER,
        NAME,
        ARROW,
        EOF,
        *_,
    ] = range(50)

    KEYWORDS_LIST = ["DEVICE", "CONNECT", "MONITOR", "INPUTS"]

    def __init__(self, path: Union[str, PathLike], names: "Names"):
        """Open specified file and initialise reserved words and IDs."""

        self.names = names
        self.file = open(path, "r")

        [
            self.DEVICE_ID,
            self.CONNECT_ID,
            self.MONITOR_ID,
            self.INPUTS_ID,
        ] = names.lookup(self.KEYWORDS_LIST)

        self.cur = None  # current character

        self.cursor_line = 1
        self.cursor_column = 1

    def advance(self):
        self.cursor_column += 1
        self.cur = self.file.read(1)

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol(self)
        self.get_next_non_whitespace()

        # name
        if self.cur.isalpha():
            name_string = self.get_name()
            if name_string in Scanner.KEYWORDS_LIST:
                symbol.type = Scanner.KEYWORD
            else:
                symbol.type = Scanner.NAME
            (symbol.id,) = self.names.lookup([name_string])

        # number
        elif self.cur.isdigit():
            symbol.id = self.get_number()
            symbol.type = Scanner.NUMBER

        # punctuation
        elif self.cur == "-":
            # must be a part of character pair "->"
            self.advance()
            if self.cur == ">":
                symbol.type = Scanner.ARROW
            else:
                print("Dash must be followed by an arrow")

        elif self.cur == ",":
            symbol.type = Scanner.COMMA

        elif self.cur == ":":
            symbol.type = Scanner.COLON

        elif self.cur == ";":
            symbol.type = Scanner.SEMICOLON

        elif self.cur == "/":
            symbol.type = Scanner.SLASH

        elif self.cur == ".":
            symbol.type = Scanner.DOT

        # eof
        elif self.cur == "":
            symbol.type = Scanner.EOF

        else:
            pass
            # non-valid symbols are allowed in comments
            # print(f"{self.cur} is not a valid symbol.")

        if symbol.type in (
            None,
            Scanner.COMMA,
            Scanner.COLON,
            Scanner.SEMICOLON,
            Scanner.ARROW,
            Scanner.SLASH,
            Scanner.DOT,
        ):
            self.advance()

        return symbol

    def get_next_non_whitespace(self) -> None:
        """Returns the next non-whitespace character in the file"""
        while self.cur is None or self.cur.isspace():
            self.advance()
            if self.cur == "\n":
                self.cursor_column = 0
                self.cursor_line += 1

    def get_name(self) -> str:
        """Starting at a letter, return a name given by a sequence of
        alphanumeric characters"""
        name_string = ""
        while self.cur.isalnum():
            name_string += self.cur
            self.advance()
        return name_string

    def get_number(self) -> int:
        """Starting at a digit, return a number given by a sequence of
        numeric characters"""
        num_string = ""
        while self.cur.isdigit():
            num_string += self.cur
            self.advance()
        return int(num_string)
