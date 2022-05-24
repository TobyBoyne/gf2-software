"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

from scanner import Scanner
from errorlog import ErrorLog

class Parser:

    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.netword = network
        self.monitors = monitors
        self.scanner: Scanner = scanner
        self.errorlog = ErrorLog()

        self.symbol = None

    def next_symbol(self):
        """Scans the next symbol, and assigns it to `self.symbol`"""
        self.symbol = self.scanner.get_symbol()

    def error(self, errortype, errormessage):
        self.errorlog(errortype, errormessage)

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.


        return True

    def device(self):
        pass

    def connection(self):
        self.outputname()
        if self.symbol.type == self.scanner.EQUALS:
            self.symbol = self.scanner.get_symbol()
            self.inputname()
        else:
            self.errorlog()

    def devicename(self):
        pass

    def inputname(self):
        self.devicename()
        self.next_symbol()
        if self.symbol.type == Scanner.DOT:
            self.next_symbol()
            # TODO: ensure this is LL(1) compliant
            if self.symbol.type == Scanner.NAME:
                if self.symbol.id[0] == "I" and self.symbol.id[1:].isalnum():
                    self.next_symbol
                    pass
                else:
                    self.error(None, "Must be a valid input")
            else:
                self.error(None, "Symbol must be a name")
        else:
            self.error(None, "Not an input - must have a dot")

    def outputname(self):
        self.devicename()
        self.next_symbol()
        if self.symbol.type == Scanner.DOT:
            self.next_symbol()
            if self.symbol.type == Scanner.NAME:
                if self.symbol.id in Scanner.OUTPUTS_LIST:
                    self.next_symbol()
                    pass
                else:
                    self.error(None, f"Must be a valid output name {Scanner.OUTPUTS_LIST}")
            else:
                self.error(None, "Symbol must be a name")
            

    def comment(self):
        """Ignore all symbols between two slash symbols"""
        if self.symbol.type == Scanner.SLASH:
            self.next_symbol()
            while self.symbol.type != Scanner.SLASH:
                self.next_symbol()
        
        self.next_symbol()