"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

import errorlog
from devices import Devices
from monitors import Monitors
from names import Names
from network import Network
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
        self.names: Names = names
        self.devices: Devices = devices
        self.network: Network = network
        self.monitors: Monitors = monitors
        self.scanner: Scanner = scanner
        self.errorlog = errorlog.ErrorLog()

        self.symbol = None

    def next_symbol(self):
        """Scans the next symbol, and assigns it to `self.symbol`"""
        self.symbol = self.scanner.get_symbol()

    def error(
        self,
        err: errorlog.CustomException,
        stopping_symbols=(Scanner.COMMA, Scanner.SEMICOLON),
    ):
        err.set_error_pos(self.symbol)
        self.errorlog(err)

        # skip current symbol, keep reading until a stopping symbol is reached
        self.next_symbol()
        while self.symbol.type not in stopping_symbols + (Scanner.EOF,):
            self.next_symbol()

    def parse_network(self):
        """Parse the circuit definition file. Returns True if there are no
        errors in the circuit definition file."""
        self.next_symbol()

        self.devicelist()
        self.connectionlist()
        self.monitorlist()

        self.errorlog.print_errors(self.scanner.path)

        return self.errorlog.no_errors()

    # --- LISTS ---

    def devicelist(self):
        try:
            if (
                self.symbol.type == Scanner.KEYWORD
                and self.symbol.id == self.names.query("DEVICE")
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
                    raise errorlog.PunctuationError(
                        "Expected device list to end in a"
                        " semicolon, or device to end in a comma"
                    )
            else:
                raise errorlog.MissingKeywordError(
                    "Expected device list to begin with DEVICE"
                )
        except errorlog.CustomException as err:
            self.error(err, stopping_symbols=(Scanner.SEMICOLON,))

    def connectionlist(self):
        try:
            if (
                self.symbol.type == Scanner.KEYWORD
                and self.symbol.id == self.names.query("CONNECT")
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
                    raise errorlog.PunctuationError(
                        "Expected connection list to end in a"
                        " semicolon, or connection to end in a comma"
                    )
            else:
                print(self.symbol)
                raise errorlog.MissingKeywordError(
                    "Expected connection list to begin with CONNECT"
                )
        except errorlog.CustomException as err:
            self.error(err, stopping_symbols=(Scanner.SEMICOLON,))

    def monitorlist(self):
        try:
            if (
                self.symbol.type == Scanner.KEYWORD
                and self.symbol.id == self.names.query("MONITOR")
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
                    raise errorlog.PunctuationError(
                        "Expected monitor list to end in a"
                        " semicolon, or monitor to end in a comma"
                    )
            else:
                raise (
                    errorlog.MissingKeywordError(
                        "Expected monitor list to begin with MONITOR"
                    )
                )
        except errorlog.CustomException as err:
            self.error(err, stopping_symbols=(Scanner.SEMICOLON,))

    # --- LIST ITEMS ---

    def device(self):
        try:
            device_id = self.devicename()
            device_kind = None
            device_property = None
            self.next_symbol()
            if self.symbol.type == Scanner.COLON:
                self.next_symbol()
                device_kind = self.symbol.id
                if (
                    self.symbol.type == Scanner.NAME
                    and self.symbol.id == self.devices.SWITCH
                ):
                    self.next_symbol()
                    if self.symbol.type == Scanner.NUMBER and self.symbol.id in (0, 1):
                        device_property = self.symbol.id
                        self.next_symbol()
                    else:
                        raise (
                            errorlog.DeviceDefinitionError(
                                "Switch must be followed by 0 (off) or 1 (on)"
                            )
                        )

                elif (
                    self.symbol.type == Scanner.NAME
                    and self.symbol.id == self.devices.CLOCK
                ):
                    self.next_symbol()
                    if self.symbol.type == Scanner.NUMBER:
                        device_property = self.symbol.id
                        self.next_symbol()
                    else:
                        raise (
                            errorlog.DeviceDefinitionError(
                                "Clock must be followed by a number (N cycles)"
                            )
                        )

                elif self.symbol.type == Scanner.NAME and self.symbol.id in (
                    self.devices.D_TYPE,
                    self.devices.NOT,
                    self.devices.XOR,
                ):
                    self.next_symbol()

                elif (
                    self.symbol.type == Scanner.NAME
                    and self.symbol.id in self.devices.gate_types
                ):
                    self.next_symbol()
                    if self.symbol.type == Scanner.NUMBER:
                        device_property = self.symbol.id
                        if not 1 < device_property <= 16:
                            raise (
                                errorlog.OutOfBoundsError(
                                    f"Number of inputs must be between 1 and 16"
                                    f" inclusive. Got {device_property} inputs instead"
                                )
                            )
                        self.next_symbol()
                        if (
                            self.symbol.type == Scanner.KEYWORD
                            and self.symbol.id == self.names.query("INPUTS")
                        ):
                            self.next_symbol()
                        else:
                            raise (
                                errorlog.MissingKeywordError(
                                    "Number of inputs must be followed by keyword"
                                    " INPUTS"
                                )
                            )

                    else:
                        raise errorlog.DeviceDefinitionError(
                            "Gate must be followed by a number of inputs"
                        )

                else:
                    # raise error, giving the invalid name if applicable
                    device_name_msg = (
                        f" (got {self.names.get_name_string(self.symbol.id)})"
                        if self.symbol.type == Scanner.NAME
                        else ""
                    )
                    raise (
                        errorlog.NameSyntaxError(
                            "Expected a valid device name" + device_name_msg
                        )
                    )

            else:
                raise (errorlog.PunctuationError("Device definition requires a colon"))

        except errorlog.CustomException as err:
            self.error(err)

        # create the device
        finally:
            if self.errorlog.no_errors():
                error_type = self.devices.make_device(
                    device_id, device_kind, device_property
                )
                if error_type != self.devices.NO_ERROR:
                    self.error(None, "Device error")

    def connection(self):
        try:
            out_device_id, out_port_id = self.outputname()
            if self.symbol.type == Scanner.ARROW:
                self.next_symbol()
                in_device_id, in_port_id = self.inputname()
                in_device = self.devices.get_device(in_device_id)
                if in_device.inputs[in_port_id] is not None:
                    # Input is already in a connection
                    raise errorlog.MultipleConnectionError(
                        "This input has an existing connection - each input can only be"
                        "connected to a single output."
                    )
            else:
                raise (
                    errorlog.PunctuationError(
                        "Connections must be linked with an arrow (->)"
                    )
                )

        except errorlog.CustomException as err:
            self.error(err)

        # create the connection
        finally:
            if self.errorlog.no_errors():
                error_type = self.network.make_connection(
                    in_device_id, in_port_id, out_device_id, out_port_id
                )
                if error_type != self.network.NO_ERROR:
                    raise (
                        errorlog.CustomException(
                            f"Network error {error_type} {self.network.NO_ERROR}"
                        )
                    )

    def monitor(self):
        try:
            out_device_id, out_port_id = self.outputname()
        except errorlog.CustomException as err:
            self.error(err)
        # create the monitor
        finally:
            if self.errorlog.no_errors():
                self.monitors.make_monitor(out_device_id, out_port_id)

    # --- DEVICES, INPUTS, AND OUTPUTS ---

    def devicename(self):
        if self.symbol.type == Scanner.NAME:
            return self.symbol.id
        elif self.symbol.type == Scanner.KEYWORD:
            raise (errorlog.ProtectedKeywordError("Device name cannot be a keyword"))
        else:
            raise (
                errorlog.NameSyntaxError(
                    "Device name must be a valid alphanumeric identifier"
                )
            )

    def inputname(self):
        device_id = self.devicename()

        if self.devices.get_device(device_id) is None:
            raise errorlog.DeviceReferenceError(
                f"The device {self.names.get_name_string(device_id)} has not been"
                f" defined in the device list"
            )

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
                        raise (
                            errorlog.PortReferenceError(
                                f"The input port must begin with I, followed by digits;"
                                f" {input_string} is invalid"
                            )
                        )
            else:
                raise (
                    errorlog.NameSyntaxError(
                        "For an input, dot must be followed by an alphanumeric name"
                    )
                )

        else:
            raise (errorlog.PunctuationError("Not an input - must have a dot"))

    def outputname(self):
        device_id = self.devicename()

        if self.devices.get_device(device_id) is None:
            raise errorlog.DeviceReferenceError(
                f"The device {self.names.get_name_string(device_id)} has not been"
                f" defined in the device list"
            )

        self.next_symbol()
        if self.symbol.type == Scanner.DOT:
            self.next_symbol()
            if self.symbol.type == Scanner.NAME:
                if self.symbol.id in self.devices.dtype_output_ids:
                    out_port_id = self.symbol.id
                    self.next_symbol()
                    return device_id, out_port_id
                else:
                    raise (
                        errorlog.NameSyntaxError(
                            f"Output {self.names.get_name_string(self.symbol.id)} is"
                            f" not a valid output name"
                        )
                    )
            else:
                raise (errorlog.NameSyntaxError("Output must be an alphanumeric name"))
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
