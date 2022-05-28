"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

from pyparsing import Optional
from devices import Devices
from errorlog import ErrorLog
from names import Names
from network import Network
from scanner import Scanner
from monitors import Monitors

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
        self.names: Names       = names
        self.devices: Devices   = devices
        self.network: Network   = network
        self.monitors: Monitors = monitors
        self.scanner: Scanner   = scanner
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
        if self.symbol.type == Scanner.KEYWORD and self.symbol.id == self.names.query(
            "DEVICE"
        ):
            self.next_symbol()
            self.device()
            while self.symbol.type == Scanner.COMMA:
                self.next_symbol()
                self.comment()
                self.device()
            if self.symbol.type == Scanner.SEMICOLON:
                self.next_symbol()
                self.comment()
            else:
                self.error(None, "Expected list to end in semicolon")
        else:
            self.error(None, "Expected device list")

    def connectionlist(self):
        if self.symbol.type == Scanner.KEYWORD and self.symbol.id == self.names.query(
            "CONNECT"
        ):
            self.next_symbol()
            self.connection()
            while self.symbol.type == Scanner.COMMA:
                self.next_symbol()
                self.comment()
                self.connection()
            if self.symbol.type == Scanner.SEMICOLON:
                self.comment()
                self.next_symbol()
            else:
                self.error(None, "Expected list to end in semicolon")
        else:
            self.error(None, "Expected connection list")

    def monitorlist(self):
        if self.symbol.type == Scanner.KEYWORD and self.symbol.id == self.names.query(
            "MONITOR"
        ):
            self.next_symbol()
            self.monitor()
            while self.symbol.type == Scanner.COMMA:
                self.next_symbol()
                self.comment()
                self.monitor()
            if self.symbol.type == Scanner.SEMICOLON:
                self.comment()
                self.next_symbol()
            else:
                self.error(None, "Expected list to end in semicolon")
        else:
            self.error(None, "Expected monitor list")

    # --- LIST ITEMS ---

    def device(self):
        device_id = self.devicename()
        device_kind = None
        device_property = None
        self.next_symbol()
        if self.symbol.type == Scanner.COLON:
            self.next_symbol()
            device_kind = self.symbol.id
            if self.symbol.type == Scanner.NAME and self.symbol.id == self.devices.SWITCH:
                self.next_symbol()
                if self.symbol.type == Scanner.NUMBER and self.symbol.id in (0, 1):
                    device_property = self.symbol.id
                    self.next_symbol()
                else:
                    self.error(None, "Switch must be followed by 0 (off) or 1 (on)")

            elif (
                self.symbol.type == Scanner.NAME
                and self.symbol.id == self.devices.CLOCK
            ):
                self.next_symbol()
                if self.symbol.type == Scanner.NUMBER:
                    device_property = self.symbol.id
                    self.next_symbol()
                else:
                    self.error(None, "Clock must be followed by a number (N cycles)")

            elif self.symbol.type == Scanner.NAME and self.symbol.id == self.devices.D_TYPE:
                self.next_symbol()

            elif (
                self.symbol.type == Scanner.NAME
                and self.symbol.id
                in self.devices.gate_types
            ):
                self.next_symbol()
                if self.symbol.type == Scanner.NUMBER:
                    device_property = self.symbol.id
                    self.next_symbol()
                    if (
                        self.symbol.type == Scanner.KEYWORD
                        and self.symbol.id == self.names.query("INPUTS")
                    ):
                        self.next_symbol()
                    else:
                        self.error(
                            None, "Number of inputs must be followed by keyword INPUTS"
                        )
            
            else:
                self.error(None, "Expected a valid device name")

        else:
            self.error(None, "Device definition requires a colon")

        # create the device
        if self.errorlog.no_errors():
            error_type = self.devices.make_device(device_id, device_kind, device_property)
            if error_type != self.devices.NO_ERROR:
                self.error(None, "Device error")

    def connection(self):
        out_device_id, out_port_id = self.outputname()
        if self.symbol.type == Scanner.ARROW:
            self.next_symbol()
            in_device_id, in_port_id = self.inputname()
        else:
            self.error(None, "Connections must be linked with an arrow (->)")

        # create the connection
        if self.errorlog.no_errors():
            error_type = self.network.make_connection(in_device_id, in_port_id, out_device_id, out_port_id)
            if error_type != self.network.NO_ERROR:
                self.error(None, f"Network error {error_type} {self.network.NO_ERROR}")

    def monitor(self):
        out_device_id, out_port_id = self.outputname()

        # create the monitor
        if self.errorlog.no_errors():
           self.monitors.make_monitor(out_device_id, out_port_id)

    # --- DEVICES, INPUTS, AND OUTPUTS ---

    def devicename(self):
        if self.symbol.type == Scanner.NAME:
            return self.symbol.id
        else:
            self.error(None, "Device name must be a valid alphanumeric identifier")

    def inputname(self):
        device_id = self.devicename()
        self.next_symbol()
        if self.symbol.type == Scanner.DOT:
            self.next_symbol()
            if self.symbol.type == Scanner.NAME:
                if self.symbol.id in self.devices.dtype_input_ids:
                    in_port_id = self.symbol.id
                    self.next_symbol()
                    return device_id, in_port_id
                else:
                    input_string = self.names.get_name_string(self.symbol.id)
                    if (
                        input_string is not None
                        and input_string[0] == "I"
                        and input_string[1:].isdigit()
                    ):
                        in_port_id = self.symbol.id
                        self.next_symbol()
                        return device_id, in_port_id

                    else:
                        self.error(None, "Must be a valid input")
            else:
                self.error(
                    None, "For an input, dot must be followed by an alphanumeric name"
                )
        else:
            self.error(None, "Not an input - must have a dot")

    def outputname(self):
        device_id = self.devicename()
        self.next_symbol()
        if self.symbol.type == Scanner.DOT:
            self.next_symbol()
            if self.symbol.type == Scanner.NAME:
                if self.symbol.id in self.devices.dtype_output_ids:
                    out_port_id = self.symbol.id
                    self.next_symbol()
                    return device_id, out_port_id
                else:
                    self.error(
                        None,
                        "Must be a valid output name",
                    )
            else:
                self.error(None, "Symbol must be a name")
        else:
            return device_id, None

    # --- COMMENT ---

    def comment(self):
        """Ignore all symbols between two slash symbols"""
        if self.symbol.type == Scanner.SLASH:
            self.next_symbol()
            while self.symbol.type != Scanner.SLASH:
                self.next_symbol()
            # continue from symbol after comment
            self.next_symbol()
