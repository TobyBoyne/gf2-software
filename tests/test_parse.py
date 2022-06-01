import pytest
import errorlog
from devices import Devices
from monitors import Monitors
from names import Names
from network import Network
from scanner import Scanner
from parse import Parser


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


@pytest.mark.parametrize('parser', ['filecontents'], indirect=True)
def test_parser_creation(parser):
    """Create a parser object using fixtures"""
    assert isinstance(parser, Parser)



devicename_test_files_1 = ["DEVICE", "CONNECT", "MONITOR", "INPUTS"]


@pytest.mark.parametrize("parser", devicename_test_files_1, indirect=True)
def test_parse_raises_semantic_errors_1(parser):
    """Test if the parser correctly raises a ProtectedKeywordError."""
    parser.next_symbol()
    with pytest.raises(errorlog.ProtectedKeywordError):
        parser.devicename()


devicename_test_files_2 = [",NOR", ":G1:", "0SW", "\t;CLK1"]


@pytest.mark.parametrize("parser", devicename_test_files_2, indirect=True)
def test_parse_raises_syntax_errors_1(parser):
    """Test if the parser correctly raises a NameSyntaxError.

    Error occurs when a name does not start at a letter"""
    parser.next_symbol()
    with pytest.raises(errorlog.NameSyntaxError):
        parser.devicename()


inputname_test_files = ["G1,I1", "G2:I2", "G3;I3", "G4 I4"]


@pytest.mark.parametrize("parser", inputname_test_files, indirect=True)
def test_parse_raises_syntax_errors_2(parser):
    """Test if the parser correctly raises a PunctuationError.

    Occurs when an input does not start with a dot. """
    parser.next_symbol()
    with pytest.raises(errorlog.PunctuationError):
        parser.inputname()