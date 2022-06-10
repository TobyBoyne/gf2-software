"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from names import Names


class Symbol:
    """Encapsulate a symbol and store its properties.

    Attributes
    ----------
    type: the type of the symbol, as listed in Scanner.SYMBOL_TYPES_LIST.
    id: the id of the symbol - either a numerical value (for Scanner.NUMBER), or the
        id of the Symbol in the Names object.
    cursor_line: the line number of the Symbol within the input text file.
    cursor_column: the index of the Symbol within a line.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None

        self.cursor_line = None
        self.cursor_column = None

    def set_cursor_pos(self, line: int, col: int) -> None:
        """Set the position of the Symbol to the current cursor position."""
        self.cursor_line = line
        self.cursor_column = col

    def __repr__(self) -> str:
        """Return a representation for the Symbol class."""
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

    Class attributes
    ----------
    SYMBOL_TYPES_LIST: all symbols with associated index
    KEYWORDS_LIST: all keywords in language definition
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

    def __init__(self, path: str, names: "Names"):
        """Open specified file and initialise reserved words and IDs."""
        self.names = names
        self.path = path
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

    def _advance(self) -> None:
        """Get the next character in the file, and increment the cursor position."""
        self.cursor_column += 1
        self.cur = self.file.read(1)
        if self.cur == "\n":
            self.cursor_column = 0
            self.cursor_line += 1

    def get_symbol(self) -> Symbol:
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        self._get_next_non_whitespace()
        symbol.set_cursor_pos(self.cursor_line, self.cursor_column)

        # name
        if self.cur.isalpha():
            name_string = self._get_name()
            if name_string in Scanner.KEYWORDS_LIST:
                symbol.type = Scanner.KEYWORD
            else:
                symbol.type = Scanner.NAME
            (symbol.id,) = self.names.lookup([name_string])

        # number
        elif self.cur.isdigit():
            symbol.id = self._get_number()
            symbol.type = Scanner.NUMBER

        # punctuation
        elif self.cur == "-":
            # must be a part of character pair "->"
            self._advance()
            if self.cur == ">":
                symbol.type = Scanner.ARROW
            else:
                symbol.type = None

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
            self.file.close()

        else:
            pass
            # non-valid symbols are allowed in comments
            # no need to raise an error here

        if symbol.type in (
            None,
            Scanner.COMMA,
            Scanner.COLON,
            Scanner.SEMICOLON,
            Scanner.ARROW,
            Scanner.SLASH,
            Scanner.DOT,
        ):
            self._advance()

        return symbol

    def _get_next_non_whitespace(self) -> None:
        """Return the next non-whitespace character in the file."""
        while self.cur is None or self.cur.isspace():
            self._advance()

    def _get_name(self) -> str:
        """Convert a sequence of alphanumeric characters to a string."""
        name_string = ""
        while self.cur.isalnum():
            name_string += self.cur
            self._advance()
        return name_string

    def _get_number(self) -> int:
        """Convert a sequence of numeric characters to a number."""
        num_string = ""
        while self.cur.isdigit():
            num_string += self.cur
            self._advance()
        return int(num_string)
