"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.
"""

from typing import Tuple, Optional

import errorlog
from devices import Devices
from monitors import Monitors
from names import Names
from network import Network
from scanner import Scanner, Symbol


class Parser:
    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Attributes
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.
    errorlog: instance of the errorlog.ErrorLog() class.
    symbol: current symbol in the file, instance of scanner.Symbol() class.
    """

    def __init__(
        self,
        names: Names,
        devices: Devices,
        network: Network,
        monitors: Monitors,
        scanner: Scanner,
    ):
        """Initialise constants.

        Parameters
        ----------
        names: instance of the names.Names() class.
        devices: instance of the devices.Devices() class.
        network: instance of the network.Network() class.
        monitors: instance of the monitors.Monitors() class.
        scanner: instance of the scanner.Scanner() class.
        """
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner
        self.errorlog = errorlog.ErrorLog()

        self.symbol = None

    def _next_symbol(self) -> None:
        """Scan the next symbol, and assign it to `self.symbol`."""
        self.symbol = self.scanner.get_symbol()

    def _error(
        self,
        err: errorlog.CustomException,
        stopping_symbols=(Scanner.COMMA, Scanner.SEMICOLON),
    ) -> None:
        """Raise an error, and continue from the next possible space in the file.

        Parameters
        ----------
        err: error instance with error message.
        stopping_symbols: the symbols from which the scanner can safely continue
            reading.
        """
        err.set_error_pos(self.symbol)
        self.errorlog(err)

        # skip current symbol, keep reading until a stopping symbol is reached
        self._next_symbol()
        while self.symbol.type not in stopping_symbols + (Scanner.EOF,):
            self._next_symbol()

    def parse_network(self) -> bool:
        """Parse the circuit definition file.

        Return True if there are no errors in the circuit definition file. Also
        prints out all errors in the definition file using the ErrorLog object.
        """
        self._next_symbol()

        self._devicelist()
        self._connectionlist()
        self._monitorlist()

        self.errorlog.print_errors(self.scanner.path)

        return self.errorlog.no_errors()

    # --- LISTS ---

    def _devicelist(self) -> None:
        try:
            if (
                self.symbol.type == Scanner.KEYWORD
                and self.symbol.id == self.names.query("DEVICE")
            ):
                self._next_symbol()
                self._device()
                while self.symbol.type == Scanner.COMMA:
                    self._next_symbol()
                    self._comment()
                    self._device()
                if self.symbol.type == Scanner.SEMICOLON:
                    self._next_symbol()
                    self._comment()
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
            self._error(err, stopping_symbols=(Scanner.SEMICOLON,))

    def _connectionlist(self) -> None:
        try:
            if (
                self.symbol.type == Scanner.KEYWORD
                and self.symbol.id == self.names.query("CONNECT")
            ):
                self._next_symbol()
                self._connection()
                while self.symbol.type == Scanner.COMMA:
                    self._next_symbol()
                    self._comment()
                    self._connection()
                if self.symbol.type == Scanner.SEMICOLON:
                    self._comment()
                    self._next_symbol()
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
            self._error(err, stopping_symbols=(Scanner.SEMICOLON,))

    def _monitorlist(self) -> None:
        try:
            if (
                self.symbol.type == Scanner.KEYWORD
                and self.symbol.id == self.names.query("MONITOR")
            ):
                self._next_symbol()
                self._monitor()
                while self.symbol.type == Scanner.COMMA:
                    self._next_symbol()
                    self._comment()
                    self._monitor()
                if self.symbol.type == Scanner.SEMICOLON:
                    self._comment()
                    self._next_symbol()
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
            self._error(err, stopping_symbols=(Scanner.SEMICOLON,))

    # --- LIST ITEMS ---

    def _device(self) -> None:
        try:
            device_id = self._devicename()
            device_kind = None
            device_property = None
            self._next_symbol()
            if self.symbol.type == Scanner.COLON:
                self._next_symbol()
                device_kind = self.symbol.id
                if (
                    self.symbol.type == Scanner.NAME
                    and self.symbol.id == self.devices.SWITCH
                ):
                    self._next_symbol()
                    if self.symbol.type == Scanner.NUMBER and self.symbol.id in (0, 1):
                        device_property = self.symbol.id
                        self._next_symbol()
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
                    self._next_symbol()
                    if self.symbol.type == Scanner.NUMBER:
                        device_property = self.symbol.id
                        self._next_symbol()
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
                    self._next_symbol()

                elif (
                    self.symbol.type == Scanner.NAME
                    and self.symbol.id in self.devices.gate_types
                ):
                    self._next_symbol()
                    if self.symbol.type == Scanner.NUMBER:
                        device_property = self.symbol.id
                        if not 1 < device_property <= 16:
                            raise (
                                errorlog.OutOfBoundsError(
                                    f"Number of inputs must be between 1 and 16"
                                    f" inclusive. Got {device_property} inputs instead"
                                )
                            )
                        self._next_symbol()
                        if (
                            self.symbol.type == Scanner.KEYWORD
                            and self.symbol.id == self.names.query("INPUTS")
                        ):
                            self._next_symbol()
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
            self._error(err)

        # create the device
        finally:
            if self.errorlog.no_errors():
                error_type = self.devices.make_device(
                    device_id, device_kind, device_property
                )
                if error_type != self.devices.NO_ERROR:
                    self._error(None, "Device error")

    def _connection(self) -> None:
        try:
            out_device_id, out_port_id = self._outputname()
            if self.symbol.type == Scanner.ARROW:
                self._next_symbol()
                in_device_id, in_port_id = self._inputname()
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
            self._error(err)

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

    def _monitor(self) -> None:
        try:
            out_device_id, out_port_id = self._outputname()
        except errorlog.CustomException as err:
            self._error(err)

        # create the monitor
        finally:
            if self.errorlog.no_errors():
                self.monitors.make_monitor(out_device_id, out_port_id)

    # --- DEVICES, INPUTS, AND OUTPUTS ---

    def _devicename(self) -> Optional[Symbol]:
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

    def _inputname(self) -> Tuple[int, int]:
        device_id = self._devicename()

        if self.devices.get_device(device_id) is None:
            raise errorlog.DeviceReferenceError(
                f"The device {self.names.get_name_string(device_id)} has not been"
                f" defined in the device list"
            )

        self._next_symbol()
        if self.symbol.type == Scanner.DOT:
            self._next_symbol()
            if self.symbol.type == Scanner.NAME:
                if self.symbol.id in self.devices.dtype_input_ids:
                    in_port_id = self.symbol.id
                    self._next_symbol()
                    return device_id, in_port_id
                else:
                    input_string = self.names.get_name_string(self.symbol.id)
                    if (
                        input_string is not None
                        and input_string[0] == "I"
                        and input_string[1:].isdigit()
                    ):
                        in_port_id = self.symbol.id
                        self._next_symbol()
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

    def _outputname(self) -> Tuple[int, int]:
        device_id = self._devicename()

        if self.devices.get_device(device_id) is None:
            raise errorlog.DeviceReferenceError(
                f"The device {self.names.get_name_string(device_id)} has not been"
                f" defined in the device list"
            )

        self._next_symbol()
        if self.symbol.type == Scanner.DOT:
            self._next_symbol()
            if self.symbol.type == Scanner.NAME:
                if self.symbol.id in self.devices.dtype_output_ids:
                    out_port_id = self.symbol.id
                    self._next_symbol()
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

    def _comment(self) -> None:
        """Ignore all symbols between two slash symbols."""
        if self.symbol.type == Scanner.SLASH:
            self._next_symbol()
            while self.symbol.type != Scanner.SLASH:
                self._next_symbol()
            # continue from symbol after comment
            self._next_symbol()
