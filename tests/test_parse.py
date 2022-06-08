import pytest

import errorlog
from devices import Devices
from monitors import Monitors
from names import Names
from network import Network
from parse import Parser
from scanner import Scanner


def new_file(tmpdir, file_contents):
    """Return a file path to a mock file used in testing"""
    p = tmpdir.mkdir("sub").join("example.txt")
    p.write(file_contents)
    return p


@pytest.fixture(scope="function")
def parser(tmpdir, request):
    """Create a new parser object
    Note that the scope is *not* module, as a new Parser is required
    for each different file path"""
    path = new_file(tmpdir, request.param)

    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    scanner = Scanner(path, names)
    return Parser(names, devices, network, monitors, scanner)


# --- TEST WORKING PARSER ---


@pytest.mark.parametrize("parser", ["filecontents"], indirect=True)
def test_parser_creation(parser):
    """Create a parser object using fixtures"""
    assert isinstance(parser, Parser)


noerrors_files = [
    """
DEVICE  G1: AND 2 INPUTS, G2: AND 2 INPUTS, G3: NOR 2 INPUTS, G4: NOR 2 INPUTS,
    SW1: SWITCH 0, / S / SW2: SWITCH 1, / R / CLK1: CLOCK 10;

CONNECT SW1 -> G1.I1, SW2 -> G2.I2, CLK1 -> G1.I2, CLK1 -> G2.I1, G1 -> G3.I1,
    G2 -> G4.I2, G3 -> G4.I1, G4 -> G3.I2;

MONITOR G3, / Q / G4; / Qbar /
""",
    """
DEVICE  SW1: SWITCH 0, SW2: SWITCH 1, CLK: CLOCK 5, NAND: NAND 2 INPUTS, 
    OR: OR 2 INPUTS, NOR: NOR 2 INPUTS;

CONNECT SW1 -> NAND.I1, CLK -> NAND.I2, CLK -> OR.I1, SW2 -> OR.I2, NAND -> NOR.I1,
        OR -> NOR.I2;

MONITOR CLK, NOR;
""",
]

noerrors_device_names = [
    ["G1", "G2", "G3", "G4", "SW1", "SW2", "CLK1"],
    ["SW1", "SW2", "CLK", "NAND", "OR", "NOR"],
]

noerrors_monitor_names = [
    ["G3", "G4"],
    ["CLK", "NOR"],
]


@pytest.mark.parametrize(
    "parser,device_names,monitor_names",
    zip(noerrors_files, noerrors_device_names, noerrors_monitor_names),
    indirect=("parser",),
)
def test_correct_parsing(parser: Parser, device_names, monitor_names):
    parser.parse_network()
    assert parser.errorlog.no_errors()

    # Test device creation
    parsed_device_names = list(
        map(parser.names.get_name_string, parser.devices.find_devices())
    )
    assert parsed_device_names == device_names

    # Test network creation
    assert parser.network.check_network()

    # Test monitors creation
    parsed_monitors = parser.monitors.get_signal_names()[0]
    assert parsed_monitors == monitor_names


# --- SEMANTIC ERRORS ---


@pytest.mark.parametrize(
    "parser", ["DEVICE G1: XOR; CONNECT G1 -> G2.I1;"], indirect=True
)
def test_raises_device_reference_error(parser):
    parser.parse_network()
    assert parser.errorlog.contains_error(errorlog.DeviceReferenceError)


@pytest.mark.parametrize(
    "parser", ["DEVICE G1: XOR, G2: XOR; CONNECT G1 -> G2.NOTVALID;"], indirect=True
)
def test_raises_port_reference_error(parser):
    parser.parse_network()
    assert parser.errorlog.contains_error(errorlog.PortReferenceError)


@pytest.mark.parametrize(
    "parser", ["DEVICE", "CONNECT", "MONITOR", "INPUTS"], indirect=True
)
def test_raises_protected_keyword_error(parser):

    """Test if the parser correctly raises a ProtectedKeywordError."""
    parser._next_symbol()
    with pytest.raises(errorlog.ProtectedKeywordError):
        parser._devicename()


@pytest.mark.parametrize(
    "parser",
    [
        "DEVICE G1: XOR, SW1: SWITCH 0, SW2: SWITCH 0; \
        CONNECT SW1 -> G1.I1, SW2 -> G1.I1;"
    ],
    indirect=True,
)
def test_raises_multiple_connection_error(parser):
    parser.parse_network()
    assert parser.errorlog.contains_error(errorlog.MultipleConnectionError)


@pytest.mark.parametrize(
    "parser", ["DEVICE G1: AND 100 INPUTS;", "DEVICE G2: AND 0 INPUTS;"], indirect=True
)
def test_raises_outofbounds(parser):
    parser.parse_network()
    assert parser.errorlog.contains_error(errorlog.OutOfBoundsError)


# --- SYNTAX ERRORS ---


@pytest.mark.parametrize(
    "parser", ["DEVICE G1: XOR; CONNECT G1 -> G2; MONITOR G1.xx;"], indirect=True
)
def test_parse_network_raises_names_syntax_error(parser):
    """Test if the parser correctly raises a NameSyntax."""
    parser.parse_network()
    assert parser.errorlog.contains_error(errorlog.NameSyntaxError)


@pytest.mark.parametrize("parser", [",NOR", ":G1:", "0SW", "\t;CLK1"], indirect=True)
def test_parse_devicename_raises_name_syntax_error(parser):
    """Test if the parser correctly raises a NameSyntaxError.
    Error occurs when a name does not start at a letter"""
    parser._next_symbol()
    with pytest.raises(errorlog.NameSyntaxError):
        parser._devicename()


define_devices = "DEVICE G1: AND 4 INPUTS, G2: XOR;"
inputname_test_files = [
    define_devices + "CONNECT G2 -> G1;",
    define_devices + "CONNECT G2 -> G1;I3;",
    define_devices + "CONNECT G2 -> G1 I4;",
]


@pytest.mark.parametrize("parser", inputname_test_files, indirect=True)
def test_parse_network_raises_punctuation_error(parser):
    """Test if the parser correctly raises a PunctuationError.
    Occurs when an input does not start with a dot."""
    parser.parse_network()
    assert parser.errorlog.contains_error(errorlog.PunctuationError)


@pytest.mark.parametrize(
    "parser", ["SW1: SWITCH 2", "CLK1: CLOCK N", "CLK2: CLOCK "], indirect=True
)
def test_parse_device_raises_device_definition_error(parser):
    """Test if the parser correctly raises a DeviceDefinitionError.
    Occurs when a switch or clock is not followed by an appropriate number."""
    parser._next_symbol()
    parser._device()
    assert parser.errorlog.contains_error(errorlog.DeviceDefinitionError)


@pytest.mark.parametrize(
    "parser", ["SW1: SWITCH 1", "CLK1: CLOCK 10", "CLK2: CLOCK 1"], indirect=True
)
def test_parse_devicelist_raises_missing_keyword_error(parser):
    """Test if the parser correctly raises a MissingKeywordError.
    Occurs when the DEVICE Keyword does not precede the device list."""
    parser._next_symbol()
    parser._devicelist()
    assert parser.errorlog.contains_error(errorlog.MissingKeywordError)
