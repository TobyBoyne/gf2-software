"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""


from lib2to3.pgen2.token import NUMBER
from typing import Union, TYPE_CHECKING
from os import PathLike

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

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None


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

    SYMBOL_TYPES_LIST = [COMMA, SEMICOLON, COLON, KEYWORD, NUMBER,
        NAME, ARROW, EOF] = range(8)

    KEYWORDS_LIST = ["DEVICES", "CONNECT", "MONITOR"]
    
    def __init__(self, path: Union[str, PathLike], names: Names):
        """Open specified file and initialise reserved words and IDs."""

        self.names = names
        self.file = open(path, "r")

        [self.DEVICES_ID, self.CONNECT_ID, 
            self.MONITOR_ID] = self.names.lookup(Scanner.KEYWORDS_LIST)
        self.cur: str = "" # current character


    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        self.get_next_character()

        # name
        if self.cur.isalpha():
            name_string = self.get_name()
            if name_string in Scanner.KEYWORDS_LIST:
                symbol.type = Scanner.KEYWORD
            else:
                symbol.type = Scanner.NAME
            symbol.id, = self.names.lookup([name_string])

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
                self.advance()
            else:
                print("Dash must be followed by an arrow")

        elif self.cur == ",":
            symbol.type = Scanner.COMMA
            self.advance()

        elif self.cur == ":":
            symbol.type = Scanner.COLON
            self.advance()

        elif self.cur == ";":
            symbol.type = Scanner.SEMICOLON
            self.advance()

        # eof
        elif self.cur == "":
            symbol.type = Scanner.EOF
        
        else:
            print("Not a valid symbol.")
            self.advance()
            
        return symbol

    def get_next_non_whitespace(self) -> None:
        """Returns the next non-whitespace character in the file"""
        while self.cur.isspace():
            self.cur = self.file.read(1)

    def get_name(self) -> str:
        """Starting at a letter, return a name given by a sequence of 
        alphanumeric characters"""
        name_string = ""
        while self.cur.isalpha():
            name_string += self.cur
        return name_string
