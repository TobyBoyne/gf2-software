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


@pytest.mark.parametrize("parser", ["filecontents"], indirect=True)
def test_parser_creation(parser):
    """Create a parser object using fixtures"""
    assert isinstance(parser, Parser)


# --- SEMANTIC ERRORS ---


@pytest.mark.parametrize(
    "parser", ["DEVICE G1: XOR; CONNECT G1 -> G2.I1;"], indirect=True
)
def test_raises_device_reference_error(parser):
    parser.parse_network()
    print("abc", parser.errorlog.error_counts())
    assert parser.errorlog.contains_error(errorlog.DeviceReferenceError)


@pytest.mark.parametrize(
    "parser", ["DEVICE G1: XOR, G2: XOR; CONNECT G1 -> G2.NOTVALID;"], indirect=True
)
def test_raises_port_reference_error(parser):
    parser.parse_network()
    print("jkl", parser.errorlog.error_counts())

    assert parser.errorlog.contains_error(errorlog.PortReferenceError)


@pytest.mark.parametrize(
    "parser", ["DEVICE", "CONNECT", "MONITOR", "INPUTS"], indirect=True
)
def test_raises_protected_keyword_error(parser):

    """Test if the parser correctly raises a ProtectedKeywordError."""
    parser.next_symbol()
    with pytest.raises(errorlog.ProtectedKeywordError):
        parser.devicename()


@pytest.mark.parametrize(
    "parser",
    [
        "DEVICE G1: XOR, SW1: SWITCH 0, SW2: SWITCH 0; CONNECT SW1 -> G1.I1, SW2 -> G1.I1;"
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
    parser.next_symbol()
    with pytest.raises(errorlog.NameSyntaxError):
        parser.devicename()


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
    parser.next_symbol()
    parser.device()
    assert parser.errorlog.contains_error(errorlog.DeviceDefinitionError)


@pytest.mark.parametrize(
    "parser", ["SW1: SWITCH 1", "CLK1: CLOCK 10", "CLK2: CLOCK 1"], indirect=True
)
def test_parse_devicelist_raises_missing_keyword_error(parser):
    """Test if the parser correctly raises a MissingKeywordError.
    Occurs when the DEVICE Keyword does not precede the device list."""
    parser.next_symbol()
    parser.devicelist()
    assert parser.errorlog.contains_error(errorlog.MissingKeywordError)
