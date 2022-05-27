"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

from errorlog import ErrorLog
from scanner import Scanner


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
        self.errorlog = ErrorLog()  # can get the errorlog from the scanner object

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
        self.next_symbol()

        self.devicelist()
        self.connectionlist()
        self.monitorlist()

        return True

    # --- LISTS ---

    def devicelist(self):
        if self.symbol.type == Scanner.KEYWORD and self.symbol.id == Scanner.DEVICE_ID:
            self.next_symbol()
            self.device()
            while self.symbol.type == self.scanner.COMMA:
                self.next_symbol()
                self.comment()
                self.device()
            if self.symbol.type == self.scanner.SEMICOLON:
                self.next_symbol()
                self.comment()
            else:
                self.error(None, "Expected list to end in semicolon")
        else:
            self.error(None, "Expected device list")

    def connectionlist(self):
        if self.symbol.type == Scanner.KEYWORD and self.symbol.id == Scanner.CONNECT_ID:
            self.next_symbol()
            self.connection()
            while self.symbol.type == self.scanner.COMMA:
                self.next_symbol()
                self.comment()
                self.connection()
            if self.symbol.type == self.scanner.SEMICOLON:
                self.comment()
                self.next_symbol()
            else:
                self.error(None, "Expected list to end in semicolon")
        else:
            self.error(None, "Expected connection list")

    def monitorlist(self):
        if (
            self.symbol.type == Scanner.KEYWORD
            and self.symbol.id == Scanner.MONITORS_ID
        ):
            self.next_symbol()
            self.outputname()
            while self.symbol.type == self.scanner.COMMA:
                self.next_symbol()
                self.comment()
                self.outputname()
            if self.symbol.type == self.scanner.SEMICOLON:
                self.comment()
                self.next_symbol()
            else:
                self.error(None, "Expected list to end in semicolon")
        else:
            self.error(None, "Expected device list")

    # --- LIST ITEMS ---

    def device(self):
        self.devicename()
        self.next_symbol()
        if self.symbol.type == Scanner.COLON:
            self.next_symbol()
            if self.symbol.type == Scanner.NAME and self.symbol.id == Scanner.SWITCH:
                self.next_symbol()
                if self.symbol.type == Scanner.NUMBER and self.symbol.id in (0, 1):
                    self.next_symbol()
                else:
                    self.error(None, "Switch must be followed by 0 (off) or 1 (on)")

            elif self.symbol.type == Scanner.NAME and self.symbol.id == Scanner.CLOCK:
                self.next_symbol()
                if self.symbol.type == Scanner.NUMBER:
                    self.next_symbol()
                else:
                    self.error(None, "Clock must be followed by a number (N cycles)")

            elif (
                self.symbol.type == Scanner.NAME
                and self.symbol.id in Scanner.DEVICES_LIST
            ):
                self.next_symbol()
                if self.symbol.type == Scanner.NUMBER:
                    self.next_symbol()
                    if (
                        self.symbol.type == Scanner.KEYWORD
                        and self.symbol.id == Scanner.INPUTS_ID
                    ):
                        self.next_symbol()
                    else:
                        self.error(
                            None, "Number of inputs must be followed by keyword INPUTS"
                        )
            else:
                self.error(None, f"Expected a device name in {Scanner.DEVICES_LIST}")

        else:
            self.error(None, "Device definition requires a colon")

    def connection(self):
        self.outputname()
        if self.symbol.type == self.scanner.ARROW:
            self.symbol = self.scanner.get_symbol()
            self.inputname()
        else:
            self.error(None, "Connections must be linked with an arrow (->)")

    # --- DEVICES, INPUTS, AND OUTPUTS ---
    def devicename(self):
        pass

    def inputname(self):
        self.devicename()
        self.next_symbol()
        if self.symbol.type == Scanner.DOT:
            self.next_symbol()
            if self.symbol.type == Scanner.NAME:
                if self.symbol.id in Scanner.DEVICE_OUTPUTS_IDS:
                    self.next_symbol()
                if self.symbol.id[0] == "I" and self.symbol.id[1:].isdigit():
                    self.next_symbol()
                    pass
                else:
                    self.error(None, "Must be a valid input")
            else:
                self.error(
                    None, "For an input, dot must be followed by an alphanumeric name"
                )
        else:
            self.error(None, "Not an input - must have a dot")

    def outputname(self):
        self.devicename()
        self.next_symbol()
        if self.symbol.type == Scanner.DOT:
            self.next_symbol()
            if self.symbol.type == Scanner.NAME:
                if self.symbol.id in Scanner.DEVICE_OUTPUTS_IDS:
                    self.next_symbol()
                else:
                    self.error(
                        None,
                        f"Must be a valid output name {Scanner.DEVICE_OUTPUTS_IDS}",
                    )
            else:
                self.error(None, "Symbol must be a name")

    # --- COMMENT ---

    def comment(self):
        """Ignore all symbols between two slash symbols"""
        if self.symbol.type == Scanner.SLASH:
            self.next_symbol()
            while self.symbol.type != Scanner.SLASH:
                self.next_symbol()
            # continue from symbol after comment
            self.next_symbol()
